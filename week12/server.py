#!/usr/bin/env python3
import argparse
import os
import socket
import sys
import time

def parse_arguments():
    parser = argparse.ArgumentParser(description='UDP 파일 전송 서버')
    parser.add_argument('--address', type=str, default='0.0.0.0',
                        help='서버 바인딩 주소 (기본값: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=2222,
                        help='서버 포트 (기본값: 2222)')
    parser.add_argument('--mtu', type=int, default=1400,
                        help='최대 전송 단위 (기본값: 1400 바이트)')
    parser.add_argument('--debug', action='store_true',
                        help='디버그 메시지 출력')

    return parser.parse_args()

def main():
    FLAGS = parse_arguments()
    if FLAGS.debug:
        print(f"서버가 {FLAGS.address}:{FLAGS.port}에서 실행 중입니다.")

    # UDP 소켓 생성
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((FLAGS.address, FLAGS.port))

    try:
        while True:
            # 클라이언트 요청 대기
            data, client = sock.recvfrom(FLAGS.mtu)
            if FLAGS.debug:
                print(f"클라이언트 {client}로부터 요청 받음: {data}")

            # 요청 파싱
            request = data.decode('utf-8')
            parts = request.split(' ')
            command = parts[0]

            if len(parts) < 2:
                continue

            filename = parts[1]

            # INFO 명령 처리
            if command == 'INFO':
                if not os.path.exists(filename):
                    response = "404 Not Found"
                    sock.sendto(response.encode('utf-8'), client)
                    continue

                size = os.path.getsize(filename)
                response = str(size)
                sock.sendto(response.encode('utf-8'), client)

            # DOWNLOAD 명령 처리
            elif command == 'DOWNLOAD':
                if not os.path.exists(filename):
                    continue

                size = os.path.getsize(filename)
                sent = 0

                with open(filename, 'rb') as f:
                    while sent < size:
                        chunk = f.read(FLAGS.mtu)
                        if not chunk:
                            break

                        try:
                            sock.sendto(chunk, client)
                            sent += len(chunk)
                            if FLAGS.debug:
                                print(f"전송됨: {sent}/{size} 바이트")
                            time.sleep(0.001)  # 네트워크 부하 방지
                        except:
                            break

    except KeyboardInterrupt:
        print("\n서버 종료 중...")
    finally:
        sock.close()

if __name__ == "__main__":
    main()