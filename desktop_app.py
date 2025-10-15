import webview
import threading
import time
import os
import sys


class Api:
    def minimize(self):
        webview.windows[0].minimize()

    def maximize(self):
        webview.windows[0].maximize()

    def restore(self):
        webview.windows[0].restore()

    def close(self):
        webview.windows[0].destroy()

    def start_drag(self):
        webview.windows[0].move(0, 0)


def run_flask_app():
    # Import here to avoid circular imports
    from main import app, socketio
    port = 5000
    socketio.run(app, host='127.0.0.1', port=port,
                 debug=False, use_reloader=False)


def create_desktop_app():
    # Start Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()

    # Wait a moment for Flask to start
    time.sleep(2)

    # Get the path to the favicon for the window icon
    icon_path = os.path.join(os.path.dirname(
        __file__), 'static', 'favicon.ico')

    # Create the desktop window with enhanced settings
    window = webview.create_window(
        'Stitch Daily Menu',
        'http://127.0.0.1:5000',
        width=1400,
        height=900,
        resizable=True,
        fullscreen=False,
        min_size=(1000, 700),
        frameless=True,  # Borderless for custom styled window controls
        js_api=Api(),  # Enable JavaScript API for window controls
        easy_drag=False,
        text_select=True,
        zoomable=True,
        draggable=True,
        confirm_close=True
    )

    # Start the webview
    webview.start()


if __name__ == '__main__':
    create_desktop_app()
