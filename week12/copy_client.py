import socket
import struct

FLAGS = _ = None
DEBUG = False
MAXSEQ = 2


def main():
    if DEBUG:
        print(f'Parsed arguments {FLAGS}')
        print(f'Unparsed arguments {_}')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f'Ready to send using {sock}')

    while True:
        try:
            sock.settimeout(FLAGS.timeout)
            filename = input('File name:').strip()
            request = f'INFO {filename}'
            sock.sendto(request.encode('utf-8'), (FLAGS.address, FLAGS.port))

            response, server = sock.recvfrom(FLAGS.chunk_maxsize)
            response = response.decode('utf-8')
            if response == '404 Not Found':
                print('File not found on server.')
                continue

            size = int(response)

            request = f'DOWNLOAD {filename}'
            sock.sendto(request.encode('utf-8'), (FLAGS.address, FLAGS.port))
            print(f'Request {filename} to ({FLAGS.address}, {FLAGS.port})')

            remain = size
            seq = 0
            sock.settimeout(FLAGS.timeout)
            with open(filename, 'wb') as f:
                while remain > 0:
                    while True:
                        try:
                            chunk, server = sock.recvfrom(FLAGS.chunk_maxsize)
                            if seq == struct.unpack('>B', chunk[:1])[0]:
                                break
                            else:
                                sock.sendto(struct.pack('>B', seq), (FLAGS.address, FLAGS.port))
                        except socket.timeout:
                            sock.sendto(struct.pack('>B', seq), (FLAGS.address, FLAGS.port))
                            continue

                    data = chunk[1:]
                    data_size = len(data)
                    if data_size == 0:
                        break
                    remain = remain - data_size
                    f.write(data)
                    if DEBUG:
                        print(f'Receiving from {server} with {seq}: {size-remain}/{size}')
                    seq = (seq+1)%MAXSEQ
                    sock.sendto(struct.pack('>B', seq), (FLAGS.address, FLAGS.port))
            print(f'File download success')
            sock.settimeout(None)
        except KeyboardInterrupt:
                print(f'Shutting down... {sock}')
                break

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', help='The present debug message')
    parser.add_argument('--address', type=str, default='100.87.116.106', help='The address to send data')
    parser.add_argument('--port', type=int, default=2222, help='The port to send data')
    parser.add_argument('--chunk_maxsize', type=int, default=1379, help='The recvfrom chunk max size')
    parser.add_argument('--timeout', type=int, default=10, help='The timeout seconds')

    FLAGS, _ = parser.parse_known_args()
    DEBUG = FLAGS.debug

    main()
