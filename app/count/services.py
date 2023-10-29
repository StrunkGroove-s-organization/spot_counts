import hashlib

from django.core.cache import cache

from best_change_zip.models import LinksCryptoInfo
from best_change_parsing.models import LinksExchangeInfo

key_mexc = 'mexc'
key_binance = 'binance'
key_bybit = 'bybit'
key_okx = 'okx'
key_kucoin = 'kucoin'
key_huobi = 'huobi'
key_bitget = 'bitget'
key_gateio = 'gateio'
key_best_rates = 'rates'


class Count:
    def __init__(self):
        self.fee = 0.15

        self.round_num = 4
        self.if_small_num = '0.000...'
        
        self.time_cash = 60

    def custom_round(self, price: float) -> float:
        price = round(price, self.round_num)
        if price == 0:
            return self.if_small_num
        return price

    def round_for_real(self, price: float) -> str:
        return '{:20f}'.format(price)

    def hashed(self, key) -> str:
        hash_object = hashlib.sha256()
        hash_object.update(key.encode())
        hashed = hash_object.hexdigest()
        return hashed
    

class CountInTwo(Count):
    def __init__(self):
        super().__init__()

        self._bid = 'bid_price'
        self._ask = 'ask_price'
        self.first = {'type': 'SELL-BUY', 'buy': self._bid, 'sell': self._ask}
        self.second = {'type': 'SELL-SELL', 'buy': self._bid, 'sell': self._bid}
        self.third = {'type': 'BUY-BUY', 'buy': self._ask, 'sell': self._ask}
        self.four = {'type': 'BUY-SELL', 'buy': self._ask, 'sell': self._bid}


    def get_data(self) -> dict:
        dict = {
            'okx': cache.get(key_okx),
            'huobi': cache.get(key_huobi),
            'bybit': cache.get(key_bybit),
            'kucoin': cache.get(key_kucoin),
            'gateio': cache.get(key_gateio),
            'bitget': cache.get(key_bitget),
            'binance': cache.get(key_binance),
        }
        return dict

    def calculate_spread(self, price_buy, price_sell) -> float:
        spread = (1 - (price_sell * price_buy)) * 100
        spread = spread - self.fee
        return round(spread, 2)

    def create_hash(self, base_first, base_second, ex_first, ex_second) -> str:
        key = f'{ex_first}--{ex_second}--{base_first}--{base_second}'
        return self.hashed(key)

    def record(self) -> dict:
        return {
            "first": {
                "exchange": str,
                "price": float,
                "full_price": float,
                "bid_qty": float,
                "ask_qty": float,
                'base': str,
                'quote': str,
            },
            "second": {
                "exchange": str,
                "price": float,
                "full_price": float,
                "bid_qty": float,
                "ask_qty": float,
                'base': str,
                'quote': str,
            },
            'spread': float,
            'hash': str,
        }
    
    def create_key(self, trade_type, ex_first, ex_second) -> str:
        return f'{trade_type}--{ex_first}--{ex_second}'

    def count(self, first_info, second_info, info):
        n = 0
        
        all_data = []

        ex_first = first_info['ex']
        ex_second = second_info['ex']
        first_price_key = info['buy']
        second_price_key = info['sell']
        type_trade = info['type']

        first_data = first_info.pop('data')
        second_data = second_info.pop('data')

        for key_buy, ad_first in first_data.items():
            if ad_first.get('fake') is True:
                continue
            
            base_first = ad_first['base']
            quote_first = ad_first['quote']
            price_first = ad_first[first_price_key]
            
            for key_sell, ad_second in second_data.items():
                base_second = ad_second['base']
                quote_second = ad_second['quote']

                if not (base_first == quote_second and quote_first == base_second): 
                    continue

                price_second = ad_second[second_price_key]

                spread = self.calculate_spread(price_first, price_second)
                if spread < 0.2: continue
                
                if ad_second.get('fake') is True:
                    base_second, quote_second = quote_second, base_second
                    price_second = 1 / price_second

                if price_first >= price_second:
                    first = 'first'
                    second = 'second'
                else:
                    second = 'first'
                    first = 'second'

                record = {
                    first: {
                        "exchange": ex_first,
                        "price": self.custom_round(price_first),
                        "full_price": self.round_for_real(price_first),
                        "bid_qty": ad_first['bid_qty'],
                        "ask_qty": ad_first['ask_qty'],
                        'base': base_first,
                        'quote': quote_first,
                    },
                    second: {
                        "exchange": ex_second,
                        "price": self.custom_round(price_second),
                        "full_price": self.round_for_real(price_second),
                        "bid_qty": ad_second['bid_qty'],
                        "ask_qty": ad_second['ask_qty'],
                        'base': base_second,
                        'quote': quote_second,
                    },
                    'spread': spread,
                    'hash': self.create_hash(base_first, base_second, ex_first, ex_second),
                }
                
                all_data.append(record)
                n += 1

        key = self.create_key(type_trade, ex_first, ex_second)
        cache.set(key, all_data, self.time_cash)
        return n

    def count_links(self, info: dict, data: dict) -> int:
        n = 0

        for ex_first, data_first in data.items():
            for ex_second, data_second in data.items():
                if ex_first == ex_second:
                    continue

                first_info = {"ex": ex_first, "data": data_first}
                second_info = {"ex": ex_second, "data": data_second}

                n += self.count(first_info, second_info, info)
        return n
    
    def main(self):
        data = self.get_data()
        
        n = 0
        n += self.count_links(self.first, data)
        n += self.count_links(self.second, data)
        n += self.count_links(self.third, data)
        n += self.count_links(self.four, data)
        return n 


class CountInThree(Count):
    def __init__(self, dict: dict):
        super().__init__()
        self.fee = 0.15
        self.base_token = ['USDT', 'USDC']
        self.key_best = key_best_rates
        self.key = dict['key']
        self.ex = dict['ex']

    def calculate_spread(self, price_buy: float,
                         best_price: float, price_sell: float) -> float:
        price = (price_buy * best_price * price_sell - 1) * 100 - self.fee
        return round(price, 2)
    
    def get_crypto_info(self) -> dict:
        crypto_info_objects = LinksCryptoInfo.objects.all()

        crypto_info_dict = {}
        for obj in crypto_info_objects:
            crypto_info_dict[obj.crypto_id] = {
                'crypto_name': obj.crypto_name,
                'abbr': obj.abbr,
                'id': obj.crypto_id,
            }
        return crypto_info_dict
    
    def get_exchange_info(self) -> dict:
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
            }
        return exchange_info_dict
    
    def create_hash(self, exchange, base_token, best_base, best_quote, best_exchange_id) -> str:
        key = (
            f'{exchange}--{base_token}--{best_base}--{best_quote}--{best_exchange_id}'
        )
        return self.hashed(key)

    def unique_keys(self) -> dict:
        unique_keys = {}

        for token in self.base_token:
            unique_keys[token] = []
        return unique_keys

    def record(self) -> dict:
        return {
            "first": {
                "base": str,
                "price": float,
                "price_full": float,
                "qty": float,
            },
            "best": {
                "price": float,
                "price_full": float,
                "base": str,
                "quote": str,
                "exchange_info": dict,
                "available": float,
                "negative_reviews": float,
                "positive_reviews": float,
                "lim_min": float,
            },
            "second": {
                "quote": str,
                "price": float,
                "price_full": float,
                "qty": float,
            },
            "spread": float,
            "exchange": str,
            "hash": str,
        }
    
    def count(self, best_data: dict, data: dict) -> dict:
        crypto_info = self.get_crypto_info()
        exchange_info = self.get_exchange_info()

        list_data = self.unique_keys()
        record = self.record()
        n = 0
        for ad_buy in data.values():
            base_buy = ad_buy['base']
            if base_buy not in self.base_token: continue

            quote_buy = ad_buy['quote']
            price_buy = ad_buy['price']

            for best in best_data:
                best_base = best['crypto_name_give']
                if quote_buy != best_base: continue

                best_base_num = best['crypto_number_give']
                best_quote_num = best['crypto_number_get']
                best_quote = best['crypto_name_get']
                best_id = best['exchange_id']
                best_price = best['price']

                for ad_sell in data.values():
                    base_sell = ad_sell['base']
                    quote_sell = ad_sell['quote']
                    if best_quote != base_sell or quote_sell != base_buy: continue

                    price_sell = ad_sell['ask_price']

                    spread = self.calculate_spread(price_buy, best_price, price_sell)
                    if spread < 0.2: continue

                    exchange_id = best['exchange_id']
                    hashed = self.create_hash(
                        self.ex, base_buy, best_base_num, best_quote_num, best_id
                    )
                    
                    record = {
                        "first": {
                            "base": base_buy,
                            "price": self.custom_round(price_buy),
                            "price_full": self.round_for_real(price_buy),
                            "qty": ad_buy['ask_qty'] * price_buy,
                        },
                        "best": {
                            "price": self.custom_round(best_price),
                            "price_full": self.round_for_real(best_price),
                            "base": crypto_info[best_base_num],
                            "quote": crypto_info[best_quote_num],
                            "exchange_info": exchange_info[exchange_id],
                            "available": best['available']
,
                            "negative_reviews": best['negative_reviews'],
                            "positive_reviews": best['positive_reviews'],
                            "lim_min": round(best['lim_min'] * best_price, 3),
                        },
                        "second": {
                            "quote": quote_sell,
                            "price": self.custom_round(price_sell),
                            "price_full": self.round_for_real(price_sell),
                            "qty": ad_sell['ask_qty'] * price_sell,
                        },
                        "spread": spread,
                        "exchange": self.ex,
                        "hash": hashed,
                    }

                    n += 1
                    list_data[base_buy].append(record)
        
        for base_buy, data in list_data.items():
            key = f'{self.ex}--{base_buy}'
            cache.set(key, data, self.time_cash)
        return n

    def main(self):
        best_data = cache.get(self.key_best)
        if not best_data: return None

        ex_data = cache.get(self.key)
        if not ex_data: return None

        n = self.count(best_data, ex_data)

        return f'{self.key}: {n}'