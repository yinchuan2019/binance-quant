# -*- coding: utf-8 -*-
from app.spot_order import SportOrder
from app.um_order import UmOrder

import time
import datetime
import math
import json,os
from app import const as c
from app.message import send_msg
from app.lib.utils import get_server_status
from apscheduler.schedulers.blocking import BlockingScheduler

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
    # 创建调度器
    scheduler = BlockingScheduler()
    # 添加时间间隔为3秒的任务
    scheduler.add_job(umManager.begin, "interval", seconds=300, id="umManager")
    scheduler.add_job(sendServiceInfo, "interval", seconds=3600*12, id="sendServiceInfo")

    # 启动调度
    scheduler.start()


# 调试看报错运行下面，正式运行用上面
if __name__ == "__main__":
    #a = (-77.44160255 // 0.001) * 0.001
    #print(a)
    # 启动，先从币安获取交易规则， https://api.binance.com/api/v3/exchangeInfo
    start()

