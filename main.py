import pandas as pd
import numpy as np
import json 
import matplotlib.pyplot as plt
import os 
from tqdm import tqdm
from collections import defaultdict
stock_map = {}
stocklist = os.listdir('data/STOCKS-DAYS')
for stock in tqdm(stocklist):
    df = pd.read_csv(os.path.join('data/STOCKS-DAYS', stock, 'price.csv'))
    df = df.set_index("date")
    stock_map[stock] = df

log = {
    'date': [],
    'asset': [],
}

user = {'cash':1e10, 'stocks':defaultdict(tuple)} # volume, trade_price
alldate_stocks = json.load(open('date.json'))
alldate = sorted(alldate_stocks.keys())

for date in alldate:
    sell_pool = set()
    buy_pool = set()
    print(date)
    log['date'].append(date)
    action = ""

    for stock_name in tqdm(alldate_stocks[date]):
        df = stock_map[stock_name]
        data_today = df.loc[date]
        price_today = data_today['open']
        mean_20t = data_today['mean-20']
        mean_5t = data_today['mean-5']
        if np.isnan(mean_20t):
            continue
        idx = df.index.get_loc(date)
        data_yesterday = df.iloc[idx-1]
        price_yesterday = data_yesterday['close']
        percentage = (price_today - price_yesterday)/price_yesterday * 100
        mean_20y = data_yesterday['mean-20']
        mean_5y = data_yesterday['mean-5']
        if np.isnan(mean_20y):
            continue

        if (mean_5t > mean_20t) and (mean_5y < mean_20y):
            # buy
            if stock_name.split('.')[1][:3] in {'688', '300'}:
                if percentage < 19.9:
                    buy_pool.add((stock_name, percentage))
            else:
                if percentage < 9.9:
                    buy_pool.add((stock_name, percentage))

        elif (mean_5t < mean_20t) and (mean_5y > mean_20y):
            # sell
            if stock_name in user['stocks']:
                if stock_name.split('.')[1][:3] in {'688', '300'}:
                    if percentage > -19.9:
                        sell_pool.add(
                        (stock_name, percentage)
                        )
                else:
                    if percentage < 9.9:
                        sell_pool.add((stock_name, percentage))

    for stock_name, percentage in sell_pool:
        df = stock_map[stock_name]
        data_today = df.loc[date]
        price_today = data_today['open']
        volume, trade_price = user['stocks'][stock_name]
        user['cash'] = user['cash'] + price_today * volume
        user['stocks'].pop(stock_name)
        action += f"卖出{stock_name} {volume}股({(price_today - trade_price) / trade_price * 100}%), "


    buy_pool = sorted(buy_pool, key=lambda x:x[1])
    asset = user['cash']
    for stock_name in user['stocks']:
        df = stock_map[stock_name]
        data_today = df.loc[date]
        price_today = data_today['open']
        volume, trade_price =  user['stocks'][stock_name]
        asset += trade_price * volume
    threshold = asset * 0.05
    
    available_cash = min(threshold, user['cash'] / len(buy_pool))
    for stock_name, percentage in buy_pool:
        df = stock_map[stock_name]
        data_today = df.loc[date]
        price_today = data_today['open']
        volume = available_cash // price_today
        user['cash'] = user['cash'] - price_today * volume
        user['stocks'][stock_name] = (volume, price_today) 
        action += f"买入{stock_name} {volume}股, "
    print(action)
    print(f"总资产: {asset}, 现金: {user['cash']}")
    log['asset'].append(asset)

log_df = pd.DataFrame(log)
log_df.to_csv("log.csv", index=False)