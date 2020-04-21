import requests
import hashlib
import random

appid = '20200411000417232'  # 你的appid
secretKey = 'qlU6c8Sles9X7LObI5Zb'  # 你的密钥
def baidu_fanyi(query):
    salt = random.randint(1, 10)  # 随机数
    code = appid + query + str(salt) + secretKey
    sign = hashlib.md5(code.encode()).hexdigest()  # 签名

    api = "http://api.fanyi.baidu.com/api/trans/vip/translate"
    query=query.encode('utf-8')
    data = {
        "q": query,
        "from": "en",
        "to": "zh",
        "appid": appid,
        "salt": salt,
        "sign": sign
    }

    response = requests.get(api, data)

    try:
        result = response.json()
        dst = result.get("trans_result")[0].get("dst")

    except Exception as e:
        dst = query

    finally:
        return dst


if __name__ == '__main__':
    query = "Father of the Bride Part II (1995)"
    ret = baidu_fanyi(query)
    print(ret)
    # 苹果
