import { z } from 'zod';

/**
 * Ethereum wallet address validation
 */
const EthereumAddressSchema = z
  .string()
  .regex(/^0x[a-fA-F0-9]{40}$/, 'Invalid Ethereum wallet address format')
  .transform((addr) => {
    return addr.toLowerCase();
  });

/**
 * Activity type validation
 */
const ActivityTypeSchema = z.enum([
  'solar_export',
  'ev_charging',
  'energy_saving',
  'carbon_offset',
  'renewable_energy',
  'green_transport',
  'waste_reduction',
]);

/**
 * Schema for submitting green energy activities
 */
export const ActivitySubmissionSchema = z.object({
  wallet_address: EthereumAddressSchema,
  activity_type: ActivityTypeSchema,
  value: z
    .number()
    .min(0, 'Activity value must be non-negative')
    .max(10000, 'Activity value cannot exceed 10000 kWh')
    .transform((val) => Math.round(val * 100) / 100), // Round to 2 decimal places
  details: z.record(z.any()).default({}),
});

/**
 * Schema for activity submission response
 */
export const ActivityResponseSchema = z.object({
  txHash: z.string(),
  status: z.string(),
});

/**
 * Schema for supported activity types
 */
export const ActivityTypeInfoSchema = z.object({
  type: z.string(),
  description: z.string(),
  expectedDetails: z.array(z.string()),
});

/**
 * Schema for OAuth login response
 */
export const OAuthLoginResponseSchema = z.object({
  auth_url: z.string().url(),
  state: z.string(),
  session_key: z.string(),
  provider: z.string(),
});

/**
 * Schema for OAuth callback response
 */
export const OAuthCallbackResponseSchema = z.object({
  message: z.string(),
  provider: z.string(),
  wallet_address: EthereumAddressSchema,
  token_id: z.number(),
  expires_in: z.number(),
  expires_at: z.string(),
  has_refresh_token: z.boolean(),
});

/**
 * Schema for health check response
 */
export const HealthResponseSchema = z.object({
  status: z.string().default('ok'),
});

/**
 * Schema for error responses
 */
export const ErrorResponseSchema = z.object({
  detail: z.string(),
  status_code: z.number().optional(),
});

export type ActivitySubmission = z.infer<typeof ActivitySubmissionSchema>;
export type ActivityResponse = z.infer<typeof ActivityResponseSchema>;
export type ActivityTypeInfo = z.infer<typeof ActivityTypeInfoSchema>;
export type OAuthLoginResponse = z.infer<typeof OAuthLoginResponseSchema>;
export type OAuthCallbackResponse = z.infer<typeof OAuthCallbackResponseSchema>;
export type HealthResponse = z.infer<typeof HealthResponseSchema>;
export type ErrorResponse = z.infer<typeof ErrorResponseSchema>;

export type ActivityType = z.infer<typeof ActivityTypeSchema>;
export const ACTIVITY_TYPES = ActivityTypeSchema.options;
