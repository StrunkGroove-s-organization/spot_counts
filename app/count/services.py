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
        pass

    def get_data(self, dict, key):
        data = cache.get(key)
        if data is None:
            return f'Data is None {key}'
        dict[key] = data


    def count(self):
        dict = {}

        self.get_data(dict, key_okx)
        self.get_data(dict, key_kucoin)
        self.get_data(dict, key_huobi)
        self.get_data(dict, key_gateio)
        self.get_data(dict, key_bitget)
