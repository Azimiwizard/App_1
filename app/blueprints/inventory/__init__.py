from flask import Blueprint

bp = Blueprint('inventory', __name__)


@bp.route('/')
def index():
    return 'Inventory stub', 200
