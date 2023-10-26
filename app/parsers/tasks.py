from main.celery import app
from parsers.info.okx import accept as okx_accept
from parsers.info.binance import accept as binance_accept
from parsers.info.bybit import accept as bybit_accept
from parsers.info.huobi import accept as huobi_accept
from parsers.info.kucoin import accept as kucoin_accept
from parsers.info.gateio import accept as gateio_accept
from parsers.info.mexc import accept as mexc_accept
from parsers.info.bitget import accept as bitget_accept
from .services import ParserSimple


@app.task
def okx():
    """
    Parser spot price of exchange Okx
    """
    key = 'okx'
    okx = {
        "url": "https://www.okx.com/api/v5/market/tickers?instType=SPOT",
        "path": ['data'],
        "accept": okx_accept,
        "price": "last",
        "symbol": "instId", 
        "ex": key,

        "ask_qty": "askSz", 
        "bid_qty": "bidSz", 
        "ask_price": "askPx", 
        "bid_price": "bidPx", 
    }

    class OkxParser(ParserSimple):
        def append_action(self, token: str) -> str:
            """
            Removing extra characters from a character
            """
            return token.replace('-', '')
    
    okx = OkxParser(key, okx)
    return okx.get_cleaned_data()

# @app.task
# def binance():
#     """
#     Parser spot price of exchange Binance
#     """
#     key = 'binance'
#     binance = {
#         "url": "https://api.binance.com/api/v3/ticker/price",
#         "accept": binance_accept,
#         "price": "price",
#         "symbol": "symbol", 
#         "ex": key,

#         "add_url": "https://api.binance.com/api/v3/ticker/bookTicker",
#         "ask_qty": "askQty", 
#         "bid_qty": "bidQty", 
#         "ask_price": "askPrice", 
#         "bid_price": "bidPrice", 
#     }
    
#     binance = ParserBase(key, binance)
#     return binance.get_cleaned_data()

# @app.task
# def bybit():
#     """
#     Parser spot price of exchange Bybit
#     """
#     key = 'bybit'
#     bybit = {
#         "url": "https://api.bybit.com/spot/v3/public/quote/ticker/price",
#         "path": ['result', 'list'],
#         "accept": bybit_accept,
#         "price": "price",
#         "symbol": "symbol", 
#         "ex": key,

#         "add_url": "https://api.bybit.com/spot/v3/public/quote/ticker/bookTicker",
#         "ask_qty": "askQty", 
#         "bid_qty": "bidQty", 
#         "ask_price": "askPrice", 
#         "bid_price": "bidPrice", 
#     }

#     bybit = ParserBase(key, bybit)
#     return bybit.get_cleaned_data()

@app.task
def huobi():
    """
    Parser spot price of exchange Huobi
    """
    key = 'huobi'
    huobi = {
        "url": "https://api-aws.huobi.pro/market/tickers",
        "path": ['data'],
        "accept": huobi_accept,
        "price": "close",
        "symbol": "symbol", 
        "ex": key, 

        "ask_qty": "askSize", 
        "bid_qty": "bidSize", 
        "ask_price": "ask", 
        "bid_price": "bid", 
    }

    class HuobiParser(ParserSimple):
        def append_action(self, token: str) -> str:
            """
            Removing extra characters from a character
            """
            return token.upper()
        
    huobi = HuobiParser(key, huobi)
    return huobi.get_cleaned_data()

@app.task
def kucoin():
    """
    Parser spot price of exchange Kucoin
    """
    key = 'kucoin'
    kucoin = {
        "url": "https://api.kucoin.com/api/v1/market/allTickers",
        "path": ['data', 'ticker'],
        "accept": kucoin_accept,
        "price": "last",
        "symbol": "symbol", 
        "ex": key, 

        "ask_qty": "volValue", 
        "bid_qty": "volValue", 
        "ask_price": "sell", 
        "bid_price": "buy", 
    }

    class KucoinParser(ParserSimple):
        def append_action(self, token: str) -> str:
            """
            Removing extra characters from a character
            """
            return token.replace('-', '')
        
    kucoin = KucoinParser(key, kucoin)
    return kucoin.get_cleaned_data()

@app.task
def gateio():
    """
    Parser spot price of exchange Gate.io
    """
    key = 'gateio'
    gateio = {
        "url": "https://api.gateio.ws/api/v4/spot/tickers",
        "accept": gateio_accept,
        "price": "last",
        "symbol": "currency_pair",
        "ex": key,

        "ask_qty": "base_volume", 
        "bid_qty": "quote_volume", 
        "ask_price": "lowest_ask", 
        "bid_price": "highest_bid", 
    }

    class GateioParser(ParserSimple):
        def append_action(self, token: str) -> str:
            """
            Removing extra characters from a character
            """
            return token.replace('_', '')
        
    gateio = GateioParser(key, gateio)
    return gateio.get_cleaned_data()

@app.task
def bitget():
    """
    Parser spot price of exchange BitGet
    """
    key = 'bitget'
    bitget = {
        "url": "https://api.bitget.com/api/spot/v1/market/tickers",
        "path": ['data'],
        "accept": bitget_accept,
        "price": "close",
        "symbol": "symbol", 
        "ex": key,

        "ask_qty": "askSz", 
        "bid_qty": "bidSz", 
        "ask_price": "sellOne", 
        "bid_price": "buyOne", 
    }

    class BitGetParser(ParserSimple):
        pass
        
    bitget = BitGetParser(key, bitget)
    return bitget.get_cleaned_data()


### Не работают ###

# @app.task
# def mexc(): # Иногда ответ от сервера достигает до 2 минут
#     """
#     Parser of exchange Mexc
#     """
#     mexc = {
#         "url": "https://api.mexc.com/api/v3/ticker/price",
#         "accept": mexc_accept,
#         "price": "price",
#         "symbol": "symbol", 
#     }
        
#     key = 'mexc'
#     mexc = ParserBase(key, mexc)
#     return mexc.get_cleaned_data()