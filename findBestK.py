import time
import pyupbit
import datetime
import requests
import numpy as np
from warnings import filterwarnings
filterwarnings("ignore", category=FutureWarning)

access = "personal"
secret = "personal"
discord = "https://discord.com/api/webhooks/1178139397682626742/NuXGwGJNm3aW1dA13TkjJXA8I4s_xu3ENX3oqODDCcTXq5Uc_fEiRdbgHt892dCxV_ck"

bestRor = 0
bestK = 0

realK = 0

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

def send_message(msg):
    """디스코드 메세지 전송"""
    now = datetime.datetime.now()
    message = {"content": f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {str(msg)}"}
    requests.post(discord, data=message)
    print(message)

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time


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
        if(realK != k):
            realK = k
            send_message(f'♨♨♨K 값이 {realK} 로 바뀌었으니, 확인하기 바랍니다.♨♨♨')
        time.sleep(600)
    except Exception as e:
        print(e)
        time.sleep(600)
