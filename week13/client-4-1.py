import socket
import struct
import argparse
import os
import time

MAX_SEQ = 2
TIMEOUT = 3

def calculate_checksum(data: bytes) -> int:
    if len(data) % 2:
        data += b'\x00'
    checksum = 0
    for i in range(0, len(data), 2):
        word = (data[i] << 8) + data[i+1]
        checksum += word
        checksum = (checksum & 0xFFFF) + (checksum >> 16)
    return ~checksum & 0xFFFF

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--address', type=str, default='localhost')
    parser.add_argument('--port', type=int, default=3034)
    parser.add_argument('--filename', type=str, required=True)
    parser.add_argument('--save', type=str, default=None)
    parser.add_argument('--mtu', type=int, default=1460)
    args = parser.parse_args()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = (args.address, args.port)
    filename = args.filename.upper()
    save_path = args.save or filename

    # 1. INFO 요청
    sock.sendto(f'INFO {filename}'.encode('utf-8'), server)
    size_data, _ = sock.recvfrom(args.mtu)
    if size_data.startswith(b'404'):
        print("File not found on server.")
        return
    filesize = int(size_data.decode('utf-8').strip())
    print(f"File size: {filesize} bytes")

    # 2. DOWNLOAD 요청
    sock.sendto(f'DOWNLOAD {filename}'.encode('utf-8'), server)

    received = 0
    seq_expected = 0
    with open(save_path, 'wb') as f:
        while received < filesize:
            try:
                sock.settimeout(TIMEOUT)
                packet, _ = sock.recvfrom(args.mtu)
                seq = struct.unpack('>H', packet[:2])[0]
                checksum = struct.unpack('>H', packet[2:4])[0]
                data = packet[4:]
                if calculate_checksum(data) == checksum and seq == seq_expected:
                    f.write(data)
                    received += len(data)
                    # Ack 전송
                    ack_pkt = struct.pack('>H', seq)
                    sock.sendto(ack_pkt, server)
                    seq_expected = (seq_expected + 1) % MAX_SEQ
                else:
                    # 중복/에러 패킷: 이전 Ack 재전송
                    ack_pkt = struct.pack('>H', (seq_expected - 1) % MAX_SEQ)
                    sock.sendto(ack_pkt, server)
            except socket.timeout:
                print("Timeout, waiting for retransmission...")
                continue
    print(f"Download complete: {save_path}")

if __name__ == '__main__':
    main()