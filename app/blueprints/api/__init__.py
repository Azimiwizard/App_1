from flask import Blueprint, jsonify

bp = Blueprint('api', __name__)


@bp.route('/status')
def status():
    return jsonify({'status': 'ok'})
