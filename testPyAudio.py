import pyaudio
import numpy as np
import time
from scipy.signal import argrelmax

# interphone setting
CHUNK = 1024
RATE = 8000    # sampling rate
dt = 1/RATE
freq = np.linspace(0,1.0/dt,CHUNK)
fn = 1/dt/2;    # nyquist freq
FREQ_HIGH_BASE = 900 # high tone frequency
FREQ_ERR = 0.02         # allowable freq error
# variable
detect_high = False

# FFTで振幅最大の周波数を取得する関数
def getMaxFreqFFT(sound, chunk, freq):
    # FFT
    f = np.fft.fft(sound)/(chunk/2)
    f_abs = np.abs(f)
    # ピーク検出
    peak_args = argrelmax(f_abs[:(int)(chunk/2)])
    f_peak = f_abs[peak_args]
    f_peak_argsort = f_peak.argsort()[::-1]
    peak_args_sort = peak_args[0][f_peak_argsort]
    # 最大ピークをreturn
    return freq[peak_args_sort[0]]

# 検知した周波数がインターホンの高音の音か判定する関数
def detectHighTone(freq_in, freq_high_base, freq_err):
    # 検知した周波数が高音のX倍音なのか調べる
    octave_h = freq_in / freq_high_base
    near_oct_h = round(octave_h)
    if near_oct_h == 0:
        return False
    # X倍音のXが整数からどれだけ離れているか
    err_h = np.abs((octave_h - near_oct_h) / near_oct_h)

    # 基音、２倍音、３倍音の付近であれば高音とする
    if err_h < freq_err:
        return True
    return False

if __name__ == '__main__':
    P = pyaudio.PyAudio()
    stream = P.open(format=pyaudio.paInt16, channels=1, rate=RATE, frames_per_buffer=CHUNK, input=True, output=False)
    
    while stream.is_active():
        try:
            input = stream.read(CHUNK, exception_on_overflow=False)
            ndarray = np.frombuffer(input, dtype='int16')
            abs_array = np.abs(ndarray) / 32768
        
            if abs_array.max() > 0.5:
                # FFTで最大振幅の周波数を取得
                freq_max = getMaxFreqFFT(ndarray, CHUNK, freq)
                print("振幅最大の周波数:", freq_max, "Hz")
                if detectHighTone(freq_max, FREQ_HIGH_BASE, FREQ_ERR):
                    detect_high = True
                    print("高音検知！")
    
                # 高音が検出された場合の処理をここに追加できます
    
        except KeyboardInterrupt:
            break
        
    stream.stop_stream()
    stream.close()
    P.terminate()
