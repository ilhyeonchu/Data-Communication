frequency_rules = {'START': 512, '0': 768, '1': 896,
                   '2': 1024, '3': 1152, '4': 1280, 
                   '5': 1408, '6': 1536, '7': 1664, 
                   '8': 1892, '9': 1920, 'A': 2048, 
                   'B': 2176, 'C': 2304, 'D': 2432, 
                   'E': 2560, 'F': 2688, 'END': 2944}
INTMAX = 2**(32-1)-1
channels = 1 
unit = 0.1
sample_rate = 48000
FREQ_START = 512
FREQ_STEP = 128
chunk_size = 1024
HEX_LIST = ['0', '1', '2', '3',
            '4', '5', '6', '7',
            '8', '9', 'A', 'B',
            'C', 'D', 'E', 'F']
HEX = set(HEX_LIST)

rules = {}
print('Frequency Rules:')
rules['START'] = FREQ_START
for i in range(len(HEX_LIST)):
    h = HEX_LIST[i]
    rules[h] = FREQ_START + FREQ_STEP + FREQ_STEP*(i+1)
rules['END'] = rules['START'] + FREQ_STEP + FREQ_STEP*(len(HEX_LIST)) + FREQ_STEP * 2

for k, v in rules.items():
    print(f'{k} => {v}')


