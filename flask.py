from flask import Flask
from flask.globals import request
from Crypto.Cipher import AES
import base64,hashlib,xmltodict,json
import socket
import struct

app = Flask(__name__)

@app.route("/",methods=["get"])
def wx_check_api():
    sToken = "cdT8EAMhdbir5ha472wxn5hDMkPfY4"
    sEncodingAESKey = "RPyxhbU2rAvnAhbKHg1HoaeVUtEvjMyWqlJW2cUR6Ja"
    sCorpID = "ww338f460e583fb71d"

    msg_signature = request.args.to_dict().get("msg_signature")
    sTimeStamp = request.args.to_dict().get("timestamp")
    sNonce = request.args.to_dict().get("nonce")
    sEchoStr = request.args.to_dict().get("echostr")

    key = base64.b64decode(sEncodingAESKey+"=")

    cryptor = AES.new(key, AES.MODE_CBC, key[:16])
    # 使用BASE64对密文进行解码，然后AES-CBC解密
    plain_text = cryptor.decrypt(base64.b64decode(sEchoStr))
    pad = plain_text[-1]
    #pad = ord(str(plain_text[-1]))
    # 去掉补位字符串
    # pkcs7 = PKCS7Encoder()
    # plain_text = pkcs7.encode(plain_text)
    # 去除16位随机字符串
    content = plain_text[16:-pad]
    xml_len = socket.ntohl(struct.unpack("I", content[: 4])[0])
    xml_content = content[4: xml_len + 4]
    from_receiveid = content[xml_len + 4:]
    return xml_content

if __name__ == "__main__":
    app.run(debug=False,host='0.0.0.0')