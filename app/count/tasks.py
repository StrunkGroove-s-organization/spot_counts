import hashlib

from main.celery import app
from django.core.cache import cache


key_mexc = 'mexc'
key_binance = 'binance'
key_bybit = 'bybit'
key_okx = 'okx'
key_kucoin = 'kucoin'
key_huobi = 'huobi'
key_bitget = 'bitget'
key_gateio = 'gateio'


def unique_keys(all_ex):
    unique_keys = {}

    for ex_first in all_ex:
        for ex_second in all_ex:
            key = f'{ex_first}--{ex_second}'
            unique_keys[key] = []
    return unique_keys


def calculate_spread(price_first, price_second):
    fee = 0.15
    spread = ((price_second * price_first) - 1) * 100
    spread = spread - fee
    return spread


def custom_round_func(price):
    price = round(price, 4)
    if price == 0:
        return '0.000...'
    return price


def count(ex_first, ex_second, data_first, data_second, dict, first_key, second_key):
    def create_hash():
        for_hash = (
            f'{ex_first}-'
            f'-{ex_second}-'
            f'-{base_first}-'
            f'-{quote_first}'
        )
        hash_object = hashlib.sha256()
        hash_object.update(for_hash.encode())
        hashed = hash_object.hexdigest()
        return hashed

    def create_record():
        return {
            "first": {
                "exchange": ex_first,
                "price": custom_round_func(price_first),
                "full_price": price_first,
                "bid_qty": bid_qty_first,
                "ask_qty": ask_qty_first,
                'base': base_first,
                'quote': quote_first,
            },
            "second": {
                "exchange": ex_second,
                "price": custom_round_func(price_second),
                "full_price": price_second,
                "bid_qty": bid_qty_second,
                "ask_qty": ask_qty_second,
                'base': base_second,
                'quote': quote_second,
            },
            'spread': spread,
            'hash': create_hash(),
        }

    n = 0
    key = f'{ex_first}--{ex_second}'

    for ad_first in data_first.values():
        
        base_first = ad_first['base']
        quote_first = ad_first['quote']
        if ad_first['fake'] is True:
            continue
        
        for ad_second in data_second.values():
            base_second = ad_second['base']
            quote_second = ad_second['quote']

            if not (base_first == quote_second and quote_first == base_second): 
                continue

            price_first = ad_first[first_key]
            bid_qty_first = ad_first['bid_qty']
            ask_qty_first = ad_first['ask_qty']

            price_second = ad_second[second_key]
            bid_qty_second = ad_second['bid_qty']
            ask_qty_second = ad_second['ask_qty']

            spread = calculate_spread(price_first, price_second)
            # if spread < 0.2: continue
            if spread < 0: continue
            dict[key].append(create_record())
            n += 1
    return n


def sorted_dict(dict):
    sorted(
        dict,
        key=lambda x: x['spread'],
        reverse=True
    )


def save_db(data, type_trade):
    time_cash = 60
    for key, dict in data.items():
        key = f'{type_trade}--{key}'
        sorted_dict(dict)
        cache.set(key, dict, time_cash)


@app.task
def main():
    def count_links(type, key_first, key_second):
        dict = unique_keys(exchanges)
        n = 0
        for ex_first, data_first in data.items():
            for ex_second, data_second in data.items():
                n += count(ex_first, ex_second, data_first, data_second, dict, key_first, key_second)
        save_db(dict, type)
        return n

    def get_data(all_data, exchanges, key):
        data = cache.get(key)
        if not data:
            return f'Data is None {key}'
        all_data[key] = data
        exchanges.append(key)

    data = {}
    exchanges = []
    # get_data(data, exchanges, key_binance)
    # get_data(data, exchanges, key_bybit)
    get_data(data, exchanges, key_okx)
    get_data(data, exchanges, key_kucoin)
    get_data(data, exchanges, key_huobi)
    get_data(data, exchanges, key_gateio)
    get_data(data, exchanges, key_bitget)
    # get_data(data, exchanges, key_pancake)

    if len(data) == 0:
        return 'All data is None!'

    bid = 'bid_price'
    ask = 'ask_price'
    
    n = 0
    n += count_links('SELL-BUY', bid, ask)
    n += count_links('SELL-SELL', bid, bid)
    n += count_links('BUY-BUY', ask, ask)
    n += count_links('BUY-SELL', ask, bid)
    return n