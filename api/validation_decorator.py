from functools import wraps
from fastapi import HTTPException
from api.validation import BaseActivitySubmission

def validate_before_execution(func):
    """Decorator to ensure validation occurs before any function execution"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
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
            if activity.value > 10000:
                raise HTTPException(status_code=422, detail="Activity value cannot exceed 10000 kWh")
            if activity.value < 0:
                raise HTTPException(status_code=422, detail="Activity value must be non-negative")
        
        return await func(*args, **kwargs)
    return wrapper
