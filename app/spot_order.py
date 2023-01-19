import json, os, time, datetime, math
import uuid

import pandas as pd
from app.message import SendMsg
from app.moving_average import MovingAverage
import schedule
from . import const as c
from binance.spot import Spot
#import client1 as client1
client = Spot()
# Get server timestamp
print(f'server time : {client.time()}')
# API key/secret are required for user data endpoints
if c.isTest:
    client = Spot(api_key=c.api_key_test, api_secret=c.api_secret_test, base_url=c.BASE_URL_V3_TEST)
else:
    client = Spot(api_key=c.api_key, api_secret=c.api_secret)

dALines = MovingAverage()
msg = SendMsg()

class exchangeInfo(object):
    def __init__(self, dict):
        if dict is not None:
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

class SportOrder(object):
    def __init__(self, baseasset, countasset, quoteasset, market):
        # base asset 指一个交易对的交易对象，即写在靠前部分的资产名
        self.base_asset = baseasset
        # 买币时最多可用资金量
        self.base_asset_count = countasset
        # 买卖币种，例如 DOGER
        self.quote_asset = quoteasset
        # 市场，例如：现货 "SPOT"
        self.market = market
        # quote asset 指一个交易对的定价资产，即写在靠后部分资产名
        self.symbol = baseasset + quoteasset
        self.exchange_rule = None
        self.account_info = None
        # 订单信息存储路径
        self.order_info_save_path = "./" + self.symbol +"_ORDER_INFO.json"

    def begin(self):
        now = datetime.datetime.now()
        ts = now.strftime('%Y-%m-%d %H:%M:%S')
        print(f'symbol: {self.symbol} now: {ts}')
        try:
            exchange_info = client.exchange_info(self.symbol)
            self.exchange_rule = exchangeInfo(exchange_info['symbols'][0])

            # 获取K线数据
            kline_list = client.klines(self.base_asset, c.kLine_type)
            # k线数据转为 DataFrame格式
            kline_df = dALines.klines_to_data_frame(kline_list)
            # 判断交易方向
            trade = dALines.trade_stock(c.ma_min, c.ma_max, self.symbol, kline_df)

            if trade is not None:
                if trade['trade'] == 'gold':
                    print(f'IS_BUY : {trade}')
                    isToBuy = self.judge_to_buy_command(self.order_info_save_path, trade)

                    if isToBuy is True:
                        params = {"recvWindow": c.recv_window}
                        ud_account = client.account(**params)
                        balances = ud_account["balances"]
                        if balances is not None and type(balances).__name__ == 'list':
                            for balance in balances:
                                if str(balance["asset"]) == self.quote_asset:
                                    self.account_info = balance

                        # 购买，所用资金量
                        balance = self.account_info["free"]
                        #if self.base_asset_count <= base_asset_count:
                            #base_asset_count = self.base_asset_count

                        print(f'买入现货: {self.account_info["asset"]}:{self.account_info["free"]}')

                        # 查询当前价格
                        ticker_price = client.ticker_price(self.symbol)
                        # 购买量
                        count = self.format_trade_quantity(balance / ticker_price["price"])

                        order_params = {}
                        # if price is not None:
                        #     order_params["price"] = self._format(price)
                        #     order_params["timeInForce"] = "GTC"
                        #     order_params["quantity"] = '%.8f' % quantity
                        # else:
                        order_params["quoteOrderQty"] = c.count_asset
                        order_params["newClientOrderId"] = ''.join(str(uuid.uuid4()).split('-'))
                        order_params["recvWindow"] = c.recv_window
                        order_result = client.new_order(self.symbol, "BUY", "MARKET", **order_params)

                        print(f'BUY RESULT:{order_result}')
                        # order_result = client.get_order(self.symbol, new_client_order_id)

                        # 存储买入订单信息
                        if order_result is not None and "symbol" in order_result:
                            self.write_order_info(self.order_info_save_path, order_result)

                        order_result_str = self.print_order_info(order_result)
                        msg.send_msg(order_result_str)

                elif trade['trade'] == 'dead':
                    print(f'IS_SELL : {trade}')
                    dictOrder = self.read_order_info(self.order_info_save_path)

                    if dictOrder is None:
                        print(f'卖出数量为空')
                        return None
                    else:
                        ud_account = client.account()
                        balances = ud_account["balances"]
                        if balances is not None and type(balances).__name__ == 'list':
                            for balance in balances:
                                if str(balance["asset"]) == self.quote_asset:
                                    self.account_info = balance

                        # 购买，所用资金量
                        print(f'卖出现货: {self.account_info["asset"]}:{self.account_info["free"]}')

                        quantity = self.format_trade_quantity(self.account_info["free"])
                        # 查询当前价格
                        # curprice = client.get_ticker_price(self.symbol)
                        if quantity <= 0:
                            print(f'quantity:{quantity}')
                            return None
                        else:
                            # 卖出
                            order_params = {}
                            order_params["newClientOrderId"] = ''.join(str(uuid.uuid4()).split('-'))
                            order_params["quoteOrderQty"] = 10
                            res_order_sell = client.new_order(self.symbol, "SELL", "MARKET", **order_params)
                            print(f'SELL RESULT: {res_order_sell}')

                            # 清理本地订单信息
                            self.clear_order_nfo(self.order_info_save_path)
                            order_result_str = self.print_order_info(res_order_sell)
                            msg.send_msg(order_result_str)

            else:
                print("暂不执行任何交易")
                if c.isOpenSellStrategy:
                    print("开启卖出策略")
                    msgInfo = self.sell_strategy(self.order_info_save_path)

        except Exception as ex:
            err_str = "出现如下异常：%s" % ex
            print(err_str)

        finally:
            None



    # 格式化交易信息结果
    def print_order_info(self, json, isUm = False):
        str_result = ""
        if type(json).__name__ == 'dict':
            all_keys = json.keys()
            if 'symbol' in json and 'orderId' in json:
                time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() / 1000))
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

    # 根据交易规则，格式化交易量
    def format_trade_quantity(self, originalQuantity):
        minQty = float(self.exchange_rule.minQty)
        print(f'{self.symbol} 原始交易量 {str(originalQuantity)}')
        print(f'{self.symbol} 最小交易量限制 {str(minQty)}')

        if self.exchange_rule is not None and minQty > 0:
            newQuantity = (float(originalQuantity)//minQty) * minQty
        else:
            newQuantity = math.floor(float(originalQuantity))

        print(f'{self.symbol} 交易量格式化 {str(newQuantity)}')
        return newQuantity



    #  执行卖出
    def do_sell_func(self, symbol, quantity, curprice):
        print("马上卖出 " + str(symbol) + " " + str(quantity) + " 个，单价：" + str(curprice))

        # 如果总价值小于10
        if (quantity * curprice) < 10:
            quantity = self.format_trade_quantity(11.0 / curprice)
            if (quantity * curprice) < 10:
                quantity = self.format_trade_quantity(13.0 / curprice)
                if (quantity * curprice) < 10:
                    quantity = self.format_trade_quantity(16.0 / curprice)
                    if (quantity * curprice) < 10:
                        quantity = self.format_trade_quantity(20.0 / curprice)

        # 卖出
        sell_result = client.sell(symbol, quantity, curprice)
        print("出售部分结果：")
        print("量：" + str(quantity) + ", 价格：" + str(curprice) + ", 总价值：" + str(quantity * curprice))
        print(sell_result)
        order_result_str = self.print_order_info(sell_result)
        msgInfo = "卖出结果：\n" + str(order_result_str)

        return msgInfo

    # 分批出售策略
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
            print("当前 " + str(self.symbol) + " 价格：" + str(curprice))
            # 查询当前资产
            asset_coin = client.get_spot_asset_by_symbol(self.quote_asset)
            print(self.quote_asset + " 资产2：")
            print(asset_coin)

            if "sellStrategy3" in dictOrder:
                print("sellStrategy--sellStrategy3--1")
                tmpSellStrategy = dictOrder['sellStrategy3']
                print("买入价格：" + str(buyPrice) + " * " + str(tmpSellStrategy) + " = " + str(
                    buyPrice * tmpSellStrategy['profit']) + " 和 当前价格：" + str(curprice) + " 比较")
                if buyPrice * tmpSellStrategy['profit'] <= curprice:
                    print("sellStrategy--sellStrategy3--2")

                    quantity = self.format_trade_quantity(asset_coin["free"] * tmpSellStrategy['sell'])
                    # 卖出
                    msgInfo = msgInfo + self.do_sell_func(self.symbol, quantity, curprice)
                    del dictOrder['sellStrategy3']
                    self.write_order_info(filePath, dictOrder)
                    dictOrder = self.read_order_info(filePath)
                    print("部分卖出--sellStrategy3")

            if "sellStrategy2" in dictOrder:
                tmpSellStrategy = dictOrder['sellStrategy2']
                print("sellStrategy--sellStrategy2--1")
                print("买入价格：" + str(buyPrice) + " * " + str(tmpSellStrategy) + " = " + str(
                    buyPrice * tmpSellStrategy['profit']) + " 和 当前价格：" + str(curprice) + " 比较")

                if buyPrice * tmpSellStrategy['profit'] <= curprice:
                    print("sellStrategy--sellStrategy2--2")

                    quantity = self.format_trade_quantity(asset_coin["free"] * tmpSellStrategy['sell'])
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

                    quantity = self.format_trade_quantity(asset_coin["free"] * tmpSellStrategy['sell'])
                    # 卖出
                    msgInfo = msgInfo + self.do_sell_func(self.symbol, quantity, curprice)
                    del dictOrder['sellStrategy1']
                    self.do_sell_func(filePath, dictOrder)
                    dictOrder = self.read_order_info(filePath)
                    print("部分卖出--sellStrategy1")

        return msgInfo
if __name__ == '__main__':
    #asset_coin = client1.account()
    print(f'server time : {client.time()}')
    print(int(round(time.time() * 1000)))
    #order_params ={}
    #order_params["recvWindow"] = c.recv_window

    client.account()

