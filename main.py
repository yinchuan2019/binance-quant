# -*- coding: utf-8 -*-
from app.spot_order import SportOrder

import time
import datetime
import schedule
import math
import json,os
from app import const as c
from app import message as send_msg
from binance.spot import Spot

log = open('log.txt', 'w')

client = Spot()
# Get server timestamp
print(f'client time : {client.time()}')
# Get klines of BTCUSDT at 1m interval
#print(client.klines(c.base_asset + c.quote_asset, "3m"))

# API key/secret are required for user data endpoints

orderManager = SportOrder(c.base_asset, c.count_asset, c.quote_asset, c.binance_market)

#orderManager_eth = OrderManager("USDT", 100, "ETH", c.binance_market)


# 发送消息通知
def sendInfoToDingDing(message, isDefaultToken):
    # 记录执行时间
    now = datetime.datetime.now()
    ts = now.strftime('%Y-%m-%d %H:%M:%S')
    message = str(ts) + "\n" + message
    send_msg.send_msg(message)


def begin():
    orderManager.begin()
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

