import wave
import numpy as np
import matplotlib.pyplot as plt
 
file_name = "intercomSound.wav" # 録音ファイル
RATE = 44100 # 録音時に設定したRATE

wf = wave.open(file_name, "rb")
data = np.frombuffer(wf.readframes(wf.getnframes()), dtype='int16')
wf.close()

x = np.arange(data.shape[0]) / RATE
plt.plot(x, data)
plt.show() # 横軸:時間(sec)
x = [i for i in range(len(data))]
plt.plot(x, data)
plt.show() # 横軸:データ点インデックス
