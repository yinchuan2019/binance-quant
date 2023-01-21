import json
import time
import math
from urllib.parse import urlencode
from binance.um_futures import UMFutures


def get_server_status():
    client = UMFutures()
    # Get server timestamp
    client.ping()
    return client.time()

# 根据交易规则，格式化交易量
def format_trade_quantity(symbol, originalQuantity, minQty):
    print(f'{symbol} 原始交易量 {str(originalQuantity)}')
    print(f'{symbol} 最小交易量限制 {str(minQty)}')

    if minQty > 0:
        newQuantity = (float(originalQuantity) // minQty) * minQty
    else:
        newQuantity = math.floor(float(originalQuantity))

    print(f'{symbol} 交易量格式化 {str(newQuantity)}')
    return newQuantity


def cleanNoneValue(d) -> dict:
    out = {}
    for k in d.keys():
        if d[k] is not None:
            out[k] = d[k]
    return out

def get_timestamp():
    return int(time.time() * 1000)


def encoded_string(query, special=False):
    if special:
        return urlencode(query).replace("%40", "@").replace("%27", "%22")
    else:
        return urlencode(query, True).replace("%40", "@")


def convert_list_to_json_array(symbols):
    if symbols is None:
        return symbols
    res = json.dumps(symbols)
    return res.replace(" ", "")


def config_logging(logging, logging_devel, log_file=None):
    logging.basicConfig(level=logging_devel, filename=log_file)
