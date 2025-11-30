# Minimal Flask webhook for TradingView alerts
import logging

# Try to import Flask; provide lightweight fallbacks when Flask is not
# available (helps static analysis / editor environments).
try:
    from flask import Flask, request, jsonify  # type: ignore
except Exception:
    # Fallback stubs so this file can be linted/inspected without Flask
    from typing import Any

    class _FlaskStub:  # minimal callable stub for Flask()
        def __init__(self, *args, **kwargs):
            pass

        def route(self, *args, **kwargs):
            def _decorator(f):
                return f

            return _decorator

        def run(self, *args, **kwargs):
            raise RuntimeError("Flask is not installed")

    class _RequestStub:  # minimal request with json attribute
        json = None

    def jsonify(x: Any):
        return x

    Flask = _FlaskStub  # type: ignore
    request = _RequestStub()  # type: ignore

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.json
    app.logger.info("Received webhook: %s", payload)
    # TODO: validate signature/HMAC; enqueue for processing
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
