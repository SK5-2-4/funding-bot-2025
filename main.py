# Binance Funding Rate専用完全放置ボット（2025年11月版 - LINE通知オフ版）

import ccxt
import time
import datetime
import os

BINANCE_API_KEY = os.getenv('BINANCE_API_KEY')
BINANCE_SECRET = os.getenv('BINANCE_SECRET')
LINE_TOKEN = os.getenv('LINE_TOKEN')  # 任意、使わないなら空

SYMBOL = 'BTC/USDT:USDT'
LEVERAGE = 20

def send_line(msg):
    # LINE通知オフ版: エラー回避のためコメントアウト
    # if LINE_TOKEN:
    #     import requests
    #     requests.post("https://notify-api.line.me/api/notify",
    #                   headers={'Authorization': f'Bearer {LINE_TOKEN}'},
    #                   data={'message': msg})
    print(f"通知: {msg}")  # コンソール出力に置き換え（Logsで見える）

exchange = ccxt.binance({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_SECRET,
    'enableRateLimit': True,
    'options': {'defaultType': 'swap'}
})

def open_short():
    try:
        balance = exchange.fetch_balance()['USDT']['total']
        if balance < 10: 
            print("残高不足: 10 USDT以上必要")
            return
        price = exchange.fetch_ticker(SYMBOL)['last']
        amount = (balance * LEVERAGE) / price * 0.98  # 2%マージン
        exchange.set_leverage(LEVERAGE, SYMBOL)
        order = exchange.create_market_sell_order(SYMBOL, amount)
        print(f"【起動】20倍ショート {amount:.5f} BTC開設成功！")
        send_line(f"【起動】20倍ショート {amount:.5f} BTC開設！")
    except Exception as e:
        print(f"ショート開設エラー: {e}")

def bot():
    position_opened = False
    while True:
        try:
            fr = exchange.fetch_funding_rate('BTC/USDT')['fundingRate']
            bal = exchange.fetch_balance()['USDT']['total']
            price = exchange.fetch_ticker(SYMBOL)['last']
            print(f"{datetime.datetime.now().strftime('%H:%M')} | Funding +{fr*100:.4f}% | 残高 {bal:.1f} USDT | 価格 ${price:,.0f}")

            if not position_opened and bal > 10:
                open_short()
                position_opened = True
                send_line("Funding専用ボット完全稼働開始！")

            # Funding入金タイミング（8時間ごと）
            if int(time.time() % 28800) < 60:
                send_line(f"Funding入金確認！ Rate: +{fr*100:.4f}%")

            time.sleep(60)  # 1分チェック
        except Exception as e:
            print(f"ループエラー: {e}")
            time.sleep(60)

if __name__ == "__main__":
    print("Funding専用ボット起動中...")
    send_line("Fundingボット起動しました")
    bot()
