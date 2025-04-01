import math
import statistics
import struct
import time

import pyaudio

def main():
    t = 10
    fs = 48000

    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt32, channels=1, rate=fs, input=True)
    audio = []

    chunk_size = 1024
    for _ in range(0, math.ceil(fs / chunk_size) * 10):
        data = struct.unpack('<' + ('l'*chunk_size), stream.read(chunk_size))
        audio.extend(data)
        print(statistics.stdev(data))

    stream.stop_stream()
    stream.close()
    p.terminate()

if __name__ == '__main__':
    main()