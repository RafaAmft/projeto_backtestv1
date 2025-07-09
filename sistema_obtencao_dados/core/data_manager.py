#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Manager Central - Orquestrador de Dados Financeiros
Integra todos os providers com cache robusto e fallback inteligente
"""

import sys
import os
import time
import logging
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Adicionar diretórios ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from .cache_manager import CacheManager
from ..models.data_models import (
    DataType, DataSource, DataQuality, PriceData, 
    ExchangeRate, HistoricalData, DataRequest, DataResponse
)
from ..providers.yahoo_finance_provider import YahooFinanceProvider
from ..providers.fundos_provider import FundosProvider

logger = logging.getLogger(__name__)

class DataManager:
    """
    Gerenciador central de dados financeiros
    Orquestra providers, cache e fallback inteligente
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Inicializa o Data Manager
        
        Args:
            config_path: Caminho para arquivo de configuração
        """
        self.config = self._load_config(config_path)
        self.cache_manager = CacheManager(self.config['cache'])
        
        # Inicializar providers
        self.providers = self._initialize_providers()
        
        # Configurações
        self.timeout = self.config['timeout']['default']
        self.retry_config = self.config['retry']
        self.fallback_config = self.config['fallback']
        
        # Threading
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.lock = threading.RLock()
        
        # Estatísticas
        self.stats = {
            'requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'provider_requests': {},
            'errors': 0,
            'fallbacks': 0
        }
        
        logger.info("Data Manager inicializado com sucesso")
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """Carrega configuração do sistema"""
        if config_path is None:
            config_path = str(Path(__file__).parent.parent / "config.yaml")
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuração carregada de: {config_path}")
            return config
        except Exception as e:
            logger.error(f"Erro ao carregar configuração: {e}")
            raise
    
    def _initialize_providers(self) -> Dict[str, Any]:
        """Inicializa todos os providers configurados"""
        providers = {}
        
        # Yahoo Finance Provider
        if self.config['apis']['yahoo_finance']['enabled']:
            try:
                providers['yahoo_finance'] = YahooFinanceProvider(
                    cache_manager=self.cache_manager,
                    delay_between_requests=2.0
                )
                logger.info("Yahoo Finance Provider inicializado")
            except Exception as e:
                logger.error(f"Erro ao inicializar Yahoo Finance Provider: {e}")
        
        # Fundos Provider
        try:
            providers['fundos'] = FundosProvider(
                cache_manager=self.cache_manager,
                delay_between_requests=2.0
            )
            logger.info("Fundos Provider inicializado")
        except Exception as e:
            logger.error(f"Erro ao inicializar Fundos Provider: {e}")
        
        return providers
    
    def get_stock_price(self, symbol: str, force_refresh: bool = False) -> Optional[PriceData]:
        """
        Obtém preço de ação
        
        Args:
            symbol: Símbolo da ação (ex: PETR4.SA)
            force_refresh: Forçar atualização ignorando cache
            
        Returns:
            Dados de preço ou None se erro
        """
        cache_key = f"stock_price_{symbol}"
        
        # Tentar cache primeiro (se não forçar refresh)
        if not force_refresh:
            cached_data = self.cache_manager.get(cache_key)
            if cached_data:
                self.stats['cache_hits'] += 1
                logger.debug(f"Cache hit para {symbol}")
                return cached_data
        
        self.stats['cache_misses'] += 1
        self.stats['requests'] += 1
        
        # Buscar dados dos providers
        data = self._fetch_from_providers(
            symbol=symbol,
            data_type=DataType.STOCK,
            sources=[DataSource.YAHOO_FINANCE],
            cache_key=cache_key
        )
        
        return data
    
    def get_crypto_price(self, symbol: str, force_refresh: bool = False) -> Optional[PriceData]:
        """
        Obtém preço de criptomoeda
        
        Args:
            symbol: Símbolo da cripto (ex: BTCUSDT)
            force_refresh: Forçar atualização ignorando cache
            
        Returns:
            Dados de preço ou None se erro
        """
        cache_key = f"crypto_price_{symbol}"
        
        # Tentar cache primeiro
        if not force_refresh:
            cached_data = self.cache_manager.get(cache_key)
            if cached_data:
                self.stats['cache_hits'] += 1
                logger.debug(f"Cache hit para {symbol}")
                return cached_data
        
        self.stats['cache_misses'] += 1
        self.stats['requests'] += 1
        
        # Buscar dados dos providers
        data = self._fetch_from_providers(
            symbol=symbol,
            data_type=DataType.CRYPTO,
            sources=[DataSource.YAHOO_FINANCE, DataSource.BINANCE],
            cache_key=cache_key
        )
        
        return data
    
    def get_exchange_rate(self, from_currency: str, to_currency: str, 
                         force_refresh: bool = False) -> Optional[ExchangeRate]:
        """
        Obtém taxa de câmbio
        
        Args:
            from_currency: Moeda origem (ex: USD)
            to_currency: Moeda destino (ex: BRL)
            force_refresh: Forçar atualização ignorando cache
            
        Returns:
            Dados de câmbio ou None se erro
        """
        cache_key = f"exchange_rate_{from_currency}_{to_currency}"
        
        # Tentar cache primeiro
        if not force_refresh:
            cached_data = self.cache_manager.get(cache_key)
            if cached_data:
                self.stats['cache_hits'] += 1
                logger.debug(f"Cache hit para {from_currency}/{to_currency}")
                return cached_data
        
        self.stats['cache_misses'] += 1
        self.stats['requests'] += 1
        
        # Buscar dados dos providers
        data = self._fetch_from_providers(
            symbol=f"{from_currency}{to_currency}=X",
            data_type=DataType.CURRENCY,
            sources=[DataSource.YAHOO_FINANCE, DataSource.EXCHANGE_RATE_API],
            cache_key=cache_key
        )
        
        return data
    
    def get_fund_data(self, cnpj: str, force_refresh: bool = False) -> Optional[Dict[str, Any]]:
        """
        Obtém dados de fundo de investimento
        
        Args:
            cnpj: CNPJ do fundo
            force_refresh: Forçar atualização ignorando cache
            
        Returns:
            Dados do fundo ou None se erro
        """
        if 'fundos' not in self.providers:
            logger.error("Fundos Provider não disponível")
            return None
        
        try:
            return self.providers['fundos'].get_fundo_data(cnpj, use_cache=not force_refresh)
        except Exception as e:
            logger.error(f"Erro ao buscar dados do fundo {cnpj}: {e}")
            return None
    
    def get_multiple_stocks(self, symbols: List[str], 
                           force_refresh: bool = False) -> Dict[str, PriceData]:
        """
        Obtém preços de múltiplas ações em paralelo
        
        Args:
            symbols: Lista de símbolos
            force_refresh: Forçar atualização ignorando cache
            
        Returns:
            Dicionário com dados de preço por símbolo
        """
        results = {}
        
        # Executar requisições em paralelo
        futures = []
        for symbol in symbols:
            future = self.executor.submit(self.get_stock_price, symbol, force_refresh)
            futures.append((symbol, future))
        
        # Coletar resultados
        for symbol, future in futures:
            try:
                data = future.result(timeout=self.timeout)
                if data:
                    results[symbol] = data
                else:
                    logger.warning(f"Nenhum dado obtido para {symbol}")
            except Exception as e:
                logger.error(f"Erro ao obter dados para {symbol}: {e}")
        
        return results
    
    def _fetch_from_providers(self, symbol: str, data_type: DataType, 
                             sources: List[DataSource], cache_key: str) -> Optional[Any]:
        """
        Busca dados dos providers com fallback
        
        Args:
            symbol: Símbolo do ativo
            data_type: Tipo de dado
            sources: Lista de fontes para tentar
            cache_key: Chave do cache
            
        Returns:
            Dados obtidos ou None se erro
        """
        for source in sources:
            try:
                logger.debug(f"Tentando {source.value} para {symbol}")
                
                if source == DataSource.YAHOO_FINANCE and 'yahoo_finance' in self.providers:
                    price = self.providers['yahoo_finance'].get_stock_price(symbol)
                    if price:
                        # Criar objeto PriceData
                        from ..models.data_models import PriceData
                        data = PriceData(
                            symbol=symbol,
                            price=price,
                            currency="BRL" if ".SA" in symbol else "USD",
                            source=source,
                            quality=DataQuality.GOOD,
                            timestamp=datetime.now()
                        )
                        
                        # Armazenar no cache
                        self.cache_manager.set(
                            key=cache_key,
                            data=data,
                            data_type=data_type,
                            expires_in=self._get_expiration_time(data_type),
                            source=source,
                            quality=DataQuality.GOOD
                        )
                        
                        self.stats['provider_requests'][source.value] = \
                            self.stats['provider_requests'].get(source.value, 0) + 1
                        
                        return data
                
                # Adicionar outros providers aqui conforme implementados
                
            except Exception as e:
                logger.warning(f"Erro com {source.value} para {symbol}: {e}")
                continue
        
        # Se chegou aqui, nenhum provider funcionou
        logger.error(f"Todos os providers falharam para {symbol}")
        self.stats['errors'] += 1
        
        # Tentar fallback se habilitado
        if self.fallback_config['enabled']:
            return self._try_fallback(symbol, data_type, cache_key)
        
        return None
    
    def _get_expiration_time(self, data_type: DataType) -> int:
        """Retorna tempo de expiração para tipo de dado"""
        expiration_config = self.config['cache']['expiration']
        
        if data_type == DataType.STOCK:
            return expiration_config['stock']
        elif data_type == DataType.CRYPTO:
            return expiration_config['crypto']
        elif data_type == DataType.CURRENCY:
            return expiration_config['currency']
        elif data_type == DataType.FUND:
            return expiration_config['fund']
        else:
            return 300  # 5 minutos padrão
    
    def _try_fallback(self, symbol: str, data_type: DataType, cache_key: str) -> Optional[Any]:
        """Tenta fallback com dados simulados"""
        if not self.fallback_config['use_simulated_data']:
            return None
        
        logger.info(f"Usando dados simulados para {symbol}")
        self.stats['fallbacks'] += 1
        
        # Criar dados simulados básicos
        if data_type == DataType.STOCK:
            simulated_data = PriceData(
                symbol=symbol,
                price=50.0,  # Preço simulado
                currency="BRL",
                source=DataSource.SIMULATED,
                quality=DataQuality.POOR,
                metadata={'simulated': True}
            )
        elif data_type == DataType.CRYPTO:
            simulated_data = PriceData(
                symbol=symbol,
                price=50000.0,  # Preço simulado
                currency="USD",
                source=DataSource.SIMULATED,
                quality=DataQuality.POOR,
                metadata={'simulated': True}
            )
        else:
            return None
        
        # Armazenar no cache com expiração curta
        self.cache_manager.set(
            key=cache_key,
            data=simulated_data,
            data_type=data_type,
            expires_in=60,  # 1 minuto para dados simulados
            source=DataSource.SIMULATED,
            quality=DataQuality.POOR
        )
        
        return simulated_data
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema"""
        cache_stats = self.cache_manager.get_stats()
        
        return {
            'data_manager': self.stats,
            'cache': cache_stats,
            'providers': {
                name: 'active' for name in self.providers.keys()
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def clear_cache(self) -> None:
        """Limpa todo o cache"""
        self.cache_manager.clear()
        logger.info("Cache limpo")
    
    def shutdown(self) -> None:
        """Desliga o Data Manager"""
        logger.info("Desligando Data Manager...")
        self.executor.shutdown(wait=True)
        self.cache_manager.shutdown()
        logger.info("Data Manager desligado")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown() 