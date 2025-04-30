from RSC import RSC_LEN, string_rsc, HEX, text
import random
import reedsolo

client_rsc = reedsolo.RSCodec(RSC_LEN)
for i in range(0, RSC_LEN):
    client_string_rsc = string_rsc
    client_string_list = list(client_string_rsc)
    for r in random.sample(range(0, len(client_string_list)//2), k=i):
        m = random.randint(0,2)
        if m == 0:
            client_string_list[(r-1)*2] = random.choice(list(HEX - {client_string_list[(r-1)*2]}))
        elif m == 1:
            client_string_list[(r-1)*2+1] = random.choice(list(HEX - {client_string_list[(r-1)*2+1]}))
        elif m == 2:
            client_string_list[(r-1)*2] = random.choice(list(HEX - {client_string_list[(r-1)*2]}))
            client_string_list[(r-1)*2+1] = random.choice(list(HEX - {client_string_list[(r-1)*2+1]}))
    client_string_rsc = ''.join(client_string_list)
    client_byte_hex = bytes.fromhex(client_string_rsc)
    try:
        clinet_byte = client_rsc.decode(client_byte_hex)[0]
        client_text = clinet_byte.decode('utf-8')
        if client_text == text:
            print(f'{i}개 오류 통과:')
            print(f'> {string_rsc}')
            print(f'> {client_string_rsc}')
    except reedsolo.ReedSolomonError:
        print(f'{i}개 오류 통과 실패:')
        print(f'> {string_rsc}')
        print(f'> {client_string_rsc}')
        break