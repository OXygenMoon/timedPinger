import os
import threading
import schedule
import platform
import subprocess
import datetime
import time
import pymysql
from pymysql.converters import escape_string

"""
1. 读取配置文件的服务器列表
2. 开始ping
3. 如果ping通，记录下ping的记录到服务器
4. 如果ping不通，重复三次ping，如果依然不通，记录下ping不通的记录到服务器
5. sleep30秒
"""

class RotatePinger():
    '''
    轮转ping类
    '''
    def __init__(self, file_addr, connect):
        url_nums, urls = self.prepareUrls(file_addr)
        self.url_nums = url_nums
        self.urls = urls
        self.id = 0
        self.conn = connect

    def prepareUrls(self, file_addr):
        '''
        预处理包含若干需要ping的服务器配置文件
        :param file_addr: 配置文件地址
        :return: url的数量和urls的列表
        '''
        try:
            f = open(file_addr, 'r')
        except:
            print('文件无法正常打开')
            raise
        url_nums = 0
        urls = []
        for line in f.readlines():
            url_nums += 1
            line = line[:-1] if line[-1] == '\n' else line
            urls.append(line)
        return url_nums, urls

    def ping(self, host):
        """
        Returns True if host (str) responds to a ping request.
        Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
        """

        ## method 1
        # # Option for the number of packets as a function of
        # param = '-n' if platform.system().lower() == 'windows' else '-c'
        #
        # # Building the command. Ex:"ping -c 1 google.com"
        # command = ['ping', param, '1', host]
        # return (subprocess.call(command) == 0)

        ## method 2
        response = os.system("ping -c 1 " + host)

        # and then check the response...
        return response == 0


    def rotatePing(self):
        '''
        轮转去ping不同的ip地址
        :param host: 指定ip地址
        :return: 返回一组数据
        '''
        ping_state = self.ping(self.urls[self.id]) # True 通 False 不通
        date = datetime.datetime.now()
        return ping_state, str(date)

    def insert2DB(self, cursor, data):
        # try:
        cursor.execute("""insert into main(time, server, state) values("%s", "%s", "%s")""" % (escape_string(data[0]), escape_string(data[1]), escape_string(data[2])))
        self.conn.commit()
        print('写入成功')
        # except:
        #     self.conn.rollback()
        #     print('写入失败')

    def task(self):
        if self.url_nums == 0:
            print('服务器数量为空')
            raise
        ping_state, date = self.rotatePing()
        if ping_state == True:
            cursor = self.conn.cursor()
            print(f'当前时间是: {date} | 服务器: {self.urls[self.id]} | 连接状态: {ping_state}')
            self.insert2DB(cursor, (date, self.urls[self.id], str(ping_state)))
            cursor.close()
            pass # 写入到数据库中
        else:
            # ping不通时，反复 rotatePing 三次
            flag = False
            for i in range(3):
                ping_state, date = self.rotatePing()
                if ping_state == True:
                    flag = True
                    break
            if flag == True:
                cursor = self.conn.cursor()
                print(f'当前时间是: {date} | 服务器: {self.urls[self.id]} | 连接状态: {ping_state}')
                self.insert2DB(cursor, (date, self.urls[self.id], str(ping_state)))
                cursor.close()
                pass # 将ping通写入
            else:
                cursor = self.conn.cursor()
                print(f'当前时间是: {date} | 服务器: {self.urls[self.id]} | 连接状态: {ping_state}')
                self.insert2DB(cursor, (date, self.urls[self.id], str(ping_state)))
                cursor.close()
                pass # 将ping不通写入
        self.id = (self.id + 1) % self.url_nums

def task_threaded(func):
    task_thread = threading.Thread(target = func)
    task_thread.start()

if __name__ == '__main__':
    connect = pymysql.connect(host='localhost',
                                port=3306,
                                user='root',
                                password='123456',
                                database='ping',
                                charset='utf8')
    rp = RotatePinger('addr.txt', connect)
    schedule.every(0.1).minutes.do(task_threaded, rp.task)
    while True:
        # rp.task()
        # rp.conn.close()
        schedule.run_pending()