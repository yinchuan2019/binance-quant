# binance-quant
数字货币，币安Binance, 比特币BTC 以太坊ETH 莱特币LTC 狗币DOGE 屎币SHIB 量化交易系统 火币 OKEX 交易策略 量化策略 自动交易


## 简介
这是一个数字货币量化交易系统，使用的Binance币安的交易API.

如果你还没有币安账号：[注册页面](https://accounts.binance.com/zh-CN/register?ref=558772431)（通过链接注册，享受交易返现优惠政策）

这世上，没有百分百赚钱的方式，量化交易策略只是一个辅助工具。

生死有命，富贵在天！币圈有风险，入市需谨慎！！

## 双均线策略
以 ETH 为例，5分钟K线数据，均线5 和 均线60 为例：

均线5上穿均线60是金叉，执行买入；
均线5下穿均线60是死叉，执行卖出；

这是一个比较震荡的情况，会亏损。


使用时，必须根据自身情况，调整 K线 和 均线！！！！



## 为什么选择币安交易所
交易的手续费看起来很少，但是随着交易次数逐步增多，手续费也是一笔不小的开支。
所以我选择了币安，手续费低的大平台交易所
> 火币手续费 Maker 0.2% Taker 0.2%

> 币安手续费 Maker 0.1% Taker 0.1% （加上BNB家持手续费低至0.075%）



## 运行环境
python3

由于交易所的api在大陆无法访问，需要科学上网。


## 快速使用

1、获取币安API的 api_key 和 api_secret



