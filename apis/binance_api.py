import requests
import hmac
import hashlib
import time
import urllib.parse
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class BinanceMercadoAPI:
    def __init__(self, base_url="https://api.binance.com"):
        self.base_url = base_url

    def get(self, endpoint, params=None):
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erro na requisição [{url}]: {response.status_code} - {response.text}")

    def get_preco(self, symbol="BTCUSDT"):
        return self.get("/api/v3/ticker/price", params={"symbol": symbol})

    def top_volume(self, limit=15):
        data = self.get("/api/v3/ticker/24hr")
        ordenado = sorted(
            [x for x in data if 'quoteVolume' in x],
            key=lambda x: float(x['quoteVolume']),
            reverse=True
        )
        return ordenado[:limit]

    def get_historical_data(self, symbol: str, start_time: Optional[datetime] = None) -> pd.DataFrame:
        try:
            if start_time is None:
                start_time = datetime.now() - timedelta(days=365)

            start_time_ms = int(start_time.timestamp() * 1000)
            params = {
                'symbol': symbol,
                'interval': '1d',
                'startTime': start_time_ms,
                'limit': 1000
            }
            response = self.get("/api/v3/klines", params)

            if not response:
                return pd.DataFrame()

            df = pd.DataFrame(response, columns=[
                'timestamp', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_volume', 'trades', 'taker_buy_base',
                'taker_buy_quote', 'ignore'
            ])

            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            numeric_cols = ['open', 'high', 'low', 'close', 'volume']
            df[numeric_cols] = df[numeric_cols].apply(pd.to_numeric)
            return df[['open', 'high', 'low', 'close', 'volume']]

        except Exception as e:
            logger.error(f"Erro ao obter dados históricos para {symbol}: {str(e)}")
            return pd.DataFrame()

class BinanceTradeAPI:
    def __init__(self, api_key, api_secret, base_url="https://api.binance.com"):
        self.api_key = api_key
        self.api_secret = api_secret.encode()
        self.base_url = base_url

    def get(self, endpoint, params=None):
        if params is None:
            params = {}

        params['timestamp'] = int(time.time() * 1000)
        query_string = urllib.parse.urlencode(params)
        signature = hmac.new(self.api_secret, query_string.encode(), hashlib.sha256).hexdigest()
        query_string += f"&signature={signature}"

        headers = {"X-MBX-APIKEY": self.api_key}
        url = f"{self.base_url}{endpoint}?{query_string}"
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erro na requisição autenticada: {response.status_code} - {response.text}")
