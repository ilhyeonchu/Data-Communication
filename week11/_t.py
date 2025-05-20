import socket

FLAGS = _ = None
DEBUG = False

def main():
    print("2")
    if DEBUG:
        print(f'Parsedarguments{FLAGS}')
        print(f'Unparsedarguments{_}')
    sock=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    print(f'Readytosendusing{sock}'),
    data=input('학번:').strip()
    sock.sendto(data.encode('utf-8'), (FLAGS.address, FLAGS.port))
    print(f'Send {data} to ({FLAGS.address}, {FLAGS.port})')
    data, server = sock.recvfrom(2**16)
    data = data.decode('utf-8')
    print(f'Received{data}from{server}')

if __name__ == '__main__':
    import argparse
    print("1")
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug',action='store_true',
                        help='Thepresentdebugmessage')
    parser.add_argument('--address',type=str,required=True,
                        help='Theaddresstosenddata')
    parser.add_argument('--port',type=int,required=True,
                        help='Theporttosenddata')
    FLAGS, _ =parser.parse_known_args()
    DEBUG=FLAGS.debug

    main()
