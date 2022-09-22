import time
import pyupbit
import telegram

access = ""
secret = ""

bot = telegram.Bot(token='')
chat_id = 

inter = "minute60"
def get_ma(ticker):
    dfma = pyupbit.get_ohlcv(ticker, interval=inter, count=15, period=1)
    ma5 = dfma['close'].rolling(3).mean().iloc[-1]
    ma51 = dfma['close'].rolling(3).mean().iloc[-2]
    return ma5, ma51

def get_balance(ticker):
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    return pyupbit.get_current_price(ticker)

upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

btc_state = 0
eth_state = 0
btc_buy_price = 0
btc_sell_price = 0
eth_buy_price = 0
eth_sell_price = 0

btc_ini = get_balance("BTC")
eth_ini = get_balance("ETH")
krw = get_balance("KRW")
time.sleep(0.5)
btcma5, btcma51 = get_ma("KRW-BTC")
time.sleep(0.5)
ethma5, ethma51 = get_ma("KRW-ETH")
bot.sendMessage(chat_id=chat_id, text="재접속")
startmsg = "KRW : %d BTC : %.8f ETH : %.8f" % (krw , btc_ini, eth_ini)
bot.sendMessage(chat_id=chat_id, text=startmsg)

if btc_ini != 0 :
    btc_state = 1
    btc_buy_price = btc_ini
if eth_ini != 0 :
    eth_state = 1
    eth_buy_price = eth_ini

startmsg2 = "btcstate : %d ethstate : %d" % (btc_state, eth_state)
bot.sendMessage(chat_id=chat_id, text=startmsg2)

while True:
    try:
        current_priceBTC = get_current_price("KRW-BTC")
        btcfee = 5000 / current_priceBTC
        btc = get_balance("BTC")
        btcma5, btcma51 = get_ma("KRW-BTC")
        btcma51up = btcma51 * (1 + 0.004)
        btcma51dn = btcma51 * (1 - 0.004)
        time.sleep(0.1)

        current_priceETH = get_current_price("KRW-ETH")
        ethfee = 5000 / current_priceETH
        eth = get_balance("ETH")
        ethma5, ethma51= get_ma("KRW-ETH")
        ethma51up = ethma51 * (1 + 0.004)
        ethma51dn = ethma51 * (1 - 0.004)
        time.sleep(0.1)

        krw = get_balance("KRW")

        if btc_state == 0 and btcma5 > btcma51up:
            btcbuycall = 0
            if eth > ethfee :
                btcbuycall = btcbuycall + 1
            if krw > 5000 and btc < btcfee:
                upbit.buy_market_order("KRW-BTC", krw / (2-btcbuycall) * 0.9995)
                btc_buy_price = current_priceBTC
                btc_state = 1
                msg = "BTC 매수 = %.2f" % (btc_buy_price)
                bot.sendMessage(chat_id=chat_id, text=msg)
            time.sleep(1)

        if eth_state == 0 and ethma5 > ethma51up:
            ethbuycall = 0
            if btc > btcfee :
                ethbuycall = ethbuycall + 1
            if krw > 5000 and eth < ethfee:
                upbit.buy_market_order("KRW-ETH", krw / (2-ethbuycall) * 0.9995)
                eth_buy_price = current_priceETH
                eth_state = 1
                msg = "ETH 매수 = %.2f" % (eth_buy_price)
                bot.sendMessage(chat_id=chat_id, text=msg)
            time.sleep(1)

        if btcma5 < btcma51dn and btc_state == 1:
            if btc != 0 :
                upbit.sell_market_order("KRW-BTC", btc)
            btc_state = 0
            btc_sell_price = current_priceBTC
            cpt = ((btc_sell_price - btc_buy_price) / btc_buy_price) * 100
            msg = "BTC 매도 %.2f , 수익률 = %.2f %%" % (btc_sell_price, cpt)
            time.sleep(5)
            krwbtc = get_balance("KRW")
            msg3 = "남은현재돈 = %d 원" % (krwbtc)
            bot.sendMessage(chat_id=chat_id, text=msg)
            bot.sendMessage(chat_id=chat_id, text=msg3)

        if ethma5 < ethma51dn and eth_state == 1:
            if eth != 0:
                upbit.sell_market_order("KRW-ETH", eth)
            eth_sell_price = current_priceETH
            cpt = ((eth_sell_price - eth_buy_price) / eth_buy_price) * 100
            msg = "ETH 매도 %.2f , 수익률 = %.2f %%" % (eth_sell_price, cpt)
            time.sleep(5)
            krweth = get_balance("KRW")
            msg3 = "남은현재돈 = %d 원" % (krweth)
            eth_state = 0
            bot.sendMessage(chat_id=chat_id, text=msg)
            bot.sendMessage(chat_id=chat_id, text=msg3)
        time.sleep(60)

    except Exception as e:
        print(e)
        bot.sendMessage(chat_id=chat_id, text="HJ ERROR")
        time.sleep(1)
