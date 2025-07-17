"""
OAuth2.0 authentication flow example for the Silvanus SDK.
"""

import asyncio
from silvanus_sdk import SilvanusClient, ActivitySubmission


async def oauth_flow_example():
    """Demonstrate OAuth2.0 authentication flow."""
    
    client = SilvanusClient(base_url="https://silvanus-a4nt.onrender.com")
    
    try:
        print("Step 1: Initiating OAuth login...")
        login_response = await client.oauth_login(
            provider="github",
            user_id="demo-user"
        )
        
        print(f"Provider: {login_response.provider}")
        print(f"Authorization URL: {login_response.auth_url}")
        print(f"State: {login_response.state}")
        print(f"Session Key: {login_response.session_key}")
        
        print("\n🔗 Please visit the authorization URL and complete the OAuth flow.")
        print("After authorization, you'll receive a 'code' parameter in the callback URL.")
        
        
        print("\nStep 2: Completing OAuth callback...")
        print("(In a real app, you'd get 'code' from the OAuth callback URL)")
        
        try:
            callback_response = await client.oauth_callback(
                provider="github",
                code="example-auth-code",  # This would be from the OAuth callback
                state=login_response.state,
                wallet_address="0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2",
                session_key=login_response.session_key
            )
            
            print(f"OAuth Success: {callback_response.message}")
            print(f"Token ID: {callback_response.token_id}")
            print(f"Expires in: {callback_response.expires_in} seconds")
            
            print("\nStep 3: Using OAuth token for API calls...")
            print("(You would set the access token from the OAuth response)")
            
            
            
        except Exception as oauth_error:
            print(f"OAuth callback failed (expected with example code): {oauth_error}")
            print("This is normal - you need a real OAuth authorization code.")
        
    except Exception as e:
        print(f"Error during OAuth flow: {e}")
        
    finally:
        await client.close()


async def oauth_with_token_example():
    """Example of using SDK with an existing OAuth token."""
    
    client = SilvanusClient(
        base_url="https://silvanus-a4nt.onrender.com",
        access_token="your-oauth-access-token-here"
    )
    
    try:
        print("Using existing OAuth token...")
        
        health = await client.health_check()
        print(f"API Status: {health.status}")
        
        activity = ActivitySubmission(
            wallet_address="0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2",
            activity_type="solar_export",
            value=7.5,
            details={"source": "oauth_authenticated"}
        )
        
        response = await client.submit_activity(activity, version="v2")
        print(f"Transaction Hash: {response.txHash}")
        print(f"Status: {response.status}")
        
    except Exception as e:
        print(f"Error with OAuth token: {e}")
        
    finally:
        await client.close()


async def provider_comparison_example():
    """Example showing different OAuth providers."""
    
    client = SilvanusClient(base_url="https://silvanus-a4nt.onrender.com")
    
    try:
        print("Comparing OAuth providers...")
        
        github_login = await client.oauth_login(provider="github")
        print(f"GitHub OAuth URL: {github_login.auth_url}")
        
        try:
            solaredge_login = await client.oauth_login(provider="solaredge")
            print(f"SolarEdge OAuth URL: {solaredge_login.auth_url}")
        except Exception as e:
            print(f"SolarEdge OAuth not configured: {e}")
        
    except Exception as e:
        print(f"Error comparing providers: {e}")
        
    finally:
        await client.close()


if __name__ == "__main__":
    print("=== OAuth2.0 Flow Example ===")
    asyncio.run(oauth_flow_example())
    
    print("\n=== OAuth Token Usage Example ===")
    asyncio.run(oauth_with_token_example())
    
    print("\n=== Provider Comparison Example ===")
    asyncio.run(provider_comparison_example())
