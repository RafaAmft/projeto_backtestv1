import yfinance as yf
import pandas as pd
import logging
import time
import random
from typing import Optional

logger = logging.getLogger(__name__)

class YahooFinanceAPI:
    """
    Cliente melhorado para baixar históricos de ações via yfinance com tratamento de rate limiting.
    """
    def __init__(self, max_retries=3, delay_between_requests=1.0):
        self.max_retries = max_retries
        self.delay_between_requests = delay_between_requests
        self.last_request_time = 0

    def _rate_limit_delay(self):
        """Implementa delay entre requisições para evitar rate limiting."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.delay_between_requests:
            sleep_time = self.delay_between_requests - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()

    def get_historico(self, ticker, start=None, end=None, interval="1d"):
        """
        Retorna DataFrame com colunas [Date, Open, High, Low, Close, Volume].
        Por padrão, pega até hoje e volta ~1 ano.
        """
        for attempt in range(self.max_retries):
            try:
                self._rate_limit_delay()
                
                logger.info(f"Tentativa {attempt + 1} para buscar dados de {ticker}")
                
                df = yf.download(ticker, start=start, end=end, interval=interval, 
                               progress=False, threads=False, timeout=30)
                
                if df.empty:
                    logger.warning(f"Dados vazios para {ticker}, tentando com período padrão")
                    df = yf.download(ticker, period="1y", interval=interval, 
                                   progress=False, threads=False, timeout=30)
                
                if df.empty:
                    raise ValueError(f"Nenhum dado encontrado para o ticker {ticker}.")
                
                df = df.reset_index()
                logger.info(f"Dados obtidos com sucesso para {ticker}: {len(df)} registros")
                return df
                
            except Exception as e:
                logger.warning(f"Tentativa {attempt + 1} falhou para {ticker}: {e}")
                
                if "429" in str(e) or "Too Many Requests" in str(e):
                    # Rate limiting - espera mais tempo
                    wait_time = (attempt + 1) * 5 + random.uniform(1, 3)
                    logger.info(f"Rate limiting detectado. Aguardando {wait_time:.1f}s...")
                    time.sleep(wait_time)
                elif attempt < self.max_retries - 1:
                    # Outros erros - espera padrão
                    time.sleep(self.delay_between_requests)
                else:
                    # Última tentativa falhou
                    logger.error(f"Todas as tentativas falharam para {ticker}: {e}")
                    raise ValueError(f"Erro ao buscar dados para {ticker}: {e}")

    def get_stock_data(self, symbol: str) -> Optional[dict]:
        """
        Obtém dados básicos de uma ação.
        """
        try:
            self._rate_limit_delay()
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'price': info.get('regularMarketPrice'),
                'change': info.get('regularMarketChange'),
                'change_percent': info.get('regularMarketChangePercent'),
                'volume': info.get('volume'),
                'market_cap': info.get('marketCap')
            }
        except Exception as e:
            logger.error(f"Erro ao obter dados de {symbol}: {e}")
            return None

    def get_multiple_stocks(self, symbols: list) -> dict:
        """
        Obtém dados de múltiplas ações com rate limiting.
        """
        results = {}
        for symbol in symbols:
            try:
                data = self.get_stock_data(symbol)
                if data:
                    results[symbol] = data
                time.sleep(self.delay_between_requests)  # Delay entre símbolos
            except Exception as e:
                logger.error(f"Erro ao obter {symbol}: {e}")
                results[symbol] = None
        return results