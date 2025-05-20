import socket

SERVER_IP = '35.192.31.92'
SERVER_PORT = 3035

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # 1) 학번 입력
    sid = input("학번: ").strip()
    
    # 2) 가위·바위·보 시퀀스 입력 (예: kawi bawi bo kawi bo)
    seq = input("kawi bawi bo 중 원하는 것을 5회 입력하세요): ")\
        .strip().lower().split()
    
    # 유효성 검사
    if not sid or any(m not in ('kawi','bawi','bo') for m in seq):
        print("Invalid 학번 or move sequence.")
        return
    
    # 3) 메시지 구성 및 전송
    msg = ' '.join([sid] + seq)
    sock.sendto(msg.encode('utf-8'), (SERVER_IP,SERVER_PORT))
    print(f"Send → {msg} to ({SERVER_IP}, {SERVER_PORT})")
    
    # 4) 서버 ACK 수신
    data, _ = sock.recvfrom(1024)
    print("Received ←", data.decode('utf-8'))

if __name__ == '__main__':
    main()
