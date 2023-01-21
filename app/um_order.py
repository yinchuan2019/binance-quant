import json, os, time, datetime, math
import uuid
import pandas as pd
from app.message import send_msg
from app.moving_average import MovingAverage
import schedule
from . import const as c
from binance.um_futures import UMFutures
from app.lib.utils import format_trade_quantity


# API key/secret are required for user data endpoints
if c.isTest:
    client = UMFutures(key=c.api_key_future_test, secret=c.api_secret_future_test, base_url=c.FUTURE_URL_TEST)
else:
    client = UMFutures(key=c.api_key, secret=c.api_secret)

dALines = MovingAverage()

class UmOrder(object):
    def __init__(self, baseasset, countasset, quoteasset, market):
        # base asset 指一个交易对的交易对象，即写在靠前部分的资产名
        self.base_asset = baseasset
        # 买币时最多可用资金量
        self.base_asset_count = countasset
        # 买卖币种，例如 USDT
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
        ts = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f'SYMBOL: {self.symbol} 时间: {ts}')
        try:
            exchange_info = client.exchange_info()
            if exchange_info is not None and type(exchange_info['symbols']).__name__ == 'list':
                for info in exchange_info['symbols']:
                    if info["symbol"] == self.symbol:
                        self.exchange_rule = exchangeInfo(info)

            # 获取K线数据
            kline_list = client.klines(self.symbol, c.kLine_type)
            # k线数据转为 DataFrame格式
            kline_df = dALines.klines_to_data_frame(kline_list)
            # 判断交易方向
            trade = dALines.trade_stock(c.ma_min, c.ma_max, self.symbol, kline_df)

            if trade is not None:
                # 金叉
                ud_account = client.account()
                if trade['trade'] == 'gold':
                    print(f'start gold--> : {trade}')
                    #isToBuy = self.judge_to_buy_command(self.order_info_save_path, trade)
                    #合约账户没有开通双向持仓的话，BUY就是做多和平空，SELL就是做空和平多
                    ##平空
                    order_result = self.sell(ud_account, "BUY")
                    print(f'gold sell order_result:{order_result}')
                    ##买入做多
                    order_result = self.buy(ud_account, "BUY")
                    print(f'gold buy order_result:{order_result}')

                    # 存储买入订单信息
                    #if order_result is not None and "symbol" in order_result:
                    #self.write_order_info(self.order_info_save_path, order_result)
                    #order_result["cummulativeQuoteQty"] = balance
                    order_result_str = self.print_order_info(order_result)
                    send_msg(order_result_str)
                # 死叉
                elif trade['trade'] == 'dead':
                    print(f'start dead--> : {trade}')
                    ##平多
                    order_result = self.sell(ud_account, "SELL")
                    print(f'dead sell order_result:{order_result}')
                    ##买入做空
                    order_result = self.buy(ud_account, "SELL")
                    print(f'dead buy order_result:{order_result}')

                    # 清理本地订单信息
                    #self.clear_order_nfo(self.order_info_save_path)
                    order_result_str = self.print_order_info(order_result)
                    send_msg(order_result_str)
            else:
                print("暂不执行任何交易")
                if c.isOpenSellStrategy:
                    print("开启卖出策略")
                    #msgInfo = self.sell_strategy(self.order_info_save_path)

        except Exception as ex:
            print("出现如下异常：%s" % ex)
        finally:
            None

    def buy(self, ud_account, flag):
        assets = ud_account["assets"]
        if assets is not None and type(assets).__name__ == 'list':
            for asset in assets:
                if str(asset["asset"]) == self.quote_asset:
                    self.account_info = asset

        # 购买，所用资金量
        balance = self.account_info["availableBalance"]
        # if self.base_asset_count <= base_asset_count:
        # base_asset_count = self.base_asset_count

        print(f'买入合约: {self.account_info["asset"]}:{self.account_info["availableBalance"]}')

        # 查询当前价格
        ticker_price = client.ticker_price(self.symbol)
        # 购买量
        count = format_trade_quantity(self.symbol, float(balance) / float(ticker_price["price"]), float(self.exchange_rule.minQty)) * 10

        order_params = {}
        # if price is not None:
        #     order_params["price"] = self._format(price)
        #     order_params["timeInForce"] = "GTC"
        #     order_params["quantity"] = '%.8f' % quantity
        # else:
        if count * float(ticker_price["price"]) < 5:
            print(f'订单的名义价值小于5')
            return None
        else:
            order_params["quantity"] = count
            # order_params["newClientOrderId"] = ''.join(str(uuid.uuid4()).split('-'))
            order_params["recvWindow"] = c.recv_window
            order_result = client.new_order(self.symbol, flag, "MARKET", **order_params)

            # order_result = client.get_order(self.symbol, new_client_order_id)
        return order_result

    def sell(self, ud_account, flag):
        positions = ud_account["positions"]
        if positions is not None and type(positions).__name__ == 'list':
            for position in positions:
                if str(position["symbol"]) == self.symbol:
                    self.account_info = position
        # dictOrder = self.read_order_info(self.order_info_save_path)
        #order_info = client.get_open_orders(self.symbol, self.read_order_info())

        # 购买，所用资金量
        print(f'卖出合约: {self.account_info["symbol"]},数量:{self.account_info["notional"]}')

        # quantity = self.format_trade_quantity(float(self.account_info["free"]))
        curprice = client.ticker_price(self.symbol)

        # 卖出
        order_params = {}
        order_params["newClientOrderId"] = ''.join(str(uuid.uuid4()).split('-'))
        # order_params["closePosition"] = True
        # order_params["stopPrice"] = curprice["price"]
        order_params["reduceOnly"] = True
        order_params["quantity"] = format_trade_quantity(self.symbol, abs(float(self.account_info["notional"])), float(self.exchange_rule.minQty))
        order_result = client.new_order(self.symbol, flag, "MARKET", **order_params)
        return order_result

    # 格式化交易信息结果
    def print_order_info(self, json):
        str_result = ""
        if type(json).__name__ == 'dict':
            all_keys = json.keys()
            if 'symbol' in json and 'orderId' in json:
                time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                str_result = str_result + "时间：" + str(time_str) + "\n"
                str_result = str_result + "方向：" + str(json['side']) + "\n"
                str_result = str_result + "币种：" + str(json['symbol']) + "\n"
                #str_result = str_result + "价格：" + str(json['fills']) + "\n"
                #str_result = str_result + "总价：" + str(json['cummulativeQuoteQty']) + "\n"
                str_result = str_result + "数量：" + str(json['origQty']) + "\n"
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
            # print(f'读取--买入信息:{data}')
            return data

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
    def write_order_info(self, filePath, data):
        self.clear_order_nfo(filePath)
        with open(filePath, 'w') as f:
            json.dump(data, f)


    def writeOrderInfoWithSellStrategy(self,filePath, dictObj):

        if c.isOpenSellStrategy:
            dictObj["sellStrategy1"] = c.sellStrategy1
            dictObj["sellStrategy2"] = c.sellStrategy2
            dictObj["sellStrategy3"] = c.sellStrategy3

        self.writeOrderInfo(filePath, dictObj)

    #  执行卖出
    # def do_sell_func(self, symbol, quantity, curprice):
    #     print("马上卖出 " + str(symbol) + " " + str(quantity) + " 个，单价：" + str(curprice))
    #
    #     # 如果总价值小于10
    #     if (quantity * curprice) < 10:
    #         quantity = self.format_trade_quantity(11.0 / curprice)
    #         if (quantity * curprice) < 10:
    #             quantity = self.format_trade_quantity(13.0 / curprice)
    #             if (quantity * curprice) < 10:
    #                 quantity = self.format_trade_quantity(16.0 / curprice)
    #                 if (quantity * curprice) < 10:
    #                     quantity = self.format_trade_quantity(20.0 / curprice)
    #
    #     # 卖出
    #     sell_result = client.sell(symbol, quantity, curprice)
    #     print("出售部分结果：")
    #     print("量：" + str(quantity) + ", 价格：" + str(curprice) + ", 总价值：" + str(quantity * curprice))
    #     print(sell_result)
    #     order_result_str = self.print_order_info(sell_result)
    #     msgInfo = "卖出结果：\n" + str(order_result_str)
    #
    #     return msgInfo
    #
    # # 分批出售策略
    # def sell_strategy(self, filePath):
    #     msgInfo = ""
    #     dictOrder = self.read_order_info(filePath)
    #     if dictOrder is None:
    #         return msgInfo
    #
    #     # 读取上次买入的价格
    #     buyPrice = self.price_of_previous_order(self.order_info_save_path)
    #     if buyPrice > 0:
    #         # 查询当前价格
    #         curprice = client.get_ticker_price(self.symbol)
    #         print("当前 " + str(self.symbol) + " 价格：" + str(curprice))
    #         # 查询当前资产
    #         asset_coin = client.get_spot_asset_by_symbol(self.quote_asset)
    #         print(self.quote_asset + " 资产2：")
    #         print(asset_coin)
    #
    #         if "sellStrategy3" in dictOrder:
    #             print("sellStrategy--sellStrategy3--1")
    #             tmpSellStrategy = dictOrder['sellStrategy3']
    #             print("买入价格：" + str(buyPrice) + " * " + str(tmpSellStrategy) + " = " + str(
    #                 buyPrice * tmpSellStrategy['profit']) + " 和 当前价格：" + str(curprice) + " 比较")
    #             if buyPrice * tmpSellStrategy['profit'] <= curprice:
    #                 print("sellStrategy--sellStrategy3--2")
    #
    #                 quantity = self.format_trade_quantity(float(asset_coin["free"]) * tmpSellStrategy['sell'])
    #                 # 卖出
    #                 msgInfo = msgInfo + self.do_sell_func(self.symbol, quantity, curprice)
    #                 del dictOrder['sellStrategy3']
    #                 self.write_order_info(filePath, dictOrder)
    #                 dictOrder = self.read_order_info(filePath)
    #                 print("部分卖出--sellStrategy3")
    #
    #         if "sellStrategy2" in dictOrder:
    #             tmpSellStrategy = dictOrder['sellStrategy2']
    #             print("sellStrategy--sellStrategy2--1")
    #             print("买入价格：" + str(buyPrice) + " * " + str(tmpSellStrategy) + " = " + str(
    #                 buyPrice * tmpSellStrategy['profit']) + " 和 当前价格：" + str(curprice) + " 比较")
    #
    #             if buyPrice * tmpSellStrategy['profit'] <= curprice:
    #                 print("sellStrategy--sellStrategy2--2")
    #
    #                 quantity = self.format_trade_quantity(float(asset_coin["free"]) * tmpSellStrategy['sell'])
    #                 # 卖出
    #                 msgInfo = msgInfo + self.do_sell_func(self.symbol, quantity, curprice)
    #                 del dictOrder['sellStrategy2']
    #                 self.write_order_info(filePath, dictOrder)
    #                 dictOrder = self.read_order_info(filePath)
    #                 print("部分卖出--sellStrategy2")
    #
    #         if "sellStrategy1" in dictOrder:
    #             tmpSellStrategy = dictOrder['sellStrategy1']
    #             print("sellStrategy--sellStrategy1--1")
    #             print("买入价格：" + str(buyPrice) + " * " + str(tmpSellStrategy) + " = " + str(
    #                 buyPrice * tmpSellStrategy['profit']) + " 和 当前价格：" + str(curprice) + " 比较")
    #
    #             if buyPrice * tmpSellStrategy['profit'] <= curprice:
    #                 print("sellStrategy--sellStrategy1--2")
    #
    #                 quantity = self.format_trade_quantity(float(asset_coin["free"]) * tmpSellStrategy['sell'])
    #                 # 卖出
    #                 msgInfo = msgInfo + self.do_sell_func(self.symbol, quantity, curprice)
    #                 del dictOrder['sellStrategy1']
    #                 self.do_sell_func(filePath, dictOrder)
    #                 dictOrder = self.read_order_info(filePath)
    #                 print("部分卖出--sellStrategy1")
    #
    #     return msgInfo

class exchangeInfo(object):
    def __init__(self, dict):
        if dict is not None:
            self.symbol = dict['symbol']
            self.baseAsset = dict['baseAsset']
            self.baseAssetPrecision = dict['baseAssetPrecision']
            self.quoteAsset = dict['quoteAsset']
            self.quotePrecision = dict['quotePrecision']
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


if __name__ == '__main__':
    #asset_coin = client1.account()
    print(f'server time : {client.time()}')
    print(int(round(time.time() * 1000)))
    #order_params ={}
    #order_params["recvWindow"] = c.recv_window

    client.account()

