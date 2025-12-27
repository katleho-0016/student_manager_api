from flask import request, jsonify
import time
import threading
from functools import wraps

# Simple in-memory fixed-window rate limiter keyed by client IP.

_counters = {}
_lock = threading.Lock()

def _get_key():
    return request.remote_addr or 'global'

def rate_limit(max_requests=60, window_seconds=60):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            key = _get_key()
            now = time.time()
            with _lock:
                count, start = _counters.get(key, (0, now))
                if now - start >= window_seconds:
                    count = 0
                    start = now
                count += 1
                _counters[key] = (count, start)
                remaining = max_requests - count

            if count > max_requests:
                retry_after = int(window_seconds - (now - start))
                resp = jsonify({'error': 'rate limit exceeded', 'retry_after': retry_after})
                return resp, 429, {'Retry-After': str(retry_after)}

            result = f(*args, **kwargs)

            # Try to attach simple rate-limit headers for common return types
            try:
                if isinstance(result, tuple):
                    body = result[0]
                    status = result[1] if len(result) > 1 else None
                    headers = result[2] if len(result) > 2 else {}
                    if headers is None:
                        headers = {}
                    if isinstance(headers, dict):
                        headers['X-RateLimit-Limit'] = str(max_requests)
                        headers['X-RateLimit-Remaining'] = str(max(0, remaining))
                        if status is not None:
                            return (body, status, headers)
                        return (body, headers)
                else:
                    # probably a Flask Response object
                    try:
                        result.headers['X-RateLimit-Limit'] = str(max_requests)
                        result.headers['X-RateLimit-Remaining'] = str(max(0, remaining))
                    except Exception:
                        pass
            except Exception:
                pass

            return result

        return wrapped
    return decorator
