import json, os, time, datetime, math
import uuid

import pandas as pd
from app.message import SendMsg
from app.client import Client
from app.moving_average import MovingAverage
import schedule
from . import const as c

client = Client(c.api_key, c.api_secret)

dALines = MovingAverage()

msg = SendMsg()

class exchangeInfo(object):
    def __init__(self, dict):
        if dict is not None and 'symbol' in dict:
            self.symbol = dict['symbol']
            self.baseAsset = dict['baseAsset']
            self.baseAssetPrecision = dict['baseAssetPrecision']
            self.quoteAsset = dict['quoteAsset']
            self.quoteAssetPrecision = dict['quoteAssetPrecision']

            filters = dict['filters']
            for filter in filters:
                if filter['filterType'] == 'PRICE_FILTER':
                    # "minPrice": "0.00001000",
                    # "maxPrice": "1000.00000000",
                    # "tickSize": "0.00001000"
                    self.minPrice = filter['minPrice']
                    self.maxPrice = filter['maxPrice']
                    self.tickSize = filter['tickSize']

                if filter['filterType'] == 'LOT_SIZE':
                    # "minQty": "0.10000000",
                    # "maxQty": "9000000.00000000",
                    # "stepSize": "0.10000000"
                    self.minQty = filter['minQty']
                    self.maxQty = filter['maxQty']
                    self.stepSize = filter['stepSize']




class OrderManager(object):

    def __init__(self, baseasset, countasset, quoteasset, market):
        # 基础币，例如USDT
        self.base_asset = baseasset
        # 买币时最多可用资金量
        self.base_asset_count = countasset
        # 买卖币种，例如 DOGER
        self.quote_asset = quoteasset
        # 市场，例如：现货 "SPOT"
        self.market = market
        # 交易符号，例如"DOGEUSDT"
        self.symbol = baseasset + quoteasset
        self.exchange_rule = None
        # 订单信息存储路径
        self.order_info_save_path = "./" + self.symbol +"_ORDER_INFO.json"

    def set_exchange_info(self, symbol):
        if self.exchange_rule is None:
            dict = client.exchangeInfo()
            if dict is not None and 'symbols' in dict:
                symbol_list = dict['symbols']
                for tmp_symbol in symbol_list:
                    if tmp_symbol['symbol'] == symbol:
                        self.exchangeRule = exchangeInfo(tmp_symbol)
                        break
        # return self.exchangeRule



    #  执行卖出
    def do_sell_func(self,symbol ,quantity, curprice):
        print("马上卖出 " + str(symbol)+" "+ str(quantity)+ " 个，单价："+str(curprice))

        #如果总价值小于10
        if (quantity*curprice)<10:
            quantity = self.format_trade_quantity(11.0/curprice)
            if (quantity * curprice) < 10:
                quantity = self.format_trade_quantity(13.0 / curprice)
                if (quantity * curprice) < 10:
                    quantity = self.format_trade_quantity(16.0 / curprice)
                    if (quantity * curprice) < 10:
                        quantity = self.format_trade_quantity(20.0 / curprice)

        # 卖出
        sell_result = client.sell(symbol, quantity, curprice)
        print("出售部分结果：")
        print("量："+str(quantity)+", 价格："+str(curprice)+", 总价值："+str(quantity*curprice))
        print(sell_result)
        order_result_str = self.print_order_info(sell_result)
        msgInfo = "卖出结果：\n" + str(order_result_str)

        return msgInfo

    #分批出售策略
    def sell_strategy(self, filePath):
        msgInfo = ""
        dictOrder = self.read_order_info(filePath)
        if dictOrder is None:
            return msgInfo

        # 读取上次买入的价格
        buyPrice = self.price_of_previous_order(self.order_info_save_path)
        if buyPrice > 0:
            # 查询当前价格
            curprice = client.get_ticker_price(self.symbol)
            print("当前 "+str(self.symbol)+" 价格："+str(curprice))
            #查询当前资产
            asset_coin = client.get_spot_asset_by_symbol(self.quote_asset)
            print(self.quote_asset + " 资产2：")
            print(asset_coin)

            if "sellStrategy3" in dictOrder:
                print("sellStrategy--sellStrategy3--1")
                tmpSellStrategy = dictOrder['sellStrategy3']
                print("买入价格："+str(buyPrice) + " * " + str(tmpSellStrategy) + " = " + str(buyPrice * tmpSellStrategy['profit'])+" 和 当前价格：" + str(curprice)+" 比较")
                if buyPrice * tmpSellStrategy['profit'] <= curprice:
                    print("sellStrategy--sellStrategy3--2")

                    quantity = self.format_trade_quantity(float(asset_coin["free"])*tmpSellStrategy['sell'])
                    # 卖出
                    msgInfo= msgInfo + self.do_sell_func(self.symbol,quantity,curprice)
                    del dictOrder['sellStrategy3']
                    self.write_order_info(filePath, dictOrder)
                    dictOrder = self.read_order_info(filePath)
                    print("部分卖出--sellStrategy3")

            if "sellStrategy2" in dictOrder:
                tmpSellStrategy = dictOrder['sellStrategy2']
                print("sellStrategy--sellStrategy2--1")
                print("买入价格："+str(buyPrice) + " * " + str(tmpSellStrategy) + " = " + str(buyPrice * tmpSellStrategy['profit'])+" 和 当前价格：" + str(curprice)+" 比较")

                if buyPrice * tmpSellStrategy['profit'] <= curprice:
                    print("sellStrategy--sellStrategy2--2")

                    quantity = self.format_trade_quantity(float(asset_coin["free"]) * tmpSellStrategy['sell'])
                    # 卖出
                    msgInfo = msgInfo + self.do_sell_func(self.symbol, quantity, curprice)
                    del dictOrder['sellStrategy2']
                    self.write_order_info(filePath, dictOrder)
                    dictOrder = self.read_order_info(filePath)
                    print("部分卖出--sellStrategy2")

            if "sellStrategy1" in dictOrder:
                tmpSellStrategy = dictOrder['sellStrategy1']
                print("sellStrategy--sellStrategy1--1")
                print("买入价格：" + str(buyPrice) + " * " + str(tmpSellStrategy) + " = " + str(
                    buyPrice * tmpSellStrategy['profit']) + " 和 当前价格：" + str(curprice) + " 比较")

                if buyPrice * tmpSellStrategy['profit'] <= curprice:
                    print("sellStrategy--sellStrategy1--2")

                    quantity = self.format_trade_quantity(float(asset_coin["free"]) * tmpSellStrategy['sell'])
                    # 卖出
                    msgInfo = msgInfo + self.do_sell_func(self.symbol, quantity, curprice)
                    del dictOrder['sellStrategy1']
                    self.do_sell_func(filePath, dictOrder)
                    dictOrder = self.read_order_info(filePath)
                    print("部分卖出--sellStrategy1")

        return msgInfo



    # 格式化交易信息结果
    def print_order_info(self, json):
        str_result = ""
        if type(json).__name__ == 'dict':
            all_keys = json.keys()
            if 'symbol' in json and 'orderId' in json:

                time_local = time.localtime(1673968939082 / 1000)
                time_str = time.strftime('%Y-%m-%d %H:%M:%S', time_local)
                str_result = str_result + "时间：" + str(time_str) + "\n"
                str_result = str_result + "币种：" + str(json['symbol']) + "\n"
                str_result = str_result + "价格：" + str(json['fills']) + "\n"
                str_result = str_result + "总价：" + str(json['cummulativeQuoteQty']) + "\n"
                str_result = str_result + "数量：" + str(json['origQty']) + "\n"
                str_result = str_result + "方向：" + str(json['side']) + "\n"
            else:
                str_result = str(json)
        else:
            str_result = str(json)

        return str_result

    # 读取本地存储的买入订单信息
    def read_order_info(self, filePath):
        if os.path.exists(filePath) is False:
            return None

        with open(filePath, 'r') as f:
            data = json.load(f)
            print(f'读取--买入信息:{data}')
            if 'symbol' in data and 'orderId' in data and 'price' in data:
                return data
            else:
                return None

    # 比较本次买入提示的str是否重复
    def judge_to_buy_command(self, filePath, trade):
        orderDict = self.read_order_info(filePath)

        if orderDict is None:
            return True # 购买

        # if "toBuy" in orderDict:
        #     if orderDict["BUY"] == trade['BUY']:
        #         print(f'本次购买时间是{str(trade["openTime"])}重复，不执行购买')
        #         return False #不执行购买，因为重复

        return True


    # 获取 上次买入订单中的价格Price
    def price_of_previous_order(self, filePath):
        dataDict = self.read_order_info(filePath)
        thePrice = 0.0

        if dataDict is not None and 'price' in dataDict:
            thePrice = float(dataDict['price'])

        return thePrice

    # 清理 本地存储的买入订单信息
    def clear_order_nfo(self, filePath):
        if os.path.exists(filePath) is True:
            os.remove(filePath)
            print("清理订单信息")

    # 存储 买入订单信息
    def write_order_info(self, filePath, dictObj):
        self.clear_order_nfo(filePath)
        with open(filePath, 'w') as f:
            json.dump(dictObj, f)


    def writeOrderInfoWithSellStrategy(self,filePath, dictObj):

        if c.isOpenSellStrategy:
            dictObj["sellStrategy1"] = c.sellStrategy1
            dictObj["sellStrategy2"] = c.sellStrategy2
            dictObj["sellStrategy3"] = c.sellStrategy3

        self.writeOrderInfo(filePath, dictObj)


    # 获取K线列表
    def get_kline(self, symbol, timeInterval = '15m'):
        # 结束时间
        millis_stamp = int(round(time.time() * 1000))

        # 如何处理虚假买点和虚假卖点，1000条数据中，第一条可能产生虚假的买点和卖点
        kline_json = client.get_klines(symbol, timeInterval, 1000, None, millis_stamp)
        if type(kline_json).__name__ == 'list':
            return kline_json
        else:
            return None

    # 根据交易规则，格式化交易量
    def format_trade_quantity(self, originalQuantity):
        minQty = float(self.exchangeRule.minQty)
        print(f'{self.symbol} 原始交易量 {str(originalQuantity)}')
        print(f'{self.symbol} 最小交易量限制 {str(minQty)}')

        if self.exchangeRule is not None and minQty > 0:
            newQuantity = (originalQuantity//minQty) * minQty
        else:
            newQuantity = math.floor(originalQuantity)

        print(f'{self.symbol} 交易量格式化 {str(newQuantity)}')
        return newQuantity

    def begin(self):
        now = datetime.datetime.now()
        ts = now.strftime('%Y-%m-%d %H:%M:%S')
        print(f'symbol: {self.symbol} now: {ts}')
        try:
            self.set_exchange_info(self.symbol)
            # 获取K线数据
            kline_list = self.get_kline(self.symbol, c.kLine_type)
            # k线数据转为 DataFrame格式
            kline_df = dALines.klines_to_data_frame(kline_list)
            # 判断交易方向
            trade = dALines.trade_stock(c.ma_min, c.ma_max, self.symbol, kline_df)

            if trade is not None:
                if trade['trade'] == 'BUY':
                    print(f'BUY : {trade}')
                    isToBuy = self.judge_to_buy_command(self.order_info_save_path, trade)

                    if isToBuy is True:
                        # base_asset = "USDT"
                        quote_asset = client.get_spot_asset_by_symbol(self.quote_asset)
                        print(f'{self.base_asset} 资产: {str(quote_asset)}')

                        # 购买，所用资金量
                        base_asset_count = float(quote_asset["free"])
                        #if self.base_asset_count <= base_asset_count:
                            #base_asset_count = self.base_asset_count

                        print(f'现货资产 {quote_asset}:{str(base_asset_count)}')
                        # 查询当前价格
                        curprice = client.get_ticker_price(self.symbol)
                        # 购买量
                        count = self.format_trade_quantity(base_asset_count / float(curprice))

                        s_uuid = ''.join(str(uuid.uuid4()).split('-'))
                        order_result = client.buy(self.symbol, count, c.count_asset, None, s_uuid)
                        print(f'BUY RESULT:{order_result}')
                        # order_result = client.get_order(self.symbol, new_client_order_id)

                        # 存储买入订单信息
                        if order_result is not None and "symbol" in order_result:
                            self.write_order_info(self.orderInfoSavePath, order_result)

                        order_result_str = self.print_order_info(order_result)
                        msg.sendMsg(order_result_str)

                elif trade['trade'] == 'SELL':
                    print(f'SELL : {trade}')
                    dictOrder = self.read_order_info(self.orderInfoSavePath)

                    if dictOrder is None:
                        print(f'卖出数量为空')
                        return None
                    else:

                        asset_coin = client.get_spot_asset_by_symbol(self.quote_asset)
                        quantity = self.format_trade_quantity(float(asset_coin["free"]))
                        # 查询当前价格
                        # curprice = client.get_ticker_price(self.symbol)

                        if quantity <= 0:
                            print(f'quantity:{quantity}')
                            return None
                        else:
                            # 卖出
                            s_uuid = ''.join(str(uuid.uuid4()).split('-'))
                            res_order_sell = client.sell(self.symbol, None, c.count_asset, None,  s_uuid)
                            print(f'SELL RESULT: {res_order_sell}')

                            # 清理本地订单信息
                            self.clear_order_nfo(self.orderInfoSavePath)
                            order_result_str = self.print_order_info(res_order_sell)
                            msg.sendMsg(order_result_str)


            else:
                print("暂不执行任何交易")
                if c.isOpenSellStrategy:
                    print("开启卖出策略")
                    msgInfo = self.sellStrategy(self.orderInfoSavePath)

        except Exception as ex:
            err_str = "出现如下异常：%s" % ex
            print(err_str)

        finally:
            None
