import zipfile

import requests

from .models import LinksCryptoInfo
from best_change_parsing.models import LinksExchangeInfo
from main.celery import app
key_best_rates = 'rates'

from django.core.cache import cache
from django.db import transaction


def download_and_extract_data():

    zip_url = "http://api.bestchange.ru/info.zip"
    zip_filename = "info.zip"

    response = requests.get(zip_url)

    with open(zip_filename, "wb") as zip_file:
        zip_file.write(response.content)

    with zipfile.ZipFile(zip_filename, "r") as zip_file:
        currencies_data = zip_file \
            .read("bm_cy.dat") \
            .decode("cp1251") \
            .splitlines()
        
        exchanges_data = zip_file \
            .read("bm_exch.dat") \
            .decode("cp1251") \
            .splitlines()

        rates_data = zip_file \
            .read("bm_rates.dat") \
            .decode("cp1251") \
            .splitlines()

    return currencies_data, exchanges_data, rates_data


def crypto_info(currencies_data):
    crypto_info_dict = {}
    crypto_records = []

    all_crypto_id_in_db = LinksCryptoInfo \
        .objects \
        .values_list('crypto_id', flat=True)

    for line in currencies_data:
        parts = line.split(";")
        currency_id = int(parts[0])
        currency_name = parts[2]

        record = LinksCryptoInfo()
        record.crypto_id = currency_id
        record.crypto_name = currency_name
        name = currency_name.split()
        abbr = name[-1] \
            .replace('(', '') \
            .replace(')', '')
        record.abbr = abbr
        crypto_info_dict[currency_id] = abbr

        if currency_id not in all_crypto_id_in_db:
            crypto_records.append(record)

    if crypto_records:
        with transaction.atomic():
            LinksCryptoInfo.objects.bulk_create(crypto_records)
    
    return crypto_info_dict


def exchange_info(exchanges_data):
    crypto_info_dict = {}
    exchanges_records = []
    all_exchange_id_in_db = LinksExchangeInfo. \
        objects.values_list('exchange_id', flat=True)

    for line in exchanges_data:
        parts = line.split(";")
        exchange_id = int(parts[0])
        exchange_name = parts[1]

        record = LinksExchangeInfo()
        record.exchange_id = exchange_id
        record.exchange_name = exchange_name

        if exchange_id not in all_exchange_id_in_db:
            exchanges_records.append(record)

    if exchanges_records:
        with transaction.atomic():
            LinksExchangeInfo.objects.bulk_create(exchanges_records)


def save_db(data):
    time_cash = 60
    cache.set(key_best_rates, data, time_cash)


def rates_tokens(rates_data, crypto_info_dict):
    rates = []

    for line in rates_data:
        parts = line.split(";")

        crypto_id_give = int(parts[0])
        crypto_id_get = int(parts[1])
        exchange_id = int(parts[2])
        rate_give = float(parts[3])
        rate_get = float(parts[4])
        price = rate_get / rate_give

        available = float(parts[5])
        reviews = parts[6].split('.')
        negative_reviews = int(reviews[0])
        positive_reviews = int(reviews[1])
        dont_use = int(parts[7])
        lim_min = round(float(parts[8]), 2)
        lim_max = round(float(parts[9]), 2)
        city_id = int(parts[10])

        item = {
            "crypto_number_give": crypto_id_give,
            "crypto_number_get": crypto_id_get,
            "crypto_name_give": crypto_info_dict[crypto_id_give],
            "crypto_name_get": crypto_info_dict[crypto_id_get],
            "exchange_id": exchange_id,
            "price": price,
            "available": available,
            "negative_reviews": negative_reviews,
            "positive_reviews": positive_reviews,
            "dont_use": dont_use,
            "lim_min": lim_min,
            "lim_max": lim_max,
            "city_id": city_id,
        }
        rates.append(item)

    return rates


@app.task
def main():

    currencies_data, exchanges_data, rates_data = download_and_extract_data()
    exchange_info(exchanges_data)
    crypto_info_dict = crypto_info(currencies_data)
    data = rates_tokens(rates_data, crypto_info_dict)
    save_db(data)

    return 'Success!'