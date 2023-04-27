import os

from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

line_bot_api = LineBotApi('cKtDec+oMDzR+76vJ8PoLAc9EAIMz5K8QEugP3899a/59RPJD0eRNQh71MFIC1UoKKYvUDGyNjNOgCPsSm7+zhdULh/yp0zdRva7y6lOqZ3C3FSLMRRFXEXN7l9Cr1nNQ2bFJLuL7QShVyQimnRilQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('fe0d85ead292f342d68123c9033c430a')

players = []

@app.route('/')
def index():
    return 'Hello World!'


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
    global players
    text = event.message.text
    if text == '!r':
        players = []
        reply_text = '参加人数を入力してください。'
    elif text.isdigit():
        num_players = int(text)
        players = [str(i) for i in range(1, num_players+1)]
        reply_text = '参加人数を登録しました。'
    elif text == '!s':
        if len(players) == 0:
            reply_text = '参加人数が登録されていません。'
        else:
            num_courts = len(players) // 12
            if num_courts < 1:
                reply_text = '参加人数が12人未満のため、組み合わせを作成できません。'
            else:
                reply_text = ''
                for i in range(num_courts):
                    reply_text += f'\nコート{i+1}:\n'
                    court_players = players[i*12:(i+1)*12]
                    for j in range(6):
                        pair = court_players[j*2:(j+1)*2]
                        reply_text += f'{pair[0]}-{pair[1]}\n'
        players = []
    else:
        reply_text = '「!r」で参加人数を登録、「!s」で組み合わせを表示します。'

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

