from flask import Flask, jsonify, request
import os
from dotenv import load_dotenv

from linebot.v3 import WebhookHandler
from linebot.v3.messaging import Configuration
from linebot.v3.exceptions import InvalidSignatureError

load_dotenv()
app = Flask(__name__)
configuration = Configuration(
    access_token=os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
)

handler = WebhookHandler(
    os.getenv("LINE_CHANNEL_SECRET")
)

@app.route("/")
def home():
    return jsonify({
        "status": "success",
        "message": "SubWise Backend is running!"
    })

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "Invalid signature", 400

    return "OK"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)