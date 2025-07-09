import requests
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import json
import time
from typing import Dict, List, Optional, Any
import logging
import numpy as np

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketIndicesManager:
    """
    Classe centralizada para gerenciar e buscar informações de índices de mercado.
    Inclui criptomoedas, ações, câmbio e outros indicadores financeiros.
    """
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MarketIndicesManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        # Evitar inicialização múltipla
        if self._initialized:
            return
            
        self._initialized = True
        self.cache = {}
        self.cache_duration = 300  # 5 minutos de cache
        self.last_update = {}
        
        # APIs e endpoints
        self.binance_base_url = "https://api.binance.com/api/v3"
        self.exchange_rate_api = "https://api.exchangerate-api.com/v4/latest/USD"
        self.ibge_api = "https://servicodados.ibge.gov.br/api/v3/agregados/1737/periodos/202401/variaveis/2266?localidades=N6[all]"
        
        # Símbolos importantes
        self.important_symbols = {
            'crypto': ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT', 'USDT'],
            'stocks': ['^BVSP', '^GSPC', '^IXIC', '^DJI', 'PETR4.SA', 'VALE3.SA'],
            'currencies': ['USDBRL=X', 'EURBRL=X', 'GBPBRL=X'],
            'commodities': ['GC=F', 'SI=F', 'CL=F']  # Ouro, Prata, Petróleo
        }
        
        # Inicializar dados
        self._initialize_data()
    
    def _format_brazilian_datetime(self, dt: datetime = None) -> str:
        """
        Formata data e hora no formato brasileiro (DD/MM/YYYY HH:MM:SS)
        """
        if dt is None:
            dt = datetime.now()
        return dt.strftime("%d/%m/%Y %H:%M:%S")
    
    def _initialize_data(self):
        """Inicializa os dados básicos do sistema"""
        logger.info("Inicializando MarketIndicesManager...")
        try:
            # Buscar câmbio atual
            self.get_exchange_rate()
            
            # Buscar principais criptomoedas
            self.get_crypto_prices()
            
            # Buscar principais índices
            self.get_stock_indices()
            
            logger.info("MarketIndicesManager inicializado com sucesso!")
        except Exception as e:
            logger.error(f"Erro na inicialização: {e}")
    
    def _is_cache_valid(self, key: str) -> bool:
        """Verifica se o cache ainda é válido"""
        if key not in self.last_update:
            return False
        
        elapsed = time.time() - self.last_update[key]
        return elapsed < self.cache_duration
    
    def _update_cache(self, key: str, data: Any):
        """Atualiza o cache com novos dados"""
        self.cache[key] = data
        self.last_update[key] = time.time()
    
    def get_exchange_rate(self, force_update: bool = False) -> Dict[str, float]:
        """
        Busca a cotação atual do dólar e outras moedas usando Yahoo Finance
        """
        cache_key = "exchange_rates"
        
        if not force_update and self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        try:
            # Usar Yahoo Finance para cotações em tempo real
            usd_brl_ticker = yf.Ticker("USDBRL=X")
            eur_brl_ticker = yf.Ticker("EURBRL=X")
            gbp_brl_ticker = yf.Ticker("GBPBRL=X")
            
            # Buscar dados mais recentes (últimos 2 dias para garantir dados atuais)
            usd_data = usd_brl_ticker.history(period="2d")
            eur_data = eur_brl_ticker.history(period="2d")
            gbp_data = gbp_brl_ticker.history(period="2d")
            
            if not usd_data.empty and not eur_data.empty and not gbp_data.empty:
                rates = {
                    'USD_BRL': float(usd_data['Close'].iloc[-1]),
                    'EUR_BRL': float(eur_data['Close'].iloc[-1]),
                    'GBP_BRL': float(gbp_data['Close'].iloc[-1]),
                    'timestamp': self._format_brazilian_datetime()
                }
                
                self._update_cache(cache_key, rates)
                logger.info(f"Cotação USD/BRL atualizada: R$ {rates['USD_BRL']:.4f}")
                return rates
            else:
                raise ValueError("Dados de câmbio não disponíveis")
            
        except Exception as e:
            logger.error(f"Erro ao buscar câmbio via Yahoo Finance: {e}")
            # Fallback para API alternativa se Yahoo Finance falhar
            try:
                response = requests.get(self.exchange_rate_api, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                rates = {
                    'USD_BRL': data['rates']['BRL'],
                    'EUR_BRL': data['rates']['BRL'] / data['rates']['EUR'],
                    'GBP_BRL': data['rates']['BRL'] / data['rates']['GBP'],
                    'timestamp': self._format_brazilian_datetime()
                }
                
                self._update_cache(cache_key, rates)
                logger.warning(f"Cotação USD/BRL via API alternativa: R$ {rates['USD_BRL']:.4f}")
                return rates
                
            except Exception as fallback_error:
                logger.error(f"Erro no fallback da API: {fallback_error}")
                # Retornar cache antigo se disponível
                return self.cache.get(cache_key, {'USD_BRL': 5.43, 'EUR_BRL': 5.9, 'GBP_BRL': 6.8})
    
    def get_crypto_prices(self, symbols: Optional[List[str]] = None, force_update: bool = False) -> Dict[str, Dict]:
        """
        Busca preços atuais de criptomoedas
        """
        if symbols is None:
            symbols = self.important_symbols['crypto']
        
        cache_key = f"crypto_prices_{','.join(symbols)}"
        
        if not force_update and self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        crypto_data = {}
        
        try:
            # Buscar câmbio uma vez para evitar loops
            exchange_rate = self.get_exchange_rate(force_update)['USD_BRL']
            
            for symbol in symbols:
                # Tratamento especial para USDT (stablecoin)
                if symbol == 'USDT':
                    crypto_data[symbol] = {
                        'price': 1.0,  # USDT sempre vale $1.00
                        'price_brl': 1.0 * exchange_rate,
                        'change_24h': 0.0,  # Stablecoin não varia
                        'volume_24h': 0.0,
                        'high_24h': 1.0,
                        'low_24h': 1.0,
                        'timestamp': self._format_brazilian_datetime()
                    }
                    continue
                
                url = f"{self.binance_base_url}/ticker/price"
                params = {'symbol': symbol}
                
                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                # Buscar informações adicionais
                ticker_url = f"{self.binance_base_url}/ticker/24hr"
                ticker_response = requests.get(ticker_url, params=params, timeout=10)
                ticker_data = ticker_response.json()
                
                crypto_data[symbol] = {
                    'price': float(data['price']),
                    'price_brl': float(data['price']) * exchange_rate,
                    'change_24h': float(ticker_data['priceChangePercent']),
                    'volume_24h': float(ticker_data['volume']),
                    'high_24h': float(ticker_data['highPrice']),
                    'low_24h': float(ticker_data['lowPrice']),
                    'timestamp': self._format_brazilian_datetime()
                }
                
                time.sleep(0.1)  # Evitar rate limiting
            
            self._update_cache(cache_key, crypto_data)
            logger.info(f"Preços de {len(symbols)} criptomoedas atualizados")
            return crypto_data
            
        except Exception as e:
            logger.error(f"Erro ao buscar preços de criptomoedas: {e}")
            return self.cache.get(cache_key, {})
    
    def get_stock_indices(self, symbols: Optional[List[str]] = None, force_update: bool = False) -> Dict[str, Dict]:
        """
        Busca dados de índices de ações e ações individuais
        """
        if symbols is None:
            symbols = self.important_symbols['stocks']
        
        cache_key = f"stock_indices_{','.join(symbols)}"
        
        if not force_update and self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        stock_data = {}
        
        try:
            # Buscar câmbio uma vez para evitar loops
            exchange_rate = self.get_exchange_rate(force_update)['USD_BRL']
            
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="2d")
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    previous_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                    change_pct = ((current_price - previous_price) / previous_price) * 100
                    
                    stock_data[symbol] = {
                        'price': current_price,
                        'price_brl': current_price * exchange_rate if 'USD' in symbol else current_price,
                        'change_24h': change_pct,
                        'volume': hist['Volume'].iloc[-1] if 'Volume' in hist.columns else 0,
                        'high_24h': hist['High'].iloc[-1],
                        'low_24h': hist['Low'].iloc[-1],
                        'name': info.get('longName', symbol),
                        'timestamp': self._format_brazilian_datetime()
                    }
                
                time.sleep(0.1)  # Evitar rate limiting
            
            self._update_cache(cache_key, stock_data)
            logger.info(f"Dados de {len(symbols)} índices/ações atualizados")
            return stock_data
            
        except Exception as e:
            logger.error(f"Erro ao buscar índices de ações: {e}")
            return self.cache.get(cache_key, {})
    
    def get_commodity_prices(self, symbols: Optional[List[str]] = None, force_update: bool = False) -> Dict[str, Dict]:
        """
        Busca preços de commodities (ouro, prata, petróleo)
        """
        if symbols is None:
            symbols = self.important_symbols['commodities']
        
        cache_key = f"commodity_prices_{','.join(symbols)}"
        
        if not force_update and self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        commodity_data = {}
        
        try:
            # Buscar câmbio uma vez para evitar loops
            exchange_rate = self.get_exchange_rate(force_update)['USD_BRL']
            
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="2d")
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    previous_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                    change_pct = ((current_price - previous_price) / previous_price) * 100
                    
                    commodity_data[symbol] = {
                        'price': current_price,
                        'price_brl': current_price * exchange_rate,
                        'change_24h': change_pct,
                        'volume': hist['Volume'].iloc[-1] if 'Volume' in hist.columns else 0,
                        'high_24h': hist['High'].iloc[-1],
                        'low_24h': hist['Low'].iloc[-1],
                        'timestamp': self._format_brazilian_datetime()
                    }
                
                time.sleep(0.1)
            
            self._update_cache(cache_key, commodity_data)
            logger.info(f"Preços de {len(symbols)} commodities atualizados")
            return commodity_data
            
        except Exception as e:
            logger.error(f"Erro ao buscar preços de commodities: {e}")
            return self.cache.get(cache_key, {})
    
    def get_all_market_data(self, force_update: bool = False) -> Dict[str, Any]:
        """
        Busca todos os dados de mercado de uma vez
        """
        cache_key = "all_market_data"
        
        if not force_update and self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        try:
            all_data = {
                'exchange_rates': self.get_exchange_rate(force_update),
                'crypto': self.get_crypto_prices(force_update=force_update),
                'stocks': self.get_stock_indices(force_update=force_update),
                'commodities': self.get_commodity_prices(force_update=force_update),
                'timestamp': self._format_brazilian_datetime()
            }
            
            self._update_cache(cache_key, all_data)
            logger.info("Todos os dados de mercado atualizados")
            return all_data
            
        except Exception as e:
            logger.error(f"Erro ao buscar todos os dados de mercado: {e}")
            return self.cache.get(cache_key, {})
    
    def convert_to_brl(self, usd_amount: float) -> float:
        """
        Converte valor em USD para BRL usando câmbio atual
        """
        exchange_rate = self.get_exchange_rate()
        return usd_amount * exchange_rate['USD_BRL']
    
    def get_portfolio_value_brl(self, portfolio_data: Dict) -> float:
        """
        Calcula o valor total do portfólio em BRL
        """
        total_brl = 0
        exchange_rate = self.get_exchange_rate()
        
        for asset, data in portfolio_data.items():
            if 'value_usd' in data:
                total_brl += data['value_usd'] * exchange_rate['USD_BRL']
            elif 'value_brl' in data:
                total_brl += data['value_brl']
        
        return total_brl 