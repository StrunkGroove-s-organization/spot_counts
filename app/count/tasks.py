from main.celery import app
from .services import CountInTwo, CountInThree 


@app.task
def count_2():
    return CountInTwo().main()

@app.task
def binance():
    ex = key_binance = 'binance'
    dict = {
        "ex": ex,
        "key": key_binance,
    }
    return CountInThree(dict).main()

@app.task
def bybit():
    ex = key_bybit = 'bybit'
    dict = {
        "ex": ex,
        "key": key_bybit,
    }
    return CountInThree(dict).main()

@app.task
def huobi():
    ex = key_huobi = 'huobi'
    dict = {
        "ex": ex,
        "key": key_huobi,
    }
    return CountInThree(dict).main()

@app.task
def kucoin():
    ex = key_kucoin = 'kucoin'
    dict = {
        "ex": ex,
        "key": key_kucoin,
    }
    return CountInThree(dict).main()

@app.task
def okx():
    ex = key_okx = 'okx'
    dict = {
        "ex": ex,
        "key": key_okx,
    }
    return CountInThree(dict).main()