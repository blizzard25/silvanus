/**
 * OAuth2.0 flow examples for the Silvanus TypeScript SDK
 */

import { SilvanusClient, OAuthCallbackParams } from '../src';

async function githubOAuthExample(): Promise<void> {
  const client = new SilvanusClient({
    baseUrl: 'https://silvanus-a4nt.onrender.com',
  });

  try {
    console.log('=== GitHub OAuth Flow Example ===');

    const loginResponse = await client.oauthLogin('github');
    console.log('OAuth Login Response:');
    console.log('- Auth URL:', loginResponse.auth_url);
    console.log('- State:', loginResponse.state);
    console.log('- Session Key:', loginResponse.session_key);
    console.log('- Provider:', loginResponse.provider);

    console.log('\n1. Visit the auth URL to authorize the application');
    console.log('2. After authorization, you will be redirected with a code parameter');
    console.log('3. Use that code in the callback step below');

    const callbackParams: OAuthCallbackParams = {
      provider: 'github',
      code: 'authorization-code-from-github', // This would be real in practice
      state: loginResponse.state,
      wallet_address: '0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2',
      session_key: loginResponse.session_key,
    };

    try {
      const callbackResponse = await client.oauthCallback(callbackParams);
      console.log('\nOAuth Callback Response:');
      console.log('- Message:', callbackResponse.message);
      console.log('- Provider:', callbackResponse.provider);
      console.log('- Wallet Address:', callbackResponse.wallet_address);
      console.log('- Token ID:', callbackResponse.token_id);
      console.log('- Expires In:', callbackResponse.expires_in, 'seconds');
      console.log('- Expires At:', callbackResponse.expires_at);
      console.log('- Has Refresh Token:', callbackResponse.has_refresh_token);

      client.setAccessToken('oauth-access-token-from-response');
      
      const health = await client.healthCheck();
      console.log('\nAuthenticated API call successful:', health.status);

    } catch (error) {
      console.log('\nCallback failed (expected with fake code):', error);
    }

  } catch (error) {
    console.error('OAuth flow error:', error);
  }
}

async function solarEdgeOAuthExample(): Promise<void> {
  const client = new SilvanusClient();

  try {
    console.log('=== SolarEdge OAuth Flow Example ===');

    const loginResponse = await client.oauthLogin(
      'solaredge',
      'https://your-app.com/callback',
      'user123'
    );

    console.log('SolarEdge OAuth Login:');
    console.log('- Auth URL:', loginResponse.auth_url);
    console.log('- Provider:', loginResponse.provider);


  } catch (error) {
    console.error('SolarEdge OAuth error:', error);
  }
}

async function oauthWithCustomRedirectExample(): Promise<void> {
  const client = new SilvanusClient();

  try {
    console.log('=== OAuth with Custom Redirect Example ===');

    const customRedirectUri = 'https://your-app.com/auth/callback';
    const userId = 'user-12345';

    const loginResponse = await client.oauthLogin(
      'github',
      customRedirectUri,
      userId
    );

    console.log('Custom OAuth Login:');
    console.log('- Auth URL:', loginResponse.auth_url);
    console.log('- Custom redirect will be used after authorization');

  } catch (error) {
    console.error('Custom OAuth error:', error);
  }
}

async function oauthErrorHandlingExample(): Promise<void> {
  const client = new SilvanusClient();

  try {
    console.log('=== OAuth Error Handling Example ===');

    await client.oauthLogin('invalid-provider');

  } catch (error) {
    const { OAuthError } = await import('../src/exceptions');
    
    if (error instanceof OAuthError) {
      console.log('OAuth Error caught:');
      console.log('- Message:', error.message);
      console.log('- Status Code:', error.statusCode);
    } else {
      console.log('Other error:', error);
    }
  }
}

async function runOAuthExamples(): Promise<void> {
  await githubOAuthExample();
  
  console.log('\n' + '='.repeat(50) + '\n');
  await solarEdgeOAuthExample();
  
  console.log('\n' + '='.repeat(50) + '\n');
  await oauthWithCustomRedirectExample();
  
  console.log('\n' + '='.repeat(50) + '\n');
  await oauthErrorHandlingExample();
}

if (require.main === module) {
  runOAuthExamples().catch(console.error);
}

export {
  githubOAuthExample,
  solarEdgeOAuthExample,
  oauthWithCustomRedirectExample,
  oauthErrorHandlingExample,
};
