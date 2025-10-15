web: gunicorn --worker-class eventlet --bind 0.0.0.0:$PORT main:app
release: python scripts/init_db_command.py
