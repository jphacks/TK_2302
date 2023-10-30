#ラズパイに接続されているマイクのデバイス番号を確認

import pyaudio

p = pyaudio.PyAudio()

for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(f"Device {i}: {info['name']}")
# Device 0: bcm2835 Headphones: - (hw:2,0)
# Device 1: USB PnP Sound Device: Audio (hw:3,0)
# Device 2: pulse
# Device 3: default
