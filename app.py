from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os

app = Flask(__name__)

# ===== 環境変数の読み込み =====
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_USER_ID = os.getenv("LINE_USER_ID")  # プッシュ先の userId

# 念のためチェック（デプロイ時にすぐ気づけるように）
if CHANNEL_ACCESS_TOKEN is None or CHANNEL_SECRET is None:
    raise ValueError("環境変数 LINE_CHANNEL_ACCESS_TOKEN / LINE_CHANNEL_SECRET が設定されていません。")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# ===== 動作確認用のトップページ =====
@app.route("/", methods=["GET"])
def index():
    return "LINE bot is running on Render.", 200

# ===== Webhook（ユーザーからのメッセージ受信） =====
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# ===== 「こんにちは」と返すだけの Bot =====
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="Hello! Your bot is running on Render 🚀")
    )

# ===== GitHub Actions から叩く定期メッセージ用のエンドポイント =====
@app.route("/job", methods=["GET", "POST"])
def job():
    """
    GitHub Actions などから叩いて定期メッセージを送る用のエンドポイント
    GET：ブラウザからのテスト
    POST：GitHub Actions などからの実行
    """
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

if __name__ == "__main__":
    # ローカルで動かすとき用（Renderでは gunicorn が使うのでほぼ通らない）
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
