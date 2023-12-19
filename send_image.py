import pyaudio
import numpy as np
import requests
import subprocess
import boto3
from linebot import LineBotApi
from linebot.models import ImageSendMessage, TextSendMessage
import time

# AWS S3の設定
aws_access_key_id = 'AKIASBTXWFRW4JEVGCMN'
aws_secret_access_key = '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'
bucket_name = 'linebot-raspi-images'

# Line Botの設定
line_bot_token = '27oMU1uJxuOyrGdcC2oNz4cT/PvDYdgZcYS5F26MMx3hg6UYPDB6GDTPQ+rHd47L0v0/++S+tbiDRCLYAkiCW41Nc0E8ifqT28nIB/qCkr7TKpgxsr1Iy/P1Kn0/ZHEYs4Vd13feAn7k7t2dkcfBbAdB04t89/1O/w1cDnyilFU='
line_bot_secret = '3287df393e1f658f8a2078f387766e77'
line_bot_api = LineBotApi(line_bot_token)
user_id = 'Ubdf7984c257cb0ee200f04a370d02b83'  # メッセージを受信するユーザーのID

# マイクとフーリエ変換に関する設定
input_device_index = 1
CHUNK = 1024 * 8
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000
rng = int(RATE / CHUNK)

# 閾値と周波数インデックス
threshold = 4.0e7
threshold2 = 5
freq_indices = [510, 511, 512, 513, 514, 515, 516, 639, 640, 641, 642, 643, 644, 768, 769, 770, 771, 1539, 2308, 2309]
freq_indices2 = [f * 2 for f in freq_indices]

def setup_audio():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    input_device_index=input_device_index,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    return p, stream

def collect_audio_data(stream, rng):
    frames = []
    for i in range(rng):
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
    d = np.frombuffer(b''.join(frames), dtype='int16')
    return d

def calc_FFT_amp(frames, freq_indices, freq_indices2):
    fft_data = np.abs(np.fft.fft(frames))
    amp, amp2 = 0, 0
    for i in freq_indices:
        amp += fft_data[i]
    for i in freq_indices2:
        amp2 += fft_data[i]
    return amp, amp2

def capture_and_save_image():
    try:
        subprocess.run(["fswebcam", "-r", "1280x720", "--no-banner", "captured_image.jpg"])
    except Exception as e:
        print(f"Failed to capture image: {e}")

def upload_image_to_s3():
    s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
    image_path = 'captured_image.jpg'
    s3_object_key = 'captured_image.jpg'
    s3.upload_file(image_path, bucket_name, s3_object_key)
    return f'https://{bucket_name}.s3.amazonaws.com/{s3_object_key}'

def send_message_and_image(line_bot_api, user_id, image_url, amp, amp2, threshold, threshold2):
    message = TextSendMessage(text="誰かきたよ！")
    image_message = ImageSendMessage(original_content_url=image_url, preview_image_url=image_url)
    line_bot_api.push_message(user_id, [message, image_message])

if __name__ == '__main__':
    p, stream = setup_audio()
    print("Watching...")
    try:
        while True:
            audio_data = collect_audio_data(stream, rng)
            amp, amp2 = calc_FFT_amp(audio_data, freq_indices, freq_indices2)
            if (amp > threshold) and (amp / amp2 > threshold2):
                print("Someone is at the door.")
                capture_and_save_image()
                image_url = upload_image_to_s3()
                send_message_and_image(line_bot_api, user_id, image_url, amp, amp2, threshold, threshold2)
                time.sleep(10)
                print("Keep watching...")
    except KeyboardInterrupt:
        print('You terminated the program.\nThe program ends.')
        stream.stop_stream()
        stream.close()
        p.terminate()
