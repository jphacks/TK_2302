#ラズパイに接続されているマイクのデバイス番号を確認

import pyaudio

p = pyaudio.PyAudio()

for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(f"Device {i}: {info['name']}")

# source myenv/bin/activate
# sudo apt-get install portaudio19-dev
# sudo apt-get install libopenblas-dev
# sudo apt-get install python3-pandas
# pip install -r requirements.txt
# python Notify.py
