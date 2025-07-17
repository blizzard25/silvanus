/**
 * Basic usage examples for the Silvanus TypeScript SDK
 */

import { SilvanusClient, ActivitySubmission } from '../src';

async function basicApiKeyExample(): Promise<void> {
  const client = new SilvanusClient({
    apiKey: 'your-api-key-here',
    baseUrl: 'https://silvanus-a4nt.onrender.com',
  });

  try {
    const health = await client.healthCheck();
    console.log('API Health:', health.status);

    const activityTypes = await client.getActivityTypes();
    console.log('Available activity types:', activityTypes.length);
    activityTypes.forEach((type) => {
      console.log(`- ${type.type}: ${type.description}`);
    });

    const activity: ActivitySubmission = {
      wallet_address: '0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2',
      activity_type: 'solar_export',
      value: 5.0,
      details: {
        panel_count: 10,
        energy_exported: 5.0,
        timestamp: new Date().toISOString(),
      },
    };

    const response = await client.submitActivity(activity);
    console.log('Activity submitted successfully!');
    console.log('Transaction Hash:', response.txHash);
    console.log('Status:', response.status);

  } catch (error) {
    console.error('Error:', error);
  }
}

async function differentApiVersionsExample(): Promise<void> {
  const client = new SilvanusClient({
    apiKey: 'your-api-key-here',
  });

  const activity: ActivitySubmission = {
    wallet_address: '0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2',
    activity_type: 'ev_charging',
    value: 3.5,
  };

  try {
    console.log('Testing different API versions...');

    const v2Response = await client.submitActivity(activity, 'v2');
    console.log('V2 Response:', v2Response.txHash);

    const v1Response = await client.submitActivity(activity, 'v1');
    console.log('V1 Response:', v1Response.txHash);

    const legacyResponse = await client.submitActivity(activity, 'legacy');
    console.log('Legacy Response:', legacyResponse.txHash);

  } catch (error) {
    console.error('Error testing API versions:', error);
  }
}

async function errorHandlingExample(): Promise<void> {
  const client = new SilvanusClient({
    apiKey: 'invalid-api-key', // Intentionally invalid
  });

  try {
    await client.healthCheck();
  } catch (error) {
    if (error instanceof Error) {
      console.log('Error type:', error.constructor.name);
      console.log('Error message:', error.message);
      
      const { 
        AuthenticationError, 
        ValidationError, 
        RateLimitError, 
        NetworkError 
      } = await import('../src/exceptions');

      if (error instanceof AuthenticationError) {
        console.log('Authentication failed - check your API key');
        console.log('Status code:', error.statusCode);
      } else if (error instanceof ValidationError) {
        console.log('Validation failed - check your input data');
      } else if (error instanceof RateLimitError) {
        console.log('Rate limit exceeded - please wait before retrying');
      } else if (error instanceof NetworkError) {
        console.log('Network error - check your connection');
      }
    }
  }
}

async function runExamples(): Promise<void> {
  console.log('=== Basic API Key Example ===');
  await basicApiKeyExample();

  console.log('\n=== Different API Versions Example ===');
  await differentApiVersionsExample();

  console.log('\n=== Error Handling Example ===');
  await errorHandlingExample();
}

if (require.main === module) {
  runExamples().catch(console.error);
}

export {
  basicApiKeyExample,
  differentApiVersionsExample,
  errorHandlingExample,
};
