# Binance Funding Rate専用完全放置ボット（2025年11月版）

import ccxt
import time
import datetime
import os
import threading
import requests

BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_SECRET = os.getenv('BINANCE_SECRET')
LINE_TOKEN = os.getenv('LINE_TOKEN')

SYMBOL = 'BTC/USDT:USDT'
LEVERAGE = 20

def send_line(msg):
    if LINE_TOKEN:
        requests.post("https://notify-api.line.me/api/notify",
                      headers={'Authorization': f'Bearer {LINE_TOKEN}'},
                      data={'message': msg})

exchange = ccxt.binance({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_SECRET,
    'enableRateLimit': True,
    'options': {'defaultType': 'swap'}
})

def open_short():
    balance = exchange.fetch_balance()['USDT']['total']
    if balance < 10: return
    price = exchange.fetch_ticker(SYMBOL)['last']
    amount = (balance * LEVERAGE) / price * 0.98
    exchange.set_leverage(LEVERAGE, SYMBOL)
    exchange.create_market_sell_order(SYMBOL, amount)
    send_line(f"【起動】20倍ショート {amount:.5f} BTC開設！")

def bot():
    while True:
        try:
            fr = exchange.fetch_funding_rate('BTC/USDT')['fundingRate']
            bal = exchange.fetch_balance()['USDT']['total']
            price = exchange.fetch_ticker(SYMBOL)['last']
            print(f"{datetime.datetime.now().strftime('%H:%M')} | Funding +{fr*100:.4f}% | 残高 {bal:.1f} USDT")

            if not hasattr(bot, 'done'):
                open_short()
                bot.done = True
                send_line("Funding専用ボット完全稼働開始！")

            time.sleep(60)
        except Exception as e:
            print("エラー:", e)
            time.sleep(60)

if __name__ == "__main__":
    send_line("Fundingボット起動しました")
    threading.Thread(target=bot, daemon=True).start()
    while True: time.sleep(1)
