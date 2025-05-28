import socket
import os
import random
import sys
import time
import argparse

class UDPFileTransfer:
    def __init__(self, host='localhost', port=12345, chunk_size=1024):
        self.host = host
        self.port = port
        self.chunk_size = chunk_size
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
                data_list[corrupt_index] = random.randint(0, 255)
                print(f"[CORRUPTION] Packet corrupted at byte {corrupt_index}")
                return bytes(data_list)
        return data
    
    def start_server(self, save_dir="received_files"):
        """UDP 서버 시작 - 파일 수신"""
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((self.host, self.port))
        print(f"[SERVER] Listening on {self.host}:{self.port}")
        
        try:
            while True:
                print("[SERVER] Waiting for file transfer...")
                
                # 파일 정보 수신 (파일명, 파일크기)
                data, addr = sock.recvfrom(self.chunk_size)
                file_info = data.decode().split('|')
                
                if len(file_info) != 2:
                    continue
                    
                filename, file_size_str = file_info
                file_size = int(file_size_str)
                
                print(f"[SERVER] Receiving file: {filename} ({file_size} bytes) from {addr}")
                
                # 파일 크기에 따른 손상률 계산
                corruption_rate = self.calculate_corruption_rate(file_size)
                print(f"[SERVER] Corruption rate set to: {corruption_rate*100:.1f}%")
                
                # ACK 전송
                sock.sendto(b"ACK", addr)
                
                # 파일 데이터 수신
                received_data = b""
                packets_received = 0
                corrupted_packets = 0
                
                while len(received_data) < file_size:
                    data, _ = sock.recvfrom(self.chunk_size)
                    
                    # 패킷 손상 시뮬레이션
                    original_data = data
                    corrupted_data = self.corrupt_data(data, corruption_rate)
                    
                    if original_data != corrupted_data:
                        corrupted_packets += 1
                    
                    received_data += corrupted_data
                    packets_received += 1
                
                # 파일 저장
                save_path = os.path.join(save_dir, f"corrupted_{filename}")
                with open(save_path, 'wb') as f:
                    f.write(received_data[:file_size])
                
                print(f"[SERVER] File saved: {save_path}")
                print(f"[SERVER] Statistics:")
                print(f"  - Total packets: {packets_received}")
                print(f"  - Corrupted packets: {corrupted_packets}")
                print(f"  - Corruption rate: {corrupted_packets/packets_received*100:.1f}%")
                print("-" * 50)
                
        except KeyboardInterrupt:
            print("\n[SERVER] Server stopped")
        finally:
            sock.close()
    
    def send_file(self, filepath):
        """클라이언트 - 파일 전송"""
        if not os.path.exists(filepath):
            print(f"[ERROR] File not found: {filepath}")
            return
        
        filename = os.path.basename(filepath)
        file_size = os.path.getsize(filepath)
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        try:
            print(f"[CLIENT] Sending file: {filename} ({file_size} bytes)")
            
            # 파일 정보 전송
            file_info = f"{filename}|{file_size}"
            sock.sendto(file_info.encode(), (self.host, self.port))
            
            # ACK 대기
            data, _ = sock.recvfrom(self.chunk_size)
            if data != b"ACK":
                print("[ERROR] Server did not acknowledge")
                return
            
            # 파일 데이터 전송
            with open(filepath, 'rb') as f:
                bytes_sent = 0
                packet_count = 0
                
                while bytes_sent < file_size:
                    chunk = f.read(self.chunk_size)
                    if not chunk:
                        break
                    
                    sock.sendto(chunk, (self.host, self.port))
                    bytes_sent += len(chunk)
                    packet_count += 1
                    
                    # 진행상황 표시
                    progress = (bytes_sent / file_size) * 100
                    print(f"\r[CLIENT] Progress: {progress:.1f}% ({packet_count} packets)", end="")
                    
                    time.sleep(0.01)  # 네트워크 시뮬레이션을 위한 지연
            
            print(f"\n[CLIENT] File transfer completed: {packet_count} packets sent")
            
        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            sock.close()

def main():
    parser = argparse.ArgumentParser(description='UDP File Transfer with Packet Corruption Simulation')
    parser.add_argument('mode', choices=['server', 'client'], help='Run as server or client')
    parser.add_argument('--file', '-f', help='File to send (client mode only)')
    parser.add_argument('--host', default='localhost', help='Server host (default: localhost)')
    parser.add_argument('--port', '-p', type=int, default=12345, help='Server port (default: 12345)')
    parser.add_argument('--chunk-size', type=int, default=1024, help='Chunk size (default: 1024)')
    
    args = parser.parse_args()
    
    transfer = UDPFileTransfer(args.host, args.port, args.chunk_size)
    
    if args.mode == 'server':
        transfer.start_server()
    elif args.mode == 'client':
        if not args.file:
            print("Error: --file argument is required for client mode")
            sys.exit(1)
        transfer.send_file(args.file)

if __name__ == "__main__":
    # 명령행 인자가 없으면 대화형 모드
    if len(sys.argv) == 1:
        print("UDP File Transfer with Packet Corruption Simulation")
        print("=" * 50)
        mode = input("Select mode (server/client): ").strip().lower()
        
        if mode == 'server':
            transfer = UDPFileTransfer()
            transfer.start_server()
        elif mode == 'client':
            host = input("Server host (default: localhost): ").strip() or 'localhost'
            port = input("Server port (default: 12345): ").strip()
            port = int(port) if port else 12345
            filepath = input("File path to send: ").strip()
            
            transfer = UDPFileTransfer(host, port)
            transfer.send_file(filepath)
        else:
            print("Invalid mode. Use 'server' or 'client'")
    else:
        main()
