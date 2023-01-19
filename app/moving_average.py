#coding=utf-8

import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from app import const as c
import datetime
plt.close()
class MovingAverage:

    def __init__(self):
        pass

    # [
    #     1499040000000, // 开盘时间
    # "0.01634790", // 开盘价
    # "0.80000000", // 最高价
    # "0.01575800", // 最低价
    # "0.01577100", // 收盘价(当前K线未结束的即为最新价)
    # "148976.11427815", // 成交量
    # 1499644799999, // 收盘时间
    # "2434.19055334", // 成交额
    # 308, // 成交笔数
    # "1756.87402397", // 主动买入成交量
    # "28.46694368", // 主动买入成交额
    # "17928899.62484339" // 请忽略该参数
    # ]

    def klines_to_data_frame(self, klines):

        if klines is None:
            print("klines_to_data_frame is None.")
            return None

        openTimeList = []
        openPriceList = []
        maxPriceList = []
        minPriceList = []
        closePriceList = []
        dealVoluMeList = []
        closeTimeList = []
        dealTotalMoneyList = []
        dealCountList = []
        dealBuyVolumeList = []
        dealBuyTotalMoneyList = []


        for kline in klines:
            if (type(kline)).__name__ == 'list':
                openTimeList.append(self.stampToTime(kline[0]))
                openPriceList.append(kline[1])
                maxPriceList.append(kline[2])
                minPriceList.append(kline[3])
                closePriceList.append(kline[4])
                dealVoluMeList.append(kline[5])
                closeTimeList.append(self.stampToTime(kline[6]))
                dealTotalMoneyList.append(kline[7])
                dealCountList.append(kline[8])
                dealBuyVolumeList.append(kline[9])
                dealBuyTotalMoneyList.append(kline[10])
            else:
                print("error: kline is not list.")

        kLinesDict = {"openTime": openTimeList, "openPrice": openPriceList, "maxPrice": maxPriceList, "minPrice":minPriceList, "closePrice":closePriceList, "closeTime":closeTimeList}

        klines_df = pd.DataFrame(kLinesDict)

        # for index, row in klines_df.iterrows():
        #     print(str(row["openTime"]) + "\t" +row["openPrice"] + "\t" +row["maxPrice"] + "\t"+row["minPrice"] + "\t"+row["closePrice"] + "\t"+str(row["closeTime"]) + "\t")

        return klines_df


    def read_json_from_file(self, filePath):
        # Opening JSON file
        f = open(filePath, )
        data = json.load(f)
        f.close()
        # Iterating through the json
        # list
        print("readJsonFromFile =")
        if (type(data)).__name__ == 'list':
            for i in data:
                print(i)
            # Closing file
            return data

        return None


    def trade_stock(self, ma_min, ma_max, symbol, df):

        print(f'{symbol} {c.kLine_type} 均线: {ma_min} 和 {ma_max}')

        df[["openTime"]] = df[["openTime"]].astype(str)  # int类型 转换 成str类型，否则会被当做时间戳使用，造成时间错误
        df['openTime'] = pd.to_datetime(df['openTime'])

        #df.set_index('openTime', inplace=True)
        df = df.sort_values('openTime', ascending=True)
        # 求出均线
        df['maMin'] = df['closePrice'].rolling(ma_min).mean()
        df['maMax'] = df['closePrice'].rolling(ma_max).mean()
        df[['closePrice', 'maMin', 'maMax']].plot()  # 绘图
        # plt.show()

        # todo
        # df = df[ma_y_line:]  # 这个切片很重要，否则会报错，因为数据不匹配
        # 因为 ma_x_line < ma_y_line ,所以均线 切到 ma_y_line
        # maX = maX[ma_y_line:]  # 切片，与 df 数据条数保持一致
        # maY = maY[ma_y_line:]  # 切片，与 df 数据条数保持一致

        # print("df数据行数=" +str(len(df)))
        # print(df)
        # 从尾部，删除1行
        # df.drop(df.tail(1).index, inplace=True)

        # print("tmp_last_df--数据切片：")
        # for index, row in df.iterrows():
        # print(str(row["openTime"]) + "\t" +row["openPrice"] + "\t" +row["maxPrice"] + "\t"+row["minPrice"] + "\t"+row["closePrice"] + "\t"+str(row["closeTime"]) + "\t")

        last_row = df.iloc[-1, :]
        print(f'last_row:\n {last_row.to_string()}')
        bool1 = df['maMin'] < df['maMax']  # 得到 bool 类型的 Series
        bool2 = df['maMin'] > df['maMax']

        death_date = df[bool1 & bool2.shift(1)]['openTime']  # 死叉日 &：两个为真才为真
        # print(f'death_date\n {death_date}')
        golden_date = df[~(bool1 | bool2.shift(1))]['openTime'] # 金叉日 &：两个为假才为假  比较运算符
        # print(f'golden_date\n {golden_date}')


        if last_row['openTime'] == death_date.sort_values().tail(1).iloc[0]:
            #sell
            return {'trade': 'dead', 'openTime': last_row['openTime'], 'closePrice': last_row['closePrice']}

        if last_row['openTime'] == golden_date.sort_values().tail(1).iloc[0]:
            #buy
            return {'trade': 'dead', 'openTime': last_row['openTime'], 'closePrice': last_row['closePrice']}
        return {'trade': 'dead', 'openTime': last_row['openTime'], 'closePrice': last_row['closePrice']}

        # for i in range(0, len(death_date)):
        #
        #     open_time = death_date.index[i]
        #     close_price = float(df.loc[open_time]['closePrice'])  # 收盘价
        #     close_time = df.loc[open_time]['closeTime']  # 收盘时间
        #     is_right_time = self.judge_current_time(str(open_time), str(close_time))
        #
        #     str_date = str(time)
        #     print(f'sell startTime:{str_date}, isRightTime:{is_right_time},close_price:{str(round(close_price, 8))}')
        #     if is_right_time:
        #         print("release_trade_stock---buy")
        #         return "sell,"+str(open_time)
        #
        # for i in range(0, len(death_date)):
        #
        #     open_time = death_date.index[i]
        #     close_price = float(df.loc[open_time]['closePrice'])  # 收盘价
        #     close_time = df.loc[open_time]['closeTime']  # 收盘时间
        #     is_right_time = self.judge_current_time(str(open_time), str(close_time))
        #
        #     str_date = str(time)
        #     print(f'sell startTime:{str_date}, isRightTime:{is_right_time},close_price:{str(round(close_price, 8))}')
        #     if is_right_time:
        #         print("release_trade_stock---buy")
        #         return "sell," + str(open_time)
        #
        # print("release_trade_stock---None")
        #





    # 判断当前时间，是否在k线时间范围内
    def judge_current_time(self, openTime, closeTime):

        dateTime_interval = pd.to_datetime(closeTime) - pd.to_datetime(openTime)

        seconds_interval = dateTime_interval.seconds # int类型，秒数
        # print("seconds_interval 的类型=")
        # print(type(seconds_interval))
        # print(seconds_interval)

        now = int(round((time.time() - seconds_interval) * 1000))

        now02 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(now / 1000))
        print(now02)
        if now02 >= openTime and now02 <= closeTime:
            # print("成功---"+openTime+"\t"+now02+"\t"+closeTime)
            return True
        else:
            # print("失败---"+openTime+"\t"+now02+"\t"+closeTime)
            return False


    def stampToTime(self, stamp):

        # now = int(round(time.time() * 1000))
        stamp_int = int(stamp)

        now02 = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stamp_int / 1000))

        # mytime = datetime.datetime.fromtimestamp(stamp/1000)
        # # print(stamp)
        # print("mytime type is : " + type(now02).__name__)
        return now02

