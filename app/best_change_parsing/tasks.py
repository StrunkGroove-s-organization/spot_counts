import re
import time
import ast

import requests
import pprint

from .models import LinksExchangeInfo
from main.celery import app

from bs4 import BeautifulSoup
from django.db.models import F, Case, When, Value
from django.db.models import IntegerField, BooleanField, CharField


GIVE_CURRNECY = [
    'bitcoin', 
    'bitcoin-cash',
    # 'ethereum',
    # 'litecoin',
    # 'ripple',
    # 'monero',
    # 'dogecoin',
    # 'dash',
    # 'tether-erc20',
    # 'tether-trc20',
    # 'tether-bep20',
    # 'usd-coin',
    # 'tron',
    # 'binance-coin',
    # 'solana',
    ]

GET_CURRNECY = [
    # 'bitcoin', 
    # 'bitcoin-cash',
    # 'ethereum',
    # 'litecoin',
    # 'ripple',
    # 'monero',
    # 'dogecoin',
    # 'dash',
    'tether-erc20',
    # 'tether-trc20',
    # 'tether-bep20',
    # 'usd-coin',
    # 'tron',
    # 'binance-coin',
    # 'solana',
    ]

HEADERS = {
    "Cookie": "userid=cf51e8108ca86c37954632c703a9e413; ...",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/116.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Referer": "https://www.bestchange.com/bitcoin-to-bitcoin-cash.html",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1",
    "Te": "trailers"
}

TIME_DELAY_REQUESTS = 10 # sec

MAX_NUMBER_ROWS_FOR_PARS = 50

def append_exchange(all_conditions, exch_name):
    if exch_name not in all_conditions['all_exchange']:
        all_conditions['all_exchange'].append(exch_name)

def custom_float_serializer(number):
    return float(number.replace(' ', ''))

def extract_data_from_html(soup):
    script_info_html = soup.find_all('script', type='text/javascript')[5]
    pattern = r'= (\{.*\});'
    match = re.search(pattern, str(script_info_html))
    
    if match:
        data_str = match.group(1).replace("'", "\"")
        data_dict = ast.literal_eval(data_str)
        return data_dict

def column_0(all_conditions, exchange_name, json):

    age = json['d']
    star = json['s']

    all_conditions['info_age_conditions'] \
        .append(When(
            exchange_name=exchange_name, 
            then=Value(age)))
    all_conditions['info_star_conditions'] \
        .append(When(
            exchange_name=exchange_name, 
            then=Value(star)))

    if bool(json['v']):
        all_conditions['info_verification_conditions'] \
            .append(When(
                exchange_name=exchange_name, 
                then=Value(True)))
    if bool(json['v']):
        all_conditions['info_registration_conditions'] \
            .append(When(
                exchange_name=exchange_name, 
                then=Value(True)))
    
def column_1(all_conditions, column):
    exchange_name = column.find('div', class_='ca').get_text(strip=True)
    additions = column.find('span', class_='lbpl')

    if not additions:
        return exchange_name
    
    if additions.find('span', class_='floating'):
        all_conditions['addition_floating_conditions'] \
            .append(When(
                exchange_name=exchange_name,
                then=Value(True)))

    if additions.find('span', class_='verifying'):
        all_conditions['addition_verifying_conditions'] \
            .append(When(
                exchange_name=exchange_name,
                then=Value(True)))

    if additions.find('span', class_='manual'):
        all_conditions['addition_manual_conditions'] \
            .append(When(
                exchange_name=exchange_name, 
                then=Value(True)))

    if additions.find('span', class_='percent'):
        all_conditions['addition_percent_conditions'] \
            .append(When(
                exchange_name=exchange_name, 
                then=Value(True)))

    if additions.find('span', class_='otherin'):
        all_conditions['addition_otherin_conditions'] \
            .append(When(
                exchange_name=exchange_name, 
                then=Value(True)))

    if additions.find('span', class_='reg'):
        all_conditions['addition_reg_conditions'] \
            .append(When(
                exchange_name=exchange_name, 
                then=Value(True)))

    return exchange_name
    
def parse_response(response, all_conditions):

    soup = BeautifulSoup(response.content, 'html.parser')
    content_table = soup.find('table', {'id': 'content_table'})

    if content_table:
        rows = soup.find_all('tr', onclick=True)
        script_info_data = extract_data_from_html(soup)

        for index, row in enumerate(rows):  
            tds = row.find_all('td')
            exch_name = column_1(all_conditions, tds[1])

            append_exchange(all_conditions, exch_name)

            if script_info_data:
                column_0(all_conditions, exch_name, script_info_data[index])
    
    return all_conditions

def create_records():

    def create_conditions_dict():
        all_conditions = {}
        all_conditions['all_exchange'] = []

        all_conditions['info_age_conditions'] = []
        all_conditions['info_star_conditions'] = []
        all_conditions['info_verification_conditions'] = []
        all_conditions['info_registration_conditions'] = []
        all_conditions['addition_floating_conditions'] = []
        all_conditions['addition_verifying_conditions'] = []
        all_conditions['addition_manual_conditions'] = []
        all_conditions['addition_percent_conditions'] = []
        all_conditions['addition_otherin_conditions'] = []
        all_conditions['addition_reg_conditions'] = []

        return all_conditions

    def get_response(give_currency, get_currency):

        url = f"https://www.bestchange.com/{give_currency}-to-{get_currency}.html"
        response = requests.get(url, headers=HEADERS)

        if response.status_code == 200:
            return response
        else:
            return response.status_code

    all_conditions = create_conditions_dict()

    for give_currency in GIVE_CURRNECY:
        for get_currency in GET_CURRNECY:
            if give_currency != get_currency:

                response = get_response(give_currency, get_currency)
                parse_response(response, all_conditions)

                time.sleep(TIME_DELAY_REQUESTS)

    return all_conditions


@app.task
def main():
    all_conditions = create_records()

    def save_db(all_conditions):
        
        LinksExchangeInfo.objects.filter(
            exchange_name__in=all_conditions['all_exchange']) \
            .update(
            info_age=Case(
                *all_conditions['info_age_conditions'],
                default=F('info_age'),
                output_field=CharField()
            ),
            info_star=Case(
                *all_conditions['info_star_conditions'],
                default=F('info_star'),
                output_field=IntegerField()
            ),
            info_verification=Case(
                *all_conditions['info_verification_conditions'],
                default=F('info_verification'),
                output_field=BooleanField()
            ),
            info_registration=Case(
                *all_conditions['info_registration_conditions'],
                default=F('info_registration'),
                output_field=BooleanField()
            ),
            addition_floating=Case(
                *all_conditions['addition_floating_conditions'],
                default=F('addition_floating'),
                output_field=BooleanField()
            ),
            addition_verifying=Case(
                *all_conditions['addition_verifying_conditions'],
                default=F('addition_verifying'),
                output_field=BooleanField()
            ),
            addition_manual=Case(
                *all_conditions['addition_manual_conditions'],
                default=F('addition_manual'),
                output_field=BooleanField()
            ),
            addition_percent=Case(
                *all_conditions['addition_percent_conditions'],
                default=F('addition_percent'),
                output_field=BooleanField()
            ),
            addition_otherin=Case(
                *all_conditions['addition_otherin_conditions'],
                default=F('addition_otherin'),
                output_field=BooleanField()
            ),
            addition_reg=Case(
                *all_conditions['addition_reg_conditions'],
                default=F('addition_reg'),
                output_field=BooleanField()
            ),
        )

    save_db(all_conditions)
    return 'Success'


if __name__ == "__main__":
    pp = pprint.PrettyPrinter(indent=4)
    m = main()
    pp.pprint(m)