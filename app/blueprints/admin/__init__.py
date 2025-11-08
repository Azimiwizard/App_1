from flask import Blueprint, redirect, url_for
from flask_login import current_user

bp = Blueprint('admin', __name__)


@bp.route('/')
def index():
    # Require login; if not logged in redirect to auth.login
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    # Placeholder admin index; later will render admin dashboard template
    return 'Admin dashboard (stub)', 200
