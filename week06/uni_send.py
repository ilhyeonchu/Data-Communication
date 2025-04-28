from frerule import rules, sample_rate, unit

import math
import struct
import wave

import pyaudio

def audio2file(audio, filename):
        with wave.open(filename, 'wb') as w:
            w.setnchannels(1)
            w.setsampwidth(4)
            w.setframerate(sample_rate)
            for a in audio:
                w.writeframes(struct.pack('<l', a))
                                                                
        print("saved to", filename)

def send():
    INTMAX = 2**(32-1)-1
    channels = 1
    unit = 0.1
    sample_rate = 48000

    print('Type some text')
    text = input('User input: ')
    string_hex = text.encode('utf-8').hex().upper()

    audio = []
    for i in range(int(unit*sample_rate*2)):
        audio.append(int(INTMAX*math.sin(2*math.pi*rules['START']*i/sample_rate)))
    for s in string_hex:
        for i in range(int(unit*sample_rate*1)):
            audio.append(int(INTMAX*math.sin(2*math.pi*rules[s]*i/sample_rate)))
    for i in range(int(unit*sample_rate*2)):
        audio.append(int(INTMAX*math.sin(2*math.pi*rules['END']*i/sample_rate)))

    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt32,
                    channels=channels,
                    rate=sample_rate,
                    output=True)

    chunk_size = 1024
    for i in range(0, len(audio), chunk_size):
        chunk = audio[i:i+chunk_size]
        stream.write(struct.pack('<' + ('l'*len(chunk)), *chunk))
    
    audio2file(audio, 'send.wav')
