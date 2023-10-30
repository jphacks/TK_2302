import pyaudio
import wave
import numpy as np
import time
import matplotlib.pyplot as plt
import requests

Check_every_time = False # 検知したときにFFTプロット。実際に運用するときはFalse。

RECORD_SECONDS = 1 # 第3回で使用した値に合わせる
threshold = 1.5e7 # 要調整
freq_indices = [ 610,  611,  612,  613,  615,  616, 1831, 1832, 1833, 1834, 1835, \
                 1836, 3056, 3057, 3058, 3059, 4277, 4278, 4280, 4281, 4282, 4283, \
                 4285 ] # 第3回で決めた値を入れる

input_device_index = 2 # 第1回で調べた値
CHUNK = 1024 * 8 # 第1~3回で使用した値に合わせる
FORMAT = pyaudio.paInt16
CHANNELS = 1 # モノラル入力
RATE = 44100 # 第1~3回で使用した値に合わせる
rng = int(RATE / CHUNK * RECORD_SECONDS)

def setup():
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    input_device_index = input_device_index,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK,
                    )
    return p, stream

def collect_data(stream, rng, CHUNK):
    frames = []
    for i in range(rng):
        data = stream.read(CHUNK, exception_on_overflow=False) # 第2回参照
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
    fft_data = np.abs(np.fft.fft(d))    #FFTした信号の強度
    freqList = np.fft.fftfreq(d.shape[0], d=1.0/RATE)    #周波数（グラフの横軸）の取得
    plt.plot(freqList, fft_data)
    plt.xlim(0, 5000)    #0～5000Hzまでとりあえず表示する
    plt.show()

def send_LINE(token, amp, threshold):
    url = "https://notify-api.line.me/api/notify" 
    token = token
    headers = {"Authorization" : "Bearer "+ token} 
    message =  "インターホンが鳴っているかも(検出強度{:.2e}/{:.1e})".format(amp,threshold) 
    payload = {"message" :  message} 
    r = requests.post(url, headers = headers, params=payload)

if __name__ == '__main__':
    p, stream = setup()
    print("Watching...")
    try:
        while True:
            d = collect_data(stream, rng, CHUNK)            
            amp = calc_FFTamp(d, freq_indices)
            if amp > threshold:
                print("Someone is at the door. (amp = {:.2e}/{:.1e})".format(amp,threshold))
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
