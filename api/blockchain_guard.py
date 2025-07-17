from functools import wraps
from fastapi import HTTPException
from api.validation import BaseActivitySubmission
import asyncio

class BlockchainGuard:
    """
    A more robust validation guard that prevents blockchain execution
    by using a context manager approach with explicit validation gates
    """
    
    def __init__(self):
        self.validation_passed = False
        self.blockchain_allowed = False
    
    def validate_activity(self, activity: BaseActivitySubmission):
        """Explicit validation that must pass before blockchain operations"""
        if activity.value > 10000:
            raise HTTPException(status_code=422, detail="Activity value cannot exceed 10000 kWh")
        if activity.value < 0:
            raise HTTPException(status_code=422, detail="Activity value must be non-negative")
        
        self.validation_passed = True
        self.blockchain_allowed = True
        return True
    
    def allow_blockchain(self):
        """Check if blockchain operations are allowed"""
        if not self.validation_passed or not self.blockchain_allowed:
            raise HTTPException(status_code=422, detail="Blockchain operations not authorized - validation failed")
        return True

def blockchain_protected(func):
    """
    Decorator that creates a blockchain guard and passes it to the function
    The function must explicitly validate and authorize blockchain operations
    """
    @wraps(func)
    async def wrapper(*args, **kwargs):
        guard = BlockchainGuard()
        
        activity = None
        for arg in args:
            if isinstance(arg, BaseActivitySubmission):
                activity = arg
                break
        
        if not activity:
            for key, value in kwargs.items():
                if isinstance(value, BaseActivitySubmission):
                    activity = value
                    break
        
        if activity:
            guard.validate_activity(activity)
        
        kwargs['guard'] = guard
        return await func(*args, **kwargs)
    
    return wrapper
