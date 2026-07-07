import os
import threading
import time

import webview

from app import app

PORT = int(os.environ.get("PORT", 5001))
URL = f"http://127.0.0.1:{PORT}/"


def start_server():
    app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False)


if __name__ == "__main__":
    server = threading.Thread(target=start_server, daemon=True)
    server.start()

    for _ in range(50):
        try:
            import urllib.request
            urllib.request.urlopen(f"http://127.0.0.1:{PORT}/", timeout=0.2)
            break
        except Exception:
            time.sleep(0.1)

    webview.create_window(
        "CyberVault",
        URL,
        width=1100,
        height=720,
        resizable=True,
    )
    webview.start()
