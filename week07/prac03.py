from RSC import RSC_LEN
from week06 import frerule
import reedsolo
import math
import pyaudio
import struct

DATA_LEN = 12

SHORTMAX = 2**(16-1) - 1
UNIT = 0.1
SAMPLERATE = 48000

text = '🧡💛💚💙💜'
byte_hex = text.encode('utf-8')
string_hex = byte_hex.hex().upper()

audio = []
for i in range(int(UNIT*SAMPLERATE*2)):
    audio.append(SHORTMAX*math.sin(2*math.pi*frerule.frequency_rules['START']*i/SAMPLERATE))

client_rsc = reedsolo.RSCodec(RSC_LEN)
for k in range(0, len(byte_hex), DATA_LEN):
    data = byte_hex[k:k+DATA_LEN]
    encoded_data = client_rsc.encode(data).hex().upper()
    print(f'encoded_data: {encoded_data}')
    for s in encoded_data:
        for i in range(int(UNIT*SAMPLERATE*1)):
            audio.append(SHORTMAX*math.sin(2*math.pi*frerule.frequency_rules[s]*i/SAMPLERATE))

for i in range(int(UNIT*SAMPLERATE*2)):
    audio.append(SHORTMAX*math.sin(2*math.pi*frerule.frequency_rules['END']*i/SAMPLERATE))

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=SAMPLERATE, output=True)

for i in range(0, len(audio), 1024):
    chunk = [int(x) for x in audio[i:i+1024]]
    stream.write(struct.pack('<' + ('l'*len(chunk)), *chunk))