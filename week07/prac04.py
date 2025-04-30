import reedsolo
import random

# 입력 메시지와 RS 설정
text = 'User Input!'
RSC_LEN = 8 # RS 부호화 길이
# RS 인코딩: 텍스트를 바이트열로 인코딩 후 RS 인코딩 적용
rsc = reedsolo.RSCodec(RSC_LEN)
encoded_bytes = rsc.encode(text.encode('utf-8'))
encoded_hex = encoded_bytes.hex().upper()
print("원본 RS 인코딩 데이터 (헥스):")
print(encoded_hex)
# 임의 오류 주입: 0~2개의 랜덤한 바이트를 변경
error_count = random.randint(0, 4)  # (또는 0~4 정도로 지정해도 됨) 이니까 0,2 나 0,4 선택?
print(f"\n주입할 오류 개수: {error_count}")
# 바이트열을 수정하기 위해 bytearray 변환
encoded_bytes_with_errors = bytearray(encoded_bytes)
indices = random.sample(range(len(encoded_bytes_with_errors)), error_count)
for idx in indices:
    original_byte = encoded_bytes_with_errors[idx]
    new_byte = random.randint(0, 255)
    # 원래의 값과 같지 않도록
    while new_byte == original_byte:
        new_byte = random.randint(0, 255)
    encoded_bytes_with_errors[idx] = new_byte

error_hex = encoded_bytes_with_errors.hex().upper()
print("오류가 주입된 RS 데이터 (헥스):")
print(error_hex)

# RS 디코딩 시도 및 오류 복원
try:
    decoded_bytes = rsc.decode(bytes(encoded_bytes_with_errors))[0]
    recovered_text = decoded_bytes.decode('utf-8')
    print("\nRS 디코딩 성공!")
    print("복원된 메시지:")
    print(recovered_text)
except reedsolo.ReedSolomonError as e:
    print("\nRS 디코딩 실패!")
    print(e)
except UnicodeDecodeError as e:
    print("\nRS 디코딩은 되었으나, UTF-8 디코딩에 실패했습니다.")
    print(e)