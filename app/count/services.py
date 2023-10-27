import hashlib

from django.core.cache import cache


key_mexc = 'mexc'
key_binance = 'binance'
key_bybit = 'bybit'
key_okx = 'okx'
key_kucoin = 'kucoin'
key_huobi = 'huobi'
key_bitget = 'bitget'
key_gateio = 'gateio'


class Count:
    def __init__(self):
        self.time_cash = 60
        
        self.fee = 0.15
        
        self.round = 4
        self.if_small_num = '0.000...'

        self._bid = 'bid_price'
        self._ask = 'ask_price'
        self.first = {'type': 'SELL-BUY', 'buy': self._bid, 'sell': self._ask}
        self.second = {'type': 'SELL-SELL', 'buy': self._bid, 'sell': self._bid}
        self.third = {'type': 'BUY-BUY', 'buy': self._ask, 'sell': self._ask}
        self.four = {'type': 'BUY-SELL', 'buy': self._ask, 'sell': self._bid}


    def get_data(self):
        dict = {}

        dict[key_okx] = cache.get(key_okx)
        dict[key_kucoin] = cache.get(key_kucoin)
        dict[key_huobi] = cache.get(key_huobi)
        dict[key_gateio] = cache.get(key_gateio)
        dict[key_bitget] = cache.get(key_bitget)
        dict[key_bybit] = cache.get(key_bybit)
        dict[key_bitget] = cache.get(key_bitget)
        
        return dict

    # def save_db(self, all_data: dict):
    #     for key, data in all_data.items():
    #         cache.set(key, data, self.time_cash)

    def calculate_spread(self, price_first, price_second):
        spread = ((price_second * price_first) - 1) * 100
        spread = spread - self.fee
        return round(spread, 2)

    def custom_round(self, price):
        price = round(price, self.round)
        if price == 0:
            return self.if_small_num
        return price

    def create_hash(self, base_first, base_second, ex_first, ex_second):
        for_hash = f'{ex_first}--{ex_second}--{base_first}--{base_second}'

        hash_object = hashlib.sha256()
        hash_object.update(for_hash.encode())
        hashed = hash_object.hexdigest()
        return hashed

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
    
    def create_key(self, type, ex_first, ex_second):
        return f'{type}--{ex_first}--{ex_second}'

    def count(self, first_info, second_info, info):
        n = 0
        
        all_data = []
        response = self.record()

        ex_first = first_info['ex']
        ex_second = second_info['ex']
        first_price_key = info['buy']
        second_price_key = info['sell']
        type_trade = info['type']

        first_data = first_info.pop('data')
        second_data = second_info.pop('data')

        for ad_first in first_data.values():
            if ad_first.get('fake') is True:
                continue
            
            base_first = ad_first['base']
            quote_first = ad_first['quote']
            price_first = ad_first[first_price_key]

            response['first']['exchange'] = ex_second
            response['first']['base'] = base_first
            response['first']['quote'] = quote_first
            response['first']['price'] = self.custom_round(price_first)
            response['first']['full_price'] = price_first
            response['first']['bid_qty'] = ad_first['bid_qty']
            response['first']['ask_qty'] = ad_first['ask_qty']
            
            for ad_second in second_data.values():
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

                response['second']['exchange'] = ex_first
                response['second']['base'] = base_second
                response['second']['quote'] = quote_second
                response['second']['price'] = self.custom_round(price_second)
                response['second']['full_price'] = price_second
                response['second']['bid_qty'] = ad_first['bid_qty']
                response['second']['ask_qty'] = ad_first['ask_qty']

                response['spread'] = spread
                response['hash'] = self.create_hash(base_first, base_second, ex_first, ex_second)

                all_data.append(response)
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

