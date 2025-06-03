import socket
import struct
import os
import argparse
import threading
import time

MAX_SEQ = 2  # 0, 1
TIMEOUT = 3  # seconds

def calculate_checksum(data: bytes) -> int:
    """2바이트 1의 보수 합 (Seq/Ack 제외, 데이터만 계산)"""
    if len(data) % 2:
        data += b'\x00'
    checksum = 0
    for i in range(0, len(data), 2):
        word = (data[i] << 8) + data[i+1]
        checksum += word
        checksum = (checksum & 0xFFFF) + (checksum >> 16)
    return ~checksum & 0xFFFF

def make_packet(seq: int, data: bytes) -> bytes:
    checksum = calculate_checksum(data)
    return struct.pack('>H', seq) + struct.pack('>H', checksum) + data

def verify_packet(seq: int, recv_checksum: int, data: bytes) -> bool:
    return calculate_checksum(data) == recv_checksum

def handle_client(sock, client_addr, filename, mtu):
    try:
        with open(filename, 'rb') as f:
            seq = 0
            while True:
                chunk = f.read(mtu - 4)
                if not chunk:
                    break
                packet = make_packet(seq, chunk)
                while True:
                    sock.sendto(packet, client_addr)
                    try:
                        sock.settimeout(TIMEOUT)
                        ack_pkt, _ = sock.recvfrom(4)
                        ack_seq = struct.unpack('>H', ack_pkt[:2])[0]
                        # Ack 번호가 일치하면 다음 블록
                        if ack_seq == seq:
                            seq = (seq + 1) % MAX_SEQ
                            break
                    except socket.timeout:
                        print(f"Timeout, retransmitting seq={seq}")
                        continue
            # 마지막 패킷 전송 후 2*TIMEOUT 대기
            time.sleep(TIMEOUT * 2)
    except Exception as e:
        print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--address', type=str, default='0.0.0.0')
    parser.add_argument('--port', type=int, default=3034)
    parser.add_argument('--dir', type=str, default='.')
    parser.add_argument('--mtu', type=int, default=1460)
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((args.address, args.port))
    print(f"Server listening on {args.address}:{args.port}")

    files = {f.upper(): os.path.join(args.dir, f) for f in os.listdir(args.dir)}

    while True:
        try:
            data, client_addr = sock.recvfrom(args.mtu)
            if not data:
                continue
            # INFO or DOWNLOAD
            if data.startswith(b'INFO '):
                filename = data[5:].decode('utf-8').strip().upper()
                if filename in files:
                    size = os.path.getsize(files[filename])
                    sock.sendto(str(size).encode('utf-8'), client_addr)
                else:
                    sock.sendto(b'404 Not Found', client_addr)
            elif data.startswith(b'DOWNLOAD '):
                filename = data[9:].decode('utf-8').strip().upper()
                if filename in files:
                    threading.Thread(target=handle_client, args=(sock, client_addr, files[filename], args.mtu)).start()
                else:
                    sock.sendto(b'404 Not Found', client_addr)
            else:
                sock.sendto(b'400 Bad Request', client_addr)
        except KeyboardInterrupt:
            print("Server shutting down.")
            break

if __name__ == '__main__':
    main()