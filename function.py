from socket import *
import binascii

stage = 0
table_3bit_dec2bin = {0: [0, 0, 0], 1: [0, 0, 1], 2: [0, 1, 0], 3: [0, 1, 1], 4: [1, 0, 0], 5: [1, 0, 1], 6: [1, 1, 0],
                      7: [1, 1, 1]}


def addr_Dec_2_Bin(dec_num):  # DONE
    return table_3bit_dec2bin[dec_num]


def addr_Bin_2_Dec(bin_string):  # DONE
    return 1 * bin_string[2] + 2 * bin_string[1] + 4 * bin_string[0]


def addr_Cap(sou, des):  # DONE
    bin_sou = addr_Dec_2_Bin(sou)
    bin_des = addr_Dec_2_Bin(des)
    parity = (sum(bin_sou) + sum(bin_des)) % 2
    if parity:
        parity = 0
    else:
        parity = 1
    return [parity] + bin_sou + [0] + bin_des


def addr_deCap(bin_string):  # DONE
    sou = addr_Bin_2_Dec(bin_string[1:4])
    des = addr_Bin_2_Dec(bin_string[5:8])
    return sou, des


def hexByte_2_binString(hex_byte):  # DONE
    bin_string = []
    for num in hex_byte:
        bin_string.append(num)
    return bin_string


def binString_2_decNumber(bin_string):  # DONE
    exp, dec = 0, 0
    for index in range(len(bin_string) - 1, -1, -1):
        dec += bin_string[index] * 2 ** exp
        exp += 1
    return dec


def splitBinString(bin_string):  # DONE
    byte_num, index = len(bin_string) // 8, 0
    bin_8_string = []
    for cnt in range(byte_num):
        bin_8_string.append(bin_string[index:index + 8])
        index += 8
    return bin_8_string


def parity_check(bin_8_string):  # DONE
    isTrue = 1
    for string in bin_8_string:
        if not sum(string) % 2:
            isTrue = 0
    return isTrue


def deParity_check(bin_8_string):  # DONE
    for string in bin_8_string:
        string[0] = 0
    return bin_8_string


def parity_binString_2_decStr(bin_8_string):  # DONE
    dec_str = ''
    deParity = deParity_check(bin_8_string)
    for bin_num in deParity:
        dec_str += chr(binString_2_decNumber(bin_num))
    return dec_str


def decNumber_2_decStr(dec_string):  # DONE
    dec_str = ''
    for dec_num in dec_string:
        dec_str += chr(dec_num)
    return dec_str


def print_by_bit(bin_string):  # DONE
    bin_str = ''
    base8_cnt = 0
    for bit in bin_string:
        if not (base8_cnt % 8):
            bin_str += ' '
        bin_str += str(bit)
        base8_cnt += 1
    return bin_str[1:] + '\n'


def strText_2_decNumber(str_text):  # DONE
    dec_string = []
    for text in str_text:
        dec_string.append(ord(text))
    return dec_string


def decNumber_2_binString(dec):  # DONE
    bin_string = []
    while dec:
        bin_num = dec % 2
        bin_string.insert(0, bin_num)
        dec //= 2
    return bin_string


def decNumber_2_binString_8bit(dec):  # DONE
    bin_string = [0, 0, 0, 0, 0, 0, 0, 0]
    bin_index = 7
    while dec:
        bin_num = dec % 2
        bin_string[bin_index] = bin_num
        dec //= 2
        bin_index -= 1
    if not sum(bin_string) % 2:  # 奇偶校验
        bin_string[0] = 1
    return bin_string


def add_delimiter_front(bin_string):  # DONE
    return [0, 1, 1, 1, 1, 1, 1, 0] + bin_string


def add_delimiter_back(bin_string):  # DONE
    return bin_string + [0, 1, 1, 1, 1, 1, 1, 0]


def strText_2_binString(str_text):  # DONE
    bin_string = []
    for auto_str in str_text:
        bin_string += decNumber_2_binString_8bit(ord(auto_str))
    return bin_string


def convert_11111_to_111110(bin_string):
    global stage
    stage = 0

    def FSM_4_code(bit):
        global stage
        if stage == 0:
            if bit:
                stage = 1
            else:
                stage = 0
        elif stage == 1:
            if bit:
                stage = 2
            else:
                stage = 0
        elif stage == 2:
            if bit:
                stage = 3
            else:
                stage = 0
        elif stage == 3:
            if bit:
                stage = 4
            else:
                stage = 0
        elif stage == 4:
            if bit:
                stage = 0
                return 1
            else:
                stage = 0
        return 0

    for index in range(1024):
        try:
            if FSM_4_code(bin_string[index]):
                index += 1
                bin_string.insert(index, 0)
        except IndexError:
            break

    return bin_string


def convert_111110_to_11111(bin_string):
    global stage
    stage = 0

    def FSM_4_code(bit):
        global stage
        if stage == 0:
            if bit:
                stage = 1
            else:
                stage = 0
        elif stage == 1:
            if bit:
                stage = 2
            else:
                stage = 0
        elif stage == 2:
            if bit:
                stage = 3
            else:
                stage = 0
        elif stage == 3:
            if bit:
                stage = 4
            else:
                stage = 0
        elif stage == 4:
            if bit:
                stage = 0
                return 1
            else:
                stage = 0
        return 0

    for index in range(len(bin_string)):
        try:
            if FSM_4_code(bin_string[index]):
                bin_string.pop(index + 1)
        except IndexError:
            break

    return bin_string


def menu():
    print('0: Cancel')
    print('1: Auto Send')
    print('2: Stop Auto Send')
    print('3: Keyboard Send')
    print('4: Print Data Bit')
    print('5: Print Data Byte')
    print('Please select the working mode:', end='')


if __name__ == '__main__':
    print(table_3bit_dec2bin[10])
