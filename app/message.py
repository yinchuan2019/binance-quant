# -*- coding: utf-8 -*-

'''
企业微信推送机器人
'''
import requests
import json
import time
from app import const as c

def get_token():
    url = f"https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={c.CORP_ID}&corpsecret={c.CORP_SECRET}"
    r = requests.get(url)
    if r.status_code == 200:
        data = json.loads(r.text)
        if data["errcode"] == 0:
            return data["access_token"]
        else:
            print("Error")
    else:
        print("Error")  # 连接服务器失败

def send_msg(data):
    print('开始企业微信推送')
    data = {
        "touser": "@all",
        "msgtype": "text",
        "agentid": 1000002,
        "text": {
            "content": data
        },
        "safe": 0
    }
    access_token = get_token()
    #r = requests.post("https://qyapi.weixin.qq.com/cgi-bin/service/get_permanent_code?suite_access_token = " + access_token, data=json.dumps(data))

    r = requests.post("https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={}".format(access_token), data=json.dumps(data))
    print(r.text)

if __name__ == "__main__":
    try:
        send_msg("123")
    except Exception as ex:
        err_str = "出现如下异常：%s" % ex
        print(err_str)


