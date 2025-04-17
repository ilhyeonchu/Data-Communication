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
    top = 0
    try:
        while True:
            # 오디오 데이터 읽기
            data = struct.unpack('<' + ('h' * chunk_size), stream.read(chunk_size))
            buffered_audio.append(data)
            
            # 현재 오디오 볼륨(소음) 계산 - RMS 값 사용
            noise_level = np.sqrt(np.mean(np.array(data)**2))
            
            if len(buffered_audio) >= unit_samples:
                # 주파수 분석
                freq = np.fft.rfftfreq(len(data), d=1/sample_rate)
                fourier = scipy.fftpack.fft(data)
                magnitude = np.abs(fourier)
                max_idx = np.argmax(magnitude)
                top = freq[max_idx]
                peak_magnitude = magnitude[max_idx]
                
                # 이전 심볼 초기화
                symbol = None
                
                # 주파수에 맞는 심볼 찾기
                for k, v in rules.items():
                    if v-padding <= top and top <= v+padding:
                        symbol = k
                        break

                # START 신호 감지 및 처리
                if symbol == 'START':
                   start_duration += 1
                else:
                    start_duration = 0
        
                # START 신호가 충분히 오래 지속되면 상태 변경
                if start_duration >= 2 and state == 'STAR':
                    state = 'DAT'
                    print("[DATA] Receiving started...")
                    hex_list = []  # 데이터 초기화
        
                # 데이터 수신 상태일 때 END 신호 처리
                if state == 'DAT':
                    if symbol == 'END':
                        end_duration += 1
                    else:
                        end_duration = 0
                    
                    if end_duration >= 2:
                        print("[END] Receiving complete.")
                        break
                    
                    now = time.time()
                    
                    # 유효한 데이터 심볼이면 저장
                    if symbol and symbol not in ['START', 'END']:
                        # 중복 심볼 필터링 (선택사항)
                        if symbol != last_symbol or (now - last_time) > min_symbol_interval:
                            hex_list.append(symbol)
                            print("Current data:", ''.join(hex_list))
                            last_symbol = symbol
                            last_time = now

                # 버퍼 초기화
                buffered_audio.clear()

            # 상태에 따른 로그 출력
            if state == 'STAR':
                if symbol in rules:
                    print(f"[START] {symbol} with freq={top:.2f}Hz, noise={noise_level:.2f}")
                else:
                    print(f"[START] None with freq={top:.2f}Hz, noise={noise_level:.2f}")
            elif state == 'DAT':
                if symbol:
                    print(f"[DATA] {symbol} with freq={top:.2f}Hz, noise={noise_level:.2f}")
                else:
                    print(f"[DATA] None with freq={top:.2f}Hz, noise={noise_level:.2f}")
                    
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

    # 수신 완료 후 데이터 처리
    hex_string = ''.join(hex_list)
    print("HEX:", hex_string)
    if len(hex_string) % 2 != 0:
        hex_string = hex_string[:-1]
    try:
        decoded = bytes.fromhex(hex_string).decode('utf-8')
        print("Decoded text:", decoded)
    except Exception as e:
        print("Decoding failed:", e)

