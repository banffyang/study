
import time
import pybithumb
import datetime

access = "3f488f612a6c6305f1d81c7f4784cbc9"
secret = "aaf84e8d1c546cb0d889304486165eba"

def get_start_time(ticker):
    """장 시작 시간 조회"""
    df = pybithumb.get_ohlcv(ticker)
    # start_time = df.index[0]
    start_time = df.index[len(df)-2]+ datetime.timedelta(days=2) + datetime.timedelta(minutes=-1)
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = pybithumb.get_balance(ticker)
    return float(balances['available'])

def get_current_price(ticker):
    """현재가 조회"""
    return pybithumb.get_current_price(ticker)

# 로그인
bithumb = pybithumb.Bithumb(access, secret)
print("autotrade start")

#자정 급등 후보 종목List
tickerForOrder =["FX","CTC","BFC","CRTS","QTCON","BOA","OBSR","FLZ","ZTX","ALEX","WOZX","WIKEN"]


# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("BTC") # 11:59
        end_time = start_time + + datetime.timedelta(minutes=1) # 00:00
        # start_time = end_time + datetime.timedelta(minutes=-1) # 11:59
        end_time2 = end_time + datetime.timedelta(minutes=1) # 00:01
        print("now",now)
        print("start_time",start_time)
        print("end_time",end_time)
        print("end_time2",end_time2)
        
        #  23:59 < 현재 < 00:00
        if  start_time < now < end_time:
            #현금 자산
            accountBalance = bithumb.get_balance("BTC")
            #주문가능 현금 액수 (현재 100만원이 있어서 좀 빼야함)
            moneyForOrder = accountBalance[2]-accountBalance[3] - 700000
            moneyFor_Once_Order = moneyForOrder/len(tickerForOrder) 
            print(len(tickerForOrder) )
            print("accountBalance : ", accountBalance)
            print("주문가능 금액 : ",moneyForOrder)
            print("종목당 주문금액 : " ,moneyFor_Once_Order)
            
            if moneyForOrder > 10000: #매수할 돈이 없으면 못함 (즉, 한번 매수 했으면 더이상 매수 못함)
                #금일 급등 후모 종목수 만큼 매수
                for targetCoin in tickerForOrder:
                    # print("매수")
                    curr_price = get_current_price(targetCoin)
                    cnt = round(moneyFor_Once_Order/curr_price,4)
                    result = bithumb.buy_market_order(targetCoin, cnt)
                    print("매수", result)
                # if moneyForOrder < 5000:
                #     print("매수해야함")
                    # buyprice = get_current_price("BTC")
        
        # ToDoList
        #10% 이상 오른 종목 판단은 나중에.........  
        # 00:00 < 현재 < 00:01에서 %10(변수) 상승 시 전량 매도
        # elif end_time < now < end_time2:
        #     up_1 = 0.1
        #     current_price = get_current_price("BTC") # 현재 coin 금액
        #     if current_price > buyprice + buyprice * up_1: # 현재금액이 구매금액의 ?% 이상 일때
        #         btc = get_balance("BTC")[0] # 코인 보유량
        #         if btc > 0.00008:
        #             bithumb.sell_market_order("BTC", btc) 
        # 00:01 < 현재 일때 전량 매도
        elif end_time2 < now:
            for targetCoin in tickerForOrder:
                 # 타겟코인 보유량
                coinBalance = get_balance(targetCoin)[0]
                if coinBalance > 0:
                    # print("매도")
                    sellResult = bithumb.sell_market_order(targetCoin, coinBalance)
                    print("매도", sellResult)
                                
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
