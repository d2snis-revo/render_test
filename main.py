import os
import random

from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)
line_bot_api = LineBotApi('cKtDec+oMDzR+76vJ8PoLAc9EAIMz5K8QEugP3899a/59RPJD0eRNQh71MFIC1UoKKYvUDGyNjNOgCPsSm7+zhdULh/yp0zdRva7y6lOqZ3C3FSLMRRFXEXN7l9Cr1nNQ2bFJLuL7QShVyQimnRilQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('fe0d85ead292f342d68123c9033c430a')

participant_list = []


@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['x-line-signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global participant_list
    cnt = 0

    # 参加人数の登録
    if event.message.text == "!r":
        message = TextSendMessage(text="参加人数 N を入力してください。\n※注意:(N >= 12)")
        line_bot_api.reply_message(event.reply_token, message)

    # 参加人数の受け取りとリスト更新
    elif isinstance(event.message.text, str) and event.message.text.isdecimal():
        n = int(event.message.text)
        participant_list = [str(i) for i in range(1, n+1)]
        message = TextSendMessage(text="参加者リストを更新しました。")
        line_bot_api.reply_message(event.reply_token, message)

    # 参加人数から組み合わせを計算
    elif event.message.text == "!s":
        num_pairs = int(len(participant_list) / 2)
        if num_pairs < 6:
            message = TextSendMessage(text="参加人数が少なすぎます。")
            line_bot_api.reply_message(event.reply_token, message)
            return

        random_participants = random.sample(participant_list, 12)

        random.shuffle(random_participants)
        assignment_list = [(random_participants[i], random_participants[i+1]) for i in range(0, len(random_participants), 2)]

        message = "ペア 1・2 は 1 コート\nペア 3・4 は 2 コート\nペア 5・6 は 3 コート\n"

        cnt+=1
        message += "-------{}試合目-------\n".format(cnt)
        for i, court_assignments in enumerate(assignment_list):
            message += "ペア{} : {} と {}\n".format(i+1, court_assignments[0], court_assignments[1])

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=message)
        )

        assignment_list = []

    else:
        pass

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
