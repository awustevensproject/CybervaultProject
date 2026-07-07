"""
Launch CyberVault as a native desktop app (no browser needed).
"""
import os
import threading
import time

import webview

from app import app

PORT = int(os.environ.get("PORT", 5001))
URL = f"http://127.0.0.1:{PORT}/login"
WINDOW_SIZE = 600


def start_server():
    os.environ["CYBERVAULT_NATIVE"] = "1"
    app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False)


if __name__ == "__main__":
    os.environ["CYBERVAULT_NATIVE"] = "1"

    server = threading.Thread(target=start_server, daemon=True)
    server.start()

    # Wait for Flask to be ready
    for _ in range(50):
        try:
            import urllib.request
            urllib.request.urlopen(f"http://127.0.0.1:{PORT}/login", timeout=0.2)
            break
        except Exception:
            time.sleep(0.1)

    webview.create_window(
        "CyberVault",
        URL,
        width=WINDOW_SIZE,
        height=WINDOW_SIZE,
        resizable=False,
    )
    webview.start()
