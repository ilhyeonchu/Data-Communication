import socket
import os

import argparse

parser = argparse.ArgumentParser(description='UDP File Transfer Client (DCFT1)')
parser.add_argument('--address', default='100.87.116.106', help='Server IP address')
parser.add_argument('--port', type=int, default=2222, help='Server UDP port')
parser.add_argument('--chunk_maxsize', type=int, default=1500, help='Maximum UDP payload size (MTU)')
FLAGS = parser.parse_args()

def main():
    while True:
        try:
            filename = input('Filename: ').strip()
            request = f'INFO {filename}'
            sock.sendto(request.encode('utf-8'), (FLAGS.address, FLAGS.port))
            response, server = sock.recvfrom(FLAGS.chunk_maxsize)
            response = response.decode('utf-8')
            if response == '404 Not Found':
                print(response)
                continue
            size = int(response)
            request = f'DOWNLOAD {filename}'
            sock.sendto(request.encode('utf-8'), (FLAGS.address, FLAGS.port))
            print(f'Request {filename} to ({FLAGS.address}, {FLAGS.port})')
            remain = size
            with open(filename, 'wb') as f:
                while remain > 0:
                    try:
                        chunk, _ = sock.recvfrom(FLAGS.chunk_maxsize)
                    except socket.timeout:
                        # 재시도 – 일정 시간 동안 데이터가 없으면 다시 recv 시도
                        print('Timeout while receiving, retrying...')
                        continue
                    # 남은 바이트보다 크게 받은 경우 잘라서 기록
                    if len(chunk) > remain:
                        chunk = chunk[:remain]
                    f.write(chunk)
                    remain -= len(chunk)
            print(f'File download success')
        except KeyboardInterrupt:
            print(f'Shutting down... {sock}')
            break

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3.0)  # 3초 타임아웃 설정
    try:
        main()
    finally:
        sock.close()