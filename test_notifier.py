import pyaudio
import wave
import numpy as np
import time
import matplotlib.pyplot as plt
import requests

Check_every_time = False  # 検知したときにFFTプロット。実際に運用するときはFalse。

RECORD_SECONDS = 1  
threshold = 7.0e5  # 要調整
freq_indices = [694, 695, 696, 697, 833, 834, 835, 1669, 2084, 2085, 2086, 2087, 2503, 2780, 2781, 2782, 3244, 3245]
input_device_index = 1
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
        data = stream.read(CHUNK, exception_on_overflow=False)  # 第2回参照
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
    freqList = np.fft.fftfreq(d.shape[0], d=1.0/RATE)  # 周波数（グラフの横軸）の取得
    plt.plot(freqList, fft_data)
    plt.xlim(0, 5000)  # 0～5000Hzまでとりあえず表示する
    plt.show()

def send_LINE(token, amp, threshold):
    url = "https://notify-api.line.me/api/notify"
    token = token
    headers = {"Authorization": "Bearer " + token}
    message = "インターホンが鳴っているかも(検出強度{:.2e}/{:.1e})".format(amp, threshold)
    payload = {"message": message}
    r = requests.post(url, headers=headers, params=payload)

if __name__ == '__main__':
    LINE_token = "YOUR_LINE_TOKEN_HERE"  # Replace with your LINE Notify token
    p, stream = setup()
    print("Watching...")
    try:
        while True:
            d = collect_data(stream, rng, CHUNK)
            amp = calc_FFTamp(d, freq_indices)
            if amp > threshold:
                print("Someone is at the door. (amp = {:.2e}/{:.1e})".format(amp, threshold))
                send_LINE(LINE_token, amp, threshold)
                if Check_every_time:
                    check_plot(d)
                time.sleep(5)
                print("Keep watching...")
    except KeyboardInterrupt:
        print('You terminated the program.\nThe program ends.')
        stream.stop_stream()
        stream.close()
        p.terminate()
