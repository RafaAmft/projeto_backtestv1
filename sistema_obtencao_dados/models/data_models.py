#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelos de Dados para Sistema de Obtenção de Dados Financeiros
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum
import json

class DataType(Enum):
    """Tipos de dados financeiros"""
    STOCK = "stock"
    CRYPTO = "crypto"
    CURRENCY = "currency"
    COMMODITY = "commodity"
    INDEX = "index"
    FUND = "fund"

class DataSource(Enum):
    """Fontes de dados disponíveis"""
    YAHOO_FINANCE = "yahoo_finance"
    BINANCE = "binance"
    ALPHA_VANTAGE = "alpha_vantage"
    INVESTING = "investing"
    BANCO_CENTRAL = "banco_central"
    EXCHANGE_RATE_API = "exchange_rate_api"
    TWELVE_DATA = "twelve_data"
    SIMULATED = "simulated"
    UNKNOWN = "unknown"

class DataQuality(Enum):
    """Qualidade dos dados"""
    EXCELLENT = "excellent"      # Dados recentes e confiáveis
    GOOD = "good"               # Dados aceitáveis
    FAIR = "fair"               # Dados com algumas limitações
    POOR = "poor"               # Dados problemáticos
    UNKNOWN = "unknown"         # Qualidade não determinada

@dataclass
class PriceData:
    """Dados de preço de um ativo"""
    symbol: str
    price: float
    currency: str = "USD"
    timestamp: datetime = field(default_factory=datetime.now)
    source: DataSource = DataSource.UNKNOWN
    quality: DataQuality = DataQuality.UNKNOWN
    
    # Dados adicionais
    change_24h: Optional[float] = None
    change_percent_24h: Optional[float] = None
    volume: Optional[float] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    open_price: Optional[float] = None
    
    # Metadados
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'symbol': self.symbol,
            'price': self.price,
            'currency': self.currency,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source.value,
            'quality': self.quality.value,
            'change_24h': self.change_24h,
            'change_percent_24h': self.change_percent_24h,
            'volume': self.volume,
            'high_24h': self.high_24h,
            'low_24h': self.low_24h,
            'open_price': self.open_price,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PriceData':
        """Cria instância a partir de dicionário"""
        return cls(
            symbol=data['symbol'],
            price=data['price'],
            currency=data.get('currency', 'USD'),
            timestamp=datetime.fromisoformat(data['timestamp']),
            source=DataSource(data.get('source', 'unknown')),
            quality=DataQuality(data.get('quality', 'unknown')),
            change_24h=data.get('change_24h'),
            change_percent_24h=data.get('change_percent_24h'),
            volume=data.get('volume'),
            high_24h=data.get('high_24h'),
            low_24h=data.get('low_24h'),
            open_price=data.get('open_price'),
            metadata=data.get('metadata', {})
        )

@dataclass
class ExchangeRate:
    """Dados de câmbio"""
    from_currency: str
    to_currency: str
    rate: float
    timestamp: datetime = field(default_factory=datetime.now)
    source: DataSource = DataSource.UNKNOWN
    quality: DataQuality = DataQuality.UNKNOWN
    
    # Metadados
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'from_currency': self.from_currency,
            'to_currency': self.to_currency,
            'rate': self.rate,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source.value,
            'quality': self.quality.value,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExchangeRate':
        """Cria instância a partir de dicionário"""
        return cls(
            from_currency=data['from_currency'],
            to_currency=data['to_currency'],
            rate=data['rate'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            source=DataSource(data.get('source', 'unknown')),
            quality=DataQuality(data.get('quality', 'unknown')),
            metadata=data.get('metadata', {})
        )

@dataclass
class HistoricalData:
    """Dados históricos de um ativo"""
    symbol: str
    data_type: DataType
    data: List[Dict[str, Any]]  # Lista de dados OHLCV
    start_date: datetime
    end_date: datetime
    interval: str = "1d"  # 1m, 5m, 15m, 1h, 1d, 1wk, 1mo
    source: DataSource = DataSource.UNKNOWN
    quality: DataQuality = DataQuality.UNKNOWN
    
    # Metadados
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'symbol': self.symbol,
            'data_type': self.data_type.value,
            'data': self.data,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'interval': self.interval,
            'source': self.source.value,
            'quality': self.quality.value,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'HistoricalData':
        """Cria instância a partir de dicionário"""
        return cls(
            symbol=data['symbol'],
            data_type=DataType(data['data_type']),
            data=data['data'],
            start_date=datetime.fromisoformat(data['start_date']),
            end_date=datetime.fromisoformat(data['end_date']),
            interval=data.get('interval', '1d'),
            source=DataSource(data.get('source', 'unknown')),
            quality=DataQuality(data.get('quality', 'unknown')),
            metadata=data.get('metadata', {})
        )

@dataclass
class CacheEntry:
    """Entrada do cache"""
    key: str
    data: Any
    data_type: DataType
    timestamp: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    source: DataSource = DataSource.UNKNOWN
    quality: DataQuality = DataQuality.UNKNOWN
    
    # Metadados do cache
    access_count: int = 0
    last_accessed: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Verifica se o cache expirou"""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'key': self.key,
            'data': self.data,
            'data_type': self.data_type.value,
            'timestamp': self.timestamp.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'source': self.source.value,
            'quality': self.quality.value,
            'access_count': self.access_count,
            'last_accessed': self.last_accessed.isoformat(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CacheEntry':
        """Cria instância a partir de dicionário"""
        return cls(
            key=data['key'],
            data=data['data'],
            data_type=DataType(data['data_type']),
            timestamp=datetime.fromisoformat(data['timestamp']),
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None,
            source=DataSource(data.get('source', 'unknown')),
            quality=DataQuality(data.get('quality', 'unknown')),
            access_count=data.get('access_count', 0),
            last_accessed=datetime.fromisoformat(data['last_accessed']),
            metadata=data.get('metadata', {})
        )

@dataclass
class DataRequest:
    """Requisição de dados"""
    symbol: str
    data_type: DataType
    sources: List[DataSource] = field(default_factory=list)
    force_refresh: bool = False
    timeout: int = 30
    retry_count: int = 3
    
    # Metadados da requisição
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'symbol': self.symbol,
            'data_type': self.data_type.value,
            'sources': [source.value for source in self.sources],
            'force_refresh': self.force_refresh,
            'timeout': self.timeout,
            'retry_count': self.retry_count,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataRequest':
        """Cria instância a partir de dicionário"""
        return cls(
            symbol=data['symbol'],
            data_type=DataType(data['data_type']),
            sources=[DataSource(source) for source in data.get('sources', [])],
            force_refresh=data.get('force_refresh', False),
            timeout=data.get('timeout', 30),
            retry_count=data.get('retry_count', 3),
            metadata=data.get('metadata', {})
        )

@dataclass
class DataResponse:
    """Resposta de dados"""
    request: DataRequest
    data: Optional[Any] = None
    success: bool = False
    error_message: Optional[str] = None
    source_used: Optional[DataSource] = None
    quality: DataQuality = DataQuality.UNKNOWN
    response_time: Optional[float] = None
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Metadados da resposta
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário"""
        return {
            'request': self.request.to_dict(),
            'data': self.data,
            'success': self.success,
            'error_message': self.error_message,
            'source_used': self.source_used.value if self.source_used else None,
            'quality': self.quality.value,
            'response_time': self.response_time,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataResponse':
        """Cria instância a partir de dicionário"""
        return cls(
            request=DataRequest.from_dict(data['request']),
            data=data.get('data'),
            success=data.get('success', False),
            error_message=data.get('error_message'),
            source_used=DataSource(data['source_used']) if data.get('source_used') else None,
            quality=DataQuality(data.get('quality', 'unknown')),
            response_time=data.get('response_time'),
            timestamp=datetime.fromisoformat(data['timestamp']),
            metadata=data.get('metadata', {})
        )

# Funções utilitárias
def serialize_dataclass(obj: Any) -> str:
    """Serializa um dataclass para JSON"""
    return json.dumps(obj.to_dict(), default=str, ensure_ascii=False)

def deserialize_dataclass(data: str, cls: type) -> Any:
    """Deserializa JSON para dataclass"""
    return cls.from_dict(json.loads(data)) 