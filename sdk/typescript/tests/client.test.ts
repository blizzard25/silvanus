import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import axios from 'axios';
import { SilvanusClient } from '../src/client';
import {
  AuthenticationError,
  ValidationError,
  RateLimitError,
  NetworkError,
  OAuthError,
} from '../src/exceptions';
import { ActivitySubmission } from '../src/models';

vi.mock('axios');
const mockedAxios = vi.mocked(axios);

describe('SilvanusClient', () => {
  let client: SilvanusClient;
  let mockAxiosInstance: any;

  beforeEach(() => {
    mockAxiosInstance = {
      request: vi.fn(),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
    };

    mockedAxios.create = vi.fn().mockReturnValue(mockAxiosInstance);
    client = new SilvanusClient({
      baseUrl: 'https://test-api.example.com',
      apiKey: 'test-api-key',
    });
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  describe('constructor', () => {
    it('should create client with default configuration', () => {
      const defaultClient = new SilvanusClient();
      expect(mockedAxios.create).toHaveBeenCalledWith({
        baseURL: 'https://silvanus-a4nt.onrender.com',
        timeout: 30000,
        headers: {
          'Content-Type': 'application/json',
        },
      });
    });

    it('should create client with custom configuration', () => {
      new SilvanusClient({
        baseUrl: 'https://custom-api.example.com',
        timeout: 60000,
        maxRetries: 5,
      });

      expect(mockedAxios.create).toHaveBeenCalledWith({
        baseURL: 'https://custom-api.example.com',
        timeout: 60000,
        headers: {
          'Content-Type': 'application/json',
        },
      });
    });
  });

  describe('authentication', () => {
    it('should set API key', () => {
      client.setApiKey('new-api-key');
      expect(client).toBeDefined();
    });

    it('should set access token', () => {
      client.setAccessToken('oauth-token');
      expect(client).toBeDefined();
    });
  });

  describe('healthCheck', () => {
    it('should return health status', async () => {
      const mockResponse = { data: { status: 'ok' } };
      mockAxiosInstance.request.mockResolvedValue(mockResponse);

      const result = await client.healthCheck();

      expect(mockAxiosInstance.request).toHaveBeenCalledWith({
        method: 'get',
        url: '/healthz',
      });
      expect(result).toEqual({ status: 'ok' });
    });

    it('should handle health check errors', async () => {
      const mockError = {
        response: { status: 500, data: { detail: 'Internal server error' } },
        config: { url: '/healthz' },
        isAxiosError: true,
      };
      mockAxiosInstance.request.mockRejectedValue(mockError);

      await expect(client.healthCheck()).rejects.toThrow('Internal server error');
    });
  });

  describe('getActivityTypes', () => {
    it('should return activity types', async () => {
      const mockResponse = {
        data: [
          {
            type: 'solar_export',
            description: 'Solar energy exported to grid',
            expectedDetails: ['panel_count', 'energy_exported'],
          },
        ],
      };
      mockAxiosInstance.request.mockResolvedValue(mockResponse);

      const result = await client.getActivityTypes();

      expect(mockAxiosInstance.request).toHaveBeenCalledWith({
        method: 'get',
        url: '/activities/types',
      });
      expect(result).toHaveLength(1);
      expect(result[0].type).toBe('solar_export');
    });
  });

  describe('submitActivity', () => {
    const validActivity: ActivitySubmission = {
      wallet_address: '0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2',
      activity_type: 'solar_export',
      value: 5.0,
      details: { panel_count: 10 },
    };

    it('should submit activity successfully', async () => {
      const mockResponse = {
        data: {
          txHash: '0x1234567890abcdef',
          status: 'confirmed',
        },
      };
      mockAxiosInstance.request.mockResolvedValue(mockResponse);

      const result = await client.submitActivity(validActivity);

      expect(mockAxiosInstance.request).toHaveBeenCalledWith({
        method: 'post',
        url: '/v2/activities/submit',
        data: expect.objectContaining({
          wallet_address: validActivity.wallet_address.toLowerCase(),
          activity_type: 'solar_export',
          value: 5.0,
          details: { panel_count: 10 },
        }),
      });
      expect(result.txHash).toBe('0x1234567890abcdef');
      expect(result.status).toBe('confirmed');
    });

    it('should submit to different API versions', async () => {
      const mockResponse = {
        data: { txHash: '0xabc', status: 'pending' },
      };
      mockAxiosInstance.request.mockResolvedValue(mockResponse);

      await client.submitActivity(validActivity, 'v1');
      expect(mockAxiosInstance.request).toHaveBeenCalledWith({
        method: 'post',
        url: '/v1/activities/submit',
        data: expect.any(Object),
      });

      await client.submitActivity(validActivity, 'legacy');
      expect(mockAxiosInstance.request).toHaveBeenCalledWith({
        method: 'post',
        url: '/activities/submit',
        data: expect.any(Object),
      });
    });

    it('should validate activity data', async () => {
      const invalidActivity = {
        wallet_address: 'invalid-address',
        activity_type: 'invalid_type' as any,
        value: -1,
      } as ActivitySubmission;

      await expect(client.submitActivity(invalidActivity)).rejects.toThrow();
    });

    it('should handle validation errors', async () => {
      const mockError = {
        response: {
          status: 422,
          data: { detail: 'Invalid wallet address format' },
        },
        config: { url: '/v2/activities/submit' },
        isAxiosError: true,
      };
      mockAxiosInstance.request.mockRejectedValue(mockError);

      await expect(client.submitActivity(validActivity)).rejects.toThrow(
        ValidationError
      );
    });
  });

  describe('OAuth flow', () => {
    describe('oauthLogin', () => {
      it('should initiate OAuth login', async () => {
        const mockResponse = {
          data: {
            auth_url: 'https://github.com/login/oauth/authorize?client_id=test',
            state: 'random-state',
            session_key: 'session-key',
            provider: 'github',
          },
        };
        mockAxiosInstance.request.mockResolvedValue(mockResponse);

        const result = await client.oauthLogin('github');

        expect(mockAxiosInstance.request).toHaveBeenCalledWith({
          method: 'get',
          url: '/oauth/login/github',
        });
        expect(result.provider).toBe('github');
        expect(result.auth_url).toContain('github.com');
      });

      it('should include optional parameters', async () => {
        const mockResponse = {
          data: {
            auth_url: 'https://github.com/login/oauth/authorize',
            state: 'state',
            session_key: 'key',
            provider: 'github',
          },
        };
        mockAxiosInstance.request.mockResolvedValue(mockResponse);

        await client.oauthLogin('github', 'https://example.com/callback', 'user123');

        expect(mockAxiosInstance.request).toHaveBeenCalledWith({
          method: 'get',
          url: '/oauth/login/github?redirect_uri=https%3A%2F%2Fexample.com%2Fcallback&user_id=user123',
        });
      });
    });

    describe('oauthCallback', () => {
      it('should complete OAuth callback', async () => {
        const mockResponse = {
          data: {
            message: 'OAuth callback successful',
            provider: 'github',
            wallet_address: '0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2',
            token_id: 1,
            expires_in: 3600,
            expires_at: '2024-01-01T12:00:00Z',
            has_refresh_token: true,
          },
        };
        mockAxiosInstance.request.mockResolvedValue(mockResponse);

        const callbackParams = {
          provider: 'github',
          code: 'auth-code',
          state: 'oauth-state',
          wallet_address: '0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2',
          session_key: 'session-key',
        };

        const result = await client.oauthCallback(callbackParams);

        expect(mockAxiosInstance.request).toHaveBeenCalledWith({
          method: 'post',
          url: '/oauth/callback/github',
          data: {
            code: 'auth-code',
            state: 'oauth-state',
            wallet_address: '0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2',
            session_key: 'session-key',
          },
        });
        expect(result.provider).toBe('github');
        expect(result.token_id).toBe(1);
      });

      it('should handle OAuth errors', async () => {
        const mockError = {
          response: {
            status: 400,
            data: { detail: 'Invalid authorization code' },
          },
          config: { url: '/oauth/callback/github' },
          isAxiosError: true,
        };
        mockAxiosInstance.request.mockRejectedValue(mockError);

        const callbackParams = {
          provider: 'github',
          code: 'invalid-code',
          state: 'state',
          wallet_address: '0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2',
          session_key: 'key',
        };

        await expect(client.oauthCallback(callbackParams)).rejects.toThrow(
          OAuthError
        );
      });
    });
  });

  describe('error handling', () => {
    it('should handle authentication errors', async () => {
      const mockError = {
        response: {
          status: 401,
          data: { detail: 'Invalid API key' },
        },
        config: { url: '/healthz' },
        isAxiosError: true,
      };
      mockAxiosInstance.request.mockRejectedValue(mockError);

      await expect(client.healthCheck()).rejects.toThrow(AuthenticationError);
    });

    it('should handle rate limit errors', async () => {
      const mockError = {
        response: {
          status: 429,
          data: { detail: 'Rate limit exceeded' },
        },
        config: { url: '/healthz' },
        isAxiosError: true,
      };
      mockAxiosInstance.request.mockRejectedValue(mockError);

      await expect(client.healthCheck()).rejects.toThrow(RateLimitError);
    });

    it('should handle network errors', async () => {
      const mockError = {
        code: 'ECONNABORTED',
        message: 'timeout of 30000ms exceeded',
        config: { url: '/healthz' },
        isAxiosError: true,
      };
      mockAxiosInstance.request.mockRejectedValue(mockError);

      await expect(client.healthCheck()).rejects.toThrow(NetworkError);
    });

    it('should retry on network errors', async () => {
      const client = new SilvanusClient({ maxRetries: 2 });
      
      const mockRequest = vi.fn()
        .mockRejectedValueOnce({ code: 'ECONNRESET' })
        .mockRejectedValueOnce({ code: 'ECONNRESET' })
        .mockResolvedValueOnce({ data: { status: 'ok' } });
      
      mockAxiosInstance.request = mockRequest;

      const result = await client.healthCheck();
      
      expect(mockRequest).toHaveBeenCalledTimes(3);
      expect(result.status).toBe('ok');
    });
  });
});
