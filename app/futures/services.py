import requests

from binance.cm_futures import CMFutures
from binance.um_futures import UMFutures
from okx import MarketData, PublicData

from django.core.cache import cache


class RedisKyesFuturesSymbols:
    def __init__(self) -> None:
        self.key_binance_futures = "key_binance_futures"
        self.key_bybit_futures = "key_bybit_futures"
        self.key_okx_futures = "key_okx_futures"
        self.key_bitget_futures = "key_bitget_futures"
        self.key_kucoin_futures = "key_kucoin_futures"
        self.key_huobi_futures = "key_huobi_futures"
        self.key_gateio_futures = "key_gateio_futures"


class SetBinanceFuturesSymbols(RedisKyesFuturesSymbols):
    def __init__(self) -> None:
        super().__init__()
        self.accept_status = {"TRADING"}
        self.symbols_trading = set()

    def __call__(self) -> int:
        return self.main()
    
    def filter_only_trading_um(self, data: dict) -> None:
        symbols_data = data["symbols"] 

        for symbol_info in symbols_data:
            if symbol_info["status"] not in self.accept_status: continue

            base = symbol_info["baseAsset"]
            quote = symbol_info["quoteAsset"]

            self.symbols_trading.add(base + quote)
            self.symbols_trading.add(quote + base)

    def filter_only_trading_cm(self, data: dict) -> None:
        symbols_data = data["symbols"] 

        for symbol_info in symbols_data:
            if symbol_info["contractStatus"] not in self.accept_status: continue

            base = symbol_info["baseAsset"]
            quote = symbol_info["quoteAsset"]

            self.symbols_trading.add(base + quote)
            self.symbols_trading.add(quote + base)

    def save(self) -> None:
        cache.set(self.key_binance_futures, self.symbols_trading)

    def main(self) -> int:
        data = UMFutures().exchange_info() # https://binance-docs.github.io/apidocs/futures/en/#exchange-information
        self.filter_only_trading_um(data)

        data = CMFutures().exchange_info() # https://binance-docs.github.io/apidocs/delivery/en/#exchange-information
        self.filter_only_trading_cm(data)

        self.save()
        return len(self.symbols_trading)


class SetBybitFuturesSymbols(RedisKyesFuturesSymbols):
    def __init__(self) -> None:
        super().__init__()
        self.symbols_trading = {
            "PEPEUSDT", "ARBUSDT", "APTUSDT", "FILUSDT", "AAVEUSDT", "XLMUSDT", "RUNEUSDT", "STXUSDT", "SUIUSDT",
            "OPUSDT", "FTMUSDT", "WOOUSDT", "GALAUSDT", "FLOWUSDT", "SANDUSDT", "APEUSDT", "CHZUSDT", "COMPUSDT",
            "LDOUSDT", "GRTUSDT", "GMXUSDT", "AXSUSDT", "SNXUSDT", "CRVUSDT", "KAVAUSDT", "ICPUSDT", "EGLDUSDT",
            "XECUSDT", "FXSUSDT", "QNTUSDT", "TWTUSDT", "ZILUSDT", "ROSEUSDT", "KLAYUSDT", "NFTUSDT", "WAXPUSDT",
            "ONEUSDT", "SUSHIUSDT", "GALUSDT", "C98USDT", "IDUSDT", "SUNUSDT", "RNDRUSDT", "BNBUSDT", "SOLUSDT",
            "BTCUSDT", "LTCUSDT", "DOGEUSDT", "ETHUSDT", "ETCUSDT", "BCHUSDT", "TRXUSDT", "BUSDUSDT", "MATICUSDT",
            "XEMUSDT", "EOSUSDT", "ADAUSDT", "WAVESUSDT", "OMGUSDT", "ZRXUSDT", "ICXUSDT", "BTTUSDT", "BATUSDT",
            "QTUMUSDT", "LINKUSDT", "ATOMUSDT", "XTZUSDT", "DOTUSDT", "UNIUSDT", "RVNUSDT", "ALGOUSDT", "MKRUSDT",
            "AVAXUSDT", "YFIUSDT", "MANAUSDT", "NEARUSDT", "TONUSDT", "CAKEUSDT", "SEIUSDT", "SCUSDT", "JASMYUSDT",
            "WLDUSDT", "GLMRUSDT", "ETHWUSDT", "SSVUSDT", "ZENUSDT", "BICOUSDT", "MEMEUSDT", "TOMIUSDT", "MAGICUSDT",
            "KDAUSDT", "ACHUSDT", "DGBUSDT", "KASUSDT", "PENDLEUSDT", "GASUSDT", "UMAUSDT", "STGUSDT", "SLPUSDT",

            "USDTPEPE", "USDTARB", "USDTAPT", "USDTFIL", "USDTAAVE", "USDTXLM", "USDTRUNE", "USDTSTX", "USDTSUI",
            "USDTOP", "USDFTM", "USDTWOO", "USDTGALA", "USDTFLOW", "USDTSAND", "USDTAPE", "USDTCHZ", "USDTCOMP",
            "USDTLDO", "USDTGRT", "USDTGMX", "USDTAXS", "USDTSNX", "USDTCRV", "USDTKAVA", "USDTICP", "USDTEGLD",
            "USDTXEC", "USDTFXS", "USDTQNT", "USDTTWT", "USDTZIL", "USDTROSE", "USDTKLAY", "USDTNFT", "USDTWAXP",
            "USDTONE", "USDTSUSHI", "USDTGAL", "USDTC98", "USDTID", "USDTSUN", "USDTRNDR", "USDTBNB", "USDTSOL",
            "USDTBTC", "USDTLTC", "USDTDOGE", "USDTETH", "USDTETC", "USDTBCH", "USDTTRX", "USDTBUSD", "USDTMATIC",
            "USDTXEM", "USDTEOS", "USDTADA", "USDTWAVES", "USDTOMG", "USDTZRX", "USDTICX", "USDTBTT", "USDTBATUS",
            "USDTQTUM", "USDTLINK", "USDTATOM", "USDTXTZ", "USDTDOT", "USDTUNI", "USDTRVN", "USDTALGO", "USDTMKR",
            "USDTAVAX", "USDTYFI", "USDTMANA", "USDTNEAR", "USDTTON", "USDTCAKE", "USDTSEI", "USDTSC", "USDTJASMY",
            "USDTWLD", "USDTGLMR", "USDTETHW", "USDTSSV", "USDTZEN", "USDTBICO", "USDTMEME", "USDTTOMI", "USDTMAGIC",
            "USDTKDA", "USDTACH", "USDTDGB", "USDTKAS", "USDTPENDLE", "USDTGAS", "USDTUMA", "USDTSTG", "USDTSLP"
        }
        self.url = "https://api.bybit.com/v5/market/instruments-info?category=option&status=Trading"
        
    def __call__(self) -> int:
        return self.main()

    def filter_only_trading(self, data: dict) -> None:
        symbols_data = data["result"]["list"] 

        for symbol_info in symbols_data:
            base = symbol_info["baseCoin"]
            quote = symbol_info["quoteCoin"]

            self.symbols_trading.add(base + quote)
            self.symbols_trading.add(quote + base)

    def save(self) -> None:
        cache.set(self.key_bybit_futures, self.symbols_trading)

    def main(self) -> int:
        # response = requests.get(self.url)
        # data = response.json()
        # self.filter_only_trading(data)
        self.save()
        return len(self.symbols_trading)


class SetOkxFuturesSymbols(RedisKyesFuturesSymbols):
    def __init__(self) -> None:
        super().__init__()
        self.symbols_trading = set()
        self.flag = "0"  # Production trading:0 , demo trading:1

    def __call__(self) -> int:
        return self.main()

    def filter_only_trading(self, data: dict) -> None:
        symbols_data = data["data"][0]

        for symbol in symbols_data:
            base = symbol.split("-")[0]
            quote = symbol.split("-")[1]
            self.symbols_trading.add(base + quote)
            self.symbols_trading.add(quote + base)

    def save(self) -> None:
        cache.set(self.key_okx_futures, self.symbols_trading)

    def main(self) -> int:
        publicDataAPI = PublicData.PublicAPI(flag=self.flag)
        result = publicDataAPI.get_underlying(
            instType="FUTURES"
        )
        self.filter_only_trading(result)
        self.save()
        return len(self.symbols_trading)


class SetBitgetFuturesSymbols(RedisKyesFuturesSymbols):
    def __init__(self) -> None:
        super().__init__()
        self.product_types = ["USDT-FUTURES", "COIN-FUTURES", "USDC-FUTURES"]
        self.url = "https://api.bitget.com/api/v2/mix/market/contracts?productType={}"
        self.symbols_trading = set()
        self.status = {"normal"}

    def __call__(self) -> int:
        return self.main()

    def filter_only_trading(self, data: dict) -> None:
        symbols_data = data["data"]

        for symbol_info in symbols_data:
            if symbol_info["symbolStatus"] not in self.status: continue

            base = symbol_info["baseCoin"]
            quote = symbol_info["quoteCoin"]
            self.symbols_trading.add(base + quote)
            self.symbols_trading.add(quote + base)

    def save(self) -> None:
        cache.set(self.key_bitget_futures, self.symbols_trading)

    def main(self) -> int:
        for product_type in self.product_types:
            url = self.url.format(product_type)
            response = requests.get(url)
            data = response.json()
            self.filter_only_trading(data)
        self.save()
        return len(self.symbols_trading)


class SetKucoinFuturesSymbols(RedisKyesFuturesSymbols):
    def __init__(self) -> None:
        super().__init__()
        self.url = "https://api-futures.kucoin.com/api/v1/contracts/active"
        self.symbols_trading = set()
        self.status = {"Open"}

    def __call__(self) -> int:
        return self.main()

    def filter_only_trading(self, data: list) -> None:
        symbol_data = data["data"]

        for symbol_info in symbol_data:
            if symbol_info["status"] not in self.status: continue

            base = symbol_info["baseCurrency"]
            quote = symbol_info["quoteCurrency"]
            self.symbols_trading.add(base + quote)
            self.symbols_trading.add(quote + base)

    def save(self) -> None:
        cache.set(self.key_kucoin_futures, self.symbols_trading)

    def main(self) -> int:
        response = requests.get(self.url)
        data = response.json()
        self.filter_only_trading(data)
        self.save()
        return len(self.symbols_trading)


class SetHuobiFuturesSymbols(RedisKyesFuturesSymbols):
    def __init__(self) -> None:
        super().__init__()
        self.symbols_trading = {
            "PEPEUSDT", "ARBUSDT", "APTUSDT", "FILUSDT", "AAVEUSDT", "XLMUSDT", "SUIUSDT", "OPUSDT", "FTMUSDT", 
            "WOOUSDT", "GALAUSDT", "SANDUSDT", "APEUSDT", "CHZUSDT", "COMPUSDT", "LDOUSDT", "GRTUSDT", "AXSUSDT", 
            "SNXUSDT", "CRVUSDT", "KAVAUSDT", "EGLDUSDT", "GMTUSDT", "ONEUSDT", "SUSHIUSDT", "GALUSDT", "RNDRUSDT", 
            "BNBUSDT", "SOLUSDT", "BTCUSDT", "LTCUSDT", "DOGEUSDT", "ETHUSDT", "XMRUSDT", "ETCUSDT", "XRPUSDT", 
            "BCHUSDT", "TRXUSDT", "BSVUSDT", "EOSUSDT", "MATICUSDT", "ADAUSDT", "WAVESUSDT", "LINKUSDT", "ATOMUSDT", 
            "DOTUSDT", "UNIUSDT", "SHIBUSDT", "ALGOUSDT", "MKRUSDT", "AVAXUSDT", "YFIUSDT", "MANAUSDT", "LUNAUSDT", 
            "NEARUSDT", "TONUSDT", "CAKEUSDT", "SEIUSDT", "WLDUSDT", "LPTUSDT", "SNTUSDT", "STORJUSDT", "SSVUSDT", 
            "POLYXUSDT", "MEMEUSDT", "ACHUSDT", "GALUSDT", "FTTUSDT", "GASUSDT", "BLZUSDT", "MTLUSDT", "STGUSDT", 
            "STEEMUSDT", "YGGUSDT", "USTCUSDT", "OGNUSDT",

            "USDTPEPE", "USDTARB", "USDTAPT", "USDTFIL", "USDTAAVE", "USDTXLM", "USDTSUI", "USDTOP", "USDTFTM", "USDTWOO",
            "USDTGALA", "USDTSAND", "USDTAPE", "USDTCHZ", "USDTCOMP", "USDTLDO", "USDTGRT", "USDTAXS", "USDTSNX", "USDTCRV",
            "USDTKAVA", "USDTEGLD", "USDTGMT", "USDONE", "USDTSUSHI", "USDTGAL", "USDTRNDR", "USDTBNB", "USDTSOL", "USDTBTC",
            "USDTLTC", "USDTDOGE", "USDTETH", "USDTXMR", "USDTETC", "USDTXRP", "USDTBCH", "USDTTRX", "USDTBSV", "USDTEOS",
            "USDTMATIC", "USDTADA", "USDTWAVES", "USDTLINK", "USDTATOM", "USDTDOT", "USDTUNI", "USDTSHIB", "USDTALGO", "USDTMKR",
            "USDTAVAX", "USDTYFI", "USDTMANA", "USDTLUNA", "USDTNEAR", "USDTTON", "USDTCAKE", "USDTSEI", "USDTWLD", "USDTLPT",
            "USDTSNT", "USDTSTORJ", "USDTSSV", "USDTPOLYX", "USDTMEME", "USDTECH", "USDTFTT", "USDTGAS", "USDTBLZ", "USDTMTL",
            "USDTSTG", "USDTSTEEM", "USDTYGG", "USDTUSTC", "USDTOGN"
        }

    def __call__(self) -> int:
        return self.main()

    def save(self) -> None:
        cache.set(self.key_huobi_futures, self.symbols_trading)

    def main(self) -> int:
        self.save()
        return len(self.symbols_trading)


class SetGateioFuturesSymbols(RedisKyesFuturesSymbols):
    def __init__(self) -> None:
        super().__init__()
        self.symbols_trading = {
            "PEPEUSDT", "ARBUSDT", "APTUSDT", "FILUSDT", "AAVEUSDT", "XLMUSDT", "RUNEUSDT", "STXUSDT", "CFXUSDT",
            "SUIUSDT", "OPUSDT", "FTMUSDT", "WOOUSDT", "GALAUSDT", "FLOWUSDT", "SANDUSDT", "APEUSDT", "CHZUSDT",
            "COMPUSDT", "LDOUSDT", "GRTUSDT", "GMXUSDT", "AXSUSDT", "SNXUSDT", "CRVUSDT", "KAVAUSDT", "ICPUSDT",
            "EGLDUSDT", "QNTUSDT", "TWTUSDT", "ZILUSDT", "ROSEUSDT", "KLAYUSDT", "IOTAUSDT", "GMTUSDT", "WAXPUSDT",
            "ONEUSDT", "SUSHIUSDT", "GALUSDT", "C98USDT", "RNDRUSDT", "BNBUSDT", "SOLUSDT", "BTCUSDT", "LTCUSDT",
            "DOGEUSDT", "ETHUSDT", "DASHUSDT", "XMRUSDT", "ETCUSDT", "XRPUSDT", "BCHUSDT", "TRXUSDT", "BUSDUSDT",
            "BSVUSDT", "MATICUSDT", "ZECUSDT", "NEOUSDT", "EOSUSDT", "ADAUSDT", "WAVESUSDT", "OMGUSDT", "XVGUSDT",
            "ZRXUSDT", "ICXUSDT", "BATUSDT", "ONTUSDT", "QTUMUSDT", "LINKUSDT", "ATOMUSDT", "XTZUSDT", "DOTUSDT",
            "UNIUSDT", "RVNUSDT", "VETUSDT", "SHIBUSDT", "ALGOUSDT", "MKRUSDT", "AVAXUSDT", "YFIUSDT", "MANAUSDT",
            "LUNAUSDT", "NEARUSDT", "CROUSDT", "TONUSDT", "CAKEUSDT", "SEIUSDT", "AUDIOUSDT", "SCUSDT", "ANTUSDT",
            "BANDUSDT", "JASMYUSDT", "WLDUSDT", "SXPUSDT", "LPTUSDT", "ONTUSDT", "BALUSDT", "ONEUSDT", "GLMRUSDT",
            "STORJUSDT", "ETHWUSDT", "IOSTUSDT", "SSVUSDT", "ZENUSDT", "BICOUSDT", "POLYXUSDT", "MEMEUSDT", "CKBUSDT",
            "TOMIUSDT", "MAGICUSDT", "PYRUSDT", "KDAUSDT", "ACHUSDT", "ORBSUSDT", "LOOMUSDT", "STRAXUSDT", "ONGUSDT",
            "GALUSDT", "SKLUSDT", "LQTYUSDT", "FLUXUSDT", "API3USDT", "STPTUSDT", "KASUSDT", "WEMIXUSDT", "XRDUSDT",
            "FTTUSDT", "ARKUSDT", "PENDLEUSDT", "GNSUSDT", "CTSIUSDT", "GASUSDT", "RIFUSDT", "MTLUSDT", "STGUSDT",
            "POWRUSDT", "CELRUSDT", "STEEMUSDT", "IDUSDT", "XVSUSDT", "EDUUSDT", "YGGUSDT", "JOEUSDT", "CVCUSDT",
            "USTCUSDT", "RDNTUSDT", "OGNUSDT", "SLPUSDT",

            "USDTPEPE", "USDTARBU", "USDTAPTU", "USDTFILU", "USDTAAVE", "USDTXLMU", "USDTRUNE", "USDTSTXU", "USDTCFXX",
            "USDTSUIU", "USDTOPUU", "USDTFTMU", "USDTWOO", "USDTGALA", "USDTFLOW", "USDTSAND", "USDTAPEU", "USDTCHZU",
            "USDTCOMPU", "USDTLDOU", "USDTGRTU", "USDTGMXU", "USDTAXSU", "USDTSNXU", "USDTCRVU", "USDTKAVAU", "USDTICPU",
            "USDTGLDU", "USDTQNTU", "USDTTWTU", "USDTZILU", "USDTROSEU", "USDTKLAYU", "USDTIOTAU", "USDTGMTU", "USDTWAXPU",
            "USDTONEU", "USDTSUSHIU", "USDTGALU", "USDTC98U", "USDTRNDRU", "USDTBNBU", "USDTSOLU", "USDTBTCU", "USDTLTCU",
            "USDTDOGEU", "USDTETHU", "USDTDASHU", "USDTXMRU", "USDTETCU", "USDTXRPU", "USDTBCHU", "USDTTRXU", "USDTBUSD",
            "USDTBSVU", "USDTMATICU", "USDTZECU", "USDTNEOU", "USDTEOSU", "USDTADAU", "USDTWAVESU", "USDTOMGU", "USDTXVGU",
            "USDTZRXU", "USDTICXU", "USDTBATU", "USDTONTU", "USDTQTUMU", "USDTLINKU", "USDTATOMU", "USDTXTZU", "USDTDOTU",
            "USDTUNIU", "USDTRVNU", "USDTVETU", "USDTSHIBU", "USDTALGOU", "USDTMKRU", "USDTAVAXU", "USDTYFIU", "USDTMANAU",
            "USDTLUNAU", "USDTNEARU", "USDTCRUU", "USDTTONU", "USDTCAKEU", "USDTSEIU", "USDTAUDIOU", "USDTSCU", "USDTANTU",
            "USDTBANDU", "USDTJASMYU", "USDTWLDU", "USDTSXPU", "USDTLPTU", "USDTONTU", "USDTBALU", "USDTONEU", "USDTGLMRU",
            "USDTSTORJU", "USDTETHWU", "USDTIOSTU", "USDTSSVU", "USDTZENU", "USDTBICOU", "USDTPOLYXU", "USDTMEMEU", "USDTCKBUU",
            "USDTTOMIU", "USDTMAGICU", "USDTPYRU", "USDTKDAU", "USDTACHU", "USDTDGBU", "USDTKASU", "USDTPENDLEU", "USDTGASU",
            "USDTUMAU", "USDTSTGU", "USDTSLPU"
        }

    def __call__(self) -> int:
        return self.main()

    def save(self) -> None:
        cache.set(self.key_gateio_futures, self.symbols_trading)

    def main(self) -> int:
        self.save()
        return len(self.symbols_trading)