# -*- coding: utf-8 -*
import uuid

import requests, time, hmac, hashlib
try:
    from urllib import urlencode
# python3
except ImportError:
    from urllib.parse import urlencode

from app import const as c


class Client(object):

    def __init__(self, key, secret):
        self.key = key
        self.secret = secret

    def ping(self):
        path = "%s/ping" % c.BASE_URL_V3
        return requests.get(path, timeout=180, verify=True).json()

    # 服务器时间
    def serverTime(self):
        path = "%s/time" % c.BASE_URL_V3
        return requests.get(path, timeout=180, verify=True).json()

    # 获取交易规则和交易对信息, GET /api/v3/exchangeInfo
    def exchangeInfo(self):
        path = "%s/exchangeInfo" % c.BASE_URL_V3
        return requests.get(path, timeout=180, verify=True).json()

    # 获取最新价格
    def get_ticker_price(self,symbol):
        path = "%s/ticker/price" % c.BASE_URL_V3
        params = {"symbol": symbol}
        res = self._get_no_sign(path, params)
        print(f'get_ticker_price:{res}')
        time.sleep(2)
        return float(res['price'])

    # 24hr 价格变动情况
    def get_ticker_24hr(self, market):
        path = "%s/ticker/24hr" % c.BASE_URL_V3
        params = {"symbol": market}
        res =  self._get_no_sign(path, params)
        return res

    #获取K线 https://api.binance.com/api/v3/klines?symbol=ETHUSDT&interval=15m&startTime=1619761128000&endTime=1619764848000
    def get_klines(self, market, interval, limit=0, starttime=None, endtime=None):
        path = "%s/klines" % c.BASE_URL_V3
        params = None
        if starttime is None:
            params = {"symbol": market, "interval":interval}    
        else:    
            params = {"symbol": market, "interval":interval, "startTime":starttime, "endTime":endtime}

        if limit is None or limit <= 0 or limit > 1000:
            limit = 500

        params['limit'] = limit

        return self._get_no_sign(path, params)


    # 现货，账户信息，GET /api/v3/account
    def account(self):
        stamp_now = int(round(time.time() * 1000))
        path = "%s/account" % c.BASE_URL_V3
        params = {"timestamp": stamp_now,"recvWindow": c.recv_window}
        res = self._get_with_sign(path, params)
        return res

    def get_spot_asset_by_symbol(self, symbol):
        ud_account = self.account()

        if ud_account is not None and "balances" in ud_account.keys():
            balances = ud_account["balances"]
            if balances is not None and type(balances).__name__ == 'list':
                for balance in balances:
                    if str(balance["asset"]) == symbol:
                        return balance


    # 查询每日资产快照，/sapi/v1/accountSnapshot
    def get_user_account_snapshot(self):
        stamp_now = int(round(time.time() * 1000))
        path = "https://www.binance.com/sapi/v1/accountSnapshot"
        params = {"type":"SPOT", "timestamp": stamp_now, "limit":5}

        # res = self._post(path, params)
        res = self._get_with_sign(path, params).json()
        return res

    def buy(self, symbol, quantity, countasset, price, newclientorderid):
        print(f'BUY newclientorderid:{newclientorderid} {quantity}:个 当前价格:{price}')
        path = "%s/order" % c.BASE_URL_V3
        params = self._order(symbol, quantity, "BUY", countasset, price, newclientorderid)
        return self._post(path, params)

    def get_order(self, symbol, newclientorderid):
        print(f'_get_order newclientorderid:{newclientorderid}')
        path = "%s/order" % c.BASE_URL_V3
        params = {"symbol": symbol, "orderId": newclientorderid}
        return self._get_with_sign(path, params)

    def delete_order(self, symbol, newclientorderid):
        print(f'delete order newclientorderid:{newclientorderid}')
        path = "%s/order" % c.BASE_URL_V3
        params = {"symbol": symbol, "newclientorderid": newclientorderid}
        return self._delete_with_sign(path, params)

    def sell(self, market, quantity, countasset, price, newclientorderid):
        print(f'SELL newClientOrderId:{newclientorderid} {quantity}:个 当前价格:{price}')
        path = "%s/order" % c.BASE_URL_V3
        params = self._order(market, quantity, "SELL", countasset, price, newclientorderid)
        return self._post(path, params)






    ### ----私有函数---- ###
    def _order(self, symbol, quantity, side, baseAssetCount, price=None, newclientorderid=None):
        '''
        :param market:币种类型。如：BTCUSDT、ETHUSDT
        :param quantity: 购买量
        :param side: 订单方向，买还是卖
        :param price: 价格
        :return:
        '''
        params = {}

        if price is not None:
            params["type"] = "LIMIT"
            params["price"] = self._format(price)
            params["timeInForce"] = "GTC"
            params["quantity"] = '%.8f' % quantity
        else:
            params["type"] = "MARKET"
            params["quoteOrderQty"] = baseAssetCount

        params["symbol"] = symbol
        params["side"] = side
        params["newClientOrderId"] = newclientorderid

        return params

    def _get_no_sign(self, path, params={}):
        query = urlencode(params)
        url = "%s?%s" % (path, query)
        return requests.get(url, timeout=180, verify=True).json()

    def _get_no_sign_header(self, path, params={},header={}):
        query = urlencode(params)
        url = "%s?%s" % (path, query)
        return requests.get(url, headers=header,timeout=180, verify=True).json()

    def _get_with_sign(self, path, params={}):
        tmp_signature = self._signature(params)
        params.update({"signature": tmp_signature})
        query = urlencode(params)
        url = "%s?%s" % (path, query)
        header = {"Content-Type": "application/json", "X-MBX-APIKEY": self.key}
        return requests.get(url, headers=header, timeout=180, verify=True).json()

    def _delete_with_sign(self, path, params={}):
        tmp_signature = self._signature(params)
        params.update({"signature": tmp_signature})
        query = urlencode(params)
        url = "%s?%s" % (path, query)
        header = {"Content-Type": "application/json", "X-MBX-APIKEY": self.key}
        return requests.delete(url, headers=header, timeout=180, verify=True).json()

    # 生成 signature
    def _signature(self, params={}):
        data = params.copy()
        # ts = int(1000 * time.time())
        # data.update({"timestamp": ts})
        h = urlencode(data)
        b = bytearray()
        b.extend(self.secret.encode())
        signature = hmac.new(b, msg=h.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
        return signature

    def _sign(self, params={}):
        data = params.copy()

        ts = int(1000 * time.time())
        data.update({"timestamp": ts})
        h = urlencode(data)
        b = bytearray()
        b.extend(self.secret.encode())
        signature = hmac.new(b, msg=h.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
        data.update({"signature": signature})
        return data

    def _post(self, path, params={}):
        params.update({"recvWindow": c.recv_window})
        query = urlencode(self._sign(params))
        url = "%s" % (path)
        header = {"X-MBX-APIKEY": self.key}
        return requests.post(url, headers=header, data=query,timeout=180, verify=True).json()

    def _format(self, price):
        return "{:.8f}".format(price)


    # 合约
    def market_future_order(self, side, symbol, quantity, baseAssetCount, positionSide, newClientOrderId):

        ''' 合约市价单
            :param side: 做多or做空 BUY SELL
            :param symbol:币种类型。如：BTCUSDT、ETHUSDT
            :param quantity: 购买量
            :param positionSide: 双向持仓 BUY-LONG 开多 SELL-SHORT 开空
            :param price: 开仓价格
        '''
        path = "%s/fapi/v1/order" % self.FUTURE_URL
        params = self._order(symbol, quantity, side, baseAssetCount, positionSide,newClientOrderId)
        return self._post(path, params)



if __name__ == "__main__":
    client = Client(c.api_key, c.api_secret)

    s_uuid = ''.join(str(uuid.uuid4()).split('-'))
    result = client.order('ETHUSDT', None, c.asset_count, None, s_uuid)
    print(result)
    #print(client.order("EOSUSDT", 5, 2))
    #print(client.get_ticker_price("WINGUSDT"))
    #print(client.get_ticker_24hr("WINGUSDT"))