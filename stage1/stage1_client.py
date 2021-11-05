# CLIENT
from socket import *
from apscheduler.schedulers.background import BackgroundScheduler
import random as rd
import function
import time
import sys

HOST_1 = '127.0.0.1'
PHY_1 = 11100
APP_1 = 11200
HOST_2 = '127.0.0.1'
PHY_2 = 12100
APP_2 = 12200


if __name__ == '__main__':
    client = socket(AF_INET, SOCK_DGRAM)
    client.bind((HOST_1, PHY_1))
    timer = BackgroundScheduler()
    cnt = 0
    print('start', time.time())

    def send_to_server():
        global cnt
        if cnt >= 20:
            timer.shutdown()
        rdm_num = rd.randint(1, 75)
        bin_string = function.decNumber_2_binString(rdm_num)
        client.sendto(bytes(bin_string), (HOST_1, PHY_2))
        print(cnt, time.time())
        cnt += 1
        print(time.time())

    job = timer.add_job(send_to_server, 'interval', seconds=0.5)
    timer.start()
    time.sleep(5)
    job.pause()
    time.sleep(2)
    job.resume()
    while 1:
        pass

