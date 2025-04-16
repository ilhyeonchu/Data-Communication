import wave
import struct
import pyaudio
import scipy.fftpack
import numpy as np
from frerule import rules, sample_rate, chunk_size

padding = 5

reverse_rules = {v: k for k, v in rules.items()}

def receive():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=sample_rate,
                    input=True,
                    frames_per_buffer=chunk_size)
    print("[START] Listening...")

    start_count = 0
    end_count = 0
    hex_list = []
    state = "WAIT_START"

    while True:
        data = stream.read(chunk_size, exception_on_overflow=False)
        audio = np.frombuffer(data, dtype=np.int16)
        spectrum = np.abs(np.fft.rfft(audio))
        freqs = np.fft.rfftfreq(len(audio), d=1/sample_rate)
        dominant_freq = freqs[np.argmax(spectrum)]
        freq = round(dominant_freq, 1)
        symbol = reverse_rules.get(round(freq), None)

        if state == "WAIT_START":
            print(f"[START] {symbol} with {freq}")
            if symbol == 'START':
                start_count += 1
                if start_count >= 2:
                    print("[DATA] Receiving...")
                    state = "RECEIVING"
                else:
                    start_count = 0

        elif state == "RECEIVING":
            if symbol is None:
                print(f"[DATA] None with {freq}")
                continue
            elif symbol == 'END':
                end_count += 1
                if end_count >= 2:
                    print("[END] Detected. Ending.")
                    break
            else:
                end_count = 0
                hex_list.append(symbol)
                print(f"[DATA] {symbol} with {freq}")
                print("Current data:", ''.join(hex_list))

    stream.stop_stream()
    stream.close()
    p.terminate()

    hex_string = ''.join(hex_list)
    print("HEX:", hex_string)
    try:
        decoded = bytes.fromhex(hex_string).decode('utf-8')
        print("Decoded text:", decoded)
    except Exception as e:
        print("Decoding failed:", e)

