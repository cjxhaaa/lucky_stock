import configparser
import os

config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')

config = configparser.ConfigParser()
config.read(config_path)

tushare_token = config['TUSHARE']['token']
dingding_webhook = config['DINGDING']['webhook']
dingding_sign = config['DINGDING']['sign']