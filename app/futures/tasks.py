from main.celery import app
from .services import (
    SetBinanceFuturesSymbols, SetBybitFuturesSymbols, SetOkxFuturesSymbols,
    SetBitgetFuturesSymbols, SetKucoinFuturesSymbols, SetHuobiFuturesSymbols,
    SetGateioFuturesSymbols
)

@app.task
def set_futures_binance():
    task = SetBinanceFuturesSymbols()
    return task()

@app.task
def set_futures_bybit():
    task = SetBybitFuturesSymbols()
    return task()

@app.task
def set_futures_okx():
    task = SetOkxFuturesSymbols()
    return task()

@app.task
def set_futures_bitget():
    task = SetBitgetFuturesSymbols()
    return task()

@app.task
def set_futures_kucoin():
    task = SetKucoinFuturesSymbols()
    return task()

@app.task
def set_futures_huobi():
    task = SetHuobiFuturesSymbols()
    return task()

@app.task
def set_futures_gateio():
    task = SetGateioFuturesSymbols()
    return task()

def set_all_exchanges_futures():
    exchange_tasks = [
        SetBinanceFuturesSymbols(),
        SetBybitFuturesSymbols(),
        SetOkxFuturesSymbols(),
        SetBitgetFuturesSymbols(),
        SetKucoinFuturesSymbols(),
        SetHuobiFuturesSymbols(),
        SetGateioFuturesSymbols(),
    ]

    for task in exchange_tasks:
        task()

    return "All exchange futures symbols set successfully."

set_all_exchanges_futures()