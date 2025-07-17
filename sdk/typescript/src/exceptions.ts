/**
 * Base class for all Silvanus API errors
 */
export class SilvanusAPIError extends Error {
  public readonly statusCode?: number;
  public readonly response?: any;

  constructor(message: string, statusCode?: number, response?: any) {
    super(message);
    this.name = 'SilvanusAPIError';
    this.statusCode = statusCode;
    this.response = response;
    
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, SilvanusAPIError);
    }
  }
}

/**
 * Authentication-related errors (401, 403)
 */
export class AuthenticationError extends SilvanusAPIError {
  constructor(message: string, statusCode?: number, response?: any) {
    super(message, statusCode, response);
    this.name = 'AuthenticationError';
  }
}

/**
 * Validation errors (422)
 */
export class ValidationError extends SilvanusAPIError {
  constructor(message: string, statusCode?: number, response?: any) {
    super(message, statusCode, response);
    this.name = 'ValidationError';
  }
}

/**
 * Rate limiting errors (429)
 */
export class RateLimitError extends SilvanusAPIError {
  constructor(message: string, statusCode?: number, response?: any) {
    super(message, statusCode, response);
    this.name = 'RateLimitError';
  }
}

/**
 * Network and timeout errors
 */
export class NetworkError extends SilvanusAPIError {
  constructor(message: string, statusCode?: number, response?: any) {
    super(message, statusCode, response);
    this.name = 'NetworkError';
  }
}

/**
 * OAuth-specific errors
 */
export class OAuthError extends SilvanusAPIError {
  constructor(message: string, statusCode?: number, response?: any) {
    super(message, statusCode, response);
    this.name = 'OAuthError';
  }
}

/**
 * Maps HTTP status codes to appropriate exception classes
 */
export function mapStatusCodeToError(
  statusCode: number,
  message: string,
  response?: any
): SilvanusAPIError {
  switch (statusCode) {
    case 401:
    case 403:
      return new AuthenticationError(message, statusCode, response);
    case 422:
      return new ValidationError(message, statusCode, response);
    case 429:
      return new RateLimitError(message, statusCode, response);
    case 500:
    case 502:
    case 503:
    case 504:
      return new NetworkError(message, statusCode, response);
    default:
      return new SilvanusAPIError(message, statusCode, response);
  }
}
