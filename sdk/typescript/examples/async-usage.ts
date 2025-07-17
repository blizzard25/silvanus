/**
 * Advanced async usage examples for the Silvanus TypeScript SDK
 */

import { SilvanusClient, ActivitySubmission } from '../src';

async function batchActivitySubmission(): Promise<void> {
  const client = new SilvanusClient({
    apiKey: 'your-api-key-here',
    baseUrl: 'https://silvanus-a4nt.onrender.com',
  });

  try {
    const activities: ActivitySubmission[] = [
      {
        wallet_address: '0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2',
        activity_type: 'solar_export',
        value: 5.0,
        details: { batch_id: 1 },
      },
      {
        wallet_address: '0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2',
        activity_type: 'ev_charging',
        value: 3.5,
        details: { batch_id: 2 },
      },
      {
        wallet_address: '0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2',
        activity_type: 'energy_saving',
        value: 2.0,
        details: { batch_id: 3 },
      },
    ];

    console.log(`Submitting ${activities.length} activities concurrently...`);

    const promises = activities.map((activity) =>
      client.submitActivity(activity, 'v2')
    );

    const results = await Promise.all(promises);

    console.log('Batch submission results:');
    results.forEach((result, index) => {
      console.log(`Activity ${index + 1}: ${result.txHash} - ${result.status}`);
    });

  } catch (error) {
    console.error('Error in batch submission:', error);
  }
}

async function retryWithExponentialBackoff(): Promise<void> {
  const client = new SilvanusClient({
    apiKey: 'your-api-key-here',
    baseUrl: 'https://silvanus-a4nt.onrender.com',
    maxRetries: 5, // Custom retry configuration
  });

  try {
    console.log('Testing with custom retry settings...');

    const health = await client.healthCheck();
    console.log(`Health check successful: ${health.status}`);

    const activity: ActivitySubmission = {
      wallet_address: '0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2',
      activity_type: 'solar_export',
      value: 6.8,
    };

    const response = await client.submitActivity(activity);
    console.log(`Activity submitted with retries: ${response.txHash}`);

  } catch (error) {
    console.error('Failed after retries:', error);
  }
}

async function errorHandlingWithTypes(): Promise<void> {
  const client = new SilvanusClient({
    apiKey: 'invalid-api-key', // Intentionally invalid
    baseUrl: 'https://silvanus-a4nt.onrender.com',
  });

  try {
    await client.healthCheck();
  } catch (error) {
    const {
      AuthenticationError,
      ValidationError,
      RateLimitError,
      NetworkError,
    } = await import('../src/exceptions');

    if (error instanceof AuthenticationError) {
      console.log(`Authentication failed: ${error.message}`);
      console.log(`Status code: ${error.statusCode}`);
    } else if (error instanceof ValidationError) {
      console.log(`Validation error: ${error.message}`);
    } else if (error instanceof RateLimitError) {
      console.log(`Rate limit exceeded: ${error.message}`);
    } else if (error instanceof NetworkError) {
      console.log(`Network error: ${error.message}`);
    } else {
      console.log(`Unexpected error: ${error}`);
    }
  }
}

async function versionComparisonExample(): Promise<void> {
  const client = new SilvanusClient({
    apiKey: 'your-api-key-here',
    baseUrl: 'https://silvanus-a4nt.onrender.com',
  });

  try {
    const activity: ActivitySubmission = {
      wallet_address: '0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2',
      activity_type: 'solar_export',
      value: 3.0,
      details: { version_test: true },
    };

    console.log('Comparing API versions...');

    const versions: Array<'legacy' | 'v1' | 'v2'> = ['legacy', 'v1', 'v2'];

    for (const version of versions) {
      try {
        const response = await client.submitActivity(activity, version);
        console.log(`${version}: ${response.txHash} - ${response.status}`);
      } catch (error) {
        console.log(`${version}: Failed - ${error}`);
      }
    }

  } catch (error) {
    console.error('Version comparison error:', error);
  }
}

async function timeoutAndConcurrencyExample(): Promise<void> {
  const client = new SilvanusClient({
    apiKey: 'your-api-key-here',
    baseUrl: 'https://silvanus-a4nt.onrender.com',
    timeout: 10000, // 10 second timeout
  });

  try {
    console.log('Testing concurrent requests with timeout...');

    const promises = [
      client.healthCheck(),
      client.getActivityTypes(),
      client.healthCheck(),
    ];

    const results = await Promise.allSettled(promises);

    results.forEach((result, index) => {
      if (result.status === 'fulfilled') {
        console.log(`Request ${index + 1}: Success`);
      } else {
        console.log(`Request ${index + 1}: Failed - ${result.reason}`);
      }
    });

  } catch (error) {
    console.error('Concurrency test error:', error);
  }
}

async function activityTypesAndValidationExample(): Promise<void> {
  const client = new SilvanusClient({
    apiKey: 'your-api-key-here',
    baseUrl: 'https://silvanus-a4nt.onrender.com',
  });

  try {
    console.log('=== Activity Types and Validation Example ===');

    const activityTypes = await client.getActivityTypes();
    console.log(`Available activity types: ${activityTypes.length}`);

    activityTypes.forEach((type) => {
      console.log(`- ${type.type}: ${type.description}`);
      console.log(`  Expected details: ${type.expectedDetails.join(', ')}`);
    });

    for (const activityType of activityTypes.slice(0, 3)) {
      try {
        const activity: ActivitySubmission = {
          wallet_address: '0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2',
          activity_type: activityType.type as any,
          value: Math.random() * 10,
          details: {
            test: true,
            timestamp: new Date().toISOString(),
          },
        };

        const response = await client.submitActivity(activity);
        console.log(`${activityType.type}: ${response.txHash}`);

      } catch (error) {
        console.log(`${activityType.type}: Validation failed - ${error}`);
      }
    }

  } catch (error) {
    console.error('Activity types example error:', error);
  }
}

async function runAdvancedExamples(): Promise<void> {
  console.log('=== Batch Activity Submission ===');
  await batchActivitySubmission();

  console.log('\n=== Retry with Exponential Backoff ===');
  await retryWithExponentialBackoff();

  console.log('\n=== Error Handling with Types ===');
  await errorHandlingWithTypes();

  console.log('\n=== Version Comparison Example ===');
  await versionComparisonExample();

  console.log('\n=== Timeout and Concurrency Example ===');
  await timeoutAndConcurrencyExample();

  console.log('\n=== Activity Types and Validation Example ===');
  await activityTypesAndValidationExample();
}

if (require.main === module) {
  runAdvancedExamples().catch(console.error);
}

export {
  batchActivitySubmission,
  retryWithExponentialBackoff,
  errorHandlingWithTypes,
  versionComparisonExample,
  timeoutAndConcurrencyExample,
  activityTypesAndValidationExample,
};
