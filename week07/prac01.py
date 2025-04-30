from RSC import HEX, RSC_LEN, string_rsc
import reedsolo


# 데이터 오류

client_string_rsc = string_rsc
client_string_list = list(client_string_rsc)
client_string_list[4] = 'A'
client_string_list[10] = 'A'
client_string_rsc = ''.join(client_string_list)
print(f'원본: {string_rsc}')
print(f'2바이트 오류: {client_string_rsc}')

client_byte_hex = bytes.fromhex(client_string_rsc)
client_rsc = reedsolo.RSCodec(RSC_LEN)
client_byte = client_rsc.decode(client_byte_hex)[0]
client_text = client_byte.decode('utf-8')
print(f'디코딩: {client_text}')


#client_error_hex = bytes.fromhex(client_string_rsc)
#client_error_text = client_error_hex.decode('utf-8')
#print(f'에러 디코딩: {client_error_text}')


# RS Code error 

client_string_rsc = string_rsc
client_string_list = list(client_string_rsc)
client_string_list[-2] = 'F'
client_string_list[-1] = 'F'
client_string_rsc = ''.join(client_string_list)
print(f'뒤쪽 2바이트: {client_string_rsc}')

client_byte_hex = bytes.fromhex(client_string_rsc)
client_rsc = reedsolo.RSCodec(RSC_LEN)
client_byte = client_rsc.decode(client_byte_hex)[0]
client_text = client_byte.decode('utf-8')
print(f'디코딩: {client_text}')

