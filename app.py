from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = Flask(__name__)

# 環境変数から読み込み
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 「こんにちは」と返すだけの Bot
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="Hello! Your bot is running on Render 🚀")
    )

@app.route("/push", methods=["GET", "POST"])
def push_message():
    # LINE_USER_ID が設定されているかチェック
    if USER_ID is None:
        return "LINE_USER_ID is not set", 500

    # 送るメッセージ（とりあえず固定文）
    message = TextSendMessage(text="⏰ 定期メッセージです！")

    # プッシュメッセージ送信
    line_bot_api.push_message(USER_ID, message)

    return "PUSH OK", 200

if __name__ == "__main__":
    app.run()
