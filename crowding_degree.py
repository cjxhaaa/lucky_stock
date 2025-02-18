import base64
import hashlib
import hmac
import time
import datetime
import os
import pandas as pd
from dsb_spider.req import request

import urllib
from config import dingding_webhook, dingding_sign, tushare_token
import matplotlib.pyplot as plt

import tushare as ts
ts.set_token(tushare_token)

pro = ts.pro_api()

DATE_FORMAT = '%Y%m%d'
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

def crowding_degree(trade_date):
    daily_data = pd.read_csv(f'{DATA_PATH}/{trade_date}.csv')
    turnover_data = daily_data[['ts_code', 'amount']]

    total_turnover = turnover_data['amount'].sum()
    sorted_turnover = turnover_data.sort_values(by='amount', ascending=False)
    num_top_stocks = int(len(sorted_turnover) * 0.05)
    top_5_percent = sorted_turnover.head(num_top_stocks)

    top_5_percent_vol = top_5_percent['amount'].sum()
    crowding_degree = (top_5_percent_vol / total_turnover)

    return crowding_degree

def save_date_data(trade_date):
    daily_data = pro.daily(trade_date=trade_date)
    daily_data.to_csv(f'{DATA_PATH}/{trade_date}.csv', index=False)

def save_trade_dates_data(start_date, end_date):
    trade_dates = get_trade_dates(start_date, end_date)
    for trade_date in trade_dates:
        file_path = f'{DATA_PATH}/{trade_date}.csv'
        if os.path.exists(file_path):
            continue
        save_date_data(trade_date)


def get_trade_dates(start_date, end_date):
    start = datetime.datetime.strptime(start_date, DATE_FORMAT)
    end = datetime.datetime.strptime(end_date, DATE_FORMAT)
    date_list = [start + datetime.timedelta(days=x) for x in range((end - start).days + 1)]

    holidays = [
        '2025-01-01', '2025-01-24', '2025-01-28', '2025-01-29', '2025-01-30', '2025-01-31', '2025-02-03', '2025-02-04', '2025-04-04', 
        '2025-06-12', '2025-06-13', '2025-06-14', '2025-06-15', '2025-06-16', '2025-09-13', '2025-09-14', '2025-09-15', '2025-09-16',
        '2025-10-01', '2025-10-02', '2025-10-03', '2025-10-04', '2025-10-05', '2025-10-06', '2025-10-07'
    ]
    holidays = [datetime.datetime.strptime(holiday, '%Y-%m-%d') for holiday in holidays]
    trade_dates = [date for date in date_list if date.weekday() < 5 and date not in holidays]
    trade_dates = [date.strftime('%Y%m%d') for date in trade_dates]
    return trade_dates

def calculate_crowding_degree_between(start_date, end_date):
    trade_dates = get_trade_dates(start_date, end_date)
    crowding_degrees = {}
    for trade_date in trade_dates:
        try:
            crowding_degrees[trade_date] = crowding_degree(trade_date)
        except Exception as e:
            print("date: ", trade_date, " error: ", e)
    return crowding_degrees


def send_to_dingding():
    timestamp = str(round(time.time() * 1000))
    secret = dingding_sign
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    request_url = f"{dingding_webhook}&timestamp={timestamp}&sign={sign}"
    formatted_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today = datetime.now().strftime(DATE_FORMAT)
    save_date_data(today)
    message = {
        "msgtype": "text",
        "text": {
            "content": f"{formatted_date} 股市拥挤度为: {crowding_degree(today)}"
        }
    }
    headers = {
    "Content-Type": "application/json;charset=utf-8"
    }
    response = request('POST', request_url, headers=headers, json=message)
    print(response.text)

def plot_crowding_degrees(start_date, end_date):
    crowding_degrees = calculate_crowding_degree_between(start_date, end_date)
    # Convert the dictionary to a DataFrame for easier plotting
    crowding_df = pd.DataFrame(list(crowding_degrees.items()), columns=['Date', 'Crowding Degree'])
    crowding_df['Date'] = pd.to_datetime(crowding_df['Date'], format='%Y%m%d')
    
    # Plot the data
    plt.figure(figsize=(10, 6))
    plt.plot(crowding_df['Date'], crowding_df['Crowding Degree'], marker='o')
    plt.title(f'Crowding Degree from {start_date} to {end_date}')
    plt.xlabel('Date')
    plt.ylabel('Crowding Degree')
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save the plot to a file
    plot_path = os.path.join(DATA_PATH, f'crowding_degree_{start_date}_to_{end_date}.png')
    plt.savefig(plot_path)
    print(f'Plot saved to {plot_path}')
    plt.show()

if __name__ == '__main__':  
    # print(crowding_degree('20250218'))
    # save_trade_dates_data('20250101', '20250218')
    # plot_crowding_degrees('20250101', '20250218')
    send_to_dingding()
