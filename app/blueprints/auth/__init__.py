from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Minimal login stub: render existing template if present, otherwise simple form
    if request.method == 'POST':
        # In full implementation, authenticate via Supabase or local DB
        email = request.form.get('email')
        flash('Login stub — implement authentication in blueprint')
        return redirect(url_for('auth.login'))
    try:
        return render_template('login.html')
    except Exception:
        return 'Login page (stub)', 200


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
