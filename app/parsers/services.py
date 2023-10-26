import requests

from typing import Dict
from django.core.cache import cache


class ParserBase:
    def __init__(self, key: str, dict: Dict[str, str]):
        """
        Initializes the class
        """
        self.key = key
        self.ex = dict['ex']

        self.ask_qty = dict['ask_qty']
        self.bid_qty = dict['bid_qty']
        self.ask_price = dict['ask_price']
        self.bid_price = dict['bid_price']
        
        self.url = dict['url']
        add_url = dict.get('add_url')

        self.add_url = add_url if add_url else self.url
        self.path_list = dict.get('path')
        self.accept = dict['accept']
        self.price = dict['price']
        self.symbol = dict['symbol']
        self.time_cash = 60
        self.session = requests.Session()

    def get_data(self) -> dict:
        """
        Get data about crypto symbols
        """
        try:
            response_data = {
                "data": self.session.get(self.url).json(),
                "add_info": self.session.get(self.add_url).json()
            }
            return response_data
        except requests.exceptions.RequestException as e:
            print("An error occurred:", str(e))
            return None

    def unpack_data(self, dict: dict) -> dict:
        """
        Unpack data and return flat list for data in response
        """
        def unpack(data, path_list):
            """
            Return flat list
            """
            if path_list:
                for path in path_list:
                    data = data[path]
            data = sorted(data, key=lambda x: x[self.symbol], reverse=True)
            return data

        return {
            "data": unpack(dict["data"], self.path_list),
            "add_info": unpack(dict["add_info"], self.path_list),
        }

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
    
    def del_fake(self, dict: dict) -> None:
        """
        Delete tokens who has fake price
        """
        indices_to_remove = []
        
        for index, ad in enumerate(dict["data"]):
            symbol = self.get_token(ad)
            if symbol not in self.accept:
                indices_to_remove.append(index)

        for i in reversed(indices_to_remove):
            dict["data"].pop(i)
            dict["add_info"].pop(i)

    def merge(self, dict: dict) -> list:
        """
        Merge three dict: 
            - dict about symbol
            - dict data  
            - dict add_info
        """
        def dict_append(dict: dict, first: str, 
                        second: str, price: float, 
                        bid_price: float, ask_price: float, 
                        bid_qty: float, ask_qty: float, 
                        ex: str) -> dict:
            """
            Create single record
            """
            dict[f"{first}{second}"] = {
                "base": first,
                "quote": second,
                "price": price,
                "bid_price": bid_price,
                "ask_price": ask_price,
                "bid_qty": bid_qty,
                "ask_qty": ask_qty,
                "ex": ex,
            }

        data = dict["data"]
        add_info = dict["add_info"]
        
        dict = {}

        for i in range(len(data)):
            ad = data[i]
            ad_add_info = add_info[i]

            token = self.get_token(ad)
            info = self.accept[token]

            bid_price = ad_add_info[self.bid_price]
            ask_price = ad_add_info[self.ask_price]
            bid_qty = ad_add_info[self.bid_qty]
            ask_qty = ad_add_info[self.ask_qty]
            ex = self.ex

            base = info["base"]
            quote = info["quote"]
            price = ad[self.price]

            if bid_price == '' or ask_price == '' or price == '': 
                continue
            
            bid_qty = float(bid_qty)
            ask_qty = float(ask_qty)
            bid_price = float(bid_price)
            ask_price = float(ask_price)
            price = float(price)

            dict_append(dict, base, quote, price, bid_price, ask_price, bid_qty, ask_qty, ex)
            dict_append(dict, quote, base, 1/price, bid_price, ask_price, bid_qty, ask_qty, ex)

        return dict

    def save_db(self, data: dict) -> None:
        """
        Save data in Redis
        """
        cache.set(self.key, data, self.time_cash)

    def get_cleaned_data(self) -> dict:
        """
        Get all info about crypto symbols and save in Redis
        """
        dict = self.get_data()
        dict = self.unpack_data(dict)
        self.del_fake(dict)
        data = self.merge(dict)
        self.save_db(data)
        return f"{self.key}: {len(data)}"
