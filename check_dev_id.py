#ラズパイに接続されているマイクのデバイス番号を確認

import pyaudio

p = pyaudio.PyAudio()

for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(f"Device {i}: {info['name']}")

# Device 0: bcm2835 Headphones: - (hw:2,0)
# Device 1: UACDemoV1.0: USB Audio (hw:3,0)
# Device 2: USB PnP Audio Device: Audio (hw:4,0)
# Device 3: USB Device 0x46d:0x825: Audio (hw:5,0)
# Device 4: pulse
# Device 5: default

