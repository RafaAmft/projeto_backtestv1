import yfinance as yf
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class YahooFinanceAPI:
    """
    Cliente simples para baixar históricos de ações via yfinance.
    """
    def __init__(self):
        pass

    def get_historico(self, ticker, start=None, end=None, interval="1d"):
        """
        Retorna DataFrame com colunas [Date, Open, High, Low, Close, Volume].
        Por padrão, pega até hoje e volta ~1 ano.
        """
        try:
            df = yf.download(ticker, start=start, end=end, interval=interval, progress=False, threads=False)
            if df.empty:
                df = yf.download(ticker, period="1y", interval=interval, progress=False, threads=False)
            if df.empty:
                raise ValueError(f"Nenhum dado encontrado para o ticker {ticker}.")
            df = df.reset_index()
            return df
        except Exception as e:
            logger.error(f"Erro ao buscar dados de {ticker}: {e}")
            raise ValueError(f"Erro ao buscar dados para {ticker}: {e}")