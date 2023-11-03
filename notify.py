import pyaudio
import wave
import numpy as np
import time
import requests
import subprocess

Check_every_time = False
LINE_token = "U7lf4Njva7q2of618fHlbXfMeDneRPSSUdWsRp3rR3G"

RECORD_SECONDS = 1
threshold = 1.0e5
threshold2 = 5
freq_indices = [510, 511, 512, 513, 514, 515, 516, 639, 640, 641, 642, 643, 644, 768, 769, 770, 771, 1539, 2308, 2309]
freq_indices2 = [f * 2 for f in freq_indices]

input_device_index = 1  # check_dev_id.pyで確認したusbマイク番号
CHUNK = 1024 * 8
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 48000 # サンプルレートの設定 一般的な値は44100Hzまたは48000Hz
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

# Capture and save an image using subprocess to call a command-line tool
def capture_and_save_image():
    try:
        subprocess.run(["fswebcam", "-r", "1280x720", "--no-banner", "captured_image.jpg"])  # Adjust resolution and other options as needed
    except Exception as e:
        print(f"Failed to capture image: {e}")

# Function to send an image via LINE Notify
def send_image_via_LINE(token, image_path, amp, amp2, threshold, threshold2):
    url = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": "Bearer " + token}
    message = "誰か来たよ〜\n強度 {:.2e} --- 基準 {:.1e}\n比率 {:.2e} --- 基準 {:.1e}".format(amp,threshold,amp/amp2,threshold2)
    payload = {"message": message}
    files = {"imageFile": (image_path, open(image_path, "rb"), "image/jpeg")}
    r = requests.post(url, headers=headers, params=payload, files=files)

if __name__ == '__main__':
    p, stream = setup()
    print("Watching...")
    try:
        while True:
            d = collect_data(stream, rng, CHUNK)
            amp, amp2 = calc_FFTamp(d, freq_indices, freq_indices2)
            if (amp > threshold) and (amp / amp2 > threshold2):
                print("Someone is at the door.")
                capture_and_save_image()  # Capture and save an image
                send_image_via_LINE(LINE_token, "captured_image.jpg")  # Send the image
                if Check_every_time:
                    pass
                time.sleep(10)
                print("Keep watching...")
    except KeyboardInterrupt:
        print('You terminated the program.\nThe program ends.')
        stream.stop_stream()
        stream.close()
        p.terminate()
