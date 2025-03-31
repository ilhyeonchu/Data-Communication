import sys
import math
import wave
import struct
import statistics
INTMAX = 2**(32-1)-1


def file2morse(filename):
    with wave.open(filename, 'rb') as w:
        audio = []
        framerate = w.getframerate()
        frames = w. getnframes()
        for i in range(frames):
            frame = w.readframes(1)
            audio.append(struct.unpack('<i', frame)[0])
        morse = ''
        unit = int(0.5 * 48000)
        for i in range(1, math.ceil(len(audio)/unit)+1):
            stdev = statistics.stdev(audio[(i-1)*unit:i*unit])
            if stdev > 10000:
                morse = morse + '.'
            else:
                morse = morse + ' '
        morse = morse.replace('...', '-')
    return morse

filename = 'morse_audio.wav'
morse_result = file2morse(filename)

output_filename = 'result_prac04.txt'

with open(output_filename, 'w') as f:
    f.write(morse_result)

print(morse_result)