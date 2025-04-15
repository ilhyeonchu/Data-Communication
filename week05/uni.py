import math
import statistics
import struct
import time
import wave
import pyaudio
from uni_send import send
from uni_receive import receive

INTMAX = 2**(32-1)-1

def send_data():
    send()

def receive_data():
    receive()

def main():
    while True:
        print('Unicode over Sound with Noise')
        print('2025 Spring Data Communication at CNU')
        print('[1] Send Unicode code over sound (play)')
        print('[2] Receive Unicode code over sound (record)')
        print('[q] Exit')
        select = input('Select menu: ').strip().upper()
        if select == '1':
            send_data()
        elif select == '2':
            receive_data()
        elif select == 'Q':
            print('Terminating...')
            break


if __name__ == '__main__':
    main()
