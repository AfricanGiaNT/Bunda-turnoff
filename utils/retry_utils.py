"""
Retry/backoff utilities for the service station operations bot.

Handles retry logic for API calls and external service interactions.
"""

import logging
import asyncio
import random
from typing import Callable, Any, Optional, TypeVar, Awaitable
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')

class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

def calculate_delay(attempt: int, config: RetryConfig) -> float:
    """Calculate delay for the given attempt number."""
    delay = config.base_delay * (config.exponential_base ** (attempt - 1))
    delay = min(delay, config.max_delay)
    
    if config.jitter:
        # Add random jitter to prevent thundering herd
        jitter = random.uniform(0, 0.1 * delay)
        delay += jitter
    
    return delay

async def retry_async(
    func: Callable[..., Awaitable[T]],
    *args,
    config: Optional[RetryConfig] = None,
    **kwargs
) -> T:
    """Retry an async function with exponential backoff."""
    if config is None:
        config = RetryConfig()
    
    last_exception = None
    
    for attempt in range(1, config.max_attempts + 1):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            logger.warning(f"Attempt {attempt} failed: {e}")
            
            if attempt < config.max_attempts:
                delay = calculate_delay(attempt, config)
                logger.info(f"Retrying in {delay:.2f} seconds...")
                await asyncio.sleep(delay)
    
    # All attempts failed
    logger.error(f"All {config.max_attempts} attempts failed. Last error: {last_exception}")
    raise last_exception

def retry_sync(
    func: Callable[..., T],
    *args,
    config: Optional[RetryConfig] = None,
    **kwargs
) -> T:
    """Retry a sync function with exponential backoff."""
    if config is None:
        config = RetryConfig()
    
    last_exception = None
    
    for attempt in range(1, config.max_attempts + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            logger.warning(f"Attempt {attempt} failed: {e}")
            
            if attempt < config.max_attempts:
                delay = calculate_delay(attempt, config)
                logger.info(f"Retrying in {delay:.2f} seconds...")
                import time
                time.sleep(delay)
    
    # All attempts failed
    logger.error(f"All {config.max_attempts} attempts failed. Last error: {last_exception}")
    raise last_exception

def retry_decorator(config: Optional[RetryConfig] = None):
    """Decorator for retrying async functions."""
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            return await retry_async(func, *args, config=config, **kwargs)
        return wrapper
    return decorator

def retry_sync_decorator(config: Optional[RetryConfig] = None):
    """Decorator for retrying sync functions."""
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            return retry_sync(func, *args, config=config, **kwargs)
        return wrapper
    return decorator

# Predefined retry configurations
AIRTABLE_RETRY_CONFIG = RetryConfig(
    max_attempts=5,
    base_delay=1.0,
    max_delay=30.0,
    exponential_base=2.0,
    jitter=True
)

TELEGRAM_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    base_delay=0.5,
    max_delay=10.0,
    exponential_base=1.5,
    jitter=True
)

OPENAI_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    base_delay=1.0,
    max_delay=20.0,
    exponential_base=2.0,
    jitter=True
) 