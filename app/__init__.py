# app/__init__.py

from flask import Flask
from linebot import LineBotApi, WebhookHandler
import pigpio

app = Flask(__name__)

# LINE Credentials
from config import CHANNEL_SECRET, CHANNEL_ACCESS_TOKEN

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# Servo Motor Configuration
from app import pigpio_config

# Import routes (defined in routes.py)
from app import routes
