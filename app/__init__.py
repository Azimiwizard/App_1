from .. import rate_limiting
from .extensions import db, migrate, login_manager, csrf, cache, socketio
from logging_config import setup_logging, init_sentry
from cors_config import init_cors
from ..security import init_security
import os
from flask import Flask
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__, instance_relative_config=False)

    # Load config from environment
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
        'DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get(
        'SECRET_KEY') or 'dev-secret-key-change-in-production'
    app.config['MAX_CONTENT_LENGTH'] = int(
        os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))
    app.config['UPLOAD_FOLDER'] = os.environ.get(
        'UPLOAD_FOLDER', 'static/uploads')
    app.config['ENABLE_HSTS'] = os.environ.get(
        'ENABLE_HSTS', 'false').lower() in ('1', 'true', 'yes')
    app.config['REDIS_URL'] = os.environ.get('REDIS_URL')

    # Init security and cors
    init_security(app)
    init_cors(app)

    # Initialize logging and sentry
    setup_logging(app)
    init_sentry(app)

    # Initialize Flask extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Cache init (Redis when REDIS_URL set)
    cache_config = {
        'CACHE_TYPE': 'RedisCache' if app.config.get('REDIS_URL') else 'SimpleCache',
        'CACHE_DEFAULT_TIMEOUT': 300,
    }
    if app.config.get('REDIS_URL'):
        cache_config['CACHE_REDIS_URL'] = app.config['REDIS_URL']
    cache.init_app(app, config=cache_config)

    # Limiter initialization uses rate_limiting module which will pick up REDIS_URL if present
    rate_limiting.init_limiter(app)

    # SocketIO: sockets.py defines and configures the global socketio instance; initialize with app
    try:
        # The socketio instance is created in sockets.py and may already have message_queue set from REDIS_URL
        from ..sockets import socketio as shared_socketio
        shared_socketio.init_app(app, async_mode='eventlet')
    except Exception:
        # If anything fails, continue without raising at factory time; runtime issues will surface later.
        pass

    # Register blueprints (stubs exist)
    from .blueprints.auth import bp as auth_bp
    from .blueprints.backoffice import bp as backoffice_bp
    from .blueprints.admin import bp as admin_bp
    from .blueprints.api import bp as api_bp
    from .blueprints.pos import bp as pos_bp
    from .blueprints.inventory import bp as inventory_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(backoffice_bp, url_prefix='/backoffice')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(pos_bp, url_prefix='/pos')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')

    # Basic health route
    @app.route('/health')
    def _health():
        return 'ok', 200

    # CLI command to seed RBAC roles and permissions
    @app.cli.command('seed_rbac')
    def seed_rbac():
        """Create default roles and permissions. Safe to run multiple times."""
        from models import Permission, Role, Users
        with app.app_context():
            # Define permissions
            perms = {
                'manage_backoffice': 'Manage backoffice UI and content',
                'pos_sell': 'Perform POS sales',
                'view_kitchen': 'View kitchen orders',
                'view_finance': 'View finance reports',
                'admin_all': 'Administrative full access'
            }

            created = {}
            for code, desc in perms.items():
                p = Permission.query.filter_by(code=code).first()
                if not p:
                    p = Permission(code=code, description=desc)
                    db.session.add(p)
                    db.session.commit()
                created[code] = p

            # Roles mapping
            roles_map = {
                'owner': ['admin_all'],
                'admin': ['admin_all'],
                'manager': ['manage_backoffice'],
                'cashier': ['pos_sell'],
                'kitchen': ['view_kitchen'],
                'accountant': ['view_finance']
            }

            for role_name, perm_codes in roles_map.items():
                r = Role.query.filter_by(name=role_name).first()
                if not r:
                    r = Role(name=role_name)
                    db.session.add(r)
                    db.session.commit()
                # assign permissions
                for code in perm_codes:
                    p = created.get(code)
                    if p and p not in r.permissions:
                        r.permissions.append(p)
                db.session.add(r)
                db.session.commit()

            # If there is no user with admin role, optionally assign to first user
            first_user = Users.query.first()
            if first_user:
                admin_role = Role.query.filter_by(name='admin').first()
                if admin_role and admin_role not in first_user.roles:
                    # users model may not have roles relationship – add if present
                    try:
                        first_user.roles.append(admin_role)
                        db.session.add(first_user)
                        db.session.commit()
                        print('Assigned admin role to first user:', first_user.id)
                    except Exception:
                        # If Users model doesn't expose roles relationship, skip assignment
                        pass

            print('RBAC seed complete')

    return app
