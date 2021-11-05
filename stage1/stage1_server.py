# SERVER
from socket import *
import random as rd
import function
from PyQt5.QtWidgets import *

HOST_1 = '127.0.0.1'
PHY_1 = 11100
APP_1 = 11200
HOST_2 = '127.0.0.1'
PHY_2 = 12100
APP_2 = 12200


if __name__ == '__main__':
    app = QApplication([])

    server = socket(AF_INET, SOCK_DGRAM)
    server.bind((HOST_2, APP_2))
    while 1:
        data = server.recvfrom(1024)
        print(data)
        num = function.binString_2_decNumber(function.hexByte_2_binString(data[0]))
        num += rd.randint(1, 75)
        if num > 100:
            bin_string = function.decNumber_2_binString(num)
            server.sendto(bytes(bin_string), (HOST_1, PHY_1))
