import wave
import struct
import pyaudio
import scipy.fftpack
import time
import numpy as np
from frerule import rules, sample_rate, chunk_size, unit 


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

    hex_list = []
    state = "STAR"
    start_duration = 0
    end_duration = 0
    unit_samples = int(sample_rate * unit)
    buffered_audio = []
    last_symbol = None
    last_time = 0
    now = 0
    min_symbol_interval = 0.25
    freq = ''
    symbol = ''
    try:
        while True:

            data = struct.unpack('<' + ('h' * chunk_size), stream.read(chunk_size))
            buffered_audio.append(data)

            if len(buffered_audio) >= unit_samples:
                freq = np.fft.rfftfreq(len(data), d=1/sample_rate)
                fourier = scipy.fftpack.fft(data)
                top = freq[np.argmax(abs(fourier))]
                
                for k, v in rules.items():
                    if v-padding <= top and top <= v+padding:
                        symbol = k

                if symbol == 'START':
                   start_duration += 1
                else:
                    start_duration = 0
        
                if start_duration >= 2:
                    state = 'DAT'
                    print("[DATA] Receiving...")
        
                if state == 'DAT':
                    if symbol == 'END':
                        end_duration += 1
                    else:
                        end_duration = 0
                    if end_duration >= 2:
                        print("[END] Receiving complete.")
                        break
 #                    now = time.time()
 #        
 #                    if symbol == last_symbol and (now - last_time) < min_symbol_interval:
 #                            continue  # 너무 빠르게 반복된 symbol은 무시
        
                    if symbol in rules and symbol not in ['START', 'END']:
                        hex_list.append(symbol)
                        print("Current data:", ''.join(hex_list))
                        last_symbol = symbol
                        last_time = now
                if symbol not in rules:
                    print(f"[DATA] None with {freq}")

                buffered_audio.clear()

            if state == 'STAR':
                if symbol in rules:
                    print(f"[START] {symbol} with {freq}")
                else:
                    print(f"[START] None with {freq}")
            elif state == 'DAT':
                print(f"[DATA] {symbol} with {freq}")
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

    hex_string = ''.join(hex_list)
    print("HEX:", hex_string)
    if len(hex_string) % 2 != 0:
        hex_string = hex_string[:-1]
    try:
        decoded = bytes.fromhex(hex_string).decode('utf-8')
        print("Decoded text:", decoded)
    except Exception as e:
        print("Decoding failed:", e)

