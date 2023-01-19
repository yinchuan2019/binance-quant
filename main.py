# -*- coding: utf-8 -*-
from app.spot_order import SportOrder
from app.um_order import UmOrder

import time
import datetime
import schedule
import math
import json,os
from app import const as c
from app import message as send_msg
from binance.spot import Spot

log = open('log.txt', 'w')

# API key/secret are required for user data endpoints

orderManager = SportOrder(c.base_asset, c.count_asset, c.quote_asset, c.binance_market)
umManager = UmOrder(c.base_asset, c.count_asset, c.quote_asset, c.binance_market)


def begin():
    #orderManager.begin()
    umManager.begin()
    # time.sleep(5)
    # orderManager_eth.binance_func()


def sendServiceInfo():
    str = "服务正常--ok"

# 创建循环任务
def tasklist():
    print("start tasklist")
    #清空任务
    schedule.clear()
    #创建一个按秒间隔执行任务
    # schedule.every().hours.at("04:05").do(binance_func)

    #schedule.every(2).minutes.do(begin)
    schedule.every(2).minutes.do(begin)

    #schedule.every(20).minutes.do(sendServiceInfo)

    while True:
        schedule.run_pending()
        time.sleep(1)


# 调试看报错运行下面，正式运行用上面
if __name__ == "__main__":

    # 启动，先从币安获取交易规则， https://api.binance.com/api/v3/exchangeInfo
    tasklist()

    #begin()

