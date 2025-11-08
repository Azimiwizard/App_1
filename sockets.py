import os
from flask_socketio import SocketIO, emit
from models import db, Order

# Use Redis message queue when REDIS_URL is set so multiple workers/containers can
# share Socket.IO messages (rooms, emits). Falls back to in-memory if not set.
redis_url = os.environ.get('REDIS_URL')
socketio = SocketIO(message_queue=redis_url, async_mode='eventlet')


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
        'order_id': order_id, 'status': status
    })
