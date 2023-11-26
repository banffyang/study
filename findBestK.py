import time
import pyupbit
import datetime
import numpy as np
from warnings import filterwarnings
filterwarnings("ignore", category=FutureWarning)

access = "personal"
secret = "personal"

bestRor = 0
bestK = 0

#Best K 값 구하기
def getBestK():
    global bestRor 
    global bestK 
    for k in np.arange(0.1, 1.0, 0.1):
        df = pyupbit.get_ohlcv("KRW-BTC",count=7)
        df['range'] = (df['high'] - df['low']) * k
        df['target'] = df['open'] + df['range'].shift(1)

        fee = 0.0032
        df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'] - fee,
                         1)

        ror = df['ror'].cumprod()[-2]
        k = round(k,1)
        print("K : ", k, "ror : ", ror)
        if(ror > bestRor):
            bestRor = ror
            bestK = k
    return bestK


def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC") #9:00
        end_time = start_time + datetime.timedelta(days=1) #09:00 +1일

        # Best K값 가져오기
        k= getBestK()
        print(k)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)