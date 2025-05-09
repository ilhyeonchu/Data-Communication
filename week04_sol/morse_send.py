import math
import re
import struct
import time
import wave

import pyaudio

INTMAX = 2**(16-1)-1
fs = 48000

english = {'A':'.-'   , 'B':'-...' , 'C':'-.-.' , 'D':'-..'  ,
           'E':'.'    , 'F':'..-.' , 'G':'--.'  , 'H':'....' , 
           'I':'..'   , 'J':'.---' , 'K':'-.-'  , 'L':'.-..' , 
           'M':'--'   , 'N':'-.'   , 'O':'---'  , 'P':'.--.' , 
           'Q':'--.-' , 'R':'.-.'  , 'S':'...'  , 'T':'-'    , 
           'U':'..-'  , 'V':'...-' , 'W':'.--'  , 'X':'-..-' , 
           'Y':'-.--' , 'Z':'--..'  }

number = { '1':'.----', '2':'..---', '3':'...--', '4':'....-',
           '5':'.....', '6':'-....', '7':'--...', '8':'---..', 
           '9':'----.', '0':'-----'}

           
def text2morse(text):
    text = text.upper()
    morse = ''

    for t in text:
        if t == ' ':
            morse += '/'
        elif t in english:
            morse += english[t]
        elif t in number:
            morse += number[t]
        morse += ' '
    print(morse)
    return morse

def morse2audio(morse):
    unit = 0.1  # 기본 단위
    f = 523.251  # 톤 주파수
    audio = []
    
    # 단어 단위로 분리 (단어 구분 기호: '/')
    words = morse.strip().split(' / ')
    for w_index, word in enumerate(words):
        # 글자 단위로 분리 (글자 구분: 공백 1개 혹은 3개를 사용할 수 있음)
        letters = word.strip().split(' ')
        for l_index, letter in enumerate(letters):
            # 부호 단위로 처리
            for s_index, symbol in enumerate(letter):
                if symbol == '.':
                    # 점: 1 단위 톤
                    for i in range(int(unit * fs)):
                        audio.append(int(INTMAX * math.sin(2 * math.pi * f * (i / fs))))
                elif symbol == '-':
                    # 대시: 3 단위 톤
                    for i in range(int(unit * fs * 3)):
                        audio.append(int(INTMAX * math.sin(2 * math.pi * f * (i / fs))))
                # 부호 내 간격 (마지막 부호가 아니라면 1 단위 침묵)
                if s_index != len(letter) - 1:
                    for i in range(int(unit * fs)):
                        audio.append(0)
            # 글자 간 간격 (글자 끝난 후, 마지막 글자가 아니라면 3 단위 침묵)
            if l_index != len(letters) - 1:
                for i in range(int(unit * fs * 3)):
                    audio.append(0)
        # 단어 간 간격 (단어 끝난 후, 마지막 단어가 아니라면 7 단위 침묵)
        if w_index != len(words) - 1:
            for i in range(int(unit * fs * 7)):
                audio.append(0)
    return audio


def audio2file(audio, filename):
    with wave.open(filename, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(4)
        w.setframerate(fs)
        for a in audio:
            w.writeframes(struct.pack('<l', a))
    
    print("saved to", filename)


def send():
    while True:
        print('Type some text (only English and Number)')
        text = input('User input: ').strip()
        if re.match(r'[A-Za-z0-9 ]+', text):
            break

    audio = morse2audio(text2morse(text))
    
    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=fs,
                    output=True)

    chunk_size = 4096
    for i in range(0, len(audio), chunk_size):
        chunk = audio[i:i+chunk_size]
        stream.write(struct.pack('<' + ('h'*len(chunk)), *chunk))

    stream.stop_stream()
    stream.close()
    p.terminate()


if __name__ == '__main__':
    send()  