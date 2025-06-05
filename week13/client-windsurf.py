import socket
import struct
import argparse
import os
import time

FLAGS = None
DEBUG = False
MAX_SEQ = 2  # 0과 1만 사용

def request_file_info(sock, server_addr, filename):
    """파일 정보 요청 함수"""
    request = f'INFO {filename}'.encode('utf-8')
    sock.sendto(request, server_addr)
    
    if DEBUG:
        print(f"[DEBUG] 파일 정보 요청: {filename}")
    
    try:
        response, _ = sock.recvfrom(1024)
        response = response.decode('utf-8')
        
        if response == '404 Not Found':
            print(f"[!] 오류: 서버에 파일이 없습니다 - {filename}")
            return None
        
        file_size = int(response)
        if DEBUG:
            print(f"[DEBUG] 파일 크기: {file_size} 바이트")
        
        return file_size
    
    except socket.timeout:
        print("[!] 오류: 서버로부터 응답이 없습니다 (타임아웃)")
        return None
    except Exception as e:
        if DEBUG:
            print(f"[DEBUG] 파일 정보 요청 오류: {e}")
        return None

def download_file(sock, server_addr, filename, filesize, output_path):
    """파일 다운로드 함수"""
    # 디렉토리가 존재하지 않으면 생성
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # 파일 다운로드 요청
    request = f'DOWNLOAD {filename}'.encode('utf-8')
    sock.sendto(request, server_addr)
    
    if DEBUG:
        print(f"[DEBUG] 파일 다운로드 요청: {filename} -> {output_path}")
    
    received_size = 0
    expected_seq = 0  # 다음에 받을 예상 시퀀스 번호
    
    with open(output_path, 'wb') as f:
        while received_size < filesize:
            try:
                # 패킷 수신
                packet, _ = sock.recvfrom(FLAGS.mtu)
                
                if len(packet) < 4:  # 최소 4바이트(시퀀스 2바이트 + 체크섬 2바이트) 필요
                    if DEBUG:
                        print("[DEBUG] 잘못된 패킷 수신 (너무 짧음)")
                    continue
                
                # 패킷 파싱
                seq_num = struct.unpack('>H', packet[:2])[0]
                checksum = struct.unpack('>H', packet[-2:])[0]
                data = packet[2:-2]  # 시퀀스 번호와 체크섬 제외
                
                # 체크섬 검증
                calculated_checksum = 0
                for b in packet[:-2]:  # 수신한 체크섬 제외
                    calculated_checksum ^= b
                
                if checksum != calculated_checksum:
                    if DEBUG:
                        print(f"[DEBUG] 체크섬 불일치: 수신={checksum}, 계산={calculated_checksum}")
                    # 잘못된 체크섬이면 ACK를 보내지 않음 (타임아웃 후 재전송 유도)
                    continue
                
                # 예상한 시퀀스 번호와 일치하는지 확인
                if seq_num == expected_seq:
                    # 데이터 저장
                    f.write(data)
                    received_size += len(data)
                    
                    # 진행 상황 출력
                    progress = (received_size / filesize) * 100
                    print(f"\r다운로드 중: {received_size}/{filesize} 바이트 ({progress:.1f}%)", end='', flush=True)
                    
                    # ACK 전송
                    ack_packet = struct.pack('>H', expected_seq)
                    sock.sendto(ack_packet, server_addr)
                    
                    if DEBUG:
                        print(f"\n[DEBUG] ACK 전송: {expected_seq}")
                    
                    # 다음 시퀀스 번호로 업데이트
                    expected_seq = (expected_seq + 1) % MAX_SEQ
                else:
                    # 잘못된 시퀀스 번호이면 마지막으로 받은 올바른 ACK 재전송
                    last_ack = (expected_seq - 1) % MAX_SEQ
                    ack_packet = struct.pack('>H', last_ack)
                    sock.sendto(ack_packet, server_addr)
                    
                    if DEBUG:
                        print(f"[DEBUG] 잘못된 시퀀스: 기대={expected_seq}, 수신={seq_num}, ACK={last_ack}")
            
            except socket.timeout:
                print("\n[!] 오류: 서버로부터 응답이 없습니다 (타임아웃)")
                return False
            except Exception as e:
                if DEBUG:
                    print(f"\n[DEBUG] 다운로드 오류: {e}")
                return False
    
    print(f"\n[+] 파일 다운로드 완료: {output_path}")
    return True

def main():
    # 명령줄 인자 파싱
    parser = argparse.ArgumentParser(description='Stop and Wait ARQ Client')
    parser.add_argument('--debug', action='store_true', help='디버그 메시지 출력')
    parser.add_argument('--server', type=str, default='localhost', help='서버 주소')
    parser.add_argument('--port', type=int, default=3034, help='서버 포트')
    parser.add_argument('--mtu', type=int, default=1400, help='최대 전송 단위')
    parser.add_argument('--timeout', type=float, default=3.0, help='타임아웃(초)')
    parser.add_argument('filename', type=str, help='다운로드할 파일 이름')
    parser.add_argument('output', type=str, help='저장할 파일 경로')
    
    global FLAGS, DEBUG
    FLAGS = parser.parse_args()
    DEBUG = FLAGS.debug
    
    # 소켓 생성
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(FLAGS.timeout)
    
    server_addr = (FLAGS.server, FLAGS.port)
    
    try:
        # 1. 파일 정보 요청
        print(f"[*] 파일 정보 요청 중: {FLAGS.filename}")
        filesize = request_file_info(sock, server_addr, FLAGS.filename)
        
        if filesize is None:
            return  # 오류 발생 시 종료
        
        # 2. 파일 다운로드
        print(f"[*] 파일 다운로드 시작: {FLAGS.filename} ({filesize} 바이트)")
        success = download_file(sock, server_addr, FLAGS.filename, filesize, FLAGS.output)
        
        if success:
            print("[+] 파일 다운로드가 성공적으로 완료되었습니다.")
        else:
            print("[!] 파일 다운로드 중 오류가 발생했습니다.")
    
    except KeyboardInterrupt:
        print("\n[!] 사용자에 의해 종료되었습니다.")
    except Exception as e:
        print(f"\n[!] 오류 발생: {e}")
    finally:
        sock.close()

if __name__ == '__main__':
    main()