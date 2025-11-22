from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = Flask(__name__)

# 環境変数
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_USER_ID = os.getenv("LINE_USER_ID")

# エラー防止（起動時にチェック）
if CHANNEL_ACCESS_TOKEN is None:
    raise ValueError("環境変数 LINE_CHANNEL_ACCESS_TOKEN が設定されていません")

if CHANNEL_SECRET is None:
    raise ValueError("環境変数 LINE_CHANNEL_SECRET が設定されていません")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)


# ====== LINE Webhook ======
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


# ====== 返信テスト ======
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="Hello! Your bot is running on Render 🚀")
    )


# ====== GitHub Actions から叩く定期送信用 ======
@app.route("/job", methods=["GET", "POST"])
def job():
    if LINE_USER_ID is None:
        return "LINE_USER_ID is not set", 500

    try:
        line_bot_api.push_message(
            LINE_USER_ID,
            TextSendMessage(text="⏰ 定期テストメッセージです")
        )
        return "OK", 200
    except Exception as e:
        return str(e), 500


# ====== root の表示（動作確認用）======
@app.route("/", methods=["GET"])
def index():
    return "LINE Bot is running.", 200


if __name__ == "__main__":
    app.run()
