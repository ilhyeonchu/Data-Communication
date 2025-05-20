from random import random
import socket

FLAGS = _ = None
DEBUG = False


def main():
    if DEBUG:
        print(f'Parsed arguments {FLAGS}')
        print(f'Unparsed arguments {_}')

    # bag 로 1~45 포함한 배열 생성
    bag = []
    for i in range(1,46):
        bag.append(i)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((FLAGS.address, FLAGS.port))
    print(f'Listeningon {sock}')
    print(f'Numbers in bag: {bag}') # bag 출력들
    max_num = 6 # 최대 숫자 

    while True:
        data, client = sock.recvfrom(2 ** 16)
        data = data.decode('utf-8')
        select_num = data.split(' ') # 선택한 숫자
        max_num = max_num - len(select_num) # 랜덤으로 뽑아야할 숫자의 개수
        
        for i in select_num:
            print(f'Selected: {i}')
        # 반복하면서 숫자 고르기
        # remove select_num in bag 하고 bag에서 하나씩 뽑기
        # 그냥 random으로 뽑고 select_num에 있는지 확인
        for i in range(max_num):
            select_num.append(random
        
        # select_num을 정렬해서 data 바꾼 후 다시 client한테 전송
        sock.sendto(data.encode('utf-8'), client)
        print(f'Send {data} to {client}')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', action='store_true',
                        help='Thepresentdebugmessage')
    parser.add_argument('--address', type=str, default='127.0.0.1',
                        help='Theaddresstoserveservice')
    parser.add_argument('--port', type=int, default=3034,
                        help='Theporttoserveservice')

    FLAGS, _ = parser.parse_known_args()
    DEBUG = FLAGS.debug

    main()
