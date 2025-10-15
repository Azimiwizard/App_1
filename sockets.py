from flask_socketio import SocketIO, emit
from models import db, Order

socketio = SocketIO()


@socketio.on('connect')
def handle_connect():
    print('Client connected')


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')


@socketio.on('join_order')
def handle_join_order(data):
    order_id = data.get('order_id')
    if order_id:
        emit('order_joined', {'order_id': order_id})


def emit_order_status_update(order_id, status):
    socketio.emit('order_status_update', {
                  'order_id': order_id, 'status': status})
