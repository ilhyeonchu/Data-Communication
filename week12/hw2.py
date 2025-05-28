#!/usr/bin/env python3
import argparse
import os
import socket
import sys
import time
import random
import importlib.util

class CorruptedUDPServer:
    def __init__(self, address='0.0.0.0', port=2222, mtu=1400, files_dir='./files', debug=False):
        self.address = address
        self.port = port
        self.mtu = mtu
        self.files_dir = files_dir
        self.debug = debug
        self.corruption_rate = 0.1  # 기본 10% 손상률
        
    def calculate_corruption_rate(self, file_size):
        """파일 크기에 따라 손상 확률 조절"""
        if file_size < 100 * 1024:  # 100KB 미만
            return 0.05  # 5%
        elif file_size < 1024 * 1024:  # 1MB 미만
            return 0.1   # 10%
        else:  # 1MB 이상
            return 0.15  # 15%
    
    def corrupt_data(self, data, corruption_rate):
        """데이터에 의도적 손상 발생"""
        if random.random() < corruption_rate:
            # 랜덤한 위치의 바이트를 변경
            data_list = list(data)
            if data_list:
                corrupt_index = random.randint(0, len(data_list) - 1)
                original_byte = data_list[corrupt_index]
                # 원본과 다른 값으로 변경
                new_byte = (original_byte + random.randint(1, 255)) % 256
                data_list[corrupt_index] = new_byte
                if self.debug:
                    print(f"[CORRUPTION] Packet corrupted at byte {corrupt_index}: {original_byte} -> {new_byte}")
                return bytes(data_list), True
        return data, False
    
    def scan_files(self):
        """파일 스캔 (기존 server.py 로직)"""
        file_info = {}
        
        if not os.path.isdir(self.files_dir):
            if self.debug:
                print(f"경고: {self.files_dir} 디렉토리가 존재하지 않습니다.")
            return file_info

        for root, _, files in os.walk(self.files_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, start=self.files_dir)
                file_size = os.path.getsize(full_path)
                file_info[rel_path] = {
                    'path': full_path,
                    'size': file_size
                }

                if self.debug:
                    print(f"발견된 파일: {rel_path}, 크기: {file_size} 바이트")

        return file_info
    
    def start_server(self):
        """손상 시뮬레이션이 포함된 UDP 서버 시작"""
        file_info = self.scan_files()
        
        if self.debug:
            print(f"[CORRUPTION SERVER] 서버가 {self.address}:{self.port}에서 실행 중입니다.")
            print(f"전송 가능한 파일 수: {len(file_info)}")
            print("=" * 60)

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.address, self.port))

        try:
            while True:
                # 클라이언트 요청 대기
                data, client = sock.recvfrom(self.mtu)
                request = data.decode('utf-8')

                if self.debug:
                    print(f"클라이언트 {client}로부터 요청 받음: {request}")

                parts = request.split(' ')
                if len(parts) < 2:
                    continue

                command = parts[0]
                filename = parts[1]
                filepath = os.path.join(self.files_dir, filename)

                # INFO 명령 처리
                if command == 'INFO':
                    if not os.path.exists(filepath):
                        if self.debug:
                            print(f"파일 없음: {filepath}")
                        response = "404 Not Found"
                        sock.sendto(response.encode('utf-8'), client)
                        continue

                    size = os.path.getsize(filepath)
                    response = str(size)
                    sock.sendto(response.encode('utf-8'), client)
                    if self.debug:
                        print(f"파일 정보 전송: {filename}, 크기: {size} 바이트")

                # DOWNLOAD 명령 처리 (손상 시뮬레이션 포함)
                elif command == 'DOWNLOAD':
                    if not os.path.exists(filepath):
                        if self.debug:
                            print(f"파일 없음: {filepath}")
                        continue

                    size = os.path.getsize(filepath)
                    corruption_rate = self.calculate_corruption_rate(size)
                    
                    print(f"\n[CORRUPTION] 파일 전송 시작: {filename}")
                    print(f"[CORRUPTION] 파일 크기: {size} 바이트")
                    print(f"[CORRUPTION] 손상률 설정: {corruption_rate*100:.1f}%")
                    
                    sent = 0
                    total_packets = 0
                    corrupted_packets = 0

                    with open(filepath, 'rb') as f:
                        while sent < size:
                            chunk = f.read(self.mtu)
                            if not chunk:
                                break

                            # 패킷 손상 시뮬레이션
                            corrupted_chunk, was_corrupted = self.corrupt_data(chunk, corruption_rate)
                            
                            if was_corrupted:
                                corrupted_packets += 1
                            
                            total_packets += 1

                            try:
                                sock.sendto(corrupted_chunk, client)
                                sent += len(chunk)  # 원본 크기로 계산

                                if self.debug and sent % (self.mtu * 10) == 0:
                                    print(f"전송 진행: {sent}/{size} 바이트 ({sent/size*100:.1f}%)")

                                time.sleep(0.001)

                            except Exception as e:
                                if self.debug:
                                    print(f"전송 오류: {e}")
                                break

                    print(f"[CORRUPTION] 전송 완료 통계:")
                    print(f"  - 총 패킷 수: {total_packets}")
                    print(f"  - 손상된 패킷 수: {corrupted_packets}")
                    print(f"  - 실제 손상률: {corrupted_packets/total_packets*100:.1f}%")
                    print("=" * 60)

        except KeyboardInterrupt:
            print("\n[CORRUPTION SERVER] 서버를 종료합니다.")
        finally:
            sock.close()


class CorruptedUDPClient:
    def __init__(self, server_addr, server_port=2222, buf_size=4096, timeout=3.0, debug=False):
        self.server_addr = (server_addr, server_port)
        self.buf_size = buf_size
        self.timeout = timeout
        self.debug = debug
    
    def request_info(self, sock, filename):
        """파일 정보 요청 (기존 client.py 로직)"""
        msg = f'INFO {filename}'.encode('utf-8')
        if self.debug:
            print(f">> 요청 전송: INFO {filename}")
        sock.sendto(msg, self.server_addr)
        try:
            data, _ = sock.recvfrom(self.buf_size)
            text = data.decode('utf-8', errors='ignore')
            if text.startswith('404'):
                print(">> 서버에 해당 파일이 없습니다.")
                return None
            if self.debug:
                print(f">> 파일 크기 응답: {text}")
            return int(text)
        except socket.timeout:
            print(">> INFO 응답 타임아웃")
            return None

    def request_download(self, sock, filename, filesize, out_path):
        """손상된 파일 다운로드"""
        # 디렉토리 처리
        if os.path.isdir(out_path):
            out_path = os.path.join(out_path, f"corrupted_{os.path.basename(filename)}")
            if self.debug:
                print(f">> 저장 경로 수정: {out_path}")

        out_dir = os.path.dirname(out_path)
        if out_dir and not os.path.exists(out_dir):
            if self.debug:
                print(f">> 디렉토리 생성: {out_dir}")
            os.makedirs(out_dir, exist_ok=True)

        print(f"\n[CLIENT] 손상된 파일 다운로드 시작: {filename}")
        sock.sendto(f'DOWNLOAD {filename}'.encode('utf-8'), self.server_addr)
        
        received = 0
        with open(out_path, 'wb') as f:
            while received < filesize:
                try:
                    chunk, _ = sock.recvfrom(self.buf_size)
                except socket.timeout:
                    print(">> 다운로드 중 타임아웃")
                    break
                if not chunk:
                    break
                f.write(chunk)
                received += len(chunk)
                print(f'\r>> 다운받은 {received}/{filesize} 바이트 ({received/filesize*100:.1f}%)', end='')
        
        print(f'\n[CLIENT] 손상된 파일 저장 완료: {out_path}')
        return out_path

    def download_file(self, filename, out_path):
        """파일 다운로드 전체 프로세스"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(self.timeout)
        
        try:
            print("1) 파일 정보 요청 중...")
            size = self.request_info(sock, filename)
            if size is None:
                return None

            print(f">> 파일 크기: {size} 바이트")
            print("2) 손상된 파일 다운로드 요청 중...")
            return self.request_download(sock, filename, size, out_path)

        finally:
            sock.close()


def main():
    parser = argparse.ArgumentParser(description='UDP 파일 전송 패킷 손상 시뮬레이션')
    parser.add_argument('mode', choices=['server', 'client'], help='서버 또는 클라이언트 모드')
    
    # 서버 관련 옵션
    parser.add_argument('--address', type=str, default='0.0.0.0',
                        help='서버 바인딩 주소 (기본값: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=2222,
                        help='서버 포트 (기본값: 2222)')
    parser.add_argument('--mtu', type=int, default=1400,
                        help='최대 전송 단위 (기본값: 1400 바이트)')
    parser.add_argument('--files', type=str, default='./files',
                        help='전송 가능한 파일이 위치한 디렉토리 (기본값: ./files)')
    
    # 클라이언트 관련 옵션
    parser.add_argument('--server', type=str, default='100.87.116.106',
                        help='서버 주소 (기본값: 100.87.116.106)')
    parser.add_argument('--filename', type=str,
                        help='다운로드할 파일명 (클라이언트 모드 필수)')
    parser.add_argument('--output', type=str, default='./downloads',
                        help='저장할 경로 (기본값: ./downloads)')
    
    # 공통 옵션
    parser.add_argument('--debug', action='store_true',
                        help='디버그 메시지 출력')

    args = parser.parse_args()

    if args.mode == 'server':
        print("UDP 파일 전송 서버 - 패킷 손상 시뮬레이션 모드")
        print("=" * 60)
        server = CorruptedUDPServer(
            address=args.address,
            port=args.port,
            mtu=args.mtu,
            files_dir=args.files,
            debug=args.debug
        )
        server.start_server()
        
    elif args.mode == 'client':
        if not args.filename:
            print("Error: --filename 인자가 필요합니다 (클라이언트 모드)")
            sys.exit(1)
        
        print("UDP 파일 전송 클라이언트 - 손상된 파일 수신 모드")
        print("=" * 60)
        client = CorruptedUDPClient(
            server_addr=args.server,
            server_port=args.port,
            debug=args.debug
        )
        
        result = client.download_file(args.filename, args.output)
        if result:
            print(f"\n손상된 파일이 저장되었습니다: {result}")
            print("원본 파일과 비교하여 손상 정도를 확인해보세요!")


if __name__ == '__main__':
    if len(sys.argv) == 1:
        # 대화형 모드
        print("UDP 파일 전송 패킷 손상 시뮬레이션")
        print("=" * 50)
        mode = input("모드를 선택하세요 (server/client): ").strip().lower()
        
        if mode == 'server':
            print("서버 모드로 시작합니다...")
            server = CorruptedUDPServer(debug=True)
            server.start_server()
            
        elif mode == 'client':
            server_addr = input("서버 주소 (기본값: 100.87.116.106): ").strip() or '100.87.116.106'
            filename = input("다운로드할 파일명: ").strip()
            output_path = input("저장 경로 (기본값: ./downloads): ").strip() or './downloads'
            
            if filename:
                client = CorruptedUDPClient(server_addr=server_addr, debug=True)
                result = client.download_file(filename, output_path)
                if result:
                    print(f"\n손상된 파일이 저장되었습니다: {result}")
            else:
                print("파일명을 입력해주세요.")
        else:
            print("잘못된 모드입니다. 'server' 또는 'client'를 입력하세요.")
    else:
        main()
