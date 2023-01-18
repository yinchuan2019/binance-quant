# -*- coding: utf-8 -*-
isTest = True
# https://www.binance.com/restapipub.html
#production
api_key = 'NG3J2K9gynjyJwzQ2RglMW4EBZqjdE7vnnD2SuDm3Lsk38vPxYnvK1mzRT9VtBOX'
api_secret = 'XSJkKB6f5AiqwI9ZJBKdsbLFwG8OUmqrulOdbCUWmeLuQbzcC1a3iFcacveh6qJ5'
# 企业微信
CORP_ID = 'ww338f460e583fb71d'
CORP_SECRET = 'Mw3ens5HxwupXW1COnNzUbza5O5cQ6j2mEhGT6e9CdU'

# 测试账号
#api_key = 'tbGkPohrz5M5Qi65l17oEMitvYaGO89NYzWrm1NsEKbNcLxBTHStU8rJ85ncodoE'
#api_secret = 'lp4yF95379K4oXG6sb2oqKWlQU224HKL4PDCmTow9qi8pCM9qJPtNrvDHZ7wAlQE'

BASE_URL_V3_TEST = "https://testnet.binance.vision/api/v3"
BASE_URL_V3 = "https://api.binance.com/api/v3"
BASE_URL = "https://www.binance.com/api/v1"
FUTURE_URL = "https://fapi.binance.com"
PUBLIC_URL = "https://www.binance.com/exchange/public/product"

# 是否分批卖出
isOpenSellStrategy = False
#分批卖出，盈利百分比
sellStrategy1 = {"profit":1.05, "sell":0.1}#盈利5%时，卖出10%的仓位
sellStrategy2 = {"profit":1.10, "sell":0.2}#盈利10%时，卖出20%的仓位
sellStrategy3 = {"profit":1.20, "sell":0.2}#盈利20%时，卖出20%的仓位

# 均线, ma_min 要大于 ma_max
ma_min = 7
ma_max = 25

# 币安
binance_market = "SPOT" #现货市场
recv_window = 2000
base_asset = "ETH"
quote_asset = "USDT" #使用USDT作为基础币种，用于购买其他货币；
count_asset = 10 # 买币时最多可用资金量 单位quote_asset
kLine_type = "3m" # 15分钟k线类型，你可以设置为5分钟K线：5m; 1小时为：1h;1天为：1d
