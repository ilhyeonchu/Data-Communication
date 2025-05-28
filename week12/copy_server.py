import os
import socket
import struct

FLAGS = _ = None
DEBUG = False
MAXSEQ = 2

def get_filedict(rootpath):
    files = {}
    with os.scandir(rootpath) as it:
        for entry in it:
            if not entry.name.startswith('.') and entry.is_file():
                info = get_fileinfo(entry.path)
                info['path'] = entry.path
                files[entry.name] = info
    return files

def get_fileinfo(path):
    size = 0
    value = None
    with open(path, 'rb') as f:
        while True:
            chunk = f.read(FLAGS.mtu)
            chunk_size = len(chunk)
            if chunk_size == 0:
                break
            size = size + chunk_size
    return {'size': size}

def main():
    if DEBUG:
        print(f'Parsed arguments {FLAGS}')
        print(f'Unparsed arguments {_}')

    files = get_filedict(FLAGS.files)
    if DEBUG:
        print(f'Ready to file transfer')
        for key, value in files.items():
            print(f'{key}: {value}')
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((FLAGS.address, FLAGS.port))
    print(f'Listening on {sock}')
    
    while True:
        try:
            data, client = sock.recvfrom(FLAGS.mtu)
            data = data.decode ('utf-8')
            data = data.split(' ')

            if len(data) < 2:
                response = 'Error'
                sock.sendto(response.encode('utf-8'), client)
                continue

            command = data[0].upper()
            target = ' '.join(data[1:])
            print(f'{command} {target} from {client}')

            target = target
            if target not in files.keys():
                print(f'{target} was not found (requested bt {client})')
                response = '404 Not Found'
                sock.sendto(response.encode('utf-8'), client)
                continue

            info = files[target]
            path = info['path']
            size = info['size']

            if command == 'INFO':
                response = f'{size}'
                sock.sendto(response.encode('utf-8'), client)
            elif command == 'DOWNLOAD':
                remain = size
                seq = 0
                sock.settimeout(FLAGS.timeout)
                with open(path, 'rb') as f:
                    while remain > 0:
                        chunk = struct.pack('>B', seq) + f.read(FLAGS.mtu)
                        chunk_size = len(chunk[1:])
                        if chunk_size == 0:
                            break
                        remain = remain - chunk_size
                        nseq = (seq+1)%MAXSEQ
                        while True:
                            try:
                                sock.sendto(chunk, client)
                                data, client = sock.recvfrom(FLAGS.mtu)
                                if nseq == struct.unpack('>B', data)[0]:
                                    break
                                else:
                                    continue
                            except socket.timeout:
                                continue
                        if DEBUG:
                            print(f'Transfering to {client} with {seq}: {size-remain}/{size}')
                        seq = nseq
                sock.settimeout(None)
            print(f'File transfer complete {target}')
        except KeyboardInterrupt:
            print(f'Shutting down... {sock}')
            break

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action = 'store_true', help = 'The present debug message')
    parser.add_argument('--address', type = str, default = '100.87.116.106', help='The address to serve service')
    parser.add_argument('--port', type=int, default=2222, help='The port to serve service')
    parser.add_argument('--mtu', type=int, default=1379, help='The port to serve service')
    parser.add_argument('--timeout', type=int, default=3, help='The timeout seconds')
    parser.add_argument('--files', type=str, default='./files', help='The file directory path')
    
    FLAGS, _ = parser.parse_known_args()
    DEBUG = FLAGS.debug

    FLAGS.files = os.path.abspath(os.path.expanduser(FLAGS.files))

    main()


        
