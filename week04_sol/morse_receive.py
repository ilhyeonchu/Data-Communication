import math
import statistics
import struct
import time

import pyaudio

fs = 48000
chunk_size = 1024

MORSE_THRESHOLD = 700  # 소리로 인식할 최소 임계값
UNSEEN_THRESHOLD = 5   # 초 단위, 연속된 무음 기준
UNIT = 0.1             # 기본 시간 단위

english = {'A':'.-'   , 'B':'-...' , 'C':'-.-.' , 'D':'-..'  ,
           'E':'.'    , 'F':'..-.' , 'G':'--.'  , 'H':'....' , 
           'I':'..'   , 'J':'.---' , 'K':'-.-'  , 'L':'.-..' , 
           'M':'--'   , 'N':'-.'   , 'O':'---'  , 'P':'.--.' , 
           'Q':'--.-' , 'R':'.-.'  , 'S':'...'  , 'T':'-'    , 
           'U':'..-'  , 'V':'...-' , 'W':'.--'  , 'X':'-..-' , 
           'Y':'-.--' , 'Z':'--..'}

number = { '1':'.----', '2':'..---', '3':'...--', '4':'....-',
           '5':'.....', '6':'-....', '7':'--...', '8':'---..', 
           '9':'----.', '0':'-----'}

def morse2text(morse):
    text = ''
    words = morse.split(' '*7)
    for word in words:
        letters = word.split(' '*3)
        for letter in letters:
            letter = letter.replace(' ', '')
            if letter in english.values():
                text += list(english.keys())[list(english.values()).index(letter)]
            elif letter in number.values():
                text += list(number.keys())[list(number.values()).index(letter)]
            else:
                text += letter
        text += ' '
    return text.strip()

def receive():
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=fs,
                    input=True)

    audio = []
    morse = ''
    tuning = True      # 데이터 시작 전에는 튜닝 상태로 둠
    in_signal = False  # 현재 신호(소리) 중인지 여부
    start_time = 0
    last_signal_time = time.time()  # 마지막 신호 감지 시간
    unseen = 0         # 연속된 무음 청크 카운터

    print("Start receiving Morse code...")

    try:
        while True:
            # 청크 단위로 오디오 데이터 읽기
            data = struct.unpack('<' + ('h' * chunk_size), stream.read(chunk_size))
            
            # 각 청크에서 임계값 이상의 소리(신호)가 있는지 확인
            if any(abs(x) >= MORSE_THRESHOLD for x in data):
                # 신호가 감지되었으므로 무음 카운터 초기화
                unseen = 0
                # 아직 튜닝 중이면, 데이터 시작 신호로 간주
                if tuning:
                    tuning = False
                    audio = []  # 기존 데이터 초기화
                    print("Data detected. Starting processing.")
                # 신호가 새로 시작되면 in_signal 플래그 업데이트
                if not in_signal:
                    start_time = time.time()
                    in_signal = True
                audio.extend(data)
            else:
                # 해당 청크에 유의미한 소리 신호가 없는 경우
                unseen += 1
                # 만약 이전 청크에서 신호가 있었다면, 신호 종료 처리
                if in_signal:
                    duration = time.time() - start_time  # 신호 지속 시간 계산
                    empty_interval = start_time - last_signal_time
                    # 신호 사이의 간격에 따라 모스 부호 사이의 공백 추가
                    if empty_interval >= 0.5 * UNIT and empty_interval < 2.5 * UNIT:
                        morse += ' '
                    elif empty_interval >= 2.5 * UNIT and empty_interval < 6.5 * UNIT:
                        morse += '   '
                    elif empty_interval >= 6.5 * UNIT and empty_interval < 10 * UNIT:
                        morse += '       '
                    # 신호 길이에 따른 부호 결정
                    if duration < UNIT * 2:
                        morse += '.'
                    else:
                        morse += '-'
                    last_signal_time = time.time()  # 마지막 신호 시간 업데이트
                    in_signal = False
                    print(f"Current morse: {morse}")

            # 목표3: 일정 시간(청크 수 기준) 연속 무음이면 녹음 종료
            if not tuning and unseen >= (UNSEEN_THRESHOLD / UNIT):
                print('Long silence detected!')
                break

    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
        print("Received Data:", morse2text(morse))

if __name__ == '__main__':
    receive()
