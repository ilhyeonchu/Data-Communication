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
    return morse

# 모스를 오디오로
def morse2audio(morse):
    audio = []
    
    with open(morse, 'r') as file:
        morse_data = file.read().strip()
    
    for m in morse_data:
        if m == '.':
            for i in range(int(t*fs*1)):
                audio.append(int(INTMAX*math.sin(2*math.pi*f*(i/fs))))
        elif m == '-':
            for i in range(int(t*fs*3)):
                audio.append(int(INTMAX*math.sin(2*math.pi*f*(i/fs))))
        elif m == ' ':
            for i in range(int(t*fs*))
        for i in range(int(t*fs*1)):
            audio.append(int(0))
    return audio

#오디오를 WAV 파일로 저장
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

#텍스트 입력 모스 반환
morse_result = text2morse('CNU CSE 201802168 ILHYEONCHU')

#위에서 받은 모스를 텍스트로 저장
with open('hw03_01.txt', 'w') as f:
    f.write(morse_result)
morsetxt = 'hw03_01.txt'
audio_01 = morse2audio(morsetxt)
wav_01 = '201802168_ilhyeonchu.wav'
audio2file(audio_01, wav_01)