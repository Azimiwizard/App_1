from flask import Blueprint

bp = Blueprint('pos', __name__)


@bp.route('/')
def index():
    return 'POS stub', 200
