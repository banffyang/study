import time
import pyupbit
import datetime

access = "58CFRFfssi46PGCL5Z37a2m866EI0jOTotg3P3xK"
secret = "qPi1R2q9DSQxC2VRyz2Igc20FBy1XLSjyvbvIyUV"

# 변수
k = 0.3 # k값
plus_1 = 1.03 # 1st 익절 % 변동에 따른 매도 진행
plus_2 = 1.05 # 2nd 익절 % 변동에 따른 매도 진행
minus_1 = 0.03 # 1st 손절 % 변동에 따른 매도 진행
minus_2 = 0.05 # 2nd 손절 % 변동에 따른 매도 진행
coin_KRW = "KRW-BTC" # 매수 coin
coinName = "BTC" # coin 잔고 조회(매도)
coin_price = 50000000 # 적용 당시 코인 금액
low_limit_coin = 5500 / coin_price # 매도 최소 coin 갯수(5000원 / 코인 금액)
sell_status = 0 # 매매 상태 정보(0:매수가능, 1:1st익절, 2:2nd익절, 3:1st손절, 4:2nd손절, 5:익절후본전)

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

target_price = get_target_price(coin_KRW, k)
print(target_price)

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
print(upbit.get_balances())
buy_avg_price = upbit.get_avg_buy_price("KRW-BTC")
print(buy_avg_price)
