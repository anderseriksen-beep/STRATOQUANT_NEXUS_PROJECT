# Minimal Flask webhook for TradingView alerts
from flask import Flask, request, jsonify
import logging

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
