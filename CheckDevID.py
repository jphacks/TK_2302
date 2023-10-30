# https://forums.raspberrypi.com/viewtopic.php?t=71062
import pyaudio
p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
  dev = p.get_device_info_by_index(i)
  print((i,dev['name'],dev['maxInputChannels']))
# (0, 'bcm2835 HDMI 1: - (hw:0,0)', 0)
# (1, 'bcm2835 Headphones: - (hw:1,0)', 0)
# (2, 'USB PnP Sound Device: Audio (hw:2,0)', 1)
# (3, 'sysdefault', 0)
# (4, 'lavrate', 0)
# (5, 'samplerate', 0)
# (6, 'speexrate', 0)
# (7, 'pulse', 32)
# (8, 'upmix', 0)
# (9, 'vdownmix', 0)
# (10, 'dmix', 0)
# (11, 'default', 32)
