import random
import socket

FLAGS = _ = None
DEBUG = False


def main():
    if DEBUG:
        print(f'Parsed arguments {FLAGS}')
        print(f'Unparsed arguments {_}')

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((FLAGS.address, FLAGS.port))
    print(f'Listeningon {sock}')

    '''
    # bag 로 1~45 포함한 배열 생성
    # bag = []
    # for i in range(1, 46):
        bag.append(i)
    '''
    max_num = 6 # 최대 숫자

    while True:
        bag = []
        for i in range(1, 46):
            bag.append(i)

        data, client = sock.recvfrom(2 ** 16)
        data = data.decode('utf-8')
        print(f'Received {data} from {client}')
        input_num = data.strip().split() # 선택한 숫자
        selected_numbers = []
        print(f'Numbers in bag: {bag}')  # bag 출력들

        # 받은 숫자들을 bag에서 제거
        for i in input_num:
            try:
                num = int(i)
                bag.remove(num)
                selected_numbers.append(num)
            except ValueError:
                continue

        for i in selected_numbers:
            print(f'Selected: {i}')

        # 반복하면서 숫자 고르기
        # remove select_num in bag 하고 bag에서 하나씩 뽑기
        # 그냥 random으로 뽑고 select_num에 있는지 확인 중에 하나를
        while len(selected_numbers) < max_num :
            rand_index = random.randrange(len(bag))
            rand_num = bag.pop(rand_index)
            selected_numbers.append(rand_num)
        
        # select_num을 정렬해서 data 바꾼 후 다시 client한테 전송
        selected_numbers.sort()
        result = ' '.join(str(n) for n in selected_numbers)
        sock.sendto(result.encode('utf-8'), client)
        print(f'Send {result} to {client}')


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
