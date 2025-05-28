#!/usr/bin/env python3
import socket
import sys
import os

# SERVER_ADDR = ('34.171.223.63', 3034)
SERVER_ADDR = ('100.87.116.106', 2222)
BUF_SIZE     = 4096
TIMEOUT_SEC  = 3.0
DEBUG        = True  # 디버그 모드 변수 추가

def request_info(sock, filename):
    msg = f'INFO {filename}'.encode('utf-8')
    if DEBUG:
        print(f">> 요청 전송: INFO {filename}")
    sock.sendto(msg, SERVER_ADDR)
    try:
        data, _ = sock.recvfrom(BUF_SIZE)
        text = data.decode('utf-8', errors='ignore')
        if text.startswith('404'):
            print(">> 서버에 해당 파일이 없습니다.")
            return None
        print(f">> 데이터: {repr(text)}")
        return int(text)
    except socket.timeout:
        print(">> INFO 응답 타임아웃")
        return None

def request_download(sock, filename, filesize, out_path):
    # 디렉토리인지 확인하고, 디렉토리라면 파일명을 추가
    if os.path.isdir(out_path):
        out_path = os.path.join(out_path, os.path.basename(filename))
        if DEBUG:
            print(f">> 저장 경로가 디렉토리입니다. 파일 경로로 수정: {out_path}")

    # 디렉토리 존재 여부 확인
    out_dir = os.path.dirname(out_path)
    if out_dir and not os.path.exists(out_dir):
        if DEBUG:
            print(f">> 디렉토리 생성: {out_dir}")
        os.makedirs(out_dir, exist_ok=True)

    sock.sendto(f'DOWNLOAD {filename}'.encode('utf-8'), SERVER_ADDR)
    received = 0
    with open(out_path, 'wb') as f:
        while received < filesize:
            try:
                chunk, _ = sock.recvfrom(BUF_SIZE)
            except socket.timeout:
                print(">> 다운로드 중 타임아웃")
                break
            if not chunk:
                break
            f.write(chunk)
            received += len(chunk)
            print(f'\r다운받은 {received}/{filesize} 바이트', end='')
    print('\n>> 다운로드 완료')

def main():
    if len(sys.argv) != 3:
        print(f'Usage: {sys.argv[0]} <파일명> <저장할_경로>')
        sys.exit(1)

    filename = sys.argv[1]
    out_path = sys.argv[2]
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT_SEC)
    try:
        print("1) 파일 정보 요청 중...")
        size = request_info(sock, filename)
        if size is None:
            return

        print(f">> 파일 크기: {size} 바이트")
        print("2) 파일 다운로드 요청 중...")
        request_download(sock, filename, size, out_path)

    finally:
        sock.close()

if __name__ == '__main__':
    main()#!/usr/bin/env python3
import socket
import sys
import os

# SERVER_ADDR = ('34.171.223.63', 3034)
SERVER_ADDR = ('100.87.116.106', 2222)
BUF_SIZE     = 4096
TIMEOUT_SEC  = 3.0

def request_info(sock, filename):
    msg = f'INFO {filename}'.encode('utf-8')
    sock.sendto(msg, SERVER_ADDR)
    try:
        data, _ = sock.recvfrom(BUF_SIZE)
        text = data.decode('utf-8', errors='ignore')
        if text.startswith('404'):
            print(">> 서버에 해당 파일이 없습니다.")
            return None
        print(f">> 데이터: {repr(text)}")
        return int(text)
    except socket.timeout:
        print(">> INFO 응답 타임아웃")
        return None

def request_download(sock, filename, filesize, out_path):
    sock.sendto(f'DOWNLOAD {filename}'.encode('utf-8'), SERVER_ADDR)
    received = 0
    with open(out_path, 'wb') as f:
        while received < filesize:
            try:
                chunk, _ = sock.recvfrom(BUF_SIZE)
            except socket.timeout:
                print(">> 다운로드 중 타임아웃")
                break
            if not chunk:
                break
            f.write(chunk)
            received += len(chunk)
            print(f'\r다운받은 {received}/{filesize} 바이트', end='')
    print('\n>> 다운로드 완료')

def main():
    if len(sys.argv) != 3:
        print(f'Usage: {sys.argv[0]} <파일명> <저장할_경로>')
        sys.exit(1)

    filename = sys.argv[1]
    out_path = sys.argv[2]
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT_SEC)
    try:
        print("1) 파일 정보 요청 중...")
        size = request_info(sock, filename)
        if size is None:
            return

        print(f">> 파일 크기: {size} 바이트")
        print("2) 파일 다운로드 요청 중...")
        request_download(sock, filename, size, out_path)

    finally:
        sock.close()

if __name__ == '__main__':
    main()
