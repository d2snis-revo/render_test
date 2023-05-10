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
input_flag = False
delete_flag = False

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
    global input_flag
    global delete_flag
    
    # 参加人数の登録
    if event.message.text == "!r":
        message = TextSendMessage(text="参加人数を入力してください.")
        input_flag = True
        line_bot_api.reply_message(event.reply_token, message)

    # 参加人数の受け取りとリスト更新
    elif isinstance(event.message.text, str) and event.message.text.isdecimal() and input_flag:
        n = int(event.message.text)
        participant_list = [str(i) for i in range(1, n+1)]
        message = TextSendMessage(text="参加人数を更新しました.")
        input_flag = False
        line_bot_api.reply_message(event.reply_token, message)

    # 参加人数から組み合わせを計算
    elif event.message.text == "!s":
        num_pairs = int(len(participant_list) / 2)
        if num_pairs < 6:
            message = TextSendMessage(text="参加人数が少なすぎます.")
            line_bot_api.reply_message(event.reply_token, message)
            return

        random_participants = random.sample(participant_list, 12)

        random.shuffle(random_participants)
        assignment_list = [(random_participants[i], random_participants[i+1]) for i in range(0, len(random_participants), 2)]

        #出力部分
        for i in range(0, len(assignment_list), 6):
            court1 = assignment_list[i:i+2]
            court2 = assignment_list[i+2:i+4]
            court3 = assignment_list[i+4:i+6]
            
            message = "・1コート\n"
            message += "-----------------------\n"
            for j in range(2):
                message += "|     {}    |     {}   |\n".format(court1[j][0].zfill(2), court1[j][1].zfill(2))
            message += "-----------------------\n"
            
            message += "・2コート\n"
            message += "-----------------------\n"
            for j in range(2):
                message += "|     {}    |     {}   |\n".format(court2[j][0].zfill(2), court2[j][1].zfill(2))
            message += "-----------------------\n"
            
            message += "・3コート\n"
            message += "-----------------------\n"
            for j in range(2):
                message += "|     {}    |     {}   |\n".format(court3[j][0].zfill(2), court3[j][1].zfill(2))
            message += "-----------------------"
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=message)
            )

        assignment_list = []
        
    # 番号の削除
    elif event.message.text == "!d":
        message = TextSendMessage(text="削除する番号を入力してください.")
        delete_flag = True
        line_bot_api.reply_message(event.reply_token, message)

    elif isinstance(event.message.text, str) and event.message.text.isdecimal() and len(participant_list) > 0 and delete_flag:
        deleted_index = int(event.message.text) - 1
        if deleted_index >= 0 and deleted_index < len(participant_list):
            deleted_player = participant_list.pop(deleted_index)
            message = TextSendMessage(text="{}を参加者リストから削除しました.".format(deleted_player))
            delete_flag = False
        else:
            message = TextSendMessage(text="正しい番号を入力してください.")

        line_bot_api.reply_message(event.reply_token, message)

    # 参加者リストの表示
    elif event.message.text == "!h":
        if len(participant_list) > 0:
            message = "・現在の参加者リスト\n" + "\n".join(participant_list)
        else:
            message = "現在, 参加者はいません."

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=message)
        )

    else:
        pass

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
