import reedsolo

RSC_LEN = 4
HEX = {'0', '1', '2', '3',
       '4', '5', '6', '7',
       '8', '9', 'A', 'B',
       'C', 'D', 'E', 'F'}

text = 'User Input!'
byte_hex = text.encode('utf-8')
string_hex = byte_hex.hex().upper()       # 왜 있는거지
rsc = reedsolo.RSCodec(RSC_LEN)
byte_rsc = rsc.encode(byte_hex)
string_rsc = byte_rsc.hex().upper()

client_string_rsc = string_rsc
client_byte_hex = bytes.fromhex(client_string_rsc)
client_rsc = reedsolo.RSCodec(RSC_LEN)
client_byte = client_rsc.decode(client_byte_hex)[0]
client_text = client_byte.decode('utf-8')

if __name__ == '__main__':
       print(f'인코딩: {string_rsc}')
       print(f'디코딩: {client_text}')