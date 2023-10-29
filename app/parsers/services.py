import requests

from typing import Dict, Union
from django.core.cache import cache


class ParserBase:
    """
    Base class for parsers
    """
    def __init__(self, key: str, dict: Dict[str, str]):
        """
        Initializes the class
        """
        # for requests
        self.url = dict['url']
        self.session = requests.Session()
        
        # redis settings
        self.key = key
        self.time_cash = 60

        # main info about symbols
        self.ex = dict['ex']
        self.accept = dict['accept']
        self.price = dict['price']
        self.symbol = dict['symbol']
        self.ask_qty = dict['ask_qty']
        self.bid_qty = dict['bid_qty']
        self.ask_price = dict['ask_price']
        self.bid_price = dict['bid_price']
        self.path_list = dict.get('path')

    def request(self, url: str) -> dict:
        """
        Get data about crypto symbols
        """
        try:
            return self.session.get(url).json()
        except requests.exceptions.RequestException as e:
            return None
        
    def unpack(self, data: dict, path_list: list):
        """
        Return flat list
        """
        if path_list:
            for path in path_list:
                data = data[path]
        return data

    def append_action(self, token: str):
        """
        Override class because sometimes symbols are present in characters
        """
        return token

    def get_token(self, ad: dict) -> str:
        """
        Get token from single dict of symbol info
        """
        return self.append_action(ad[self.symbol])
    
    def parse(self, value: Union[str, float]):
        value = float(value) if value != '' else None
        value = value if value != 0.0 else None
        return value

    def save_db(self, data: dict) -> None:
        """
        Save data in Redis
        """
        cache.set(self.key, data, self.time_cash)

    def del_fake(self, data: dict) -> None:
        """
        Delete tokens who has fake price
        """
        indices_to_remove = []

        for index, ad in enumerate(data):
            symbol = self.get_token(ad)

            if symbol not in self.accept:
                indices_to_remove.append(index)

        for i in reversed(indices_to_remove):
            data.pop(i)


class ParserTwoRequest(ParserBase):
    """
    A class for parsers where price and data are separated in the order book
    """
    def __init__(self, key: str, dict: Dict[str, str]):
        """
        Initializes the class
        """
        super().__init__(key, dict)
        self.add_url = dict['add_url']

    def merge(self, data: dict, data_add: dict) -> list:
        """
        Merge three dict: 
            - dict data  
            - dict data_add
        """

        new_data = {}

        for ad, add_ad in zip(data, data_add):
            token = self.get_token(ad)
            info = self.accept[token]

            base = info["base"]
            quote = info["quote"]

            params = {
                "price": self.parse(ad[self.price]),
                "bid_price": self.parse(add_ad[self.bid_price]),
                "ask_price": self.parse(add_ad[self.ask_price]),
                "bid_qty": self.parse(add_ad[self.bid_qty]),
                "ask_qty": self.parse(add_ad[self.ask_qty]),
                "ex": self.ex,
            }

            if None in params.values():
                continue

            new_data[f'{base}{quote}'] = {
                'base': base,
                'quote': quote,
                **params,
            }
            try:
                new_data[f'{quote}{base}fake'] = {
                    'fake': True,
                    'quote': base,
                    'base': quote,
                    'price': 1 / params.pop('price'),
                    'ask_price': 1 / params.pop('ask_price'),
                    'bid_price': 1 / params.pop('bid_price'),
                    **params
                }
            except:
                print(f'---------\n {params} \n')

        return new_data

    def get_cleaned_data(self) -> dict:
        """
        Get all info about crypto symbols and save in Redis
        """
        data = self.request(self.url)
        data_add = self.request(self.add_url)
        if data is None or data_add is None: return None

        data = self.unpack(data, self.path_list)
        data_add = self.unpack(data_add, self.path_list)

        self.del_fake(data)
        self.del_fake(data_add)
        
        data = sorted(data, key=lambda x: x[self.symbol])
        data_add = sorted(data_add, key=lambda x: x[self.symbol])

        data_dict = self.merge(data, data_add)
        self.save_db(data_dict)
        return f"{self.key}: {len(data_dict)}"


class ParserSimple(ParserBase):
    """
    A class where price and data about order book in one request
    """
    def transformation(self, data: dict) -> list:
        """
        Merge three dict: 
            - dict about symbol
            - dict data  
        """
        
        new_data = {}

        for ad in data: # FIXME iterate with pop mb for save memory
            token = self.get_token(ad)
            info = self.accept[token]

            base = info["base"]
            quote = info["quote"]

            params = {
                "price": self.parse(ad[self.price]),
                "bid_price": self.parse(ad[self.bid_price]),
                "ask_price": self.parse(ad[self.ask_price]),
                "bid_qty": self.parse(ad[self.bid_qty]),
                "ask_qty": self.parse(ad[self.ask_qty]),
                "ex": self.ex,
            }

            if None in params.values():
                continue

            new_data[f'{base}{quote}'] = {
                'base': base,
                'quote': quote,
                **params,
            }
            new_data[f'{quote}{base}fake'] = {
                'fake': True,
                'quote': base,
                'base': quote,
                'price': 1 / params.pop('price'),
                'ask_price': 1 / params.pop('ask_price'),
                'bid_price': 1 / params.pop('bid_price'),
                **params
            }

        return new_data

    def get_cleaned_data(self) -> dict:
        """
        Get all info about crypto symbols and save in Redis
        """
        data = self.request(self.url)
        if data is None: return None
        data = self.unpack(data, self.path_list)
        self.del_fake(data)
        data_dict = self.transformation(data)
        self.save_db(data_dict)
        return f"{self.key}: {len(data_dict)}"
