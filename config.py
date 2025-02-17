import configparser

config = configparser.ConfigParser()
config.read('config.ini')

tushare_token = config['TUSHARE']['token']
dingding_webhook = config['DINGDING']['webhook']
dingding_sign = config['DINGDING']['sign']