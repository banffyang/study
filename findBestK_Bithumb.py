import pybithumb
import numpy as np
from datetime import datetime, timedelta
import time
import requests

access = "3f488f612a6c6305f1d81c7f4784cbc9"
secret = "aaf84e8d1c546cb0d889304486165eba"
discords = ["https://discord.com/api/webhooks/1178139397682626742/NuXGwGJNm3aW1dA13TkjJXA8I4s_xu3ENX3oqODDCcTXq5Uc_fEiRdbgHt892dCxV_ck","https://discord.com/api/webhooks/1177931669756461196/KzVlnTu3__p664r35nqvntU6eBBg3m9xWO1pVnTbpo-nx_fHlIfw7c00LsYFm9wt0dia"]

coinName = "BTC"

bestRor = 0
bestK = 0
lastK = 0

def get_BestK():
    global bestRor 
    global bestK 
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)

    # 해당 기간 동안의 일봉 데이터 가져오기
    all_data = pybithumb.get_ohlcv(coinName, interval="day")
    df = all_data.loc[start_date:end_date].copy()
    for k in np.arange(0.1, 1.0, 0.1):
        df['range'] = (df['high'] - df['low']) * k
        df['target'] = df['open'] + df['range'].shift(1)

        df['ror'] = np.where(df['high'] > df['target'],
                            df['close'] / df['target'],
                            1)

        ror = df['ror'].cumprod().iloc[-2]
        k = round(k,1)
        print("K : ", k, "ror : ", ror)
        if(ror > bestRor):
            bestRor = ror
            bestK = k
    return bestK
def send_message(msg,discord):
    """디스코드 메세지 전송"""
    now = datetime.now()
    message = {"content": f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {str(msg)}"}
    requests.post(discord, data=message)
    print(message)
    
# 로그인
bithumb = pybithumb.Bithumb(access, secret)
print("Best K 감시 start")

# 자동매매 시작
while True:
    try:
        # Best K값 가져오기
        k = get_BestK()
        print(k)
        if(lastK != k):
            lastK = k
            for discord in discords:
                send_message(f'♨♨♨Bithumb, K 값이 {lastK} 로 바뀌었으니, 확인하기 바랍니다.♨♨♨', discord)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
    
