"""
Security configuration for the application.
This module contains security-related configurations and middleware.
"""
from functools import wraps
import secrets
from flask import request, abort, g


def init_security(app):
    """Initialize security configurations, CSP nonces, and response headers."""
    # Set session cookie settings
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=86400,  # 24 hours in seconds
    )

    # Configure CSRF protection
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 hour
    app.config['WTF_CSRF_SSL_STRICT'] = True

    # Configure password hashing (existing choice kept)
    app.config['PASSWORD_HASH_METHOD'] = 'pbkdf2:sha256:600000'

    # Per-request CSP nonce
    @app.before_request
    def _set_csp_nonce():
        g.csp_nonce = secrets.token_urlsafe(16)

    # Expose nonce to templates
    @app.context_processor
    def _inject_nonce():
        return {'csp_nonce': getattr(g, 'csp_nonce', '')}

    # Add security headers to all responses
    @app.after_request
    def _security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # Content Security Policy: do not use unsafe-inline. Use per-request nonce for scripts/styles.
        nonce = getattr(g, 'csp_nonce', '')
        csp = (
            "default-src 'self'; "
            f"script-src 'self' 'nonce-{nonce}'; "
            f"style-src 'self' 'nonce-{nonce}'; "
            "img-src 'self' data:; connect-src 'self' blob:; frame-ancestors 'none'; base-uri 'self';"
        )
        response.headers['Content-Security-Policy'] = csp

        # HSTS only when explicitly enabled and request is secure (or via X-Forwarded-Proto)
        if app.config.get('ENABLE_HSTS') and (request.is_secure or request.headers.get('X-Forwarded-Proto') == 'https'):
            response.headers['Strict-Transport-Security'] = 'max-age=63072000; includeSubDomains; preload'

        return response


def require_secure():
    """Decorator to require HTTPS"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_secure and not request.headers.get('X-Forwarded-Proto', 'http') == 'https':
                abort(403)  # Forbidden - HTTPS required
            return f(*args, **kwargs)
        return decorated_function
    return decorator
