"""
Rate limiting configuration for the application.
This module contains rate limiting setup and decorators.
"""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os

limiter = None


def init_limiter(app):
    """Initialize rate limiting for the application"""
    global limiter
    # Prefer explicit RATELIMIT_STORAGE_URL, otherwise fall back to REDIS_URL if set,
    # otherwise keep memory storage for local/dev.
    storage = os.environ.get('RATELIMIT_STORAGE_URL') or os.environ.get(
        'REDIS_URL') or 'memory://'

    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        storage_uri=storage,
        strategy="fixed-window",
        # Default limits can be configured via env RATELIMIT_DEFAULT
        default_limits=[app.config.get('RATELIMIT_DEFAULT', '100/hour')],
    )

    return limiter


def configure_route_limits(app, limiter):
    """Configure rate limits for specific routes"""
    # Apply limits if the view functions exist (some may be moved to blueprints).
    def safe_limit(endpoint_name, limit):
        try:
            view = app.view_functions.get(endpoint_name)
            if view is not None:
                limiter.limit(limit)(view)
        except Exception:
            # If a route isn't present yet (blueprint not registered), skip silently.
            pass

    # Authentication routes
    safe_limit('login', '5/minute')
    safe_limit('register', '3/minute')

    # API routes (names may change after blueprint split)
    safe_limit('add_to_cart', '30/minute')
    safe_limit('place_order', '60/minute')

    # Admin routes - more permissive
    safe_limit('admin_dashboard', '300/hour')

    # Review submission
    safe_limit('add_review', '10/hour')
