import pyaudio
import wave
import numpy as np
import time
import matplotlib.pyplot as plt
import requests
import cv2  # OpenCVライブラリを追加

Check_every_time = False 
LINE_token = "U7lf4Njva7q2of618fHlbXfMeDneRPSSUdWsRp3rR3G"

RECORD_SECONDS = 1
threshold = 1.0e5
threshold2 = 5
freq_indices = [694, 695, 696, 697, 833, 834, 835, 1669, 2084, 2085, 2086, 2087, 2503, 2780, 2781, 2782, 3244, 3245]
freq_indices2 = [f * 2 for f in freq_indices]

input_device_index = 1  # check_dev_id.pyで確認したusbマイク番号
CHUNK = 1024 * 8
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
rng = int(RATE / CHUNK * RECORD_SECONDS)

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

def calc_FFTamp(frames, freq_indices, freq_indices2):
    fft_data = np.abs(np.fft.fft(frames))
    amp, amp2 = 0, 0
    for i in freq_indices:
        amp += fft_data[i]
    for i in freq_indices2:
        amp2 += fft_data[i]
    return amp, amp2

def check_plot(d):
    fft_data = np.abs(np.fft.fft(d))    #FFTした信号の強度
    freqList = np.fft.fftfreq(d.shape[0], d=1.0/RATE)    #周波数（グラフの横軸）の取得
    plt.plot(freqList, fft_data)
    plt.xlim(0, 5000)    #0～5000Hzまでとりあえず表示する
    plt.show()

def send_LINE(token, amp, amp2, threshold, threshold2):
    url = "https://notify-api.line.me/api/notify"
    token = token
    headers = {"Authorization": "Bearer " + token}
    message =  "が鳴ってるよ\n強度 {:.2e} --- 基準 {:.1e}\n比率 {:.2e} --- 基準 {:.1e}".format(amp, threshold, amp/amp2, threshold2)
    payload = {"message": message}
    r = requests.post(url, headers=headers, params=payload)

# 画像のキャプチャと送信を行う関数を追加
def capture_and_send_image(token):
    cap = cv2.VideoCapture(0)  # カメラデバイスのIDは必要に応じて調整する

    ret, frame = cap.read()
    if ret:
        cv2.imwrite('captured_image.jpg', frame)

        url = "https://notify-api.line.me/api/notify"
        headers = {"Authorization": "Bearer " + token}
        message = "Someone is at the door."
        payload = {"message": message}
        files = {'imageFile': open('captured_image.jpg', 'rb')}
        r = requests.post(url, headers=headers, params=payload, files=files)

        cap.release()
    else:
        print("Failed to capture image")

if __name__ == '__main__':
    p, stream = setup()
    print("Watching...")
    try:
        while True:
            d = collect_data(stream, rng, CHUNK)
            amp, amp2 = calc_FFTamp(d, freq_indices, freq_indices2)
            if (amp > threshold) & (amp/amp2 > threshold2):
                print("Someone is at the door.")
                send_LINE(LINE_token, amp, amp2, threshold, threshold2)
                capture_and_send_image(LINE_token)  # 画像をキャプチャして送信
                if Check_every_time:
                    check_plot(d)
                time.sleep(5)
                print("Keep watching...")
    except KeyboardInterrupt:
        print('You terminated the program.\nThe program ends.')
        stream.stop_stream()
        stream.close()
        p.terminate()
