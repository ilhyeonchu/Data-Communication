#!/usr/bin/env python3
import argparse
import os
import socket
import sys
import time
import glob

def parse_arguments():
    parser = argparse.ArgumentParser(description='UDP 파일 전송 서버')
    parser.add_argument('--address', type=str, default='0.0.0.0',
                        help='서버 바인딩 주소 (기본값: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=2222,
                        help='서버 포트 (기본값: 2222)')
    parser.add_argument('--mtu', type=int, default=1400,
                        help='최대 전송 단위 (기본값: 1400 바이트)')
    parser.add_argument('--files', type=str, default='./files',
                        help='전송 가능한 파일이 위치한 디렉토리 (기본값: ./files)')
    parser.add_argument('--debug', action='store_true',
                        help='디버그 메시지 출력')

    return parser.parse_args()

def scan_files(directory, debug=False):

    file_info = {}

    if not os.path.isdir(directory):
        if debug:
            print(f"경고: {directory} 디렉토리가 존재하지 않습니다.")
        return file_info

    for root, _, files in os.walk(directory):
        for file in files:
            full_path = os.path.join(root, file)
            rel_path = os.path.relpath(full_path, start=directory)
            file_size = os.path.getsize(full_path)
            file_info[rel_path] = {
                'path': full_path,
                'size': file_size
            }

            if debug:
                print(f"발견된 파일: {rel_path}, 크기: {file_size} 바이트")

    return file_info

def main():
    FLAGS = parse_arguments()

    # 파일 정보 스캔
    file_info = scan_files(FLAGS.files, FLAGS.debug)

    if FLAGS.debug:
        print(f"서버가 {FLAGS.address}:{FLAGS.port}에서 실행 중입니다.")
        print(f"전송 가능한 파일 수: {len(file_info)}")

    # UDP 소켓 생성
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((FLAGS.address, FLAGS.port))

    try:
        while True:
            # 클라이언트 요청 대기
            data, client = sock.recvfrom(FLAGS.mtu)
            request = data.decode('utf-8')

            if FLAGS.debug:
                print(f"클라이언트 {client}로부터 요청 받음: {request}")

            parts = request.split(' ')
            if len(parts) < 2:
                continue

            command = parts[0]
            filename = parts[1]

            # 실제 파일 경로 확인 (기본 파일 경로 + 요청 파일명)
            filepath = os.path.join(FLAGS.files, filename)

            # INFO 명령 처리
            if command == 'INFO':
                # 파일 존재 확인
                if not os.path.exists(filepath):
                    if FLAGS.debug:
                        print(f"파일 없음: {filepath}")
                    response = "404 Not Found"
                    sock.sendto(response.encode('utf-8'), client)
                    continue

                # 파일 크기 전송
                size = os.path.getsize(filepath)
                response = str(size)
                sock.sendto(response.encode('utf-8'), client)
                if FLAGS.debug:
                    print(f"파일 정보 전송: {filename}, 크기: {size} 바이트")

            # DOWNLOAD 명령 처리
            elif command == 'DOWNLOAD':
                # 파일 존재 확인
                if not os.path.exists(filepath):
                    if FLAGS.debug:
                        print(f"파일 없음: {filepath}")
                    continue

                # 파일 전송
                size = os.path.getsize(filepath)
                sent = 0

                with open(filepath, 'rb') as f:
                    while sent < size:
                        # MTU 크기만큼 파일 읽기
                        chunk = f.read(FLAGS.mtu)
                        if not chunk:
                            break

                        try:
                            # 청크 전송
                            sock.sendto(chunk, client)
                            sent += len(chunk)

                            if FLAGS.debug and sent % (FLAGS.mtu * 10) == 0:
                                print(f"전송 진행: {sent}/{size} 바이트 ({sent/size*100:.1f}%)")

                            # 네트워크 과부하 방지를 위한 짧은 대기
                            time.sleep(0.001)

                        except Exception as e:
                            if FLAGS.debug:
                                print(f"전송 오류: {e}")
                            break

                if FLAGS.debug:
                    print(f"파일 전송 완료: {filename}, {sent}/{size} 바이트")

    except KeyboardInterrupt:
        print("\n서버를 종료합니다.")
    finally:
        sock.close()

if __name__ == "__main__":
    main()