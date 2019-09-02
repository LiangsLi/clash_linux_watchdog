# -*- coding: utf-8 -*-
# Created by li huayong on 2019/8/16
import json
import os
import requests
import time
from datetime import datetime
# import threading
import multiprocessing


def get_now_server(port=9090, proxy="Auto - UrlTest"):
    try:
        response = requests.get(f'http://127.0.0.1:{port}/proxies')
    except Exception as e:
        time.sleep(4)
        response = requests.get(f'http://127.0.0.1:{port}/proxies')
    content = json.loads(response.content)
    return content['proxies'][proxy]['now']


def watch_server(sleep_time=5):
    print('Now watch server...')
    # restart_clash()
    change_times = 0
    previous_proxy = ''
    while True:
        if not previous_proxy:
            previous_proxy = get_now_server()
            print(f'{datetime.now()} - guard start; proxy:{previous_proxy}')
        else:
            now_proxy = get_now_server()
            if now_proxy != previous_proxy:
                restart_clash()
                change_times += 1
                print(f'watch server: now server {now_proxy}')
                # print(f'{datetime.now()} - {change_times} : {previous_proxy} -> {now_proxy}; restart clash')
                previous_proxy = get_now_server()
        time.sleep(sleep_time)


def watch_delay(sleep_time=5, timeout=500):
    delay = get_delay(1)
    print(f"Now watch delay... {delay}ms")
    time.sleep(sleep_time)
    while True:
        delay = get_delay(1)
        # print(f'\t\t -> delay : {delay}')
        restart_times = 0
        while not delay or delay > timeout:
            time.sleep(4)
            if restart_times == 20:
                raise RuntimeError('max restart times, quit...')
            print(f'watch delay: delay timeout: {delay}, restart clash......')
            os.system("pm2 restart clash-linux --update-env -s")
            time.sleep(1)
            now_proxy = get_now_server()
            print(f'watch delay: now server {now_proxy}')
            delay = get_delay(1)
            print(f'\t\t -> delay : {delay}')
            restart_times += 1
        time.sleep(sleep_time)


def restart_clash(timeout=500):
    os.system("pm2 restart clash-linux --update-env -s")
    delay = get_delay()
    # print(f'\t\t -> delay : {delay}')
    restart_times = 0
    while not delay or delay > timeout:
        time.sleep(4)
        if restart_times == 20:
            raise RuntimeError('max restart times, quit...')
        print('restart: timeout, restart clash......')
        os.system("pm2 restart clash-linux --update-env -s")
        time.sleep(1)
        delay = get_delay()
        print(f'\t\t -> delay : {delay}')
        restart_times += 1


def get_delay(num=1):
    assert num <= 4
    try:
        r1 = requests.get('https://www.google.com', timeout=1)
    except Exception as e1:
        delay1 = 1100
        # print(e1)
    else:
        delay1 = r1.elapsed.total_seconds() * 100
    try:
        r2 = requests.get('https://zh.wikipedia.org', timeout=1)
    except Exception as e2:
        delay2 = 1100
        # print(e2)
    else:
        delay2 = r2.elapsed.total_seconds() * 100
    try:
        r3 = requests.get('https://www.gstatic.com/generate_204', timeout=1)
    except Exception as e3:
        delay3 = 1100
        # print(e3)
    else:
        delay3 = r3.elapsed.total_seconds() * 100
    try:
        r4 = requests.get('https://github.com/', timeout=1)
    except Exception as e4:
        delay4 = 1100
    else:
        delay4 = r4.elapsed.total_seconds() * 100
    return sum([delay3, delay1, delay4, delay1][:num]) / num


def is_clash_start():
    with os.popen("ps|grep clash-linux")as f:
        result = f.read()
    if result:
        return True
    else:
        return False


def check_web_connection(url):
    try:
        requests.get(url)
    except Exception as e:
        return False
    else:
        return True


def main():
    # if not check_web_connection("https://www.baidu.com") and not check_web_connection("https://www.zhihu.com"):
    #    raise RuntimeError('please check network connection')
    if not is_clash_start():
        os.system("clash")
    t1 = multiprocessing.Process(target=watch_server)
    t2 = multiprocessing.Process(target=watch_delay)
    t1.start()
    t2.start()


if __name__ == '__main__':
    main()
