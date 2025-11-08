from flask import Blueprint, redirect, url_for
from flask_login import current_user

bp = Blueprint('backoffice', __name__)


@bp.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    return 'Backoffice (stub)', 200
