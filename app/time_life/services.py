from itertools import product
from datetime import datetime

from django.core.cache import cache
from django.db import transaction

from .models import TimeLifeModel 
from count.services import CountInTwo


class FillDataBaseTimeLife(CountInTwo):
    def __init__(self):
        self.exchanges = ['binance', 'bybit', 'huobi', 'kucoin', 'okx', 
                          'bitget', 'pancake', 'gateio']
        self.trade_types = ['SELL-BUY', 'SELL-SELL', 'BUY-BUY', 'BUY-SELL']

    def get_coins(self):
        from parsers.info.accepts.okx import accept as okx_accept
        from parsers.info.accepts.bybit import accept as bybit_accept
        from parsers.info.accepts.huobi import accept as huobi_accept
        from parsers.info.accepts.kucoin import accept as kucoin_accept
        from parsers.info.accepts.gateio import accept as gateio_accept
        from parsers.info.accepts.bitget import accept as bitget_accept
        from parsers.infoaccepts.binance import accept as binance_accept

        accepts = [
            okx_accept, bybit_accept, huobi_accept,
            kucoin_accept, gateio_accept, bitget_accept, binance_accept
        ]

        merged_dict = {}

        for accept in accepts:
            merged_dict.update(accept)

        return list(set(merged_dict.keys()))

    def main(self):
        combinations = product(
            self.trade_types,
            self.get_coins(),
            self.exchanges,
            self.exchanges,
        )
        
        with transaction.atomic():
            for combination in combinations:
                unique_hash = self.create_hash(*combination)
                TimeLifeModel.objects.get_or_create(
                    unique_hash=unique_hash,
                )


class SaveLinkForCountTimeLife(CountInTwo):
    def __init__(self):
        self.exchanges = [
            'binance', 'bybit', 'huobi', 'kucoin', 'okx', 'bitget', 'pancake', 
            'gateio'
        ]
        self.trade_types = ['SELL-BUY', 'SELL-SELL', 'BUY-BUY', 'BUY-SELL']

        self.start_links = []
        self.continue_links = []
        self.end_links = []

    def current_timestamp(self):
        return datetime.timestamp(datetime.now())
    
    def key(self, trade_type, ex_buy, ex_sell):
        return f'{trade_type}--{ex_buy}--{ex_sell}'
    
    def get_data(self):
        pairs = [(a, b) for a in self.exchanges for b in self.exchanges if a != b]
        hashs = [
            value['hash']
            for trade_type in self.trade_types
            for a, b in pairs
            if (value := cache.get(self.key(trade_type, a, b))) and 'hash' in value
        ]
        return hashs

    def start(self, hashs: list):
        for unique_hash in hashs:
            time_life_model = TimeLifeModel.objects.get(unique_hash=unique_hash)

            new_entry = {'start': self.current_timestamp, 'stop': None}
            
            time_life_model.life = True
            time_life_model.times_life.append(new_entry)
            time_life_model.save()

    def end(self, hashs: list):
        for unique_hash in hashs:
            time_life_model = TimeLifeModel.objects.get(unique_hash=unique_hash)

            time_life_model.life = False
            time_life_model.times_life[-1]['stop'] = self.current_timestamp
            time_life_model.save()

    def main(self):
        hashs = set(self.get_data())
        active_hashes = set(
            TimeLifeModel.objects.filter(life=True) \
                .values_list('unique_hash', flat=True)
        )

        hashs_start = hashs - active_hashes
        self.start(hashs_start)
        hashs_continue = active_hashes & hashs
        hashs_end = active_hashes - hashs
        self.end(hashs_end)


