import socket

FLAGS = _ = None
DEBUG = False

def main ():
    if DEBUG:
        print(f'Parsed arguments {FLAGS}')
        print(f'Unparsed arguments {_}')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((FLAGS.address, FLAGS.port))
    print(f'Listening on {sock}')

    while True:
        try:
            data, client = sock.recvfrom(FLAGS.mtu)
            data = data.decode('utf-8')
            print(f'Received {data} from {client}')

            data = data
            sock.sendto(data.encode('utf-8'), client)
            print(f'Send {data} to {client}')
        except KeyboardInterrupt:
            print(f'Shuttin down... {sock}')
            break


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true', help='The present debug message') 
    parser.add_argument('--address', type=str, default='0.0.0.0', help='The address to serve service') 
    parser.add_argument('--port', type=int, default=3034, help='The port to serve service') 
    parser.add_argument('--mtu', type=int, default=1500, help='The maximum transmission unit')

    FLAGS, _ = parser.parse_known_args()
    DEBUG = FLAGS.debug

    main()

