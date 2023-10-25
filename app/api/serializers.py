from rest_framework import serializers


class TriangularSerializer(serializers.Serializer):
    market = serializers.CharField()
    token = serializers.CharField()

    def validate_market(self, value):
        list = ['binance', 'bybit', 'huobi', 'kucoin', 'okx']
        if value not in list:
            raise serializers.ValidationError(f'Допустимые значения: {list}')
        return value

    def validate_token(self, value):
        list = ['USDT', 'USDC']
        if value not in list:
            raise serializers.ValidationError(f'Допустимые значения: {list}')
        return value
    
    
class InterSerializer(serializers.Serializer):
    valid_exchanges = [
        'binance', 'bybit', 'huobi', 'kucoin', 'okx', 'bitget',
        'pancake', 'gateio'
    ]
    valid_trade_type = [
        'T-T_BUY-SELL', 'T-M_BUY-BUY', 'M-T_SELL-SELL', 'M-M_SELL-BUY'
    ]

    exchanges_buy = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    exchanges_sell = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )
    trade_type = serializers.CharField()

    def validate_trade_type(self, value):
        if value not in self.valid_trade_type:
            raise serializers.ValidationError(f'Invalid exchange: {value}')
        return value
    
    def validate_exchanges_buy(self, value):
        for exchange in value:
            if exchange not in self.valid_exchanges:
                raise serializers.ValidationError(
                    f'Invalid exchange: {exchange}'
                )
        return value
    
    def validate_exchanges_sell(self, value):
        for exchange in value:
            if exchange not in self.valid_exchanges:
                raise serializers.ValidationError(
                    f'Invalid exchange: {exchange}'
                )
        return value