from main.celery import app
from .services import ParserSimple, ParserTwoRequest
from futures.services import RedisKyesFuturesSymbols

from django.core.cache import cache

from parsers.info.accepts.okx import accept as okx_accept
from parsers.info.accepts.binance import accept as binance_accept
from parsers.info.accepts.bybit import accept as bybit_accept
from parsers.info.accepts.huobi import accept as huobi_accept
from parsers.info.accepts.kucoin import accept as kucoin_accept
from parsers.info.accepts.gateio import accept as gateio_accept
from parsers.info.accepts.mexc import accept as mexc_accept
from parsers.info.accepts.bitget import accept as bitget_accept

from parsers.info.networks.info import bybit as network_bybit
from parsers.info.networks.info import binance as network_binance
from parsers.info.networks.info import kucoin as network_kucoin
from parsers.info.networks.info import huobi as network_huobi
from parsers.info.networks.info import bitget as network_bitget
from parsers.info.networks.info import gateio as network_gateio
from parsers.info.networks.info import okx as network_okx


@app.task
def okx():
    """
    Parser spot price of exchange Okx
    """
    key = 'okx'
    futures_keys = RedisKyesFuturesSymbols()
    okx = {
        "url": "https://www.okx.com/api/v5/market/tickers?instType=SPOT",
        "path": ['data'],
        "accept": okx_accept,
        "price": "last",
        "symbol": "instId", 
        "ex": key,
        "network": network_okx, 
        "futures_set": cache.get(futures_keys.key_okx_futures), 

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

@app.task
def binance():
    """
    Parser spot price of exchange Binance
    """
    key = 'binance'
    futures_keys = RedisKyesFuturesSymbols()
    binance = {
        "url": "https://api.binance.com/api/v3/ticker/price",
        "accept": binance_accept,
        "futures_symbols": set(),
        "price": "price",
        "symbol": "symbol", 
        "ex": key,
        "network": network_binance, 
        "futures_set": cache.get(futures_keys.key_binance_futures), 

        "add_url": "https://api.binance.com/api/v3/ticker/bookTicker",
        "ask_qty": "askQty", 
        "bid_qty": "bidQty", 
        "ask_price": "askPrice", 
        "bid_price": "bidPrice", 
    }
    
    binance = ParserTwoRequest(key, binance)
    return binance.get_cleaned_data()

@app.task
def bybit():
    """
    Parser spot price of exchange Bybit
    """
    key = 'bybit'
    futures_keys = RedisKyesFuturesSymbols()
    bybit = {
        "url": "https://api.bybit.com/spot/v3/public/quote/ticker/price",
        "path": ['result', 'list'],
        "accept": bybit_accept,
        "futures_symbols": set(),
        "price": "price",
        "symbol": "symbol", 
        "ex": key,
        "network": network_bybit, 
        "futures_set": cache.get(futures_keys.key_bybit_futures), 

        "add_url": "https://api.bybit.com/spot/v3/public/quote/ticker/bookTicker",
        "ask_qty": "askQty", 
        "bid_qty": "bidQty", 
        "ask_price": "askPrice", 
        "bid_price": "bidPrice", 
    }

    bybit = ParserTwoRequest(key, bybit)
    return bybit.get_cleaned_data()

@app.task
def huobi():
    """
    Parser spot price of exchange Huobi
    """
    key = 'huobi'
    futures_keys = RedisKyesFuturesSymbols()
    huobi = {
        "url": "https://api-aws.huobi.pro/market/tickers",
        "path": ['data'],
        "accept": huobi_accept,
        "futures_symbols": set(),
        "price": "close",
        "symbol": "symbol", 
        "ex": key, 
        "network": network_huobi, 
        "futures_set": cache.get(futures_keys.key_huobi_futures), 

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
    futures_keys = RedisKyesFuturesSymbols()
    kucoin = {
        "url": "https://api.kucoin.com/api/v1/market/allTickers",
        "path": ['data', 'ticker'],
        "accept": kucoin_accept,
        "futures_symbols": set(),
        "price": "last",
        "symbol": "symbol", 
        "ex": key, 
        "network": network_kucoin, 
        "futures_set": cache.get(futures_keys.key_kucoin_futures), 

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

        def append_action_qty(self, qty: str) -> str:
            """
            Override class because sometimes qty are not valid
            """
            return float(qty) / 1440

    kucoin = KucoinParser(key, kucoin)
    return kucoin.get_cleaned_data()

@app.task
def gateio():
    """
    Parser spot price of exchange Gate.io
    """
    key = 'gateio'
    futures_keys = RedisKyesFuturesSymbols()
    gateio = {
        "url": "https://api.gateio.ws/api/v4/spot/tickers",
        "accept": gateio_accept,
        "futures_symbols": set(),
        "price": "last",
        "symbol": "currency_pair",
        "ex": key,
        "network": network_gateio, 
        "futures_set": cache.get(futures_keys.key_gateio_futures), 

        "ask_qty": "quote_volume", 
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

        def append_action_qty(self, qty: float) -> float:
            """
            Override class because sometimes qty are not valid
            """
            return float(qty) / 1440

    gateio = GateioParser(key, gateio)
    return gateio.get_cleaned_data()

@app.task
def bitget():
    """
    Parser spot price of exchange BitGet
    """
    key = 'bitget'
    futures_keys = RedisKyesFuturesSymbols()
    bitget = {
        "url": "https://api.bitget.com/api/spot/v1/market/tickers",
        "path": ['data'],
        "accept": bitget_accept,
        "futures_symbols": set(),
        "price": "close",
        "symbol": "symbol", 
        "ex": key,
        "network": network_bitget, 
        "futures_set": cache.get(futures_keys.key_bitget_futures), 

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