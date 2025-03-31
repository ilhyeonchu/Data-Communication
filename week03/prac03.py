import sys
import math
import wave
import struct
import statistics
INTMAX = 2**(32-1)-1

def morse2audio(morse):
    t = 0.5
    fs = 48000
    f = 261.626
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
        for i in range(int(t*fs*1)):
            audio.append(int(0))
    return audio

def audio2file(audio, filename):
    with wave.open(filename, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(4)
        w.setframerate(48000)
        for a in audio:
            w.writeframes(struct.pack('<l', a))
            

morse_txt = 'morse_output.txt'
morse_audio = 'morse_audio.wav'
audio2file(morse2audio(morse_txt), morse_audio)
