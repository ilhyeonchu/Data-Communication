import math
import statistics
import struct
import time
import wave
import os

import pyaudio

INTMAX = 2**(32-1)-1

english = {'A':'.-'   , 'B':'-...' , 'C':'-.-.' ,
           'D':'-..'  , 'E':'.'    , 'F':'..-.' ,
           'G':'--.'  , 'H':'....' , 'I':'..'   ,
           'J':'.---' , 'K':'-.-'  , 'L':'.-..' ,
           'M':'--'   , 'N':'-.'   , 'O':'---'  ,
           'P':'.--.' , 'Q':'--.-' , 'R':'.-.'  ,
           'S':'...'  , 'T':'-'    , 'U':'..-'  ,
           'V':'...-' , 'W':'.--'  , 'X':'-..-' ,
           'Y':'-.--' , 'Z':'--..'  }
number = { '1':'.----', '2':'..---', '3':'...--',
           '4':'....-', '5':'.....', '6':'-....',
           '7':'--...', '8':'---..', '9':'----.',
           '0':'-----'}
char_to_morse = {**english, **number}
morse_to_char = {v: k for k, v in char_to_morse.items()}

t = 0.1
fs = 48000
f = 523.251 #C5


def file2morse(filename):
    with wave.open(filename, 'rb') as w:
        audio = []
        framerate = w.getframerate()
        frames = w.getnframes()
        for i in range(frames):
            frame = w.readframes(1)
            audio.append(struct.unpack('<i', frame)[0])
        morse = ''
        unit = int(t * fs)
        for i in range(1, math.ceil(len(audio) / unit) + 1):
            stdev = statistics.stdev(audio[(i - 1) * unit:i * unit])
            if stdev > 10000:
                morse = morse + '.'
            else:
                morse = morse + ' '
        morse = morse.replace('...', '-')
        morse = morse.replace('       ', ' / ')  # 단어 바뀜
        morse = morse.replace('   ', ' + ')  # 문자 바뀜
    return morse


# 모스를 오디오로
def morse2audio(morse):
    audio = []
    blank = 0
    for m in morse:
        if m == '.':
            blank = 0
            for i in range(int(t * fs * 1)):
                audio.append(int(INTMAX * math.sin(2 * math.pi * f * (i / fs))))
        elif m == '-':
            blank = 0
            for i in range(int(t * fs * 3)):
                audio.append(int(INTMAX * math.sin(2 * math.pi * f * (i / fs))))
        elif m == ' ':  # 공백의 경우 처리
            blank += 1  # 하나의 char의 경우는 공백이 1개 단어의 경우는 공백이 2개
            if blank >= 2:  # 공백이 2개이므로 단어 바뀜
                for i in range(int(t * fs * 3)):  # 3유닛의 공백 추가 이유는 보고서에 따로 작성
                    audio.append(int(0))
            else:  # 공백이 1개이므로 문자 바뀜
                for i in range(int(t * fs * 2)):  # 2유닛의 공백 추가 이유는 보고서에 따로 작성
                    audio.append(int(0))
        for i in range(int(t * fs * 1)):
            audio.append(int(0))
    return audio


# 오디오를 WAV 파일로 저장
def audio2file(audio, filename):
    with wave.open(filename, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(4)
        w.setframerate(fs)
        for a in audio:
            w.writeframes(struct.pack('<l', a))


# 텍스트를 모스로
def text2morse(text):
    text = text.upper()
    morse = ''

    for t in text:
        if t == ' ':
            morse = morse + ' '
            continue

        for key, value in english.items():
            if t == key:
                morse = morse + value + ' '
        for key, value in number.items():
            if t == key:
                morse = morse + value + ' '

    return morse


# 모스를 텍스트로 변환
def morse2text(morse):
    text = ''
    word = ''
    
    for code in morse.split(' '):  # 모스코드 단어 단위로 나누기
        if code == '+':  # 문자 바뀜 word에 모여있는 모스 코드들을 문자로 변환 후 text에 추가
            if word in morse_to_char:
                text += morse_to_char[word]
            word = ''
        elif code == '/':  # 단어 바뀜 word에 모여있는 모스 코드들을 문자로 변환 후 text에 추가
            if word in morse_to_char:
                text += morse_to_char[word]
            text += ' '
            word = ''
        else:  # 모스 코드를 word에 추가시켜 나중에 문자단위로 변환
            word += code

    return text


def send_data():
    text = input('Enter text: ').strip()
    morse = text2morse(text)
    print("Morse code: ", morse)
    audio = morse2audio(morse)
    audio2file(audio, 'send.wav')
    pass

def receive_data():
    THRESHOLD = 1000
    UNSEEN_LIMIT = 10
    UNIT = int(t * fs)

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt32, channels=1, rate=fs, input=True)
    print("신호 대기 중")
    audio = []
    unseen = 0
    recording_start = False
    morse = ''
    try:
        while True:
            data = stream.read(UNIT)
            values = struct.unpack('<' + 'h' * UNIT, data)
            stdev = statistics.stdev(values)

            if stdev > THRESHOLD:
                if not recording_start:
                    print("녹음 시작")
                    recording_start = True
                audio.extend(values)
                morse += '.'
                unseen = 0
            elif recording_start:
                unseen += 1
                morse += ' '
                if unseen > UNSEEN_LIMIT:
                    recording_start = False
                    print("녹음 종료")
                    break
            if recording_start:
                print(f"\r녹음 중 Morse: {morse}", end='')

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

    filename = 'receive.wav'
    with wave.open(filename, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(4)
        w.setframerate(fs)
        for a in audio:
            w.writeframes(struct.pack('<l', a))

    print("저장 완료")
    morse = file2morse(filename)
    print("수신한 코드: ", morse)
    text = morse2text(morse)
    print("수신한 문자열: ", text)
    pass

def main():
    while True:
        print('Morse Code over Sound with Noise')
        print('2025 Spring Data Communication at CNU')
        print('[1] Send morse code over sound (play)')
        print('[2] Receive morse code over sound (record)')
        print('[q] Exit')
        select = input('Select menu: ').strip().upper()
        if select == '1':
            send_data()
        elif select == '2':
            receive_data()
        elif select == 'Q':
            print('Terminating...')
            break;

if __name__ == '__main__':
    main()