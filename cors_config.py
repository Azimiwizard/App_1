"""
CORS configuration for the application.
"""
from flask_cors import CORS
from flask import current_app


def init_cors(app):
    """Initialize CORS with secure configuration"""
    # In development, allow all origins
    if app.debug:
        CORS(app)
    else:
        # In production, only allow specific origins
        allowed_origins = app.config.get('CORS_ALLOWED_ORIGINS', [
            'https://stitch-daily-menu.com',
            'https://www.stitch-daily-menu.com'
        ])

        CORS(app, resources={
            r"/*": {
                "origins": allowed_origins,
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization", "X-CSRF-Token"],
                "expose_headers": ["Content-Range", "X-Content-Range"],
                "supports_credentials": True,
                "max_age": 600  # Cache preflight requests for 10 minutes
            }
        })
