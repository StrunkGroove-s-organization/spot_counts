import os
import unittest

from rest_framework.test import APITestCase
from rest_framework import status
from django.core.cache import cache
from django.test import RequestFactory, TestCase
from unittest.mock import patch

from .views import Triangular, Inter


class TriangularTestCase(unittest.TestCase):
    url = '/api/v1/triangular-arbitrage/'

    def test_post_valid_serializer(self):
        factory = RequestFactory()
        payload = {"market": "binance", "token": "USDT"}
        request = factory.post(self.url, payload)

        with patch.object(cache, 'get', return_value=None):
            view = Triangular.as_view()
            response = view(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data'], None)

    def test_post_invalid_serializer(self):
        factory = RequestFactory()
        payload = {"invalid_data": "Invalid"}
        request = factory.post(self.url, payload)

        view = Triangular.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_valid_data(self):
        factory = RequestFactory()
        payload = {"market": "binance", "token": "USDT"}
        request = factory.post(self.url, payload)

        view = Triangular.as_view()
        response = view(request)
        response_data = response.data

        for data in response_data['data'].values():
            sorted_data = sorted(data, key=lambda x: x['spread_with_fee'], reverse=True)
            self.assertEqual(data, sorted_data)

        spreads = []

        for data in response_data['data'].values():
            spreads.append(data[0]['spread_with_fee'])

        sorted_spreads = sorted(spreads, reverse=True)
        self.assertEqual(spreads, sorted_spreads)


class InterTestCase(APITestCase):
    url = '/api/v1/inter-arbitrage/'

    def test_post_valid_serializer(self):
        factory = RequestFactory()
        payload = {
            "exchanges_buy": [],
            "exchanges_sell": [],
            "trade_type": "T-T_BUY-SELL"
        }
        request = factory.post(self.url, payload)
        response = self.client.post(self.url, payload)

        with patch.object(cache, 'get', return_value=None):
            view = Inter.as_view()
            response = view(request)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data'], [])

    def test_post_invalid_serializer(self):
        factory = RequestFactory()
        payload = {"invalid_data": "Invalid"}
        request = factory.post(self.url, payload)

        view = Inter.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_valid_data(self):
        payload = {
            "exchanges_buy": [],
            "exchanges_sell": [],
            "trade_type": "T-T_BUY-SELL"
        }
        response = self.client.post(self.url, payload)
        response_data = response.data
        data = response_data['data']

        sorted_data = sorted(data, key=lambda x: x['spread'], reverse=True)
        self.assertEqual(data, sorted_data)