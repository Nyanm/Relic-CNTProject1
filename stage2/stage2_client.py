from socket import *
from apscheduler.schedulers.background import BackgroundScheduler
import function
from PyQt5.QtWidgets import *
from stage2.quin import Ui_APPwithLNK
import threading
import sys

iWorkMode = 0
# iWorkMode = 0 --> 地球上最自由的状态，可以进入其他模式
# iWorkMode = 1 --> 自动发送
# iWorkMode = 2 --> 接收并打印bit流
# iWorkMode = 3 --> 接收并打印byte流

SendCount = 0    # 总发送数量
ResendCount = 0  # 重传数量
ReceiveCount = 0     # 接受数量
Error = 0        # 错帧数量

AutoSendString = []  # 自动发送缓存
isFastSend = 0       # 自动发送数量
ResendData = []      # 重发缓存


HOST = '127.0.0.1'
PHY_1 = 11100
APP_1 = 11200
PHY_2 = 12100
APP_2 = 12200

# 本机属性
SelfID = 1
myPHY = PHY_1
myAPP = APP_1


def set_text(text):
    window.text_receive.setText(text)


def append_text(text):
    window.text_receive.append(text)


class MainWindow(QMainWindow, Ui_APPwithLNK):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)

    def auto_send(self):
        global iWorkMode, SendCount, AutoSendString, ResendData
        if not iWorkMode:
            iWorkMode = 1
            window.num_iworkmode.display(iWorkMode)
            send_text = window.edit_input.toPlainText()
            if send_text:
                window.edit_input.clear()
                send_buf = function.strText_2_binString(send_text)
                send_buf = function.convert_11111_to_111110(send_buf)
                send_buf = [0, 1, 1, 1, 1, 1, 1, 0] + send_buf + [0, 1, 1, 1, 1, 1, 1, 0]
                AutoSendString = ResendData = send_buf
                job_slow.resume()
            else:
                return
        else:
            return

    def stop_send(self):
        global iWorkMode
        job_slow.pause()
        job_fast.pause()
        if iWorkMode == 1:
            iWorkMode = 0
            window.num_iworkmode.display(iWorkMode)
        else:
            return

    def send_once(self):
        global SendCount, ResendData
        if not iWorkMode:
            send_text = window.edit_input.toPlainText()
            if send_text:
                window.edit_input.clear()
                send_buf = function.strText_2_binString(send_text)
                send_buf = function.convert_11111_to_111110(send_buf)
                send_buf = [0, 1, 1, 1, 1, 1, 1, 0] + send_buf + [0, 1, 1, 1, 1, 1, 1, 0]
                ResendData = send_buf
                sock.sendto(bytes(send_buf), (HOST, myPHY))
                SendCount += 1
                window.num_total_send.display(SendCount)
            else:
                return
        else:
            return

    def print_bit(self):
        global iWorkMode
        if not iWorkMode:
            iWorkMode = 2
            window.num_iworkmode.display(iWorkMode)
            window.textBrowser.setText('')  # ?????将setText放到类外可解决崩溃问题，原因未知?????
        else:
            return

    def print_byte(self):
        global iWorkMode
        if not iWorkMode:
            iWorkMode = 3
            window.num_iworkmode.display(iWorkMode)
            window.textBrowser.setText('')
        else:
            return

    def stop_printing(self):
        global iWorkMode
        if iWorkMode == 2 or iWorkMode == 3:
            iWorkMode = 0
            window.num_iworkmode.display(iWorkMode)
        else:
            return


class ReceiveThread(threading.Thread):
    def __init__(self):
        super(ReceiveThread, self).__init__()
        self.data = b''

    def resend(self):
        global ResendCount
        ResendCount += 1
        window.num_total_resend.display(ResendCount)

        if ResendData:
            sock.sendto(bytes(ResendData), (HOST, myPHY))

    def AntiACK(self):
        sock.sendto(bytes([0, 0]), (HOST, myPHY))

    def display(self, is_true, str_data):
        if is_true:
            window.textBrowser.append(str_data + ' ///gotcha!///')
        else:
            window.textBrowser.append(str_data + ' ///but failed...///')

    def run(self):
        global ReceiveCount, Error
        while 1:
            self.data = sock.recvfrom(1024)
            if self.data:
                if iWorkMode < 2:
                    self.resend()
                else:
                    isDelimiter = -1
                    raw_string = function.hexByte_2_binString(self.data[0])
                    ReceiveCount += 1
                    window.num_received.display(ReceiveCount)

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
                    separated = function.splitBinString(data_string)
                    isParity = function.parity_check(separated)
                    byte_str = function.parity_binString_2_decStr(separated)

                    isTrue = isParity * isDelimiter
                    if isTrue:
                        if iWorkMode == 2:
                            self.display(1, bit_str)
                        elif iWorkMode == 3:
                            self.display(1, byte_str)
                    else:
                        Error += 1
                        window.num_failed.display(Error)
                        if iWorkMode == 2:
                            self.display(0, bit_str)
                        elif iWorkMode == 3:
                            self.display(0, bit_str)
                        self.AntiACK()
            else:
                pass


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


def Job_AutoSend():
    global SendCount, isFastSend
    send_string = AutoSendString
    sock.sendto(bytes(send_string), (HOST, myPHY))
    SendCount += 1
    isFastSend += 1
    window.num_total_send.display(SendCount)
    window.num_iworkmode.display(iWorkMode)
    if isFastSend > 4:
        job_slow.pause()
        job_fast.resume()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    sock = socket(AF_INET, SOCK_DGRAM)
    sock.bind((HOST, myAPP))

    # 例化模组
    window = MainWindow()
    window.num_port.display(SelfID)
    find = Delimiter()

    # 添加自动发送定时器
    timer = BackgroundScheduler()
    job_slow = timer.add_job(Job_AutoSend, 'interval', seconds=0.5)
    job_fast = timer.add_job(Job_AutoSend, 'interval', seconds=0.25)
    job_slow.pause()
    job_fast.pause()
    timer.start()

    # 初始化接收用监听线程
    receive = ReceiveThread()
    receive.setDaemon(True)
    receive.start()

    # 绑定按键功能
    window.btn_auto_send.clicked.connect(MainWindow.auto_send)
    window.btn_stop_send.clicked.connect(MainWindow.stop_send)
    window.btn_send_once.clicked.connect(MainWindow.send_once)
    window.btn_print_bit.clicked.connect(MainWindow.print_bit)
    window.btn_print_byte.clicked.connect(MainWindow.print_byte)
    window.btn_stop_print.clicked.connect(MainWindow.stop_printing)

    window.show()
    sys.exit(app.exec_())
