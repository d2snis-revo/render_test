import itertools
import math
import os

from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ["cKtDec+oMDzR+76vJ8PoLAc9EAIMz5K8QEugP3899a/59RPJD0eRNQh71MFIC1UoKKYvUDGyNjNOgCPsSm7+zhdULh/yp0zdRva7y6lOqZ3C3FSLMRRFXEXN7l9Cr1nNQ2bFJLuL7QShVyQimnRilQdB04t89/1O/w1cDnyilFU="])
handler = WebhookHandler(os.environ["fe0d85ead292f342d68123c9033c430a"])

pair_count = 0
pair_combinations = []

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global pair_count, pair_combinations
    message = ""
    if event.message.text == "!r":
        pair_count = 0
        pair_combinations = []
        message = "参加人数を入力してください。"
    elif event.message.text == "!s":
        if pair_count > 0:
            match_count = int(math.ceil(pair_count / 3))
            for i, pair_combination in enumerate(pair_combinations):
                if i % match_count == 0:
                    message += "\n試合{}\n".format(int(i / match_count) + 1)
                for j, pair in enumerate(pair_combination):
                    court = j % 3 + 1
                    message += "コート{}：{}と{}\n".format(court, pair[0] + 1, pair[1] + 1)
        else:
            message = "参加人数が入力されていません。"
    elif event.message.text.isdigit():
        X = int(event.message.text)
        if X >= 12 and X <= 100:
            pair_count = int(X / 2)
            message = "ペア数：{}\n".format(pair_count)

            pairs = list(itertools.combinations(range(X), 2))
            pair_combinations = list(itertools.combinations(pairs, pair_count))
            message += "組み合わせ数：{}\n\n".format(len(pair_combinations))

            for i, pair_combination in enumerate(pair_combinations):
                if i == 0:
                    message += "最初のペア：\n"
                message += "ペア{}：{}と{}\n".format(i + 1, pair_combination[0][0] + 1, pair_combination[0][1] + 1)
            message += "\nペアが決定されました。試合を始める場合は、\"!s\"を入力してください。"
        else:
            message = "12以上100以下の整数を半角で入力してください。"
    else:
        message = "正しい形式で整数を入力してください。"

    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))

if __name__ == "__main__":
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
