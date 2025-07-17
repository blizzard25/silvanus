import logging
from datetime import datetime
from typing import Dict, Any

security_logger = logging.getLogger('silvanus_security')
security_logger.setLevel(logging.INFO)

def log_validation_attempt(endpoint: str, wallet_address: str, value: float, success: bool, details: Dict[str, Any] = None):
    """Log all validation attempts for security monitoring"""
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'endpoint': endpoint,
        'wallet_address': wallet_address,
        'value': value,
        'validation_success': success,
        'details': details or {}
    }
    
    if success:
        security_logger.info(f"VALIDATION_SUCCESS: {log_data}")
    else:
        security_logger.warning(f"VALIDATION_FAILED: {log_data}")

def log_blockchain_transaction(endpoint: str, wallet_address: str, value: float, tx_hash: str, success: bool):
    """Log blockchain transactions for security monitoring"""
    log_data = {
        'timestamp': datetime.now().isoformat(),
        'endpoint': endpoint,
        'wallet_address': wallet_address,
        'value': value,
        'tx_hash': tx_hash,
        'transaction_success': success
    }
    
    security_logger.info(f"BLOCKCHAIN_TRANSACTION: {log_data}")
