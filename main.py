# -*- coding: utf-8 -*-
from app.spot_order import SportOrder
from app.um_order import UmOrder

import time
import datetime
import schedule
import math
import json,os
from app import const as c
from app.message import send_msg
from app.lib.utils import get_server_status
from binance.spot import Spot

log = open('log.txt', 'w')

# API key/secret are required for user data endpoints
orderManager = SportOrder(c.base_asset, c.count_asset, c.quote_asset, c.binance_market)
umManager = UmOrder(c.base_asset, c.count_asset, c.quote_asset, c.binance_market)

def sendServiceInfo():
    server_time = get_server_status()
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    send_msg(f'Time: {now} \nserver Time: {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(server_time["serverTime"]) / 1000))}')

# 创建循环任务
def start():
    print("start main")
    #orderManager.begin()
    #umManager.begin()
    #清空任务
    schedule.clear()
    #创建一个按秒间隔执行任务
    # schedule.every().hours.at("04:05").do(binance_func)
    schedule.every(2).minutes.do(umManager.begin)

    schedule.every(12).hours.do(sendServiceInfo)

    while True:
        schedule.run_pending()
        time.sleep(1)


# 调试看报错运行下面，正式运行用上面
if __name__ == "__main__":
    #a = (-77.44160255 // 0.001) * 0.001
    #print(a)
    # 启动，先从币安获取交易规则， https://api.binance.com/api/v3/exchangeInfo
    start()

