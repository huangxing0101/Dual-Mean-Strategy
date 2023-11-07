
import os 
import os.path as osp
from datetime import datetime, timedelta
import json
from tqdm import tqdm
import pandas as pd

STOCKS_PATH = "data/STOCKS-DAYS"

def getList(path):
    listdir = os.listdir(path)
    return listdir
     
def tostring(time: datetime):
    return f"{time.year}-{time.month:02d}-{time.day:02d}"

start_date = datetime(year=2021, month=7, day=1)
end_date = datetime(year=2022, month=1, day=1)

DATA = {}
stocks_list = getList(STOCKS_PATH)
for stock in tqdm(stocks_list):
    current_date = start_date
    df = pd.read_csv(osp.join(STOCKS_PATH, stock, 'price.csv'))
    df = df.set_index("date")
    
    while current_date <= end_date:
        date = tostring(current_date)
        data = None
        try:
            data = df.loc[date]
        except KeyError:
            pass
        if data is not None and data['volume'] > 0:
            if date in DATA:
                DATA[date].append(stock)
            else:
                DATA[date] = [stock]      
        current_date += timedelta(days=1)

with open('./date.json', 'w') as f:
    json.dump(DATA, f, indent=4)

