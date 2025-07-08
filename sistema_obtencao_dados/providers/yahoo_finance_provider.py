#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Provider Otimizado para Yahoo Finance
Integra com Cache Manager e evita rate limiting
"""

import sys
import os
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import requests

# Adicionar diretórios ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from ..core.cache_manager import CacheManager
from ..models.data_models import DataType, DataSource, DataQuality

logger = logging.getLogger(__name__)

class YahooFinanceProvider:
    """
    Provider otimizado para Yahoo Finance com cache integrado
    """
    
    def __init__(self, cache_manager: CacheManager, delay_between_requests: float = 2.0):
        """
        Inicializa o provider Yahoo Finance
        
        Args:
            cache_manager: Instância do Cache Manager
            delay_between_requests: Delay em segundos entre requisições
        """
        self.cache_manager = cache_manager
        self.delay = delay_between_requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        logger.info(f"Yahoo Finance Provider inicializado com delay de {self.delay}s")
    
    def get_stock_price(self, symbol: str, use_cache: bool = True) -> Optional[float]:
        """
        Obtém o preço atual de uma ação com cache
        
        Args:
            symbol: Símbolo da ação (ex: 'PETR4.SA', 'AAPL')
            use_cache: Se deve usar cache
            
        Returns:
            Preço atual ou None se erro
        """
        cache_key = f"yahoo_price_{symbol}"
        
        # Tentar cache primeiro
        if use_cache:
            cached_data = self.cache_manager.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit para {symbol}: {cached_data}")
                return cached_data
        
        # Buscar dados reais
        try:
            logger.info(f"Buscando preço real para {symbol}...")
            
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                    result = data['chart']['result'][0]
                    if 'meta' in result and 'regularMarketPrice' in result['meta']:
                        price = result['meta']['regularMarketPrice']
                        
                        # Armazenar no cache
                        if use_cache:
                            self.cache_manager.set(
                                key=cache_key,
                                data=price,
                                data_type=DataType.STOCK,
                                expires_in=300,  # 5 minutos
                                source=DataSource.YAHOO_FINANCE,
                                quality=DataQuality.GOOD
                            )
                            logger.debug(f"Preço de {symbol} armazenado no cache: {price}")
                        
                        return price
            
            elif response.status_code == 429:
                logger.warning(f"Rate limit atingido para {symbol}. Aguardando 10 segundos...")
                time.sleep(10)
                return self.get_stock_price(symbol, use_cache)  # Retry
                
            logger.warning(f"Erro ao buscar {symbol}: Status {response.status_code}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar {symbol}: {e}")
            return None
    
    def get_multiple_prices(self, symbols: List[str], use_cache: bool = True) -> Dict[str, float]:
        """
        Obtém preços de múltiplas ações com cache e delays adequados
        
        Args:
            symbols: Lista de símbolos
            use_cache: Se deve usar cache
            
        Returns:
            Dicionário com símbolo -> preço
        """
        results = {}
        
        for i, symbol in enumerate(symbols):
            logger.info(f"Processando {symbol}... ({i+1}/{len(symbols)})")
            
            price = self.get_stock_price(symbol, use_cache)
            if price:
                results[symbol] = price
                logger.info(f"✅ {symbol}: ${price:.2f}")
            else:
                logger.warning(f"❌ {symbol}: Erro ao obter preço")
            
            # Delay entre requisições (exceto na última)
            if i < len(symbols) - 1:
                logger.debug(f"Aguardando {self.delay} segundos...")
                time.sleep(self.delay)
        
        return results
    
    def get_stock_data(self, symbol: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Obtém dados completos de uma ação com cache
        
        Args:
            symbol: Símbolo da ação
            use_cache: Se deve usar cache
            
        Returns:
            Dicionário com dados da ação ou None
        """
        cache_key = f"yahoo_data_{symbol}"
        
        # Tentar cache primeiro
        if use_cache:
            cached_data = self.cache_manager.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit para dados de {symbol}")
                return cached_data
        
        # Buscar dados reais
        try:
            logger.info(f"Buscando dados completos para {symbol}...")
            
            url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}"
            params = {
                'modules': 'financialData,quoteType,defaultKeyStatistics,assetProfile,summaryDetail',
                'formatted': 'false'
            }
            
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extrair dados relevantes
                stock_data = {
                    'symbol': symbol,
                    'timestamp': datetime.now().isoformat(),
                    'source': 'yahoo_finance'
                }
                
                # Dados financeiros
                if 'financialData' in data and data['financialData']:
                    fin_data = data['financialData']
                    stock_data.update({
                        'current_price': fin_data.get('currentPrice'),
                        'target_price': fin_data.get('targetMeanPrice'),
                        'pe_ratio': fin_data.get('forwardPE'),
                        'market_cap': fin_data.get('marketCap'),
                        'beta': fin_data.get('beta')
                    })
                
                # Dados do resumo
                if 'summaryDetail' in data and data['summaryDetail']:
                    sum_data = data['summaryDetail']
                    stock_data.update({
                        'volume': sum_data.get('volume'),
                        'avg_volume': sum_data.get('averageVolume'),
                        'day_high': sum_data.get('dayHigh'),
                        'day_low': sum_data.get('dayLow'),
                        'open': sum_data.get('open'),
                        'previous_close': sum_data.get('previousClose')
                    })
                
                # Armazenar no cache
                if use_cache:
                    self.cache_manager.set(
                        key=cache_key,
                        data=stock_data,
                        data_type=DataType.STOCK,
                        expires_in=600,  # 10 minutos
                        source=DataSource.YAHOO_FINANCE,
                        quality=DataQuality.GOOD
                    )
                    logger.debug(f"Dados de {symbol} armazenados no cache")
                
                return stock_data
            
            elif response.status_code == 429:
                logger.warning(f"Rate limit atingido para {symbol}. Aguardando 15 segundos...")
                time.sleep(15)
                return self.get_stock_data(symbol, use_cache)  # Retry
                
            logger.warning(f"Erro ao buscar dados de {symbol}: Status {response.status_code}")
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar dados de {symbol}: {e}")
            return None
    
    def get_portfolio_data(self, symbols: List[str], use_cache: bool = True) -> Dict[str, Any]:
        """
        Obtém dados de um portfólio de ações
        
        Args:
            symbols: Lista de símbolos
            use_cache: Se deve usar cache
            
        Returns:
            Dicionário com dados do portfólio
        """
        logger.info(f"Obtendo dados do portfólio com {len(symbols)} ações...")
        
        portfolio_data = {
            'timestamp': datetime.now().isoformat(),
            'symbols': symbols,
            'data': {},
            'summary': {
                'total_symbols': len(symbols),
                'successful_requests': 0,
                'failed_requests': 0
            }
        }
        
        for i, symbol in enumerate(symbols):
            try:
                data = self.get_stock_data(symbol, use_cache)
                if data:
                    portfolio_data['data'][symbol] = data
                    portfolio_data['summary']['successful_requests'] += 1
                    logger.info(f"✅ {symbol}: Dados obtidos")
                else:
                    portfolio_data['summary']['failed_requests'] += 1
                    logger.warning(f"❌ {symbol}: Falha ao obter dados")
                
                # Delay entre requisições
                if i < len(symbols) - 1:
                    time.sleep(self.delay)
                    
            except Exception as e:
                portfolio_data['summary']['failed_requests'] += 1
                logger.error(f"Erro ao processar {symbol}: {e}")
        
        # Armazenar portfólio no cache
        if use_cache:
            cache_key = f"portfolio_{'_'.join(sorted(symbols))}"
            self.cache_manager.set(
                key=cache_key,
                data=portfolio_data,
                data_type=DataType.PORTFOLIO,
                expires_in=900,  # 15 minutos
                source=DataSource.YAHOO_FINANCE,
                quality=DataQuality.GOOD
            )
        
        logger.info(f"Portfólio processado: {portfolio_data['summary']['successful_requests']}/{len(symbols)} sucessos")
        return portfolio_data

def test_yahoo_provider():
    """Teste do provider Yahoo Finance"""
    print("🧪 TESTE YAHOO FINANCE PROVIDER")
    print("=" * 50)
    
    try:
        # Configuração do cache
        config = {
            'memory': {
                'enabled': True,
                'max_size': 100,
                'cleanup_interval': 300
            },
            'persistent': {
                'enabled': True,
                'storage_type': 'json',
                'directory': 'test_yahoo_cache',
                'backup_enabled': False,
                'backup_interval': 3600
            },
            'expiration': {
                'crypto': 60,
                'stock': 300
            }
        }
        
        # Inicializar Cache Manager
        cache_manager = CacheManager(config)
        
        # Inicializar Provider
        provider = YahooFinanceProvider(cache_manager, delay_between_requests=3.0)
        
        # Teste 1: Preços individuais
        print("📊 Teste 1: Preços individuais...")
        symbols = ['PETR4.SA', 'VALE3.SA']
        
        for symbol in symbols:
            price = provider.get_stock_price(symbol)
            if price:
                print(f"✅ {symbol}: R$ {price:.2f}")
            else:
                print(f"❌ {symbol}: Erro")
        
        # Teste 2: Múltiplos preços
        print("\n📊 Teste 2: Múltiplos preços...")
        prices = provider.get_multiple_prices(symbols)
        print(f"Resultados: {len(prices)}/{len(symbols)} preços obtidos")
        
        # Teste 3: Dados completos
        print("\n📊 Teste 3: Dados completos...")
        data = provider.get_stock_data('PETR4.SA')
        if data:
            print(f"✅ PETR4.SA: Preço R$ {data.get('current_price', 'N/A')}")
            print(f"   Volume: {data.get('volume', 'N/A')}")
            print(f"   PE Ratio: {data.get('pe_ratio', 'N/A')}")
        else:
            print("❌ Erro ao obter dados completos")
        
        # Teste 4: Portfólio
        print("\n📊 Teste 4: Dados de portfólio...")
        portfolio = provider.get_portfolio_data(symbols)
        print(f"Portfólio: {portfolio['summary']['successful_requests']}/{len(symbols)} sucessos")
        
        # Estatísticas do cache
        stats = cache_manager.get_stats()
        print(f"\n📈 Estatísticas do Cache:")
        print(f"   Hit Rate: {stats.get('hit_rate', 0):.1f}%")
        print(f"   Hits: {stats['hits']}")
        print(f"   Misses: {stats['misses']}")
        print(f"   Sets: {stats['sets']}")
        
        # Shutdown
        cache_manager.shutdown()
        print("\n✅ Teste concluído com sucesso!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_yahoo_provider() 