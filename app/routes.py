import time
import random
import pigpio
import pygame
from flask import request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from app import app

# ラインボットAPIとハンドラの初期化
line_bot_api = LineBotApi(app.config['LINE_CHANNEL_ACCESS_TOKEN'])
handler = WebhookHandler(app.config['LINE_CHANNEL_SECRET'])

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

def delivery_unlock_sequence():
    set_servo_angle(60)
    time.sleep(0.5)
    set_servo_angle(90)
    time.sleep(0.5)
    play_sound("audio/app/announcement.mp3", volume=20.0)
    set_servo_angle(119)
    time.sleep(0.5)
    set_servo_angle(90)
    time.sleep(1)

def homecoming_unlock_sequence():
    set_servo_angle(60)
    time.sleep(0.5)
    set_servo_angle(90)
    time.sleep(0.5)
    audio_choice = random.choice(["audio/voice1.mp3", "audio/voice2.mp3","audio/voice3.mp3" ])
    play_sound(audio_choice, volume=20.0)
    set_servo_angle(119)
    time.sleep(0.5)
    set_servo_angle(90)
    time.sleep(1)

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
