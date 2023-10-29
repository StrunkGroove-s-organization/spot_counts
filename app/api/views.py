import os

from django.core.cache import cache
from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework import status

from .serializers import TriangularSerializer, InterSerializer


class CustomPermission(permissions.BasePermission):
    ALLOWED_IPS = os.getenv('ALLOWED_IPS', '80.87.201.112').split(',')

    def has_permission(self, request, view):
        client_ip = self.get_client_ip(request)
        if client_ip in self.ALLOWED_IPS:
            return True
        return False

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
class BaseAPIView(APIView):
    pass
    # permission_classes = [CustomPermission]

class Triangular(BaseAPIView):
    def post(self, request):
        serializer = TriangularSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data

        market = validated_data.get('market')
        token = validated_data.get('token')

        key = f'{market}--{token}'
        data = cache.get(key)
        
        return Response({'data': data, 'favourite': []})
    

class Inter(BaseAPIView):
    all_ex = [
        'binance', 'bybit', 'huobi', 'kucoin', 'okx', 'bitget', 'pancake', 'gateio'
    ]

    def post(self, request):
        def filter_exchanges(exs):
            return [ex for ex in self.all_ex if ex not in exs] if exs else self.all_ex

        def get_data(fil_ex_buy, fil_ex_sell, trade_type):
            def key(trade_type, ex_buy, ex_sell):
                return f'{trade_type}--{ex_buy}--{ex_sell}'

            pairs = [(a, b) for a in fil_ex_buy for b in fil_ex_sell if a != b]
            values = [cache.get(key(trade_type, a, b)) for a, b in pairs]
            total_value = [value for sublist in values if sublist for value in sublist]
            sorted_data = sorted(total_value, key=lambda item: item['spread'], reverse=True)
            return sorted_data
    
        serializer = InterSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer.validated_data

        exs_buy = validated_data.get('exchanges_buy')
        exs_sell = validated_data.get('exchanges_sell')
        trade_type = validated_data.get('trade_type') \
            .split('_')[1]

        exs_buy = filter_exchanges(exs_buy)
        exs_sell = filter_exchanges(exs_sell)

        data = get_data(exs_buy, exs_sell, trade_type)

        return Response({'data': data, 'favourite': []})
    