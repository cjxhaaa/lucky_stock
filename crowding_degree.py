import tushare as ts
from datetime import datetime

def get_token():
    with open("token", 'r') as fb:
        return fb.read()

token = get_token()
ts.set_token(token)

pro = ts.pro_api()


def get_today():
    return datetime.now().strftime('%Y%m%d')

def crowding_degree():
    daily_data = pro.daily(trade_date=get_today())
    turnover_data = daily_data[['ts_code', 'amount']]

    total_turnover = turnover_data['amount'].sum()
    sorted_turnover = turnover_data.sort_values(by='amount', ascending=False)
    num_top_stocks = int(len(sorted_turnover) * 0.05)
    print('stocks num: ', num_top_stocks)
    top_5_percent = sorted_turnover.head(num_top_stocks)

    top_5_percent_vol = top_5_percent['amount'].sum()
    crowding_degree = (top_5_percent_vol / total_turnover)

    return crowding_degree

if __name__ == '__main__':  
    print(crowding_degree())
