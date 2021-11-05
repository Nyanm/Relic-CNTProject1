from socket import *
import function
from PyQt5.QtWidgets import *
from stage3.client import Ui_Client
import threading
import sys

SendCount = 0  # 总发送数量
ResendCount = 0  # 重传数量
ReceiveCount = 0  # 接受数量
Error = 0  # 错帧数量

ResendData = []  # 重发缓存
isWaiting = 0  # 等待标识

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
myPHY = PHY_2_0
myAPP = 12200


class MainWindow(QMainWindow, Ui_Client):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

    def send_once(self):
        global SendCount, ResendData, isWaiting
        if isWaiting:
            return

        des = window.num_des.value()
        send_text = window.edit_input.toPlainText()

        if send_text:
            window.edit_input.clear()

            bin_text = function.strText_2_binString(send_text)
            addr = function.addr_Cap(SelfID, des)
            send_buf = addr + bin_text
            send_buf = function.convert_11111_to_111110(send_buf)
            send_buf = [0, 1, 1, 1, 1, 1, 1, 0] + send_buf + [0, 1, 1, 1, 1, 1, 1, 0]
            ResendData = send_buf

            isWaiting = 1
            resend_timer = threading.Timer(0.5, Timer_Resend)
            resend_timer.start()  # 启动超时重传计时器

            sock.sendto(bytes(send_buf), (HOST, myPHY))
            SendCount += 1
            window.num_total_send.display(SendCount)
        else:
            return

    def clear_text(self):
        self.textBrowser.setText('')


class ReceiveThread(threading.Thread):
    def __init__(self):
        super(ReceiveThread, self).__init__()
        self.data = b''

    def resend(self):
        global ResendCount
        if ResendData:
            sock.sendto(bytes(ResendData), (HOST, myPHY))
            ResendCount += 1
            window.num_total_resend.display(ResendCount)

    def ACK(self, flag, des):
        addr = function.addr_Cap(SelfID, des)
        if flag:
            ACK_data = [0, 1, 1, 1, 1, 1, 1, 0] + addr + [1, 1] + [0, 1, 1, 1, 1, 1, 1, 0]
        else:
            ACK_data = [0, 1, 1, 1, 1, 1, 1, 0] + addr + [0] + [0, 1, 1, 1, 1, 1, 1, 0]
        sock.sendto(bytes(ACK_data), (HOST, myPHY))

    def display(self, flag, str_data):
        if flag == -3:
            window.textBrowser.append(str_data + ' ///Parity Error///')
        elif flag == -2:
            window.textBrowser.append(str_data + ' ///Address Blurred///')
        elif flag == 0:
            window.textBrowser.append(str_data + ' ///Wrong Destination///')
        elif flag == 1:
            window.textBrowser.append(str_data + ' ///Gotcha!///')
        else:
            return

    def run(self) -> None:
        global ReceiveCount, Error, isWaiting
        while 1:
            self.data = sock.recvfrom(1024)
            if self.data:
                isDelimiter = -1
                raw_string = function.hexByte_2_binString(self.data[0])

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
                bit_str = function.print_by_bit(data_string)

                if isDelimiter < 1:  # 判断帧是否完整
                    continue

                data_type = len(data_string)
                separated = function.splitBinString(data_string)
                addr = separated[0]

                if not function.parity_check([addr]):  # 判断地址是否有误
                    Error += 1
                    window.num_failed.display(Error)
                    self.display(-2, bit_str)
                    continue

                sou, des = function.addr_deCap(addr)

                if des == SelfID or des == 7:
                    if data_type == 8:  # 询问地址
                        self.ACK(1, sou)

                    elif data_type == 9:  # 重传请求
                        if isWaiting:
                            self.resend()
                            resend_timer.cancel()
                            isWaiting = 0

                    elif data_type == 10:  # 确认
                        print('yes!')
                        resend_timer.cancel()
                        isWaiting = 0

                    else:  # 正常帧
                        ReceiveCount += 1
                        window.num_received.display(ReceiveCount)  # 接收帧数量+1

                        isParity = function.parity_check(separated)

                        if not isParity:  # 判断奇偶校验结果
                            Error += 1
                            window.num_failed.display(Error)
                            self.display(-3, bit_str)
                            self.ACK(0, sou)
                            continue
                        else:
                            separated.pop(0)
                            byte_str = function.parity_binString_2_decStr(separated)
                            self.display(1, byte_str)
                            self.ACK(1, sou)
                else:  # 本机非目的地址
                    self.display(0, bit_str)
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


def Timer_Resend():
    global ResendCount, isWaiting
    if isWaiting:
        if ResendData:
            sock.sendto(bytes(ResendData), (HOST, myPHY))
            ResendCount += 1
            window.num_total_resend.display(ResendCount)
        isWaiting = 0


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind((HOST, myAPP))

    window = MainWindow()
    window.num_id.display(SelfID)
    find = Delimiter()

    # 初始化接收用监听线程
    receive = ReceiveThread()
    receive.setDaemon(True)
    receive.start()

    # 添加超时重发定时器
    resend_timer = threading.Timer(0.5, Timer_Resend)

    # 绑定按键功能
    window.btn_send.clicked.connect(MainWindow.send_once)
    window.btn_cln.clicked.connect(MainWindow.clear_text)

    window.show()
    sys.exit(app.exec_())
