# version.2023-02v(11/27 변동성 함수 [-1] -> [-2], ma 소숫점 1자리수정)

import time
import pybithumb
import datetime
import requests
import numpy as np
import pandas as pd

# 수호의 API
#access = "3ee00a7eaafc56a70057e56f2fda344d"
#secret = "f4de7995d1b1869c468712a7d98fafac"
#discord = "https://discord.com/api/webhooks/1177931669756461196/KzVlnTu3__p664r35nqvntU6eBBg3m9xWO1pVnTbpo-nx_fHlIfw7c00LsYFm9wt0dia"

# 기태의 API
access = "3f488f612a6c6305f1d81c7f4784cbc9"
secret = "aaf84e8d1c546cb0d889304486165eba"
discord = "https://discord.com/api/webhooks/1178139397682626742/NuXGwGJNm3aW1dA13TkjJXA8I4s_xu3ENX3oqODDCcTXq5Uc_fEiRdbgHt892dCxV_ck"


# 변수 모음
checkDayPeriod = 7 # K값을 구하기 위한 일자별 기록 구간
coinName = "BTC"
trade_status = 0 # 매매 상태 정보(0:매수가능, 1:1st익절, 2:2nd익절, 3:1st손절, 4:2nd손절, 5:익절후본전)
send_OnTimeMsg_YN = "N"
send_SellMsg_YN = "N"
bestRor = 0
bestK = 0
lastK = 0
ma_days = 15 # ma 이동평균선 몇일?

def get_BestK():
    global bestRor 
    global bestK 
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=checkDayPeriod)

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
        # print("K : ", k, "ror : ", ror)
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

def send_buy_message(buy_result, current_price):
    send_message(f'★★★★★Bithumb 매수체결★★★★★')
    send_message(f'매수결과: {buy_result}')
    # 실제 산가격은 아님. 나중엔 산금액을 balance로 조회한 정보를 가져와야함.
    send_message(f'매수금액: {current_price}')

def send_sell_message(sell_result, current_price):
    send_message(f'★★★★★Bithumb  매도체결★★★★★')
    send_message(f'매도결과: {sell_result}')
    send_message(f'매도금액: {current_price}')


def get_target_price(ticker, k):
    """변동성 돌파 전략으로 Bithumb 매수 목표가 조회"""
    df = pybithumb.get_ohlcv(ticker)
    target_price = df['close'].iloc[-2] + (df['high'].iloc[-2] - df['low'].iloc[-2]) * k
    return target_price

def get_start_time(ticker):
    """장 시작 시간 조회"""
    df = pybithumb.get_ohlcv(ticker)
    start_time = df.index[len(df) - 1].replace(hour=0, minute=0, second=0, microsecond=0)
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = pybithumb.get_balance(ticker)
    return float(balances['available'])

def get_current_price(ticker):
    """현재가 조회"""
    return pybithumb.get_current_price(ticker)


def get_moving_average(ticker, days):
    """이동 평균 계산"""
    df = pybithumb.get_ohlcv(ticker)
    ma = df['close'].rolling(window=days).mean().iloc[-1]
    return ma

# 로그인
bithumb = pybithumb.Bithumb(access, secret)
target_price = get_target_price(coinName, 0.5)
current_price = get_current_price(coinName)
ma_days_price = round(get_moving_average(coinName, ma_days),1)
send_message(f'===Bithumb Autotrade start=== {coinName, 0.5, ma_days}')
send_message(f'Bithumb 현재가격: {current_price}')
send_message(f'Bithumb 타겟가격: {target_price}')
send_message(f'Bithumb MA타겟가격: {ma_days_price}')

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        standard_time = get_start_time("BTC")  # 23:59
        start_time = standard_time.replace(hour=0, minute=1, second=0, microsecond=0)  # 당일 00:01
        end_time = standard_time.replace(hour=23, minute=55, second=0, microsecond=0)  # 당일 23:55
        checkOnTime = datetime.datetime.now().minute
        # Best K값 가져오기
        k = get_BestK()
        # print(k)
        if(lastK != k):
            lastK = k
            send_message(f'♨♨♨K 값이 {lastK} 로 바뀌었으니, 확인하기 바랍니다.♨♨♨')
        
        # 당일 00:01 < 지금 < 당일 23:55
        if start_time <= now <= end_time:
            target_price = get_target_price(coinName, lastK)
            current_price = get_current_price(coinName)

            # 15일 이동 평균 계산
            ma_days_price = round(get_moving_average(coinName, ma_days),1)

            # 매 30분 단위로 디스코드로 현재시간과 타겟 가격, 현재가격 정보를 보내준다.
            if (checkOnTime == 0 or checkOnTime == 30) and send_OnTimeMsg_YN == "N":
                send_message(f'Bithumb 진행중  : {coinName, lastK, ma_days}')
                send_message(f'Bithumb 현재가격: {current_price}')
                send_message(f'Bithumb K타겟가격: {target_price}')
                send_message(f'Bithumb MA타겟가격: {ma_days_price}')
                send_OnTimeMsg_YN = "Y"
            # 정각에 메시지 한번만 보내기 위함.
            if (checkOnTime == 1 or checkOnTime == 31) and send_OnTimeMsg_YN == "Y":
                send_OnTimeMsg_YN = "N"

            if target_price < current_price and ma_days_price < current_price and trade_status == 0:
                accountBalance = bithumb.get_balance("BTC")
                moneyForOrder = accountBalance[2] - accountBalance[3]
                if moneyForOrder > 8000:
                    cnt = round(moneyForOrder / current_price, 5) * 0.8
                    buy_result = bithumb.buy_market_order(coinName, cnt)
                    buy_price = get_current_price(coinName)
                    trade_status = 1 # 매수 진행

                    send_buy_message(buy_result, buy_price)

        # 당일 23:55 < 지금 < 당일 23:59
        else:
            coinBalance = bithumb.get_balance(coinName)[0]
            trade_status = 0 # 매도 진행 or 시간으로 인한 reset
            if coinBalance > 0.0008:
                sell_result = bithumb.sell_market_order(coinName, coinBalance)
                sell_price = get_current_price(coinName)

                send_sell_message(sell_result, sell_price)

        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
