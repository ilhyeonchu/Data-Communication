import wave
import struct

import scipy.fftpack
import numpy as np

from prac03 import rules
from prac04 import sample_rate

unit = 0.1
samplerate = 48000
padding = 5

filename = '실습6-example4-fsk.wav'

print('Raw hex:')
text = ''
with wave.open(filename, 'rb') as w:
    framerate = w.getframerate()
    frames = w.getnframes()
    audio = []
    for i in range(frames):
        frame = w.readframes(1)
        d = struct.unpack('<l', frame)[0]
        audio.append(d)
        if len(audio) >= unit*framerate:
            freq = scipy.fftpack.fftfreq(len(audio), d=1/samplerate)
            fourier = scipy.fftpack.fft(audio)
            top = freq[np.argmax(abs(fourier))]

            data = ''
            for k, v in rules.items():
                if v-padding <= top and top <= v+padding:
                    data = k

            if data == 'END':
                print()
                print(data, end='')
            if data != 'START' and data != 'END':
                text = f'{text}{data}'
                print(data, end='')
            if data == 'START':
                print(data)

            audio.clear()
        print()

    print(f'Decoded: {bytes.fromhex(text).decode("utf-8")}')
