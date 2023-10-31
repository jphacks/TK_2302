import pyaudio
import numpy as np
import time
import matplotlib.pyplot as plt
import os
import subprocess
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

# LINE Botのアクセストークンと送信先のLINEユーザーID
CHANNEL_ACCESS_TOKEN = "27oMU1uJxuOyrGdcC2oNz4cT/PvDYdgZcYS5F26MMx3hg6UYPDB6GDTPQ+rHd47L0v0/++S+tbiDRCLYAkiCW41Nc0E8ifqT28nIB/qCkr7TKpgxsr1Iy/P1Kn0/ZHEYs4Vd13feAn7k7t2dkcfBbAdB04t89/1O/w1cDnyilFU="
LINE_USER_ID = "Ubdf7984c257cb0ee200f04a370d02b83"

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)

def setup():
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    input_device_index=input_device_index,
                    rate=RATE,
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

def delivery_unlock_sequence():
    # ここに宅配のアンロックシーケンスを追加
    pass

def homecoming_unlock_sequence():
    # ここに帰宅のアンロックシーケンスを追加
    pass

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
                    # 画像をLINEに送信
                    image_message = ImageSendMessage(
                        original_content_url=image_filename,
                        preview_image_url=image_filename
                    )
                    line_bot_api.push_message(LINE_USER_ID, image_message)

                time.sleep(5)
                print("Keep watching...")
    except KeyboardInterrupt:
        print('You terminated the program.\nThe program ends.')
        stream.stop_stream()
        stream.close()
        p.terminate()
