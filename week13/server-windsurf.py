import socket
import struct
import argparse
import os
import time

FLAGS = None
DEBUG = False
MAX_SEQ = 2  # 0과 1만 사용

def get_file_info(root_dir):
    """디렉토리 내 파일 정보를 수집하는 함수"""
    files = {}
    try:
        for entry in os.scandir(root_dir):
            if entry.is_file() and not entry.name.startswith('.'):
                size = os.path.getsize(entry.path)
                files[entry.name] = {
                    'path': entry.path,
                    'size': size
                }
                if DEBUG:
                    print(f"Found file: {entry.name}, Size: {size} bytes")
    except FileNotFoundError:
        if DEBUG:
            print(f"Directory not found: {root_dir}")
    return files

def main():
    # 명령줄 인자 파싱
    parser = argparse.ArgumentParser(description='Stop and Wait ARQ Server')
    parser.add_argument('--debug', action='store_true', help='디버그 메시지 출력')
    parser.add_argument('--address', type=str, default='0.0.0.0', help='서버 주소')
    parser.add_argument('--port', type=int, default=3034, help='서버 포트')
    parser.add_argument('--dir', type=str, default='./files', help='파일 디렉토리')
    parser.add_argument('--mtu', type=int, default=1400, help='최대 전송 단위')
    parser.add_argument('--timeout', type=float, default=3.0, help='타임아웃(초)')
    
    global FLAGS, DEBUG
    FLAGS = parser.parse_args()
    DEBUG = FLAGS.debug

    # 파일 정보 수집
    files = get_file_info(FLAGS.dir)
    if not files:
        print(f"[!] {FLAGS.dir} 디렉토리에 파일이 없습니다.")
        return

    # 소켓 생성 및 바인딩
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((FLAGS.address, FLAGS.port))
    sock.settimeout(FLAGS.timeout)
    
    print(f"[*] 서버 시작: {FLAGS.address}:{FLAGS.port}")
    print(f"[*] 파일 디렉토리: {os.path.abspath(FLAGS.dir)}")
    print(f"[*] MTU: {FLAGS.mtu} 바이트")
    print(f"[*] 타임아웃: {FLAGS.timeout}초")

    seq_expected = 0  # 다음에 받을 예상 시퀀스 번호

    try:
        while True:
            try:
                # 클라이언트 요청 수신
                data, client = sock.recvfrom(FLAGS.mtu)
                
                if DEBUG:
                    print(f"\n[DEBUG] 수신: {data[:100]}... from {client}")

                # 요청 파싱
                try:
                    command = data.decode('utf-8').strip().split(' ', 1)
                    if len(command) < 2:
                        if DEBUG:
                            print(f"[DEBUG] 잘못된 요청 형식: {command}")
                        continue
                except UnicodeDecodeError:
                    if DEBUG:
                        print("[DEBUG] 요청 디코딩 오류")
                    continue

                cmd, filename = command[0].upper(), command[1]
                
                if DEBUG:
                    print(f"[DEBUG] 명령: {cmd}, 파일: {filename}")

                # INFO 명령 처리
                if cmd == 'INFO':
                    if filename in files:
                        file_size = files[filename]['size']
                        response = str(file_size).encode('utf-8')
                        if DEBUG:
                            print(f"[DEBUG] 파일 정보 전송: {filename}, 크기: {file_size} 바이트")
                    else:
                        response = '404 Not Found'.encode('utf-8')
                        if DEBUG:
                            print(f"[DEBUG] 파일을 찾을 수 없음: {filename}")
                    
                    # 응답 전송
                    sock.sendto(response, client)

                # DOWNLOAD 명령 처리
                elif cmd == 'DOWNLOAD':
                    if filename not in files:
                        if DEBUG:
                            print(f"[DEBUG] 파일을 찾을 수 없음: {filename}")
                        sock.sendto(b'404 Not Found', client)
                        continue

                    filepath = files[filename]['path']
                    filesize = files[filename]['size']
                    
                    if DEBUG:
                        print(f"[DEBUG] 파일 전송 시작: {filename} ({filesize} 바이트)")

                    # 파일 전송
                    with open(filepath, 'rb') as f:
                        seq_num = 0  # 시퀀스 번호 초기화
                        while True:
                            # 파일에서 데이터 읽기
                            chunk = f.read(FLAGS.mtu - 4)  # 4바이트(시퀀스 2바이트 + 체크섬 2바이트) 제외
                            if not chunk:
                                break  # 전송 완료

                            # 패킷 생성 (시퀀스 번호 + 데이터)
                            packet = struct.pack('>H', seq_num) + chunk
                            
                            # 체크섬 계산 (간단한 XOR 체크섬)
                            checksum = 0
                            for b in packet:
                                checksum ^= b
                            packet += struct.pack('>H', checksum)
                            
                            # 패킷 전송
                            while True:  # ACK를 받을 때까지 재전송
                                try:
                                    sock.sendto(packet, client)
                                    if DEBUG:
                                        print(f"[DEBUG] 전송: 시퀀스={seq_num}, 크기={len(packet)}바이트")
                                    
                                    # ACK 대기
                                    sock.settimeout(FLAGS.timeout)
                                    ack_data, _ = sock.recvfrom(FLAGS.mtu)
                                    
                                    # ACK 확인
                                    if len(ack_data) >= 2:  # 최소 2바이트(시퀀스) 필요
                                        ack_seq = struct.unpack('>H', ack_data[:2])[0]
                                        if ack_seq == seq_num:
                                            if DEBUG:
                                                print(f"[DEBUG] ACK 수신: {ack_seq}")
                                            seq_num = (seq_num + 1) % MAX_SEQ  # 시퀀스 번호 업데이트
                                            break  # 다음 패킷으로
                                        else:
                                            if DEBUG:
                                                print(f"[DEBUG] 잘못된 ACK: 기대={seq_num}, 수신={ack_seq}")
                                    else:
                                        if DEBUG:
                                            print("[DEBUG] 잘못된 ACK 패킷")
                                
                                except socket.timeout:
                                    if DEBUG:
                                        print(f"[DEBUG] 타임아웃, 재전송: 시퀀스={seq_num}")
                                    continue  # 재전송
                    
                    if DEBUG:
                        print(f"[DEBUG] 파일 전송 완료: {filename}")

            except socket.timeout:
                if DEBUG:
                    print("[DEBUG] 클라이언트 요청 대기 중...")
                continue
            except Exception as e:
                if DEBUG:
                    print(f"[ERROR] 오류 발생: {e}")
                continue

    except KeyboardInterrupt:
        print("\n[!] 서버를 종료합니다.")
    finally:
        sock.close()

if __name__ == '__main__':
    main()