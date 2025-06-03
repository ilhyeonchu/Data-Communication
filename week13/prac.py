import socket
import struct
import argparse

FLAGS = None


def calculate_checksum(data: bytes) -> int:
    if len(data) % 2 == 1:
        data += b'\x00'
    s = 0
    for i in range(0, len(data), 2):
        word = data[i] << 8 | data[i + 1]
        s += word
        s = (s & 0xFFFF) + (s >> 16)
    return (~s) & 0xFFFF


def verify_checksum(data: bytes, checksum: int) -> bool:
    return calculate_checksum(struct.pack('>H', checksum) + data) == 0


def send_ack(sock, addr, seq: int) -> None:
    chk = calculate_checksum(b'')
    packet = struct.pack('>H', seq) + struct.pack('>H', chk)
    sock.sendto(packet, addr)


def recv_file(sock: socket.socket, filename: str, size: int, chunk_size: int) -> None:
    expected = 0
    remain = size
    with open(filename, 'wb') as f:
        while remain > 0:
            try:
                packet, server = sock.recvfrom(chunk_size + 4)
            except socket.timeout:
                continue
            seq = struct.unpack('>H', packet[:2])[0]
            data = packet[2:-2]
            checksum = struct.unpack('>H', packet[-2:])[0]
            if seq == expected and verify_checksum(data, checksum):
                if remain < len(data):
                    data = data[:remain]
                f.write(data)
                remain -= len(data)
                expected = (expected + 1) % 2
            send_ack(sock, server, expected)


def main() -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(FLAGS.timeout)

    while True:
        try:
            filename = input('Filename: ').strip()
            request = f'INFO {filename}'
            sock.sendto(request.encode('utf-8'), (FLAGS.address, FLAGS.port))
            response, server = sock.recvfrom(FLAGS.mtu)
            response = response.decode('utf-8')
            if response == '404 Not Found':
                print(response)
                continue
            size = int(response)
            request = f'DOWNLOAD {filename}'
            sock.sendto(request.encode('utf-8'), (FLAGS.address, FLAGS.port))
            print(f'Request {filename} ({size} bytes)')
            recv_file(sock, filename, size, FLAGS.mtu - 4)
            print('File download success')
        except KeyboardInterrupt:
            print(f'Shutting down... {sock}')
            break

    sock.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--address', default='localhost', help='Server address')
    parser.add_argument('--port', type=int, default=3034, help='Server port')
    parser.add_argument('--mtu', type=int, default=1500, help='MTU size')
    parser.add_argument('--timeout', type=int, default=3, help='Timeout seconds')
    FLAGS = parser.parse_args()
    main()
