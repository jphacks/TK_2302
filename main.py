import pyaudio
import numpy as np
import time
import matplotlib.pyplot as plt
import os
import subprocess
import requests  # Add this import
from linebot import LineBotApi
from linebot.models import ImageSendMessage

Check_every_time = True  # 検知したときにFFTプロット。実際に運用するときはFalse。

RECORD_SECONDS = 1
threshold = 5.0e5  # 要調整
freq_indices = [694, 695, 696, 697, 833, 834, 835, 1669, 2084, 2085, 2086, 2087, 2503, 2780, 2781, 2782, 3244, 3245]

input_device_index = 1  # check_dev_id.pyで確認したデバイス番号に置き換え
CHUNK = 1024 * 8
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
rng = int(RATE / CHUNK * RECORD_SECONDS)

# LINE Notifyのアクセストークン
LINE_NOTIFY_TOKEN = "U7lf4Njva7q2of618fHlbXfMeDneRPSSUdWsRp3rR3GE"  # LINE Notifyのトークンを設定

line_bot_api = LineBotApi(LINE_NOTIFY_TOKEN)

def setup():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    input_device_index=input_device_index,
                    rate=gRATE,
                    
                    input=True,
                    frames_per_buffer=CHUNK,
                    )
    return p, stream

def collect_data(stream, rng, CHUNK):
    frames = []
    for i in range(rng):
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)
    d = np.frombuffer(b''.join(frames), dtype='int16')
    return d

def calc_FFTamp(frames, freq_indices):
    fft_data = np.abs(np.fft.fft(frames))
    amp = 0
    for i in freq_indices:
        amp += fft_data[i]
    return amp

def check_plot(d):
    fft_data = np.abs(np.fft.fft(d))  # FFTした信号の強度
    freqList = np.fft.fftfreq(d.shape[0], d=1.0 / RATE)  # 周波数（グラフの横軸）の取得
    plt.plot(freqList, fft_data)
    plt.xlim(0, 5000)  # 0～5000Hzまでとりあえず表示する
    plt.show()

# カメラキャプチャ関数
def capture_image():
    try:
        # fswebcamコマンドを使用して画像をキャプチャ
        image_filename = "captured_image.jpg"
        subprocess.call(["fswebcam", "-r", "1280x720", "--no-banner", image_filename])
        return image_filename
    except Exception as e:
        print("Error capturing image:", str(e))
        return None

if __name__ == '__main__':
    p, stream = setup()
    print("Watching...")
    try:
        while True:
            d = collect_data(stream, rng, CHUNK)
            amp = calc_FFTamp(d, freq_indices)
            if amp > threshold:
                print("Someone is at the door. (amp = {:.2e}/{:.1e})".format(amp, threshold))
                if Check_every_time:
                    check_plot(d)
                
                # USBカメラで画像をキャプチャ
                image_filename = capture_image()
                
                if image_filename:
                    # 画像をLINE Notifyに送信
                    message = 'Someone is at the door!'
                    image_url = "https://notify-api.line.me/api/notify"
                    headers = {'Authorization': f'Bearer {LINE_NOTIFY_TOKEN}'}
                    payload = {'message': message}
                    files = {'imageFile': open(image_filename, 'rb')}
                    response = requests.post(image_url, headers=headers, params=payload, files=files)
                    print("Notification sent:", response.text)

                time.sleep(5)
                print("Keep watching...")
    except KeyboardInterrupt:
        print('You terminated the program.\nThe program ends.')
        stream.stop_stream()
        stream.close()
        p.terminate()
