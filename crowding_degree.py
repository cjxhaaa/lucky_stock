import base64
import hashlib
import hmac
import time
import tushare as ts
from datetime import datetime
from dsb_spider.req import request

import urllib
from config import dingding_webhook, dingding_sign, tushare_token

ts.set_token(tushare_token)

pro = ts.pro_api()


def crowding_degree():
    daily_data = pro.daily(trade_date=datetime.now().strftime('%Y%m%d'))
    turnover_data = daily_data[['ts_code', 'amount']]

    total_turnover = turnover_data['amount'].sum()
    sorted_turnover = turnover_data.sort_values(by='amount', ascending=False)
    num_top_stocks = int(len(sorted_turnover) * 0.05)
    print('stocks num: ', num_top_stocks)
    top_5_percent = sorted_turnover.head(num_top_stocks)

    top_5_percent_vol = top_5_percent['amount'].sum()
    crowding_degree = (top_5_percent_vol / total_turnover)

    return crowding_degree

def send_to_dingding():
    timestamp = str(round(time.time() * 1000))
    secret = dingding_sign
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    request_url = f"{dingding_webhook}&timestamp={timestamp}&sign={sign}"
    formatted_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = {
        "msgtype": "text",
        "text": {
            "content": f"{formatted_date} 股市拥挤度为: {crowding_degree()}"
        }
    }
    headers = {
    "Content-Type": "application/json;charset=utf-8"
    }
    response = request('POST', request_url, headers=headers, json=message)
    print(response.text)


if __name__ == '__main__':  
    # print(crowding_degree())
    send_to_dingding()
