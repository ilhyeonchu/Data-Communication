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
    tuning = True
    last_symbol = None
    last_time = 0
    now = 0
    min_symbol_interval = 0.25  # 초 단위, 같은 symbol이 이내로 반복되면 무시

    while True:
        data = stream.read(chunk_size, exception_on_overflow=False)
        audio = np.frombuffer(data, dtype=np.int16)
        buffered_audio.extend(audio)

        if len(buffered_audio) < unit_samples:
            continue

        combined = np.array(buffered_audio[:unit_samples])
        buffered_audio = buffered_audio[unit_samples:]
        spectrum = np.abs(np.fft.rfft(combined))
        freqs = np.fft.rfftfreq(len(combined), d=1/sample_rate)
        dominant_freq = freqs[np.argmax(spectrum)]
        freq = round(dominant_freq, 1)
        symbol = None
        matched_freq = None
        tolerance = 15
        for target_freq, symb in reverse_rules.items():
            if abs(freq - target_freq) <= tolerance:
                symbol = symb
                matched_freq = target_freq
                break

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
            now = time.time()

            if symbol == last_symbol and (now - last_time) < min_symbol_interval:
                    continue  # 너무 빠르게 반복된 symbol은 무시

            if symbol in rules and symbol not in ['START', 'END']:
                hex_list.append(symbol)
                print("Current data:", ''.join(hex_list))
                last_symbol = symbol
                last_time = now

        if state == 'STAR':
            print(f"[START] {symbol} with {matched_freq if matched_freq is not None else freq}")
        elif state == 'DAT':
            print(f"[DATA] {symbol} with {matched_freq if matched_freq is not None else freq}")

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

