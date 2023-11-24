import time
import pyupbit
import datetime

access = ""
secret = ""

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

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time(coin_KRW) #9:00
        end_time = start_time + datetime.timedelta(days=1) #09:00 +1일
        print("now",now)
        print("start_time",start_time)
        print("end_time",end_time)
        # 9:00 < 현재 < 다음날 8:58:00
        if start_time < now < end_time - datetime.timedelta(minutes=2):
            target_price = get_target_price(coin_KRW, k)
            current_price = get_current_price(coin_KRW)

            # target 가격(변동성)에 도달 하고 sell_status 상태 정보가 '0'일 때 매수 진행
            if target_price < current_price and sell_status == 0:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order(coin_KRW, krw*0.9995)
                    sell_status = 9 # 매수 진행 시 sell_status 상태 정보 9
                    print("buy")
                    print(current_price)

            buy_avg_price = upbit.get_avg_buy_price(coinName)
            if(buy_avg_price != None):
                print("target_price",target_price)
                print("current_price",current_price)
                print("buy_avg_price",buy_avg_price)
                sell_price_plus_1 = buy_avg_price * plus_1
                sell_price_plus_2 = buy_avg_price * plus_2
                sell_price_minus_1 = buy_avg_price - buy_avg_price * minus_1
                sell_price_minus_2 = buy_avg_price - buy_avg_price * minus_2
                print(f'현재가격:{current_price}', f'target가격:{target_price}', f'평균매수가격:{buy_avg_price}')
                print(f'%1st수익예상:{sell_price_plus_1}',f'%2nd수익예상:{sell_price_plus_2}')
                print(f'%1st손절예상:{sell_price_minus_1}',f'%2nd손절예상:{sell_price_minus_2}', sell_status)
                # 익절 %변동에 따른 1st 50% 매도 진행
                if current_price > sell_price_plus_1 and (sell_status == 9 or sell_status == 0):
                    coin = get_balance(coinName)
                    if coin > low_limit_coin:
                        upbit.sell_market_order(coin_KRW, coin*0.5)
                        sell_status = 1
                        print("plus 1st sell")
                        print(current_price)
                # 익절 % 변동에 따른 1st 이후 진입가격(하락) 도달 시 100% 매도
                if current_price < buy_avg_price and (sell_status == 1 or sell_status == 0):
                    coin = get_balance(coinName)
                    if coin > low_limit_coin:
                        upbit.sell_market_order(coin_KRW, coin*0.9995)
                        sell_status = 5
                        print("same same sell")
                        print(current_price)
                # 익절 %변동에 따른 2nd 100% 매도 진행
                if current_price > sell_price_plus_2 and (sell_status == 1 or sell_status == 0):
                    coin = get_balance(coinName)
                    if coin > low_limit_coin:
                        upbit.sell_market_order(coin_KRW, coin*0.9995)
                        sell_status = 2
                        print("plus 2nd sell")
                        print(current_price)

                # 손절 %변동에 따른 1st 50% 매도 진행
                if current_price < sell_price_minus_1 and (sell_status == 9 or sell_status == 0):
                    coin = get_balance(coinName)
                    if coin > low_limit_coin:
                        upbit.sell_market_order(coin_KRW, coin*0.5)
                        sell_status = 3
                        print("minus 1st sell")
                        print(current_price)
                # 손절 %변동에 따른 2nd 100% 매도 진행
                if current_price < sell_price_minus_2 and (sell_status == 3 or sell_status == 0):
                    coin = get_balance(coinName)
                    if coin > low_limit_coin:
                        upbit.sell_market_order(coin_KRW, coin*0.9995)
                        sell_status = 4
                        print("minus 2nd sell")
                        print(current_price)
        # 다음날 08:59:00 < 현재 < 다음날 08:59:55 장 마감시간 전량 매도
        elif end_time - datetime.timedelta(minutes=1) < now < end_time - datetime.timedelta(seconds=5):
            btc = get_balance(coinName)
            sell_status = 0
            if btc > low_limit_coin:
                upbit.sell_market_order(coin_KRW, btc*0.9995)
                sell_coin = get_current_price(coin_KRW)
                print(sell_coin)
                print(current_price)
                         
        # else:
        #     btc = get_balance(coinName)
        #     sell_status = 0
        #     if btc > low_limit_coin:
        #         upbit.sell_market_order(coin_KRW, btc*0.9995)
        #         sell_coin = get_current_price(coin_KRW)
        #         print(sell_coin)
        #         print(current_price)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
