import hashlib

from main.celery import app
key_best_rates = 'rates'
key_binance = 'binance'
key_bybit = 'bybit'
key_okx = 'okx'
key_kucoin = 'kucoin'
key_huobi = 'huobi'
base_token = [
    'USDT',
    'USDC',
]
from best_change_zip.models import LinksCryptoInfo
from best_change_parsing.models import LinksExchangeInfo
from django.core.cache import cache


def unique_keys():
    unique_keys = {}

    for token in base_token:
        key = f'{token}'
        unique_keys[key] = []
    return unique_keys


def calculate_spread_with_fee(ad_price_first, best_price, ad_price_second):
    fee = 0.15
    spread_with_fee = (ad_price_first * best_price * ad_price_second - 1) * 100
    return spread_with_fee


def custom_round_func(price):
    price = round(price, 5)
    if price == 0:
        return '0.000...'
    return price


def get_data_from_redis(key):
    data = cache.get(key)
    return data


def get_crypto_info_dict():
    crypto_info_objects = LinksCryptoInfo.objects.all()

    crypto_info_dict = {}
    for obj in crypto_info_objects:
        crypto_info_dict[obj.crypto_id] = {
            'crypto_name': obj.crypto_name,
            'abbr': obj.abbr,
            'id': obj.crypto_id,
        }
    return crypto_info_dict


def get_exchange_info_dict():
    exchange_info_objects = LinksExchangeInfo.objects.all().values(
        'exchange_id', 
        'exchange_name', 
        'info_age', 
        'info_star',
        'info_verification', 
        'info_registration',
    )

    exchange_info_dict = {}
    for obj in exchange_info_objects:
        exchange_info_dict[obj['exchange_id']] = {
            'exchange_id': obj['exchange_id'],
            'exchange_name': obj['exchange_name'],
            'info_age': obj['info_age'],
            'info_star': obj['info_star'],
            'info_verification': obj['info_verification'],
            'info_registration': obj['info_registration'],
            
            # 'info_reverse': obj['info_reverse'],
            # 'addition_floating': obj['addition_floating'],
            # 'addition_verifying': obj['addition_verifying'],
            # 'addition_manual': obj['addition_manual'],
            # 'addition_percent': obj['addition_percent'],
            # 'addition_otherin': obj['addition_otherin'],
            # 'addition_reg': obj['addition_reg'],
        }
    return exchange_info_dict


def calculate_hash(exchange, base_token, best_give_number, best_get_number, exchange_id):
    for_hash = (
        f'{exchange}-'
        f'-{base_token}-'
        f'-{best_give_number}-'
        f'-{best_get_number}-'
        f'-{exchange_id}'
    )
    hash_object = hashlib.sha256()
    hash_object.update(for_hash.encode())
    hashed = hash_object.hexdigest()
    return hashed


def count_link_3_actions(dict, best_change_data, data, exchange):
    n = 0
    crypto_info_dict = get_crypto_info_dict()
    exchange_info_dict = get_exchange_info_dict()

    for token_first, ad_first in data.items():
        ad_give_first = ad_first['base']
        if ad_give_first not in base_token:
            continue
        ad_get_first = ad_first['quote']
        ad_price_first = ad_first['price']
        real_price_first = ad_first['price']

        for best_row in best_change_data:
            best_give = best_row['crypto_name_give']
            if ad_get_first != best_give:
                continue
            best_give_number = best_row['crypto_number_give']
            best_get_number = best_row['crypto_number_get']
            best_get = best_row['crypto_name_get']
            best_price = best_row['price']

            for token_second, ad_second in data.items():
                ad_give_second = ad_second['base']
                ad_get_second = ad_second['quote']
                if best_get != ad_give_second or ad_get_second != ad_give_first:
                    continue
                ad_price_second = ad_second['ask_price']
                real_price_second = ad_second['ask_price']

                spread_with_fee = calculate_spread_with_fee(
                    ad_price_first,
                    best_price,
                    ad_price_second
                )

                spread_with_fee = round(spread_with_fee, 2)

                if spread_with_fee < 0.2:
                    continue

                exchange_id = best_row['exchange_id']
                hashed = calculate_hash(
                    exchange,
                    ad_give_first,
                    best_give_number,
                    best_get_number,
                    exchange_id
                )

                record = {
                    "first": {
                        "base": ad_give_first,
                        "price": custom_round_func(real_price_first),
                        "price_full": '{:13f}'.format(real_price_first),
                        "qty": ad_second['ask_qty'] * real_price_first,
                    },
                    "best": {
                        "price": custom_round_func(best_price),
                        "price_full": '{:13f}'.format(best_price),
                        "base": crypto_info_dict[best_get_number],
                        "quote": crypto_info_dict[best_give_number],
                        "exchange_info": exchange_info_dict[exchange_id],
                        "available": best_row['available'],
                        "negative_reviews": best_row['negative_reviews'],
                        "positive_reviews": best_row['positive_reviews'],
                        "lim_min": round(best_row['lim_min'] * real_price_first, 3),
                    },
                    "second": {
                        "base": ad_get_second,
                        "price": custom_round_func(real_price_second),
                        "price_full": '{:13f}'.format(real_price_second),
                        "qty": ad_second['ask_qty'] * real_price_second,
                    },
                    "spread": spread_with_fee,
                    "exchange": exchange,
                    "hash": hashed,
                }
                dict[ad_give_first].append(record)
                n += 1
    return n


def sorted_dict(dict):
    sorted_data = sorted(
        dict,
        key=lambda x: x['spread_with_fee'],
        reverse=True
    )

    grouped_objects = {}
    
    for obj in sorted_data:
        key = (
            f"{obj['ad_give_first']}--"
            f"{obj['ad_get_first']['abbr']}--"
            f"{obj['ad_give_second']['abbr']}--"
            f"{obj['ad_get_second']}"
        )

        if key not in grouped_objects:
            grouped_objects[key] = []
        grouped_objects[key].append(obj)

    return grouped_objects


def save_db(data, exchange):
    time_cash = 60
    for key, dict in data.items():
        sort_data = sorted_dict(dict)
        key = f'{exchange}--{key}'
        cache.set(key, sort_data, time_cash)


def process_data(exchange, key):
    best_change_data = get_data_from_redis(key_best_rates)
    if not best_change_data:
        return f'No data Best Change!'

    dict = unique_keys()
    data = get_data_from_redis(key)
    if not data:
        return f'No data {exchange}!'

    len_links = count_link_3_actions(dict, best_change_data, data, exchange)
    save_db(dict, exchange)
    return f'{exchange}: {len_links}'


@app.task
def binance():
    return process_data('binance', key_binance)

@app.task
def bybit():
    return process_data('bybit', key_bybit)

@app.task
def huobi():
    return process_data('huobi', key_huobi)

@app.task
def kucoin():
    return process_data('kucoin', key_kucoin)

@app.task
def okx():
    return process_data('okx', key_okx)
