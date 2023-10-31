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

# Import additional libraries
import pyaudio
import wave
import numpy as np
import requests
from PIL import ImageGrab  # Use ImageGrab from Pillow

app = Flask(__name__)

# LINE Credentials (Your existing code)

# Servo Motor Configuration (Your existing code)

# ... (Other functions and configurations)

# Capture an image from the webcam using Pillow (ImageGrab)
def capture_image():
    image = ImageGrab.grab()
    image_filename = "captured_image.jpg"
    image.save(image_filename)
    return image_filename

# ... (Other functions)

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=8000, help='port')
    parser.add_argument('-d', '--debug', default=False, help='debug')
    args = parser.parse_args()
    app.run(debug=args.debug, port=args.port)
