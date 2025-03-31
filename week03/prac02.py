import sys
import math
import wave
import struct
import statistics

english = {'A':'.-'   , 'B':'-...' , 'C':'-.-.' , 
           'D':'-..'  , 'E':'.'    , 'F':'..-.' , 
           'G':'--.'  , 'H':'....' , 'I':'..'   , 
           'J':'.---' , 'K':'-.-'  , 'L':'.-..' , 
           'M':'--'   , 'N':'-.'   , 'O':'---'  , 
           'P':'.--.' , 'Q':'--.-' , 'R':'.-.'  , 
           'S':'...'  , 'T':'-'    , 'U':'..-'  , 
           'V':'...-' , 'W':'.--'  , 'X':'-..-' , 
           'Y':'-.--' , 'Z':'--..'  }
number = { '1':'.----', '2':'..---', '3':'...--', 
           '4':'....-', '5':'.....', '6':'-....', 
           '7':'--...', '8':'---..', '9':'----.', 
           '0':'-----'}

def text2morse(text):
    text = text.upper()
    morse = ''
    
    for t in text:
        for key, value in english.items():
            if t == key:
                morse = morse + value
        for key, value in number.items():
            if t == key:
                morse = morse + value
                
    return morse

morse_result = text2morse('HelloWorld')

with open('morse_output.txt', 'w') as f:
    f.write(morse_result)

print (morse_result)
