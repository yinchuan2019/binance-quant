from binance.spot import Spot
from app import const as c

# client = Spot()
# # Get server timestamp
# print(f'client time : {client.time()}')
# # API key/secret are required for user data endpoints
# if c.isTest:
#     client = Spot(api_key=c.api_key_test, api_secret=c.api_key_test, kwargs={"base_url": c.BASE_URL_V3_TEST})
# else:
#     client = Spot(api_key=c.api_key, api_secret=c.api_secret)


# Get account and balance information
# print(client.account())
#
# # Post a new order
# params = {
#     'symbol': 'BTCUSDT',
#     'side': 'SELL',
#     'type': 'LIMIT',
#     'timeInForce': 'GTC',
#     'quantity': 0.002,
#     'price': 9500
# }
#
# response = client.new_order(**params)
# print(response)


