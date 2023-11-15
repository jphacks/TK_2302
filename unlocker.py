import os
import sys
import time
import random
import pigpio
import pygame
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# LINE Credentials
CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET', None)
CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

if CHANNEL_SECRET is None:
    print('Specify LINE_CHANNEL_SECRET as an environment variable.')
    sys.exit(1)

if CHANNEL_ACCESS_TOKEN is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as an environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# Servo Motor Configuration
SERVO_PIN = 18
pi = pigpio.pi()

def set_servo_angle(angle):
    assert 0 <= angle <= 180, '角度は0から180の間に注意する'
    pulse_width = (angle / 180) * (2500 - 500) + 500
    pi.set_servo_pulsewidth(SERVO_PIN, pulse_width)

def play_sound(file_path, volume=20.0):
    pygame.mixer.init()
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

# 置き配の時は、アナウンスして鍵を開ける
def unlock_playsound():
    set_servo_angle(60)
    time.sleep(0.5)
    set_servo_angle(90)
    time.sleep(0.5)
    audio_choice = random.choice(["audio/delivery_announcement.mp3" ])
    play_sound(audio_choice, volume=20.0)
    set_servo_angle(119)
    time.sleep(0.5)
    set_servo_angle(90)
    time.sleep(1)

# アナウンスなしで鍵を開ける
def unlock():
    set_servo_angle(60)
    time.sleep(0.5)
    set_servo_angle(90)
    time.sleep(0.5)
    set_servo_angle(119)
    time.sleep(0.5)
    set_servo_angle(90)
    time.sleep(1)

HOMECOMING_MESSAGES = [
    'おかえり！鍵開けたよー！',
    'お帰りなさい！今日も一日ご苦労様です！',
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
    if text in ['ただいま〜！']:
        unlock()
        response_message = random.choice(HOMECOMING_MESSAGES)
    elif text in ['開けて！']:
        unlock()
        response_message = '開けたよ〜！'
    elif text in ['置き配して！']:
        unlock_playsound() 
        response_message = '置き配しておいたよー'
    else:
        response_message = text
    line_bot_api.reply_message(event.reply_token, TextSendMessage(response_message))

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8000, help='port')
    parser.add_argument('-d', '--debug', default=False, help='debug')
    args = parser.parse_args()
    app.run(debug=args.debug, port=args.port)