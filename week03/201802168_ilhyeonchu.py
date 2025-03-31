import sys
import math
import wave
import struct
import statistics

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
t = 0.1
fs = 48000
f = 523.251 #C5

# wav파일을 모스로
def file2morse(filename):
    with wave.open(filename, 'rb') as w:
        audio = []
        framerate = w.getframerate()
        frames = w. getnframes()
        for i in range(frames):
            frame = w.readframes(1)
            audio.append(struct.unpack('<i', frame)[0])
        morse = ''
        unit = int(t * fs)
        for i in range(1, math.ceil(len(audio)/unit)+1):
            stdev = statistics.stdev(audio[(i-1)*unit:i*unit])
            if stdev > 10000:
                morse = morse + '.'
            else:
                morse = morse + ' '
        morse = morse.replace('...', '-')
        morse = morse.replace('       ', ' / ') # 단어 바뀜
        morse = morse.replace('   ', ' + ')     # 문자 바뀜
    return morse

# 모스를 오디오로
def morse2audio(morse):
    audio = []
    blank = 0
    # with open(morse, 'r') as file:
    #     morse_data = file.read().strip()
    for m in morse:
        if m == '.':
            blank = 0
            for i in range(int(t*fs*1)):
                audio.append(int(INTMAX*math.sin(2*math.pi*f*(i/fs))))
        elif m == '-':
            blank = 0
            for i in range(int(t*fs*3)):
                audio.append(int(INTMAX*math.sin(2*math.pi*f*(i/fs))))
        elif m == ' ':      # 공백의 경우 처리
            blank +=1       # 하나의 char의 경우는 공백이 1개 단어의 경우는 공백이 2개
            if blank >= 2:  # 공백이 2개이므로 단어 바뀜
                for i in range(int(t*fs*3)):    # 3유닛의 공백 추가 이유는 보고서에 따로 작성
                    audio.append(int(0))
            else:           # 공백이 1개이므로 문자 바뀜
                for i in range(int(t*fs*2)):    # 2유닛의 공백 추가 이유는 보고서에 따로 작성
                    audio.append(int(0))
        for i in range(int(t*fs*1)):
            audio.append(int(0))
    return audio

# 오디오를 WAV 파일로 저장
def audio2file(audio, filename):
    with wave.open(filename, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(4)
        w.setframerate(48000)
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
    morse_to_text = {v: k for k, v in english.items()}
    morse_to_text.update({v: k for k, v in number.items()})

    print(morse)
    for code in morse.split(' '):   # 모스코드 단어 단위로 나누기
        if code == '+':     # 문자 바뀜 word에 모여있는 모스 코드들을 문자로 변환 후 text에 추가
            if word in morse_to_text:
                text += morse_to_text[word]
            word = ''
        elif code == '/':   # 단어 바뀜 word에 모여있는 모스 코드들을 문자로 변환 후 text에 추가
            if word in morse_to_text:
                text += morse_to_text[word]
            text += ' '
            word = ''
        else :              # 모스 코드를 word에 추가시켜 나중에 문자단위로 변환
            word += code
    print (text)
    return text

# 텍스트 입력 모스 반환
morse_result = text2morse('CNU CSE 201802168 ILHYEONCHU')
morse_01_text = 'hw03_01.txt'

# 위에서 받은 모스를 텍스트로 저장
with open(morse_01_text, 'w') as file:
    file.write(morse_result)

# 모스 파일을 읽어와 오디오로 변환 준비 원래는 위의 함수에 있었음
with open(morse_01_text, 'r') as file:
    morse_data = file.read().strip()

# 모스 파일을 오디오로 변환 후 저장
audio_01 = morse2audio(morse_data)
wav_01 = '201802168_ilhyeonchu.wav'
audio2file(audio_01, wav_01)

# hw2 파일을 모스 코드로 변환 후 저장
hw03_02 = 'output_201802168_추일현.wav'
morse_02 = file2morse(hw03_02)
morse_02_text = 'hw03_02.txt'
with open(morse_02_text, 'w') as file:
    file.write(morse_02)

# morse_02를 텍스트로 변환 후 저장
hw03_02_result = morse2text(morse_02)
hw03_02_text = 'hw03_02_text.txt'
with open(hw03_02_text, 'w') as file:
    file.write(hw03_02_result)