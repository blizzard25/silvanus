import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import {
  ActivitySubmission,
  ActivitySubmissionSchema,
  ActivityResponse,
  ActivityResponseSchema,
  ActivityTypeInfo,
  ActivityTypeInfoSchema,
  OAuthLoginResponse,
  OAuthLoginResponseSchema,
  OAuthCallbackResponse,
  OAuthCallbackResponseSchema,
  HealthResponse,
  HealthResponseSchema,
} from './models';
import {
  AuthenticationError,
  ValidationError,
  NetworkError,
  OAuthError,
  mapStatusCodeToError,
} from './exceptions';

/**
 * Configuration options for the Silvanus client
 */
export interface SilvanusClientConfig {
  baseUrl?: string;
  apiKey?: string;
  accessToken?: string;
  timeout?: number;
  maxRetries?: number;
}

/**
 * OAuth callback parameters
 */
export interface OAuthCallbackParams {
  provider: string;
  code: string;
  state: string;
  wallet_address: string;
  session_key: string;
  code_verifier?: string;
}

/**
 * Main Silvanus SDK client for TypeScript/JavaScript
 */
export class SilvanusClient {
  private readonly httpClient: AxiosInstance;
  private readonly maxRetries: number;
  private apiKey?: string;
  private accessToken?: string;

  constructor(config: SilvanusClientConfig = {}) {
    const {
      baseUrl = 'https://silvanus-a4nt.onrender.com',
      apiKey,
      accessToken,
      timeout = 30000,
      maxRetries = 3,
    } = config;

    this.apiKey = apiKey;
    this.accessToken = accessToken;
    this.maxRetries = maxRetries;

    this.httpClient = axios.create({
      baseURL: baseUrl,
      timeout,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.httpClient.interceptors.request.use((config) => {
      if (this.accessToken) {
        config.headers.Authorization = `Bearer ${this.accessToken}`;
      } else if (this.apiKey) {
        config.headers['X-API-Key'] = this.apiKey;
      }
      return config;
    });

    this.httpClient.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        throw this.handleError(error);
      }
    );
  }

  /**
   * Set API key for authentication
   */
  setApiKey(apiKey: string): void {
    this.apiKey = apiKey;
    this.accessToken = undefined;
  }

  /**
   * Set OAuth2.0 access token for authentication
   */
  setAccessToken(accessToken: string): void {
    this.accessToken = accessToken;
    this.apiKey = undefined;
  }

  /**
   * Check API health status
   */
  async healthCheck(): Promise<HealthResponse> {
    const response = await this.makeRequest<HealthResponse>('GET', '/healthz');
    return HealthResponseSchema.parse(response.data);
  }

  /**
   * Get supported activity types
   */
  async getActivityTypes(): Promise<ActivityTypeInfo[]> {
    const response = await this.makeRequest<ActivityTypeInfo[]>(
      'GET',
      '/activities/types'
    );
    return response.data.map((item) => ActivityTypeInfoSchema.parse(item));
  }

  /**
   * Submit green energy activity
   */
  async submitActivity(
    activity: ActivitySubmission,
    version: 'legacy' | 'v1' | 'v2' = 'v2'
  ): Promise<ActivityResponse> {
    const validatedActivity = ActivitySubmissionSchema.parse(activity);

    const endpoint = version === 'legacy' 
      ? '/activities/submit' 
      : `/${version}/activities/submit`;

    const response = await this.makeRequest<ActivityResponse>(
      'POST',
      endpoint,
      validatedActivity
    );

    return ActivityResponseSchema.parse(response.data);
  }

  /**
   * Initiate OAuth2.0 login flow
   */
  async oauthLogin(
    provider: string,
    redirectUri?: string,
    userId?: string
  ): Promise<OAuthLoginResponse> {
    const params = new URLSearchParams();
    if (redirectUri) params.append('redirect_uri', redirectUri);
    if (userId) params.append('user_id', userId);

    const queryString = params.toString();
    const endpoint = `/oauth/login/${provider}${queryString ? `?${queryString}` : ''}`;

    const response = await this.makeRequest<OAuthLoginResponse>('GET', endpoint);
    return OAuthLoginResponseSchema.parse(response.data);
  }

  /**
   * Complete OAuth2.0 callback flow
   */
  async oauthCallback(params: OAuthCallbackParams): Promise<OAuthCallbackResponse> {
    const {
      provider,
      code,
      state,
      wallet_address,
      session_key,
      code_verifier,
    } = params;

    const requestBody = {
      code,
      state,
      wallet_address,
      session_key,
      ...(code_verifier && { code_verifier }),
    };

    const response = await this.makeRequest<OAuthCallbackResponse>(
      'POST',
      `/oauth/callback/${provider}`,
      requestBody
    );

    return OAuthCallbackResponseSchema.parse(response.data);
  }

  /**
   * Make HTTP request with retry logic
   */
  private async makeRequest<T>(
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    endpoint: string,
    data?: any
  ): Promise<AxiosResponse<T>> {
    let lastError: Error;

    for (let attempt = 0; attempt <= this.maxRetries; attempt++) {
      try {
        const config = {
          method: method.toLowerCase(),
          url: endpoint,
          ...(data && { data }),
        };

        return await this.httpClient.request<T>(config);
      } catch (error) {
        lastError = error as Error;

        if (
          error instanceof AuthenticationError ||
          error instanceof ValidationError
        ) {
          throw error;
        }

        if (attempt === this.maxRetries) {
          throw error;
        }

        const delay = Math.pow(2, attempt) * 1000;
        await this.sleep(delay);
      }
    }

    throw lastError!;
  }

  /**
   * Handle HTTP errors and map to appropriate exceptions
   */
  private handleError(error: AxiosError): Error {
    if (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT') {
      return new NetworkError('Request timeout', undefined, error.response?.data);
    }

    if (!error.response) {
      return new NetworkError(
        error.message || 'Network error',
        undefined,
        error
      );
    }

    const { status, data } = error.response;
    let message = 'Unknown error';

    if (data) {
      if (typeof data === 'string') {
        message = data;
      } else if (typeof data === 'object' && data !== null) {
        const errorData = data as Record<string, any>;
        if ('detail' in errorData && errorData.detail) {
          message = errorData.detail;
        } else if ('message' in errorData && errorData.message) {
          message = errorData.message;
        } else if ('error' in errorData && errorData.error) {
          message = errorData.error;
        }
      }
    }

    if (error.config?.url?.includes('/oauth/')) {
      return new OAuthError(message, status, data);
    }

    return mapStatusCodeToError(status, message, data);
  }

  /**
   * Sleep utility for retry delays
   */
  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

/**
 * Default export for convenience
 */
export default SilvanusClient;
