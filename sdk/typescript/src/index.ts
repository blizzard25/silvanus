export { SilvanusClient } from './client';
export type { SilvanusClientConfig, OAuthCallbackParams } from './client';
export { default } from './client';

export type {
  ActivitySubmission,
  ActivityResponse,
  ActivityTypeInfo,
  OAuthLoginResponse,
  OAuthCallbackResponse,
  HealthResponse,
  ErrorResponse,
  ActivityType,
} from './models';
export { ACTIVITY_TYPES } from './models';

export {
  ActivitySubmissionSchema,
  ActivityResponseSchema,
  ActivityTypeInfoSchema,
  OAuthLoginResponseSchema,
  OAuthCallbackResponseSchema,
  HealthResponseSchema,
  ErrorResponseSchema,
} from './models';

export {
  SilvanusAPIError,
  AuthenticationError,
  ValidationError,
  RateLimitError,
  NetworkError,
  OAuthError,
  mapStatusCodeToError,
} from './exceptions';
