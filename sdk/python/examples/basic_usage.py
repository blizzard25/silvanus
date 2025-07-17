"""
Basic usage example for the Silvanus SDK with API key authentication.
"""

import asyncio
from silvanus_sdk import SilvanusClient, ActivitySubmission


async def main():
    """Demonstrate basic SDK usage with API key authentication."""
    
    client = SilvanusClient(
        api_key="your-api-key-here",
        base_url="https://silvanus-a4nt.onrender.com"
    )
    
    try:
        print("Checking API health...")
        health = await client.health_check()
        print(f"API Status: {health.status}")
        
        print("\nGetting supported activity types...")
        activity_types = await client.get_activity_types()
        for activity_type in activity_types:
            print(f"- {activity_type.type}: {activity_type.description}")
        
        print("\nSubmitting solar export activity...")
        activity = ActivitySubmission(
            wallet_address="0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2",
            activity_type="solar_export",
            value=5.0,
            details={
                "panel_count": 10,
                "efficiency": 0.85,
                "location": "rooftop"
            }
        )
        
        response = await client.submit_activity(activity, version="v2")
        print(f"Transaction Hash: {response.txHash}")
        print(f"Status: {response.status}")
        
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        await client.close()


def sync_example():
    """Demonstrate synchronous SDK usage."""
    from silvanus_sdk import SilvanusClientSync
    
    client = SilvanusClientSync(
        api_key="your-api-key-here",
        base_url="https://silvanus-a4nt.onrender.com"
    )
    
    try:
        health = client.health_check()
        print(f"API Status: {health.status}")
        
        activity = ActivitySubmission(
            wallet_address="0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2",
            activity_type="solar_export",
            value=3.5
        )
        
        response = client.submit_activity(activity)
        print(f"Transaction Hash: {response.txHash}")
        
    except Exception as e:
        print(f"Error: {e}")
        
    finally:
        client.close()


if __name__ == "__main__":
    print("=== Async Example ===")
    asyncio.run(main())
    
    print("\n=== Sync Example ===")
    sync_example()
