"""
Advanced async usage examples for the Silvanus SDK.
"""

import asyncio
from typing import List
from silvanus_sdk import SilvanusClient, ActivitySubmission, ActivityResponse


async def batch_activity_submission():
    """Example of submitting multiple activities concurrently."""
    
    client = SilvanusClient(
        api_key="your-api-key-here",
        base_url="https://silvanus-a4nt.onrender.com"
    )
    
    try:
        activities = [
            ActivitySubmission(
                wallet_address="0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2",
                activity_type="solar_export",
                value=5.0,
                details={"batch_id": 1}
            ),
            ActivitySubmission(
                wallet_address="0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2",
                activity_type="ev_charging",
                value=3.5,
                details={"batch_id": 2}
            ),
            ActivitySubmission(
                wallet_address="0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2",
                activity_type="energy_saving",
                value=2.0,
                details={"batch_id": 3}
            )
        ]
        
        print(f"Submitting {len(activities)} activities concurrently...")
        
        tasks = [
            client.submit_activity(activity, version="v2")
            for activity in activities
        ]
        
        results: List[ActivityResponse] = await asyncio.gather(*tasks)
        
        print("Batch submission results:")
        for i, result in enumerate(results):
            print(f"Activity {i+1}: {result.txHash} - {result.status}")
            
    except Exception as e:
        print(f"Error in batch submission: {e}")
        
    finally:
        await client.close()


async def context_manager_usage():
    """Example using async context manager for automatic cleanup."""
    
    async with SilvanusClient(
        api_key="your-api-key-here",
        base_url="https://silvanus-a4nt.onrender.com"
    ) as client:
        
        try:
            health = await client.health_check()
            print(f"API Health: {health.status}")
            
            activity_types = await client.get_activity_types()
            print(f"Available activity types: {len(activity_types)}")
            
            activity = ActivitySubmission(
                wallet_address="0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2",
                activity_type="solar_export",
                value=4.2
            )
            
            response = await client.submit_activity(activity)
            print(f"Activity submitted: {response.txHash}")
            
        except Exception as e:
            print(f"Error: {e}")


async def error_handling_example():
    """Example demonstrating comprehensive error handling."""
    
    client = SilvanusClient(
        api_key="invalid-api-key",  # Intentionally invalid
        base_url="https://silvanus-a4nt.onrender.com"
    )
    
    try:
        await client.health_check()
        
    except Exception as e:
        from silvanus_sdk import AuthenticationError, ValidationError, RateLimitError
        
        if isinstance(e, AuthenticationError):
            print(f"Authentication failed: {e.message}")
            print(f"Status code: {e.status_code}")
        elif isinstance(e, ValidationError):
            print(f"Validation error: {e.message}")
        elif isinstance(e, RateLimitError):
            print(f"Rate limit exceeded: {e.message}")
        else:
            print(f"Unexpected error: {e}")
            
    finally:
        await client.close()


async def retry_and_timeout_example():
    """Example showing retry logic and timeout handling."""
    
    client = SilvanusClient(
        api_key="your-api-key-here",
        base_url="https://silvanus-a4nt.onrender.com",
        timeout=10.0,  # 10 second timeout
        max_retries=5   # 5 retry attempts
    )
    
    try:
        print("Testing with custom timeout and retry settings...")
        
        health = await client.health_check()
        print(f"Health check successful: {health.status}")
        
        activity = ActivitySubmission(
            wallet_address="0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2",
            activity_type="solar_export",
            value=6.8
        )
        
        response = await client.submit_activity(activity)
        print(f"Activity submitted with retries: {response.txHash}")
        
    except Exception as e:
        print(f"Failed after retries: {e}")
        
    finally:
        await client.close()


async def version_comparison_example():
    """Example comparing different API versions."""
    
    client = SilvanusClient(
        api_key="your-api-key-here",
        base_url="https://silvanus-a4nt.onrender.com"
    )
    
    try:
        activity = ActivitySubmission(
            wallet_address="0x742d35Cc6634C0532925a3b8D4C2C2C2C2C2C2C2",
            activity_type="solar_export",
            value=3.0,
            details={"version_test": True}
        )
        
        print("Comparing API versions...")
        
        versions = ["legacy", "v1", "v2"]
        
        for version in versions:
            try:
                response = await client.submit_activity(activity, version=version)
                print(f"{version}: {response.txHash} - {response.status}")
            except Exception as e:
                print(f"{version}: Failed - {e}")
                
    except Exception as e:
        print(f"Version comparison error: {e}")
        
    finally:
        await client.close()


if __name__ == "__main__":
    print("=== Batch Activity Submission ===")
    asyncio.run(batch_activity_submission())
    
    print("\n=== Context Manager Usage ===")
    asyncio.run(context_manager_usage())
    
    print("\n=== Error Handling Example ===")
    asyncio.run(error_handling_example())
    
    print("\n=== Retry and Timeout Example ===")
    asyncio.run(retry_and_timeout_example())
    
    print("\n=== Version Comparison Example ===")
    asyncio.run(version_comparison_example())
