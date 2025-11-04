"""
Gemini API Rate Limiter
=======================

Centralized rate limiting utility for Gemini API calls in the CHRONOS pipeline.
Handles exponential backoff, retry logic, and rate limit errors (429).
"""

import time
import logging
import re
import google.generativeai as genai
from google.api_core import retry
from typing import Optional, Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiRateLimiter:
    """
    Centralized rate limiter for Gemini API calls with comprehensive error handling.
    """
    
    def __init__(
        self,
        initial_delay: float = 2.0,
        max_delay: float = 300.0,  # 5 minutes
        base_delay: float = 12.0,   # Base delay between requests
        max_retries: int = 5,
        total_timeout: int = 1800   # 30 minutes total timeout
    ):
        """
        Initialize the rate limiter.
        
        Args:
            initial_delay: Initial retry delay in seconds
            max_delay: Maximum retry delay in seconds  
            base_delay: Base delay between requests in seconds
            max_retries: Maximum number of retries
            total_timeout: Total timeout for all retries in seconds
        """
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.base_delay = base_delay
        self.max_retries = max_retries
        self.total_timeout = total_timeout
        self.request_count = 0
        self.last_request_time = 0
        
        # Configure retry policy for Google API Core
        self.retry_policy = retry.Retry(
            initial=initial_delay,
            multiplier=2.0,
            maximum=max_delay,
            timeout=total_timeout
        )
        
        logger.info(f"GeminiRateLimiter initialized:")
        logger.info(f"  Initial delay: {initial_delay}s")
        logger.info(f"  Max delay: {max_delay}s")
        logger.info(f"  Base request delay: {base_delay}s")
        logger.info(f"  Max retries: {max_retries}")
        logger.info(f"  Total timeout: {total_timeout}s")

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay with jitter."""
        import random
        
        # Exponential backoff: initial * (2^attempt) with random jitter
        base_delay = self.initial_delay * (2 ** attempt)
        jitter = random.uniform(0.1, 0.9)  # 10-90% jitter
        delay = min(base_delay + jitter, self.max_delay)
        
        return delay

    def _extract_retry_delay(self, error_message: str) -> Optional[float]:
        """
        Extract retry delay from 429 error response.
        
        Args:
            error_message: Error message from API response
            
        Returns:
            Delay in seconds if found, None otherwise
        """
        # Look for retryDelay in JSON response
        patterns = [
            r'"retryDelay":\s*"(\d+)s"',  # "retryDelay": "30s"
            r'"retryDelay":\s*(\d+)',     # "retryDelay": 30
            r'retryAfter:\s*(\d+)',       # retryAfter: 30
            r'Retry-After:\s*(\d+)',      # Retry-After: 30
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_message, re.IGNORECASE)
            if match:
                delay = float(match.group(1))
                logger.info(f"Extracted server-suggested retry delay: {delay}s")
                return delay
        
        # Fallback: look for "too many requests" with suggested delay
        fallback_match = re.search(r'(\d+)\s*seconds?', error_message, re.IGNORECASE)
        if fallback_match:
            delay = float(fallback_match.group(1))
            logger.info(f"Extracted suggested delay: {delay}s")
            return delay
            
        return None

    def _handle_rate_limit_error(self, error: Exception) -> float:
        """
        Handle rate limit (429) errors by extracting retry delay.
        
        Args:
            error: The exception that occurred
            
        Returns:
            Delay in seconds before next retry
        """
        error_str = str(error)
        logger.warning(f"Rate limit detected: {error_str}")
        
        # Try to extract server-suggested delay
        server_delay = self._extract_retry_delay(error_str)
        if server_delay:
            return max(server_delay, self.base_delay)
        
        # Use exponential backoff
        return self.base_delay

    def _enforce_request_delay(self):
        """Enforce minimum delay between requests."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.base_delay:
            wait_time = self.base_delay - time_since_last
            logger.info(f"Rate limiting: waiting {wait_time:.1f}s before next request")
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
        self.request_count += 1

    def generate_content(
        self,
        model,
        prompt: str,
        max_attempts: Optional[int] = None,
        **kwargs
    ) -> Any:
        """
        Make a rate-limited request to Gemini API with retry logic.
        
        Args:
            model: Gemini model instance
            prompt: The prompt to send
            max_attempts: Override default max retries
            **kwargs: Additional arguments for generate_content
            
        Returns:
            API response or raises exception
        """
        max_attempts = max_attempts or self.max_retries
        start_time = time.time()
        
        logger.info(f"Starting rate-limited API request (attempt 1/{max_attempts + 1})")
        logger.info(f"Prompt length: {len(prompt):,} characters")
        
        for attempt in range(max_attempts + 1):
            try:
                # Enforce delay between requests
                if attempt > 0:  # Only delay on retries, not first request
                    self._enforce_request_delay()
                
                # Add request options with retry policy
                request_options = {
                    "retry": self.retry_policy
                }
                
                # Merge any additional kwargs
                request_options.update(kwargs)
                
                logger.info(f"Request {self.request_count}: Attempt {attempt + 1}")
                
                # Make the API call
                response = model.generate_content(
                    prompt,
                    request_options=request_options
                )
                
                if not response or not hasattr(response, 'text') or not response.text:
                    raise ValueError("Empty or invalid response from Gemini API")
                
                # Success!
                elapsed_time = time.time() - start_time
                logger.info(f"✅ Request successful after {attempt + 1} attempts ({elapsed_time:.1f}s)")
                return response
                
            except Exception as e:
                error_str = str(e)
                elapsed_time = time.time() - start_time
                
                logger.warning(f"Request failed (attempt {attempt + 1}/{max_attempts + 1}): {error_str}")
                
                # Check if this is a rate limit error
                is_rate_limit = (
                    "429" in error_str or
                    "RESOURCE_EXHAUSTED" in error_str or
                    "quota" in error_str.lower() or
                    "rate limit" in error_str.lower() or
                    "too many requests" in error_str.lower()
                )
                
                if is_rate_limit:
                    # Handle rate limiting
                    delay = self._handle_rate_limit_error(e)
                    logger.info(f"Rate limit handled, waiting {delay}s before retry")
                    time.sleep(delay)
                else:
                    # For non-rate-limit errors, still apply backoff but shorter
                    if attempt < max_attempts:
                        delay = self._calculate_delay(attempt)
                        logger.info(f"Non-rate-limit error, waiting {delay}s before retry")
                        time.sleep(delay)
                
                # If this was the last attempt, raise the error
                if attempt == max_attempts:
                    logger.error(f"❌ All {max_attempts + 1} attempts failed. Total time: {elapsed_time:.1f}s")
                    raise e
                
        # Should never reach here, but just in case
        raise Exception("Maximum retry attempts exceeded")

    def get_stats(self) -> Dict[str, Any]:
        """Get rate limiter statistics."""
        return {
            "request_count": self.request_count,
            "last_request_time": self.last_request_time,
            "configured_delays": {
                "initial": self.initial_delay,
                "max": self.max_delay,
                "base": self.base_delay,
                "max_retries": self.max_retries,
                "total_timeout": self.total_timeout
            }
        }

    def reset_stats(self):
        """Reset request statistics."""
        self.request_count = 0
        self.last_request_time = 0
        logger.info("Rate limiter statistics reset")


# Global rate limiter instance
_rate_limiter = None


def get_rate_limiter(**kwargs) -> GeminiRateLimiter:
    """
    Get the global rate limiter instance, creating it if needed.
    
    Args:
        **kwargs: Override default rate limiter settings
        
    Returns:
        GeminiRateLimiter instance
    """
    global _rate_limiter
    
    if _rate_limiter is None or kwargs:
        # Create new instance with any overrides
        default_settings = {
            "initial_delay": 2.0,
            "max_delay": 300.0,
            "base_delay": 12.0,
            "max_retries": 5,
            "total_timeout": 1800
        }
        default_settings.update(kwargs)
        
        _rate_limiter = GeminiRateLimiter(**default_settings)
        logger.info("Created new global rate limiter instance")
    
    return _rate_limiter


def rate_limited_request(
    model,
    prompt: str,
    delay_between_requests: float = 12.0,
    **kwargs
) -> Any:
    """
    Convenience function for making a single rate-limited request.
    
    Args:
        model: Gemini model instance
        prompt: The prompt to send
        delay_between_requests: Delay between requests in seconds
        **kwargs: Additional arguments for generate_content
        
    Returns:
        API response
    """
    rate_limiter = get_rate_limiter(base_delay=delay_between_requests)
    return rate_limiter.generate_content(model, prompt, **kwargs)


# Example usage
if __name__ == "__main__":
    # Test the rate limiter
    import os
    
    # Configure Gemini
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found in environment variables")
        exit(1)
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash-exp")
    
    # Create rate limiter
    rate_limiter = get_rate_limiter(
        base_delay=5.0,  # 5 second delay between requests
        max_retries=3
    )
    
    # Test prompt
    test_prompt = """
    Test prompt for rate limiting. 
    Please respond with: "Rate limiting test successful"
    """
    
    try:
        print("Testing rate limiter...")
        response = rate_limiter.generate_content(model, test_prompt)
        print(f"✅ Success: {response.text}")
        
        # Get statistics
        stats = rate_limiter.get_stats()
        print(f"Request count: {stats['request_count']}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")