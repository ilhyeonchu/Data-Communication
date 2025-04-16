import wave
import struct
import pyaudio
import scipy.fftpack
import numpy as np
from frerule import rules, sample_rate, chunk_size unit 


padding = 5
unit_samples = int(sample_rate * unit)
buffered_audio = []
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
    state = "STAR"
    current_symbol = None
    symbol_duration = 0
    unit_threshold = 2

    while True:
        data = stream.read(chunk_size, exception_on_overflow=False)
        audio = np.frombuffer(data, dtype=np.int16)
        buffered_audio.extend(audio)

        if len(buffered_audio) < unit_samples:
            continue

        combined = np.array(buffered_audio[:unit_samples])
        buffered_audio = buffered_audio[unit_samples:]
        spectrum = np.abs(np.fft.rfft(audio))
        freqs = np.fft.rfftfreq(len(audio), d=1/sample_rate)
        dominant_freq = freqs[np.argmax(spectrum)]
        freq = round(dominant_freq, 1)
        symbol = None
        matched_freq = None
        tolerance = 40
        for target_freq, symb in reverse_rules.items():
            if abs(freq - target_freq) <= tolerance:
                symbol = symb
                matched_freq = target_freq
                break

        if symbol == current_symbol:
           symbol_duration += 1

        else:
            if current_symbol == 'START' and state == 'STAR' and symbol_duration >= unit_threshold:
                print("[DATA] Receiving...")
                state = 'DAT'

            elif current_symbol == 'END' and state == 'DAT' and symbol_duration >= unit_threshold:
                print("[END] Detected. Ending.")
                break

            elif current_symbol in rules and state == 'DAT' and symbol_duration >= unit_threshold:
                hex_list.append(current_symbol)
                print(f"[DATA] {current_symbol} with {matched_freq if matched_freq is not None else freq}")
                print("Current data:", ''.join(hex_list))

            current_symbol = symbol
            symbol_duration = 1 

        if state == 'STAR':
            print(f"[START] {symbol} with {matched_freq if matched_freq is not None else freq}")
        elif state == 'DAT' and symbol is not None:
            print(f"[DATA] {symbol} with {matched_freq if matched_freq is not None else freq}")

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

