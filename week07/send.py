import reedsolo
import random
import pyaudio
import struct
import math
import wave
from week06 import frerule


RSC_LEN = 12
DATA_LEN = 12
SHORTMAX = 2**(16-1) - 1
UNIT = 0.1
SAMPLERATE = 48000

def send():
    text = input('Input your string: ')
    original_byte = text.encode('utf-8')
    original_hex = original_byte.hex().upper()
    rsc = reedsolo.RSCodec(RSC_LEN)
    encoded_bytes = bytearray()
    for k in range(0, len(original_byte), DATA_LEN):
        chunk = original_byte[k:k + DATA_LEN]
        encoded_bytes += rsc.encode(chunk)
    encoded_hex = encoded_bytes.hex().upper()
    print(f"원본 인코딩 데이터 (헥스): {original_hex}")
    print(f"원본 RS 인코딩 데이터 (헥스): {encoded_hex}")

    error_count = random.randint(0, 4)
    print(f'주입할 오류 개수: {error_count}')

    encoded_bytes_with_errors = bytearray(encoded_bytes)
    indices = random.sample(range(len(encoded_bytes_with_errors)), error_count)
    for idx in indices:
        rsc_original_byte = encoded_bytes_with_errors[idx]
        new_byte = random.randint(0, 255)
        while new_byte == rsc_original_byte:
            new_byte = random.randint(0, 255)
        encoded_bytes_with_errors[idx] = new_byte


    error_hex = encoded_bytes_with_errors.hex().upper()
    print(f"오류가 주입된 RS 데이터 (헥스): {error_hex}")

    original_audio = []
    error_audio = []

    for i in range(int(UNIT*SAMPLERATE*2)):
        original_audio.append(SHORTMAX*math.sin(2*math.pi*frerule.frequency_rules['START']*i/SAMPLERATE))
        error_audio.append(SHORTMAX*math.sin(2*math.pi*frerule.frequency_rules['START']*i/SAMPLERATE))

    for k in range(0, len(original_byte), DATA_LEN):
        data = original_byte[k:k+DATA_LEN]
        encoded_data = rsc.encode(data).hex().upper()
        for s in encoded_data:
            for i in range(int(UNIT*SAMPLERATE*1)):
                original_audio.append(SHORTMAX*math.sin(2*math.pi*frerule.frequency_rules[s]*i/SAMPLERATE))

    block_length = DATA_LEN + RSC_LEN
    num_chunks = (len(original_byte) + DATA_LEN - 1) // DATA_LEN
    for chunk_idx in range(num_chunks):
        start_idx = chunk_idx * block_length
        block = encoded_bytes_with_errors[start_idx:start_idx + block_length]
        encoded_block_hex = block.hex().upper()
        for s in encoded_block_hex:
            for i in range(int(UNIT * SAMPLERATE * 1)):
                error_audio.append(SHORTMAX * math.sin(2 * math.pi * frerule.frequency_rules[s] * i / SAMPLERATE))

    for i in range(int(UNIT*SAMPLERATE*2)):
        original_audio.append(SHORTMAX*math.sin(2*math.pi*frerule.frequency_rules['END']*i/SAMPLERATE))
        error_audio.append(SHORTMAX*math.sin(2*math.pi*frerule.frequency_rules['END']*i/SAMPLERATE))


    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=48000, output=True)
    with wave.open('original.wav', 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLERATE)
        for a in original_audio:
            w.writeframes(struct.pack('<h', int(a)))
            stream.write(struct.pack('<h', int(a)))

    p2 = pyaudio.PyAudio()
    stream2 = p2.open(format=pyaudio.paInt16, channels=1, rate=48000, output=True)
    with wave.open('error.wav', 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SAMPLERATE)
        for a in error_audio:
            w.writeframes(struct.pack('<h', int(a)))
            stream2.write(struct.pack('<h', int(a)))

    stream.close()
    stream2.close()
    p.terminate()
    p2.terminate()


    try:
        wf = wave.open('error.wav')
        frames = wf.getnframes()
        data = wf.readframes(frames)
        wf.close()
        samples = list(struct.iter_unpack('<h', data))
        samples = [s[0] for s in samples]

        message_samples = samples[int(UNIT*SAMPLERATE*2):-int(UNIT*SAMPLERATE*2)]
        blocks = [message_samples[i:i+int(UNIT*SAMPLERATE*1)] for i in range(0, len(message_samples), int(UNIT*SAMPLERATE*1))
                  if len(message_samples[i:i+int(UNIT*SAMPLERATE*1)]) == int(UNIT*SAMPLERATE*1)]

        receive_hex = ""
        tolerance = 20  # 주파수 매칭 허용 오차

        for block in blocks:
            crossings = 0
            for i in range(1, len(block)):
                if block[i - 1] < 0 and block[i] >= 0:
                    crossings += 1
            estimated_freq = crossings / UNIT
            matched = None
            for char, freq in frerule.frequency_rules.items():
                if abs(estimated_freq - freq) < tolerance:
                    matched = char
                    break
            if matched is None:
                matched = '?'  # 매칭 실패 시
            receive_hex += matched
        print(f"수신한 RS 데이터 (헥스): {receive_hex}")
        receive_bytes = bytes.fromhex(receive_hex)
        decoded_bytes = bytearray()
        block_length = DATA_LEN + RSC_LEN
        for i in range(0, len(receive_bytes), block_length):
            block = receive_bytes[i:i + block_length]
            try:
                decoded_block = rsc.decode(block)[0]
                decoded_bytes += decoded_block
            except reedsolo.ReedSolomonError as e:
                print(f"\n블록 {i // block_length} 디코딩 실패: {e}")
                decoded_bytes += b'?' * DATA_LEN  # 실패한 블록을 ?로 채움
        recover_text = decoded_bytes.decode('utf-8')

        error_num = sum(1 for rb, db in zip(receive_bytes, decoded_bytes) if rb != db)
        print("\nRS 디코딩 성공!")
        print(f'오류 개수: {error_num}')
        print("복원된 메시지:")
        print(recover_text)
    except reedsolo.ReedSolomonError as e:
        print("\nRS 디코딩 실패!")
        print(e)
    except UnicodeDecodeError as e:
        print("\nRS 디코딩은 되었으나, UTF-8 디코딩에 실패했습니다.")
        print(e)


if __name__ == '__main__':
    send()