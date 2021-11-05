from socket import *
import function
from PyQt5.QtWidgets import *
from stage3.router import Ui_Switch
import threading
import sys

LookupTable = {}


HOST = '127.0.0.1'
PHY_1 = 11100
APP_1 = 11200
PHY_2_0 = 12100
PHY_2_1 = 12101
PHY_2_2 = 12102
LNK_2_0 = 12200
LNK_2_1 = 12201
LNK_2_2 = 12202
PHY_3 = 13100
APP_3 = 13200
PHY_4_0 = 14100
PHY_4_1 = 14101
PHY_4_2 = 14102
LNK_4_0 = 14200
LNK_4_1 = 14201
LNK_4_2 = 14202
PHY_5 = 15100
APP_5 = 15200
PHY_6 = 16100
APP_6 = 16200

# 本机属性
SelfID = 2
myPHY_0 = PHY_2_0
myPHY_1 = PHY_2_1
myPHY_2 = PHY_2_2
myLNK_0 = LNK_2_0
myLNK_1 = LNK_2_1
myLNK_2 = LNK_2_2


class MainWindow(QMainWindow, Ui_Switch):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)


class ReceiveThread0(threading.Thread):
    def __init__(self):
        super(ReceiveThread0, self).__init__()
        self.data = b''
        self.id_lnk = 0

    def broadcast(self, data):
        sock_1.sendto(bytes(data), (HOST, myPHY_1))
        sock_2.sendto(bytes(data), (HOST, myPHY_2))

    def inquiry(self, des):
        addr = function.addr_Cap(SelfID, des)
        inquiry_data = [0, 1, 1, 1, 1, 1, 1, 0] + addr + [0, 1, 1, 1, 1, 1, 1, 0]
        sock_1.sendto(bytes(inquiry_data), (HOST, myPHY_1))
        sock_2.sendto(bytes(inquiry_data), (HOST, myPHY_2))

    def transmit(self, data, port):
        print(data, port)
        if port == 0:
            sock_0.sendto(bytes(data), (HOST, myPHY_0))
        elif port == 1:
            sock_1.sendto(bytes(data), (HOST, myPHY_1))
        elif port == 2:
            sock_2.sendto(bytes(data), (HOST, myPHY_2))
        else:
            return

    def run(self) -> None:
        while 1:
            self.data = sock_0.recvfrom(1024)
            if self.data:
                isDelimiter = -1
                raw_string = function.hexByte_2_binString(self.data[0])
                origin_data = raw_string
                print(raw_string, LookupTable)

                for index in range(len(raw_string)):
                    if find.FSM_4_delimiter(raw_string[index]):
                        raw_string = raw_string[index + 1:]
                        isDelimiter += 1
                        break
                for index in range(len(raw_string)):
                    if find.FSM_4_delimiter(raw_string[index]):
                        raw_string = raw_string[: index - 7]
                        isDelimiter += 1
                        break

                data_string = function.convert_111110_to_11111(raw_string)

                if isDelimiter < 1:  # 判断帧是否完整
                    continue

                separated = function.splitBinString(data_string)
                addr = separated[0]

                if not function.parity_check([addr]):  # 判断地址是否有误
                    continue

                sou, des = function.addr_deCap(addr)

                try:  # 根据转进端口查表，失败则写入
                    from_port = LookupTable[sou]
                except KeyError:
                    LookupTable[sou] = self.id_lnk
                    print(LookupTable)
                    window.route_table.insertRow(0)
                    sou_item = QTableWidgetItem(str(sou))
                    port_item = QTableWidgetItem(str(self.id_lnk))
                    window.route_table.setItem(0, 0, sou_item)
                    window.route_table.setItem(0, 1, port_item)

                if des == 7:  # 目的地址为[1, 1, 1]时广播
                    self.broadcast(origin_data)
                    continue

                if des == SelfID:  # 目的为自己吞下该帧
                    continue

                try:
                    to_port = LookupTable[des]
                    print(des, to_port)
                    self.transmit(origin_data, to_port)
                except KeyError:
                    self.inquiry(des)
                    print('///')
                    continue


class ReceiveThread1(threading.Thread):
    def __init__(self):
        super(ReceiveThread1, self).__init__()
        self.data = b''
        self.id_lnk = 1

    def broadcast(self, data):
        sock_0.sendto(bytes(data), (HOST, myPHY_0))
        sock_2.sendto(bytes(data), (HOST, myPHY_2))

    def inquiry(self, des):
        addr = function.addr_Cap(SelfID, des)
        inquiry_data = [0, 1, 1, 1, 1, 1, 1, 0] + addr + [0, 1, 1, 1, 1, 1, 1, 0]
        sock_0.sendto(bytes(inquiry_data), (HOST, myPHY_0))
        sock_2.sendto(bytes(inquiry_data), (HOST, myPHY_2))

    def transmit(self, data, port):
        if port == 0:
            sock_0.sendto(bytes(data), (HOST, myPHY_0))
        elif port == 1:
            sock_1.sendto(bytes(data), (HOST, myPHY_1))
        elif port == 2:
            sock_2.sendto(bytes(data), (HOST, myPHY_2))
        else:
            return

    def run(self) -> None:
        while 1:
            self.data = sock_1.recvfrom(1024)
            if self.data:
                isDelimiter = -1
                raw_string = function.hexByte_2_binString(self.data[0])
                origin_data = raw_string

                for index in range(len(raw_string)):
                    if find.FSM_4_delimiter(raw_string[index]):
                        raw_string = raw_string[index + 1:]
                        isDelimiter += 1
                        break
                for index in range(len(raw_string)):
                    if find.FSM_4_delimiter(raw_string[index]):
                        raw_string = raw_string[: index - 7]
                        isDelimiter += 1
                        break

                data_string = function.convert_111110_to_11111(raw_string)

                if isDelimiter < 1:  # 判断帧是否完整
                    continue

                separated = function.splitBinString(data_string)
                addr = separated[0]

                if not function.parity_check([addr]):  # 判断地址是否有误
                    continue

                sou, des = function.addr_deCap(addr)

                try:  # 根据转进端口查表，失败则写入
                    from_port = LookupTable[sou]
                except KeyError:
                    LookupTable[sou] = self.id_lnk
                    print(LookupTable)
                    window.route_table.insertRow(0)
                    sou_item = QTableWidgetItem(str(sou))
                    port_item = QTableWidgetItem(str(self.id_lnk))
                    window.route_table.setItem(0, 0, sou_item)
                    window.route_table.setItem(0, 1, port_item)

                if des == 7:  # 目的地址为[1, 1, 1]时广播
                    self.broadcast(origin_data)
                    continue

                if des == SelfID:  # 目的为自己吞下该帧
                    continue

                try:
                    to_port = LookupTable[des]
                    self.transmit(origin_data, to_port)
                except KeyError:
                    self.inquiry(des)
                    continue


class ReceiveThread2(threading.Thread):
    def __init__(self):
        super(ReceiveThread2, self).__init__()
        self.data = b''
        self.id_lnk = 2

    def broadcast(self, data):
        sock_0.sendto(bytes(data), (HOST, myPHY_0))
        sock_1.sendto(bytes(data), (HOST, myPHY_1))

    def inquiry(self, des):
        addr = function.addr_Cap(SelfID, des)
        inquiry_data = [0, 1, 1, 1, 1, 1, 1, 0] + addr + [0, 1, 1, 1, 1, 1, 1, 0]
        sock_0.sendto(bytes(inquiry_data), (HOST, myPHY_0))
        sock_1.sendto(bytes(inquiry_data), (HOST, myPHY_1))

    def transmit(self, data, port):
        if port == 0:
            sock_0.sendto(bytes(data), (HOST, myPHY_0))
        elif port == 1:
            sock_1.sendto(bytes(data), (HOST, myPHY_1))
        elif port == 2:
            sock_2.sendto(bytes(data), (HOST, myPHY_2))
        else:
            return

    def run(self) -> None:
        while 1:
            self.data = sock_2.recvfrom(1024)
            if self.data:
                isDelimiter = -1
                raw_string = function.hexByte_2_binString(self.data[0])
                origin_data = raw_string
                print(raw_string, LookupTable)

                for index in range(len(raw_string)):
                    if find.FSM_4_delimiter(raw_string[index]):
                        raw_string = raw_string[index + 1:]
                        isDelimiter += 1
                        break
                for index in range(len(raw_string)):
                    if find.FSM_4_delimiter(raw_string[index]):
                        raw_string = raw_string[: index - 7]
                        isDelimiter += 1
                        break

                data_string = function.convert_111110_to_11111(raw_string)

                if isDelimiter < 1:  # 判断帧是否完整
                    continue

                separated = function.splitBinString(data_string)
                addr = separated[0]

                if not function.parity_check([addr]):  # 判断地址是否有误
                    continue

                sou, des = function.addr_deCap(addr)

                try:  # 根据转进端口查表，失败则写入
                    from_port = LookupTable[sou]
                except KeyError:
                    LookupTable[sou] = self.id_lnk
                    print(LookupTable)
                    window.route_table.insertRow(0)
                    sou_item = QTableWidgetItem(str(sou))
                    port_item = QTableWidgetItem(str(self.id_lnk))
                    window.route_table.setItem(0, 0, sou_item)
                    window.route_table.setItem(0, 1, port_item)

                if des == 7:  # 目的地址为[1, 1, 1]时广播
                    self.broadcast(origin_data)
                    continue

                if des == SelfID:  # 目的为自己吞下该帧
                    continue

                try:
                    to_port = LookupTable[des]
                    self.transmit(origin_data, to_port)
                except KeyError:
                    self.inquiry(des)
                    continue


class Delimiter(object):
    def __init__(self):
        self.stage = 0

    def FSM_4_delimiter(self, bit):
        if self.stage == 0:
            if bit:
                self.stage = 0
            else:
                self.stage = 1
        elif self.stage == 1:
            if bit:
                self.stage = 2
            else:
                self.stage = 1
        elif self.stage == 2:
            if bit:
                self.stage = 3
            else:
                self.stage = 1
        elif self.stage == 3:
            if bit:
                self.stage = 4
            else:
                self.stage = 1
        elif self.stage == 4:
            if bit:
                self.stage = 5
            else:
                self.stage = 1
        elif self.stage == 5:
            if bit:
                self.stage = 6
            else:
                self.stage = 1
        elif self.stage == 6:
            if bit:
                self.stage = 7
            else:
                self.stage = 1
        elif self.stage == 7:
            if bit:
                self.stage = 0
            else:
                self.stage = 0
                return 1
        return 0


if __name__ == '__main__':
    app = QApplication(sys.argv)

    sock_0 = socket(AF_INET, SOCK_DGRAM)
    sock_1 = socket(AF_INET, SOCK_DGRAM)
    sock_2 = socket(AF_INET, SOCK_DGRAM)
    sock_0.bind((HOST, myLNK_0))
    sock_1.bind((HOST, myLNK_1))
    sock_2.bind((HOST, myLNK_2))

    window = MainWindow()
    window.num_id.display(SelfID)
    find = Delimiter()

    receive_0 = ReceiveThread0()
    receive_0.setDaemon(True)
    receive_0.start()

    receive_1 = ReceiveThread1()
    receive_1.setDaemon(True)
    receive_1.start()

    receive_2 = ReceiveThread2()
    receive_2.setDaemon(True)
    receive_2.start()

    window.show()
    sys.exit(app.exec_())
