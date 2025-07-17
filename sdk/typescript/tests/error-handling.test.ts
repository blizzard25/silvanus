import { describe, it, expect } from 'vitest';
import { AxiosError } from 'axios';
import { SilvanusClient } from '../src/client';
import {
  AuthenticationError,
  ValidationError,
  RateLimitError,
  NetworkError,
  OAuthError,
  mapStatusCodeToError,
} from '../src/exceptions';

describe('Error Handling', () => {
  describe('mapStatusCodeToError', () => {
    it('should map 401 to AuthenticationError', () => {
      const error = mapStatusCodeToError(401, 'Unauthorized', { detail: 'Invalid API key' });
      expect(error).toBeInstanceOf(AuthenticationError);
      expect(error.message).toBe('Unauthorized');
      expect(error.statusCode).toBe(401);
    });

    it('should map 403 to AuthenticationError', () => {
      const error = mapStatusCodeToError(403, 'Forbidden', { detail: 'Access denied' });
      expect(error).toBeInstanceOf(AuthenticationError);
      expect(error.message).toBe('Forbidden');
      expect(error.statusCode).toBe(403);
    });

    it('should map 422 to ValidationError', () => {
      const error = mapStatusCodeToError(422, 'Validation failed', { detail: 'Invalid input' });
      expect(error).toBeInstanceOf(ValidationError);
      expect(error.message).toBe('Validation failed');
      expect(error.statusCode).toBe(422);
    });

    it('should map 429 to RateLimitError', () => {
      const error = mapStatusCodeToError(429, 'Rate limit exceeded', { detail: 'Too many requests' });
      expect(error).toBeInstanceOf(RateLimitError);
      expect(error.message).toBe('Rate limit exceeded');
      expect(error.statusCode).toBe(429);
    });

    it('should map 500 to generic SilvanusAPIError', () => {
      const error = mapStatusCodeToError(500, 'Internal server error', { detail: 'Server error' });
      expect(error.message).toBe('Internal server error');
      expect(error.statusCode).toBe(500);
    });
  });

  describe('Client handleError method', () => {
    let client: SilvanusClient;

    beforeEach(() => {
      client = new SilvanusClient();
    });

    it('should handle network timeout errors', () => {
      const axiosError = {
        code: 'ECONNABORTED',
        message: 'timeout of 30000ms exceeded',
        config: { url: '/healthz' },
        isAxiosError: true,
      } as AxiosError;

      const handleError = (client as any).handleError.bind(client);
      const error = handleError(axiosError);

      expect(error).toBeInstanceOf(NetworkError);
      expect(error.message).toBe('Request timeout');
    });

    it('should handle network connection errors', () => {
      const axiosError = {
        code: 'ECONNRESET',
        message: 'socket hang up',
        config: { url: '/healthz' },
        isAxiosError: true,
      } as AxiosError;

      const handleError = (client as any).handleError.bind(client);
      const error = handleError(axiosError);

      expect(error).toBeInstanceOf(NetworkError);
      expect(error.message).toBe('socket hang up');
    });

    it('should handle OAuth-specific errors', () => {
      const axiosError = {
        response: {
          status: 400,
          data: { detail: 'Invalid authorization code' },
        },
        config: { url: '/oauth/callback/github' },
        isAxiosError: true,
      } as AxiosError;

      const handleError = (client as any).handleError.bind(client);
      const error = handleError(axiosError);

      expect(error).toBeInstanceOf(OAuthError);
      expect(error.message).toBe('Invalid authorization code');
      expect(error.statusCode).toBe(400);
    });

    it('should handle authentication errors', () => {
      const axiosError = {
        response: {
          status: 401,
          data: { detail: 'Invalid API key' },
        },
        config: { url: '/healthz' },
        isAxiosError: true,
      } as AxiosError;

      const handleError = (client as any).handleError.bind(client);
      const error = handleError(axiosError);

      expect(error).toBeInstanceOf(AuthenticationError);
      expect(error.message).toBe('Invalid API key');
      expect(error.statusCode).toBe(401);
    });

    it('should extract error messages from different response formats', () => {
      const handleError = (client as any).handleError.bind(client);

      const stringError = {
        response: { status: 500, data: 'Internal server error' },
        config: { url: '/test' },
        isAxiosError: true,
      } as AxiosError;
      
      const error1 = handleError(stringError);
      expect(error1.message).toBe('Internal server error');

      const detailError = {
        response: { status: 500, data: { detail: 'Detailed error message' } },
        config: { url: '/test' },
        isAxiosError: true,
      } as AxiosError;
      
      const error2 = handleError(detailError);
      expect(error2.message).toBe('Detailed error message');

      const messageError = {
        response: { status: 500, data: { message: 'Message error' } },
        config: { url: '/test' },
        isAxiosError: true,
      } as AxiosError;
      
      const error3 = handleError(messageError);
      expect(error3.message).toBe('Message error');

      const errorError = {
        response: { status: 500, data: { error: 'Error field message' } },
        config: { url: '/test' },
        isAxiosError: true,
      } as AxiosError;
      
      const error4 = handleError(errorError);
      expect(error4.message).toBe('Error field message');
    });
  });
});
