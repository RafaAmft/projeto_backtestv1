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
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300  # 5 minutos de cache
        self.last_update = {}
        
        # APIs e endpoints
        self.binance_base_url = "https://api.binance.com/api/v3"
        self.exchange_rate_api = "https://api.exchangerate-api.com/v4/latest/USD"
        self.ibge_api = "https://servicodados.ibge.gov.br/api/v3/agregados/1737/periodos/202401/variaveis/2266?localidades=N6[all]"
        
        # Símbolos importantes
        self.important_symbols = {
            'crypto': ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT'],
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
            for symbol in symbols:
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
                    'price_brl': float(data['price']) * self.get_exchange_rate()['USD_BRL'],
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
                        'price_brl': current_price * self.get_exchange_rate()['USD_BRL'] if 'USD' in symbol else current_price,
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
            for symbol in symbols:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="2d")
                
                if not hist.empty:
                    current_price = hist['Close'].iloc[-1]
                    previous_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                    change_pct = ((current_price - previous_price) / previous_price) * 100
                    
                    commodity_data[symbol] = {
                        'price': current_price,
                        'price_brl': current_price * self.get_exchange_rate()['USD_BRL'],
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
    
    def save_market_data(self, filename: str = None):
        """
        Salva os dados de mercado em arquivo JSON
        """
        if filename is None:
            filename = f"market_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            data = self.get_all_market_data()
            
            # Converter tipos numpy para tipos Python nativos
            def convert_numpy_types(obj):
                if isinstance(obj, dict):
                    return {key: convert_numpy_types(value) for key, value in obj.items()}
                elif isinstance(obj, list):
                    return [convert_numpy_types(item) for item in obj]
                elif hasattr(obj, 'item'):  # numpy types
                    return obj.item()
                else:
                    return obj
            
            data = convert_numpy_types(data)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Dados de mercado salvos em {filename}")
            return filename
        except Exception as e:
            logger.error(f"Erro ao salvar dados de mercado: {e}")
            return None
    
    def get_market_summary(self) -> Dict[str, Any]:
        """
        Retorna um resumo dos principais indicadores de mercado
        """
        try:
            data = self.get_all_market_data()
            
            summary = {
                'timestamp': self._format_brazilian_datetime(),
                'exchange_rate_usd_brl': data['exchange_rates']['USD_BRL'],
                'bitcoin_price_brl': data['crypto'].get('BTCUSDT', {}).get('price_brl', 0),
                'bitcoin_change_24h': data['crypto'].get('BTCUSDT', {}).get('change_24h', 0),
                'ibovespa_price': data['stocks'].get('^BVSP', {}).get('price', 0),
                'ibovespa_change_24h': data['stocks'].get('^BVSP', {}).get('change_24h', 0),
                'sp500_price': data['stocks'].get('^GSPC', {}).get('price', 0),
                'sp500_change_24h': data['stocks'].get('^GSPC', {}).get('change_24h', 0),
                'gold_price_brl': data['commodities'].get('GC=F', {}).get('price_brl', 0),
                'gold_change_24h': data['commodities'].get('GC=F', {}).get('change_24h', 0)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Erro ao gerar resumo de mercado: {e}")
            return {}
    
    def get_enhanced_market_summary(self, days: int = 30) -> Dict[str, Any]:
        """
        Retorna um resumo completo com dados históricos e métricas avançadas
        """
        try:
            # Dados atuais
            current_data = self.get_all_market_data()
            
            # Dados históricos dos benchmarks
            benchmarks = self.calculate_benchmark_metrics(days)
            
            # Dados históricos do dólar
            usd_history = self.get_historical_exchange_rate(days)
            
            # Calcular período de análise
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            period_info = {
                'days': days,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'period_description': f"{days} dias ({start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')})",
                'analysis_date': end_date.strftime('%d/%m/%Y às %H:%M')
            }
            
            summary = {
                'timestamp': self._format_brazilian_datetime(),
                'period_info': period_info,
                
                # Dados atuais
                'current_data': {
                    'exchange_rate_usd_brl': current_data['exchange_rates']['USD_BRL'],
                    'bitcoin_price_brl': current_data['crypto'].get('BTCUSDT', {}).get('price_brl', 0),
                    'bitcoin_change_24h': current_data['crypto'].get('BTCUSDT', {}).get('change_24h', 0),
                    'ibovespa_price': current_data['stocks'].get('^BVSP', {}).get('price', 0),
                    'ibovespa_change_24h': current_data['stocks'].get('^BVSP', {}).get('change_24h', 0),
                    'sp500_price': current_data['stocks'].get('^GSPC', {}).get('price', 0),
                    'sp500_change_24h': current_data['stocks'].get('^GSPC', {}).get('change_24h', 0),
                    'gold_price_brl': current_data['commodities'].get('GC=F', {}).get('price_brl', 0),
                    'gold_change_24h': current_data['commodities'].get('GC=F', {}).get('change_24h', 0)
                },
                
                # Métricas históricas dos benchmarks
                'benchmarks': benchmarks,
                
                # Dados históricos do dólar
                'usd_history': usd_history,
                
                # Análise de correlação
                'correlation_analysis': self._calculate_correlations(benchmarks),
                
                # Indicadores de mercado
                'market_indicators': {
                    'fear_greed_index': self._estimate_fear_greed_index(current_data),
                    'market_sentiment': self._analyze_market_sentiment(current_data),
                    'volatility_regime': self._classify_volatility_regime(benchmarks)
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Erro ao gerar resumo completo de mercado: {e}")
            return {}
    
    def _calculate_correlations(self, benchmarks: Dict) -> Dict[str, float]:
        """Calcula correlações entre diferentes benchmarks"""
        try:
            correlations = {}
            
            # Extrair retornos diários
            returns_data = {}
            for name, data in benchmarks.items():
                if 'historical_data' in data and 'daily_returns' in data['historical_data']:
                    returns_data[name] = data['historical_data']['daily_returns']
            
            # Calcular correlações
            if len(returns_data) >= 2:
                for i, (name1, returns1) in enumerate(returns_data.items()):
                    for name2, returns2 in list(returns_data.items())[i+1:]:
                        if len(returns1) == len(returns2):
                            correlation = np.corrcoef(returns1, returns2)[0, 1]
                            correlations[f"{name1}_vs_{name2}"] = correlation
            
            return correlations
            
        except Exception as e:
            logger.error(f"Erro ao calcular correlações: {e}")
            return {}
    
    def _estimate_fear_greed_index(self, current_data: Dict) -> Dict[str, Any]:
        """Estima um índice de medo/ganância baseado nos dados atuais"""
        try:
            # Calcular componentes do índice
            components = {}
            
            # 1. Volatilidade do Bitcoin (25% peso)
            btc_change = abs(current_data['crypto'].get('BTCUSDT', {}).get('change_24h', 0))
            components['bitcoin_volatility'] = min(100, btc_change * 10)  # Normalizar para 0-100
            
            # 2. Performance do S&P 500 (25% peso)
            sp500_change = current_data['stocks'].get('^GSPC', {}).get('change_24h', 0)
            components['sp500_momentum'] = 50 + (sp500_change * 5)  # 50 é neutro
            
            # 3. Força do dólar (25% peso)
            usd_brl = current_data['exchange_rates']['USD_BRL']
            # Assumir que dólar forte = medo, dólar fraco = ganância
            components['dollar_strength'] = 50 + ((usd_brl - 5.0) * 20)  # Normalizar
            
            # 4. Performance do ouro (25% peso)
            gold_change = current_data['commodities'].get('GC=F', {}).get('change_24h', 0)
            components['gold_momentum'] = 50 + (gold_change * 5)
            
            # Calcular índice final (média ponderada)
            fear_greed = (
                components['bitcoin_volatility'] * 0.25 +
                components['sp500_momentum'] * 0.25 +
                components['dollar_strength'] * 0.25 +
                components['gold_momentum'] * 0.25
            )
            
            # Classificar
            if fear_greed >= 80:
                sentiment = "Extreme Greed"
            elif fear_greed >= 60:
                sentiment = "Greed"
            elif fear_greed >= 40:
                sentiment = "Neutral"
            elif fear_greed >= 20:
                sentiment = "Fear"
            else:
                sentiment = "Extreme Fear"
            
            return {
                'value': fear_greed,
                'sentiment': sentiment,
                'components': components
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular índice de medo/ganância: {e}")
            return {'value': 50, 'sentiment': 'Neutral', 'components': {}}
    
    def _analyze_market_sentiment(self, current_data: Dict) -> str:
        """Analisa o sentimento geral do mercado"""
        try:
            positive_count = 0
            total_count = 0
            
            # Verificar variações positivas
            for asset_type, assets in current_data.items():
                if asset_type in ['crypto', 'stocks', 'commodities']:
                    for asset, data in assets.items():
                        if 'change_24h' in data:
                            total_count += 1
                            if data['change_24h'] > 0:
                                positive_count += 1
            
            if total_count == 0:
                return "Neutral"
            
            positive_ratio = positive_count / total_count
            
            if positive_ratio >= 0.7:
                return "Bullish"
            elif positive_ratio >= 0.4:
                return "Neutral"
            else:
                return "Bearish"
                
        except Exception as e:
            logger.error(f"Erro ao analisar sentimento do mercado: {e}")
            return "Neutral"
    
    def _classify_volatility_regime(self, benchmarks: Dict) -> str:
        """Classifica o regime de volatilidade atual"""
        try:
            volatilities = []
            
            for name, data in benchmarks.items():
                if 'volatility' in data:
                    volatilities.append(data['volatility'])
            
            if not volatilities:
                return "Unknown"
            
            avg_volatility = np.mean(volatilities)
            
            if avg_volatility >= 0.3:
                return "High Volatility"
            elif avg_volatility >= 0.15:
                return "Normal Volatility"
            else:
                return "Low Volatility"
                
        except Exception as e:
            logger.error(f"Erro ao classificar regime de volatilidade: {e}")
            return "Unknown"
    
    def get_historical_exchange_rate(self, days: int = 30) -> pd.DataFrame:
        """
        Busca dados históricos do câmbio USD/BRL
        """
        try:
            # Usar Yahoo Finance para dados históricos do USD/BRL
            ticker = yf.Ticker("USDBRL=X")
            hist_data = ticker.history(period=f"{days}d")
            
            if not hist_data.empty:
                # Calcular variações
                hist_data['daily_return'] = hist_data['Close'].pct_change()
                hist_data['cumulative_return'] = (1 + hist_data['daily_return']).cumprod() - 1
                
                # Converter para formato mais simples
                historical_rates = {
                    'dates': hist_data.index.strftime('%Y-%m-%d').tolist(),
                    'rates': hist_data['Close'].tolist(),
                    'daily_returns': hist_data['daily_return'].fillna(0).tolist(),
                    'cumulative_return': hist_data['cumulative_return'].iloc[-1],
                    'volatility': hist_data['daily_return'].std() * np.sqrt(252),  # Anualizada
                    'max_rate': hist_data['High'].max(),
                    'min_rate': hist_data['Low'].min(),
                    'current_rate': hist_data['Close'].iloc[-1]
                }
                
                logger.info(f"Dados históricos do USD/BRL obtidos para {days} dias")
                return historical_rates
            else:
                logger.warning("Nenhum dado histórico encontrado para USD/BRL")
                return {}
                
        except Exception as e:
            logger.error(f"Erro ao buscar dados históricos do USD/BRL: {e}")
            return {}
    
    def get_historical_crypto_data(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """
        Busca dados históricos de criptomoedas
        """
        try:
            # Usar Yahoo Finance para dados históricos
            ticker = yf.Ticker(f"{symbol}-USD")
            hist_data = ticker.history(period=f"{days}d")
            
            if not hist_data.empty:
                # Calcular métricas
                hist_data['daily_return'] = hist_data['Close'].pct_change()
                hist_data['cumulative_return'] = (1 + hist_data['daily_return']).cumprod() - 1
                
                historical_data = {
                    'dates': hist_data.index.strftime('%Y-%m-%d').tolist(),
                    'prices': hist_data['Close'].tolist(),
                    'volumes': hist_data['Volume'].tolist(),
                    'daily_returns': hist_data['daily_return'].fillna(0).tolist(),
                    'cumulative_return': hist_data['cumulative_return'].iloc[-1],
                    'volatility': hist_data['daily_return'].std() * np.sqrt(252),  # Anualizada
                    'max_price': hist_data['High'].max(),
                    'min_price': hist_data['Low'].min(),
                    'current_price': hist_data['Close'].iloc[-1]
                }
                
                logger.info(f"Dados históricos de {symbol} obtidos para {days} dias")
                return historical_data
            else:
                logger.warning(f"Nenhum dado histórico encontrado para {symbol}")
                return {}
                
        except Exception as e:
            logger.error(f"Erro ao buscar dados históricos de {symbol}: {e}")
            return {}
    
    def get_historical_stock_data(self, symbol: str, days: int = 30) -> pd.DataFrame:
        """
        Busca dados históricos de ações/índices
        """
        try:
            ticker = yf.Ticker(symbol)
            hist_data = ticker.history(period=f"{days}d")
            
            if not hist_data.empty:
                # Calcular métricas
                hist_data['daily_return'] = hist_data['Close'].pct_change()
                hist_data['cumulative_return'] = (1 + hist_data['daily_return']).cumprod() - 1
                
                historical_data = {
                    'dates': hist_data.index.strftime('%Y-%m-%d').tolist(),
                    'prices': hist_data['Close'].tolist(),
                    'volumes': hist_data['Volume'].tolist(),
                    'daily_returns': hist_data['daily_return'].fillna(0).tolist(),
                    'cumulative_return': hist_data['cumulative_return'].iloc[-1],
                    'volatility': hist_data['daily_return'].std() * np.sqrt(252),  # Anualizada
                    'max_price': hist_data['High'].max(),
                    'min_price': hist_data['Low'].min(),
                    'current_price': hist_data['Close'].iloc[-1],
                    'name': ticker.info.get('longName', symbol)
                }
                
                logger.info(f"Dados históricos de {symbol} obtidos para {days} dias")
                return historical_data
            else:
                logger.warning(f"Nenhum dado histórico encontrado para {symbol}")
                return {}
                
        except Exception as e:
            logger.error(f"Erro ao buscar dados históricos de {symbol}: {e}")
            return {}
    
    def calculate_benchmark_metrics(self, days: int = 30) -> Dict[str, Dict]:
        """
        Calcula métricas completas dos benchmarks usando dados históricos
        """
        try:
            benchmarks = {}
            
            # Calcular período de análise
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            period_info = {
                'days': days,
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'period_description': f"{days} dias ({start_date.strftime('%d/%m/%Y')} a {end_date.strftime('%d/%m/%Y')})"
            }
            
            # 1. Dados históricos do dólar
            usd_data = self.get_historical_exchange_rate(days)
            if usd_data:
                benchmarks['USD'] = {
                    'annual_return': usd_data['cumulative_return'] * (365/days),
                    'volatility': usd_data['volatility'],
                    'max_drawdown': self._calculate_max_drawdown(usd_data['rates']),
                    'sharpe_ratio': self._calculate_sharpe_ratio(usd_data['daily_returns']),
                    'description': 'Dólar Americano (dados históricos)',
                    'current_rate': usd_data['current_rate'],
                    'historical_data': usd_data,
                    'period_info': period_info
                }
            
            # 2. Dados históricos do Ibovespa
            ibov_data = self.get_historical_stock_data('^BVSP', days)
            if ibov_data:
                benchmarks['IBOV'] = {
                    'annual_return': ibov_data['cumulative_return'] * (365/days),
                    'volatility': ibov_data['volatility'],
                    'max_drawdown': self._calculate_max_drawdown(ibov_data['prices']),
                    'sharpe_ratio': self._calculate_sharpe_ratio(ibov_data['daily_returns']),
                    'description': 'Índice Bovespa (dados históricos)',
                    'current_price': ibov_data['current_price'],
                    'historical_data': ibov_data,
                    'period_info': period_info
                }
            
            # 3. Dados históricos do S&P 500
            sp500_data = self.get_historical_stock_data('^GSPC', days)
            if sp500_data:
                benchmarks['SP500'] = {
                    'annual_return': sp500_data['cumulative_return'] * (365/days),
                    'volatility': sp500_data['volatility'],
                    'max_drawdown': self._calculate_max_drawdown(sp500_data['prices']),
                    'sharpe_ratio': self._calculate_sharpe_ratio(sp500_data['daily_returns']),
                    'description': 'S&P 500 (dados históricos)',
                    'current_price': sp500_data['current_price'],
                    'historical_data': sp500_data,
                    'period_info': period_info
                }
            
            # 4. Dados históricos do Bitcoin
            btc_data = self.get_historical_crypto_data('BTC', days)
            if btc_data:
                benchmarks['BTC'] = {
                    'annual_return': btc_data['cumulative_return'] * (365/days),
                    'volatility': btc_data['volatility'],
                    'max_drawdown': self._calculate_max_drawdown(btc_data['prices']),
                    'sharpe_ratio': self._calculate_sharpe_ratio(btc_data['daily_returns']),
                    'description': 'Bitcoin (dados históricos)',
                    'current_price': btc_data['current_price'],
                    'historical_data': btc_data,
                    'period_info': period_info
                }
            
            # 5. CDI (dados reais via API do Banco Central)
            cdi_data = self.get_cdi_rate()
            cdi_annual_rate = cdi_data['annual_rate']
            cdi_daily_rate = cdi_data['daily_rate']
            
            benchmarks['CDI'] = {
                'annual_return': cdi_annual_rate,
                'volatility': 0.008,  # 0.8% volatilidade (baixa volatilidade do CDI)
                'max_drawdown': -0.0005,  # Mínimo drawdown
                'sharpe_ratio': cdi_annual_rate / 0.008,  # Sharpe alto
                'description': f'Certificado de Depósito Interbancário (dados reais - {cdi_data["source"]})',
                'current_rate': cdi_daily_rate,  # Taxa diária real
                'current_rate_pct': cdi_data['daily_rate_pct'],
                'annual_rate_pct': cdi_data['annual_rate_pct'],
                'date': cdi_data['date'],
                'period_info': period_info
            }
            
            logger.info(f"Métricas de {len(benchmarks)} benchmarks calculadas para período de {days} dias")
            return benchmarks
            
        except Exception as e:
            logger.error(f"Erro ao calcular métricas dos benchmarks: {e}")
            return {}
    
    def _calculate_max_drawdown(self, prices: List[float]) -> float:
        """Calcula o máximo drawdown de uma série de preços"""
        try:
            if not prices:
                return 0
            
            peak = prices[0]
            max_dd = 0
            
            for price in prices:
                if price > peak:
                    peak = price
                dd = (price - peak) / peak
                if dd < max_dd:
                    max_dd = dd
            
            return max_dd
        except Exception:
            return 0
    
    def _calculate_sharpe_ratio(self, returns: List[float], risk_free_rate: float = 0.12) -> float:
        """Calcula o Sharpe Ratio de uma série de retornos"""
        try:
            if not returns:
                return 0
            
            # Converter para numpy array
            returns_array = np.array(returns)
            
            # Calcular retorno médio e desvio padrão
            mean_return = np.mean(returns_array)
            std_return = np.std(returns_array)
            
            if std_return == 0:
                return 0
            
            # Sharpe Ratio anualizado
            sharpe = (mean_return * 252 - risk_free_rate) / (std_return * np.sqrt(252))
            return sharpe
        except Exception:
            return 0
    
    def get_cdi_rate(self, force_update: bool = False) -> Dict[str, Any]:
        """
        Busca a taxa do CDI em tempo real via API do Banco Central do Brasil
        
        Returns:
            dict: Dados do CDI incluindo taxa diária e anualizada
        """
        cache_key = "cdi_rate"
        
        if not force_update and self._is_cache_valid(cache_key):
            return self.cache[cache_key]
        
        try:
            # API do Banco Central do Brasil - Série 12 (CDI)
            url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.12/dados/ultimos/1?formato=json"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data and len(data) > 0:
                # Converter taxa diária para anual
                daily_rate = float(data[0]['valor']) / 100  # Converter de % para decimal
                annual_rate = ((1 + daily_rate) ** 252) - 1  # 252 dias úteis no ano
                
                cdi_data = {
                    'daily_rate': daily_rate,
                    'annual_rate': annual_rate,
                    'daily_rate_pct': daily_rate * 100,
                    'annual_rate_pct': annual_rate * 100,
                    'date': data[0]['data'],
                    'source': 'Banco Central do Brasil',
                    'timestamp': self._format_brazilian_datetime()
                }
                
                self._update_cache(cache_key, cdi_data)
                logger.info(f"Taxa do CDI atualizada: {cdi_data['daily_rate_pct']:.4f}% ao dia ({cdi_data['annual_rate_pct']:.2f}% ao ano)")
                return cdi_data
            else:
                raise ValueError("Dados do CDI não encontrados na API")
                
        except Exception as e:
            logger.error(f"Erro ao buscar taxa do CDI: {e}")
            # Retornar dados de fallback
            fallback_data = {
                'daily_rate': 0.0004,  # 0.04% ao dia (aproximado)
                'annual_rate': 0.105,  # 10.5% ao ano (aproximado)
                'daily_rate_pct': 0.04,
                'annual_rate_pct': 10.5,
                'date': datetime.now().strftime('%d/%m/%Y'),
                'source': 'Fallback (dados aproximados)',
                'timestamp': self._format_brazilian_datetime()
            }
            return fallback_data

    def get_historical_analysis_periods(self) -> Dict[str, Dict]:
        """
        Define os períodos de análise temporal
        """
        now = datetime.now()
        
        periods = {
            '1_month': {
                'days': 30,
                'description': 'Último mês',
                'start_date': (now - timedelta(days=30)).strftime('%d/%m/%Y'),
                'end_date': now.strftime('%d/%m/%Y')
            },
            '3_months': {
                'days': 90,
                'description': 'Últimos 3 meses',
                'start_date': (now - timedelta(days=90)).strftime('%d/%m/%Y'),
                'end_date': now.strftime('%d/%m/%Y')
            },
            '6_months': {
                'days': 180,
                'description': 'Últimos 6 meses',
                'start_date': (now - timedelta(days=180)).strftime('%d/%m/%Y'),
                'end_date': now.strftime('%d/%m/%Y')
            },
            '1_year': {
                'days': 365,
                'description': 'Último ano',
                'start_date': (now - timedelta(days=365)).strftime('%d/%m/%Y'),
                'end_date': now.strftime('%d/%m/%Y')
            },
            '3_years': {
                'days': 1095,
                'description': 'Últimos 3 anos',
                'start_date': (now - timedelta(days=1095)).strftime('%d/%m/%Y'),
                'end_date': now.strftime('%d/%m/%Y')
            },
            '5_years': {
                'days': 1825,
                'description': 'Últimos 5 anos',
                'start_date': (now - timedelta(days=1825)).strftime('%d/%m/%Y'),
                'end_date': now.strftime('%d/%m/%Y')
            }
        }
        
        return periods

    def get_monthly_returns(self, symbol: str, months: int = 60) -> Dict[str, Any]:
        """
        Calcula retornos mensais para os últimos N meses
        
        Args:
            symbol: Símbolo do ativo
            months: Número de meses (padrão: 60 = 5 anos)
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months * 30)
            
            # Buscar dados históricos
            if 'USDT' in symbol:  # Criptomoeda
                data = self.get_historical_crypto_data(symbol.replace('USDT', ''), months * 30)
            elif symbol in ['^BVSP', '^GSPC', '^IXIC', '^DJI']:  # Índice
                data = self.get_historical_stock_data(symbol, months * 30)
            else:  # Ação
                data = self.get_historical_stock_data(symbol, months * 30)
            
            if not data or 'prices' not in data:
                return {}
            
            # Calcular retornos mensais
            prices = data['prices']
            dates = data['dates']
            
            monthly_returns = []
            monthly_dates = []
            
            for i in range(0, len(prices), 30):  # Agrupar por mês
                if i + 30 < len(prices):
                    start_price = prices[i]
                    end_price = prices[i + 30]
                    monthly_return = (end_price - start_price) / start_price
                    monthly_returns.append(monthly_return)
                    monthly_dates.append(dates[i])
            
            return {
                'symbol': symbol,
                'monthly_returns': monthly_returns,
                'monthly_dates': monthly_dates,
                'total_months': len(monthly_returns),
                'avg_monthly_return': np.mean(monthly_returns) if monthly_returns else 0,
                'monthly_volatility': np.std(monthly_returns) if monthly_returns else 0,
                'best_month': max(monthly_returns) if monthly_returns else 0,
                'worst_month': min(monthly_returns) if monthly_returns else 0
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular retornos mensais para {symbol}: {e}")
            return {}

    def get_annual_returns(self, symbol: str, years: int = 5) -> Dict[str, Any]:
        """
        Calcula retornos anuais para os últimos N anos
        
        Args:
            symbol: Símbolo do ativo
            years: Número de anos (padrão: 5)
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=years * 365)
            
            # Buscar dados históricos
            if 'USDT' in symbol:  # Criptomoeda
                data = self.get_historical_crypto_data(symbol.replace('USDT', ''), years * 365)
            elif symbol in ['^BVSP', '^GSPC', '^IXIC', '^DJI']:  # Índice
                data = self.get_historical_stock_data(symbol, years * 365)
            else:  # Ação
                data = self.get_historical_stock_data(symbol, years * 365)
            
            if not data or 'prices' not in data:
                return {}
            
            # Calcular retornos anuais
            prices = data['prices']
            dates = data['dates']
            
            annual_returns = []
            annual_dates = []
            
            for i in range(0, len(prices), 365):  # Agrupar por ano
                if i + 365 < len(prices):
                    start_price = prices[i]
                    end_price = prices[i + 365]
                    annual_return = (end_price - start_price) / start_price
                    annual_returns.append(annual_return)
                    annual_dates.append(dates[i])
            
            return {
                'symbol': symbol,
                'annual_returns': annual_returns,
                'annual_dates': annual_dates,
                'total_years': len(annual_returns),
                'avg_annual_return': np.mean(annual_returns) if annual_returns else 0,
                'annual_volatility': np.std(annual_returns) if annual_returns else 0,
                'best_year': max(annual_returns) if annual_returns else 0,
                'worst_year': min(annual_returns) if annual_returns else 0
            }
            
        except Exception as e:
            logger.error(f"Erro ao calcular retornos anuais para {symbol}: {e}")
            return {}

    def generate_temporal_analysis(self, symbols: List[str], period: str = '5_years') -> Dict[str, Any]:
        """
        Gera análise temporal completa para múltiplos ativos
        
        Args:
            symbols: Lista de símbolos para analisar
            period: Período de análise ('1_month', '3_months', '6_months', '1_year', '3_years', '5_years')
        """
        try:
            periods = self.get_historical_analysis_periods()
            period_info = periods.get(period, periods['5_years'])
            
            analysis = {
                'period_info': period_info,
                'analysis_date': datetime.now().strftime('%d/%m/%Y às %H:%M:%S'),
                'monthly_analysis': {},
                'annual_analysis': {},
                'summary': {}
            }
            
            # Análise mensal
            for symbol in symbols:
                monthly_data = self.get_monthly_returns(symbol, period_info['days'] // 30)
                if monthly_data:
                    analysis['monthly_analysis'][symbol] = monthly_data
            
            # Análise anual
            for symbol in symbols:
                annual_data = self.get_annual_returns(symbol, period_info['days'] // 365)
                if annual_data:
                    analysis['annual_analysis'][symbol] = annual_data
            
            # Resumo consolidado
            analysis['summary'] = self._calculate_temporal_summary(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Erro ao gerar análise temporal: {e}")
            return {}

    def _calculate_temporal_summary(self, analysis: Dict) -> Dict[str, Any]:
        """Calcula resumo da análise temporal"""
        try:
            monthly_data = analysis.get('monthly_analysis', {})
            annual_data = analysis.get('annual_analysis', {})
            
            # Estatísticas mensais
            all_monthly_returns = []
            for symbol_data in monthly_data.values():
                all_monthly_returns.extend(symbol_data.get('monthly_returns', []))
            
            # Estatísticas anuais
            all_annual_returns = []
            for symbol_data in annual_data.values():
                all_annual_returns.extend(symbol_data.get('annual_returns', []))
            
            summary = {
                'total_assets_analyzed': len(monthly_data),
                'period_description': analysis.get('period_info', {}).get('description', ''),
                'monthly_stats': {
                    'avg_return': np.mean(all_monthly_returns) if all_monthly_returns else 0,
                    'volatility': np.std(all_monthly_returns) if all_monthly_returns else 0,
                    'best_month': max(all_monthly_returns) if all_monthly_returns else 0,
                    'worst_month': min(all_monthly_returns) if all_monthly_returns else 0,
                    'positive_months': sum(1 for r in all_monthly_returns if r > 0),
                    'total_months': len(all_monthly_returns)
                },
                'annual_stats': {
                    'avg_return': np.mean(all_annual_returns) if all_annual_returns else 0,
                    'volatility': np.std(all_annual_returns) if all_annual_returns else 0,
                    'best_year': max(all_annual_returns) if all_annual_returns else 0,
                    'worst_year': min(all_annual_returns) if all_annual_returns else 0,
                    'positive_years': sum(1 for r in all_annual_returns if r > 0),
                    'total_years': len(all_annual_returns)
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Erro ao calcular resumo temporal: {e}")
            return {}

# Instância global para uso em outros módulos
market_indices = MarketIndicesManager() 