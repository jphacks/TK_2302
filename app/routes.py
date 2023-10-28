# app/routes.py

from flask import request, abort
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from app import app, handler, line_bot_api
import pygame
import time
import random
from app.pigpio_config import set_servo_angle
from app.audio_config import play_sound

DELIVERY_MESSAGES = [
    '開けておいたよ！',
    '置き配って伝えておいたよ〜！'
]

HOMECOMING_MESSAGES = [
    'おかえり〜！鍵開けたよー',
    'お帰りなさい！',
    'おかえりだね！鍵開けたよー',
    'おつかれさま！'
]

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    if text in ['ただいま', '鍵開けて']:
        homecoming_unlock_sequence()
        response_message = random.choice(HOMECOMING_MESSAGES)
    elif text in ['宅配']:
        delivery_unlock_sequence()
        response_message = random.choice(DELIVERY_MESSAGES)
    else:
        response_message = text
    line_bot_api.reply_message(event.reply_token, TextSendMessage(response_message))
