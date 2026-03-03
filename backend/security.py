"""
Security and Rate Limiting Module

Provides:
- API key authentication
- Rate limiting (per API key and per IP)
- Usage quotas (daily/monthly limits)
- Cost tracking
- Request validation

Designed to prevent abuse and control costs for public demos.
"""

import os
import time
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Optional, Tuple
from flask import request, jsonify
from dotenv import load_dotenv

load_dotenv()


class UsageTracker:
    """Track API usage per key for quotas and cost monitoring."""

    def __init__(self):
        self.usage = {}  # {api_key: {date: count, cost: float}}
        self.rate_limits = {}  # {api_key: [(timestamp, endpoint), ...]}
        self._last_cleanup = time.time()
        self.cleanup_interval = 3600  # Run cleanup every hour

    def get_daily_usage(self, api_key: str) -> int:
        """Get number of requests today for this API key."""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.usage.get(api_key, {}).get(today, {}).get('count', 0)

    def get_daily_cost(self, api_key: str) -> float:
        """Get estimated cost today for this API key."""
        today = datetime.now().strftime('%Y-%m-%d')
        return self.usage.get(api_key, {}).get(today, {}).get('cost', 0.0)

    def increment_usage(self, api_key: str, estimated_cost: float = 0.0):
        """Increment usage count and cost for today."""
        today = datetime.now().strftime('%Y-%m-%d')

        if api_key not in self.usage:
            self.usage[api_key] = {}

        if today not in self.usage[api_key]:
            self.usage[api_key][today] = {'count': 0, 'cost': 0.0}

        self.usage[api_key][today]['count'] += 1
        self.usage[api_key][today]['cost'] += estimated_cost

    def check_rate_limit(self, api_key: str, endpoint: str, window_seconds: int, max_requests: int) -> Tuple[bool, Optional[int]]:
        """
        Check if request is within rate limit.

        Returns:
            (is_allowed, retry_after_seconds)
        """
        now = time.time()

        if api_key not in self.rate_limits:
            self.rate_limits[api_key] = []

        # Clean old entries outside window
        self.rate_limits[api_key] = [
            (ts, ep) for ts, ep in self.rate_limits[api_key]
            if now - ts < window_seconds and ep == endpoint
        ]

        # Check if limit exceeded
        if len(self.rate_limits[api_key]) >= max_requests:
            oldest_ts = min(ts for ts, _ in self.rate_limits[api_key])
            retry_after = int(window_seconds - (now - oldest_ts)) + 1
            return False, retry_after

        # Add current request
        self.rate_limits[api_key].append((now, endpoint))
        return True, None

    def get_stats(self, api_key: str) -> Dict:
        """Get usage statistics for an API key."""
        today = datetime.now().strftime('%Y-%m-%d')
        return {
            'api_key': api_key[:8] + '...',  # Masked
            'today': self.usage.get(api_key, {}).get(today, {'count': 0, 'cost': 0.0}),
            'total_days': len(self.usage.get(api_key, {})),
            'all_time_requests': sum(
                day_data.get('count', 0)
                for day_data in self.usage.get(api_key, {}).values()
            ),
            'all_time_cost': sum(
                day_data.get('cost', 0.0)
                for day_data in self.usage.get(api_key, {}).values()
            )
        }

    def cleanup_old_data(self, days_to_keep: int = 7):
        """
        Remove usage data older than specified days to prevent memory leaks.
        
        Args:
            days_to_keep: Number of days to keep in memory (default: 7)
        """
        cutoff_date = (datetime.now() - timedelta(days=days_to_keep)).strftime('%Y-%m-%d')
        
        # Clean up old usage data
        keys_to_remove = []
        for api_key, dates in list(self.usage.items()):
            # Remove old dates
            old_dates = [date for date in dates if date < cutoff_date]
            for date in old_dates:
                del dates[date]
            
            # Remove API key entry if no data left
            if not dates:
                keys_to_remove.append(api_key)
        
        for key in keys_to_remove:
            del self.usage[key]
        
        # Clean up empty rate_limit entries (keeps only active keys)
        now = time.time()
        empty_keys = []
        for api_key, timestamps in list(self.rate_limits.items()):
            # Remove timestamps older than 1 hour
            self.rate_limits[api_key] = [
                (ts, ep) for ts, ep in timestamps
                if now - ts < 3600
            ]
            # Mark for removal if empty
            if not self.rate_limits[api_key]:
                empty_keys.append(api_key)
        
        for key in empty_keys:
            del self.rate_limits[key]
        
        if keys_to_remove or empty_keys:
            print(f"UsageTracker: Cleaned up {len(keys_to_remove)} usage entries, {len(empty_keys)} rate limit entries")
    
    def auto_cleanup_if_needed(self):
        """
        Automatically run cleanup if enough time has passed.
        Called on each request to prevent memory buildup.
        """
        now = time.time()
        if now - self._last_cleanup > self.cleanup_interval:
            self.cleanup_old_data()
            self._last_cleanup = now


# Global usage tracker
usage_tracker = UsageTracker()


# Configuration from environment variables
class SecurityConfig:
    """Security configuration loaded from environment."""

    # API Keys (comma-separated in .env)
    VALID_API_KEYS = set(
        key.strip()
        for key in os.getenv('API_KEYS', '').split(',')
        if key.strip()
    )

    # Rate Limits (requests per minute)
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '10'))
    RATE_LIMIT_PER_HOUR = int(os.getenv('RATE_LIMIT_PER_HOUR', '100'))

    # Daily Quotas
    DAILY_REQUEST_QUOTA = int(os.getenv('DAILY_REQUEST_QUOTA', '500'))
    DAILY_COST_QUOTA = float(os.getenv('DAILY_COST_QUOTA', '10.0'))  # $10/day default

    # Cost estimates (approximate, in USD)
    COST_PER_BIAS_OPERATION = float(os.getenv('COST_PER_BIAS_OPERATION', '0.01'))  # $0.01 per operation
    COST_PER_GRAPH_EXPANSION = float(os.getenv('COST_PER_GRAPH_EXPANSION', '0.02'))  # $0.02 per expansion

    # Enable/disable security features
    REQUIRE_API_KEY = os.getenv('REQUIRE_API_KEY', 'false').lower() == 'true'  # Disabled by default for public demo
    ENABLE_RATE_LIMITING = os.getenv('ENABLE_RATE_LIMITING', 'true').lower() == 'true'
    ENABLE_QUOTAS = os.getenv('ENABLE_QUOTAS', 'true').lower() == 'true'

    # IP-based rate limiting (primary protection for public demo)
    IP_RATE_LIMIT_PER_MINUTE = int(os.getenv('IP_RATE_LIMIT_PER_MINUTE', '10'))
    IP_RATE_LIMIT_PER_HOUR = int(os.getenv('IP_RATE_LIMIT_PER_HOUR', '100'))

    # IP-based daily quotas
    IP_DAILY_REQUEST_QUOTA = int(os.getenv('IP_DAILY_REQUEST_QUOTA', '200'))
    IP_DAILY_COST_QUOTA = float(os.getenv('IP_DAILY_COST_QUOTA', '5.0'))  # $5/day per IP

    # Admin key for monitoring
    ADMIN_API_KEY = os.getenv('ADMIN_API_KEY', '')

    @classmethod
    def is_valid_api_key(cls, api_key: str) -> bool:
        """Check if API key is valid."""
        if not cls.REQUIRE_API_KEY:
            return True
        return api_key in cls.VALID_API_KEYS

    @classmethod
    def is_admin_key(cls, api_key: str) -> bool:
        """Check if API key is admin key."""
        return api_key == cls.ADMIN_API_KEY and cls.ADMIN_API_KEY

    @classmethod
    def get_config_summary(cls) -> Dict:
        """Get current security configuration (for admin)."""
        return {
            'require_api_key': cls.REQUIRE_API_KEY,
            'enable_rate_limiting': cls.ENABLE_RATE_LIMITING,
            'enable_quotas': cls.ENABLE_QUOTAS,
            'rate_limit_per_minute': cls.RATE_LIMIT_PER_MINUTE,
            'rate_limit_per_hour': cls.RATE_LIMIT_PER_HOUR,
            'daily_request_quota': cls.DAILY_REQUEST_QUOTA,
            'daily_cost_quota': cls.DAILY_COST_QUOTA,
            'num_valid_keys': len(cls.VALID_API_KEYS),
            'ip_rate_limit_per_minute': cls.IP_RATE_LIMIT_PER_MINUTE
        }


def get_api_key_from_request() -> Optional[str]:
    """Extract API key from request headers or query params."""
    # Try header first (preferred)
    api_key = request.headers.get('X-API-Key') or request.headers.get('Authorization')

    if api_key and api_key.startswith('Bearer '):
        api_key = api_key[7:]  # Remove 'Bearer ' prefix

    # Fallback to query parameter
    if not api_key:
        api_key = request.args.get('api_key')

    return api_key


def get_client_ip() -> str:
    """Get client IP address (handles proxies)."""
    # Check for forwarded IP (from proxies, load balancers)
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    if request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    return request.remote_addr or 'unknown'


def require_api_key(f):
    """Decorator to require valid API key."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not SecurityConfig.REQUIRE_API_KEY:
            return f(*args, **kwargs)

        api_key = get_api_key_from_request()

        if not api_key:
            return jsonify({
                'error': 'API key required',
                'message': 'Please provide an API key in X-API-Key header or api_key query parameter'
            }), 401

        if not SecurityConfig.is_valid_api_key(api_key):
            return jsonify({
                'error': 'Invalid API key',
                'message': 'The provided API key is not valid'
            }), 403

        # Store API key in request context for use by other decorators
        request.api_key = api_key

        return f(*args, **kwargs)

    return decorated_function


def rate_limit(endpoint_name: str = None, cost_estimate: float = 0.0):
    """
    Decorator to enforce IP-based rate limits and quotas.
    Works with or without API keys - primary protection is IP-based.

    Args:
        endpoint_name: Name of endpoint for tracking (defaults to function name)
        cost_estimate: Estimated cost of this operation in USD
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not SecurityConfig.ENABLE_RATE_LIMITING and not SecurityConfig.ENABLE_QUOTAS:
                return f(*args, **kwargs)

            # Run periodic cleanup to prevent memory leaks
            usage_tracker.auto_cleanup_if_needed()

            # Get identifier - prioritize IP-based tracking
            client_ip = get_client_ip()
            api_key = getattr(request, 'api_key', None)

            # Use IP as primary identifier (even if API key exists)
            ip_identifier = f"ip:{client_ip}"
            endpoint = endpoint_name or f.__name__

            # Check IP-based rate limits (ALWAYS enforced)
            if SecurityConfig.ENABLE_RATE_LIMITING:
                # Per-minute rate limit (IP-based)
                allowed, retry_after = usage_tracker.check_rate_limit(
                    ip_identifier,
                    endpoint,
                    window_seconds=60,
                    max_requests=SecurityConfig.IP_RATE_LIMIT_PER_MINUTE
                )

                if not allowed:
                    return jsonify({
                        'error': 'Rate limit exceeded',
                        'message': f'Too many requests from your IP. Please try again in {retry_after} seconds.',
                        'retry_after': retry_after,
                        'limit_type': 'ip_per_minute'
                    }), 429

                # Per-hour rate limit (IP-based)
                allowed, retry_after = usage_tracker.check_rate_limit(
                    ip_identifier,
                    endpoint,
                    window_seconds=3600,
                    max_requests=SecurityConfig.IP_RATE_LIMIT_PER_HOUR
                )

                if not allowed:
                    return jsonify({
                        'error': 'Hourly rate limit exceeded',
                        'message': f'Hourly limit reached from your IP. Please try again in {retry_after // 60} minutes.',
                        'retry_after': retry_after,
                        'limit_type': 'ip_per_hour'
                    }), 429

                # Additional per-key limits if API key is present
                if api_key:
                    allowed, retry_after = usage_tracker.check_rate_limit(
                        api_key,
                        endpoint,
                        window_seconds=60,
                        max_requests=SecurityConfig.RATE_LIMIT_PER_MINUTE
                    )

                    if not allowed:
                        return jsonify({
                            'error': 'API key rate limit exceeded',
                            'message': f'Too many requests with this API key. Please try again in {retry_after} seconds.',
                            'retry_after': retry_after,
                            'limit_type': 'api_key_per_minute'
                        }), 429

            # Check IP-based daily quotas (ALWAYS enforced)
            if SecurityConfig.ENABLE_QUOTAS:
                daily_usage = usage_tracker.get_daily_usage(ip_identifier)
                daily_cost = usage_tracker.get_daily_cost(ip_identifier)

                if daily_usage >= SecurityConfig.IP_DAILY_REQUEST_QUOTA:
                    return jsonify({
                        'error': 'Daily quota exceeded',
                        'message': f'Daily request quota of {SecurityConfig.IP_DAILY_REQUEST_QUOTA} exceeded from your IP',
                        'usage': {
                            'requests_today': daily_usage,
                            'quota': SecurityConfig.IP_DAILY_REQUEST_QUOTA
                        },
                        'limit_type': 'ip_daily_requests'
                    }), 429

                if daily_cost + cost_estimate > SecurityConfig.IP_DAILY_COST_QUOTA:
                    return jsonify({
                        'error': 'Daily cost quota exceeded',
                        'message': f'Daily cost quota of ${SecurityConfig.IP_DAILY_COST_QUOTA:.2f} would be exceeded from your IP',
                        'usage': {
                            'cost_today': f'${daily_cost:.2f}',
                            'quota': f'${SecurityConfig.IP_DAILY_COST_QUOTA:.2f}'
                        },
                        'limit_type': 'ip_daily_cost'
                    }), 429

                # Additional per-key quotas if API key is present
                if api_key:
                    key_daily_usage = usage_tracker.get_daily_usage(api_key)
                    key_daily_cost = usage_tracker.get_daily_cost(api_key)

                    if key_daily_usage >= SecurityConfig.DAILY_REQUEST_QUOTA:
                        return jsonify({
                            'error': 'API key daily quota exceeded',
                            'message': f'Daily request quota of {SecurityConfig.DAILY_REQUEST_QUOTA} exceeded for this API key',
                            'usage': {
                                'requests_today': key_daily_usage,
                                'quota': SecurityConfig.DAILY_REQUEST_QUOTA
                            },
                            'limit_type': 'api_key_daily_requests'
                        }), 429

            # Track usage (both IP and API key if present)
            usage_tracker.increment_usage(ip_identifier, cost_estimate)
            if api_key:
                usage_tracker.increment_usage(api_key, cost_estimate)

            # Execute the function
            response = f(*args, **kwargs)

            # Add rate limit headers to response
            if isinstance(response, tuple):
                response_obj, status_code = response[0], response[1]
            else:
                response_obj, status_code = response, 200

            if hasattr(response_obj, 'headers'):
                # IP-based limits in headers
                response_obj.headers['X-RateLimit-Limit-Minute'] = str(SecurityConfig.IP_RATE_LIMIT_PER_MINUTE)
                response_obj.headers['X-RateLimit-Limit-Hour'] = str(SecurityConfig.IP_RATE_LIMIT_PER_HOUR)
                remaining_today = SecurityConfig.IP_DAILY_REQUEST_QUOTA - usage_tracker.get_daily_usage(ip_identifier)
                response_obj.headers['X-RateLimit-Remaining-Today'] = str(max(0, remaining_today))

            # Return tuple if original response was a tuple, otherwise just the response object
            if isinstance(response, tuple):
                return response_obj, status_code
            else:
                return response_obj

        return decorated_function

    return decorator


def admin_only(f):
    """Decorator to require admin API key."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = get_api_key_from_request()

        if not SecurityConfig.is_admin_key(api_key):
            return jsonify({
                'error': 'Admin access required',
                'message': 'This endpoint requires admin privileges'
            }), 403

        return f(*args, **kwargs)

    return decorated_function


def generate_api_key() -> str:
    """Generate a new API key."""
    import secrets
    return secrets.token_urlsafe(32)


def hash_api_key(api_key: str) -> str:
    """Hash an API key for secure storage."""
    return hashlib.sha256(api_key.encode()).hexdigest()
