#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo de Teste do Sistema Robusto de Cache
Demonstra as funcionalidades do novo sistema
"""

import sys
import os
import time
import yaml
from pathlib import Path

# Adicionar o diretório pai ao path
sys.path.append(str(Path(__file__).parent.parent))

from models.data_models import DataType, DataSource, DataQuality, PriceData, ExchangeRate
from core.cache_manager import CacheManager

def load_config():
    """Carrega configuração do sistema"""
    config_file = Path(__file__).parent.parent / "config.yaml"
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config

def test_cache_basic_operations():
    """Testa operações básicas do cache"""
    print("🧪 TESTE 1: Operações Básicas do Cache")
    print("=" * 50)
    
    config = load_config()
    
    with CacheManager(config['cache']) as cache:
        # Teste 1: Armazenar dados de preço
        price_data = PriceData(
            symbol="PETR4.SA",
            price=35.50,
            currency="BRL",
            source=DataSource.YAHOO_FINANCE,
            quality=DataQuality.EXCELLENT,
            change_24h=0.75,
            change_percent_24h=2.16
        )
        
        cache.set(
            key="PETR4.SA_price",
            data=price_data,
            data_type=DataType.STOCK,
            expires_in=300,  # 5 minutos
            source=DataSource.YAHOO_FINANCE,
            quality=DataQuality.EXCELLENT
        )
        
        print("✅ Dados de preço armazenados no cache")
        
        # Teste 2: Recuperar dados
        retrieved_data = cache.get("PETR4.SA_price")
        if retrieved_data:
            print(f"✅ Dados recuperados: {retrieved_data.symbol} = R$ {retrieved_data.price}")
        else:
            print("❌ Falha ao recuperar dados")
        
        # Teste 3: Verificar existência
        exists = cache.exists("PETR4.SA_price")
        print(f"✅ Chave existe: {exists}")
        
        # Teste 4: Estatísticas
        stats = cache.get_stats()
        print(f"✅ Estatísticas: {stats['hits']} hits, {stats['misses']} misses")
        
        # Teste 5: Listar chaves
        keys = cache.get_keys()
        print(f"✅ Chaves no cache: {keys}")

def test_cache_expiration():
    """Testa expiração do cache"""
    print("\n🧪 TESTE 2: Expiração do Cache")
    print("=" * 50)
    
    config = load_config()
    
    with CacheManager(config['cache']) as cache:
        # Armazenar dados com expiração curta
        exchange_rate = ExchangeRate(
            from_currency="USD",
            to_currency="BRL",
            rate=5.42,
            source=DataSource.EXCHANGE_RATE_API,
            quality=DataQuality.GOOD
        )
        
        cache.set(
            key="USD_BRL_rate",
            data=exchange_rate,
            data_type=DataType.CURRENCY,
            expires_in=5,  # 5 segundos
            source=DataSource.EXCHANGE_RATE_API,
            quality=DataQuality.GOOD
        )
        
        print("✅ Taxa de câmbio armazenada (expira em 5s)")
        
        # Verificar imediatamente
        data = cache.get("USD_BRL_rate")
        if data:
            print(f"✅ Dados válidos: {data.from_currency}/{data.to_currency} = {data.rate}")
        
        # Aguardar expiração
        print("⏳ Aguardando 7 segundos para expiração...")
        time.sleep(7)
        
        # Verificar após expiração
        data = cache.get("USD_BRL_rate")
        if data:
            print(f"❌ Dados ainda válidos (erro): {data.rate}")
        else:
            print("✅ Dados expiraram corretamente")

def test_cache_persistence():
    """Testa persistência do cache"""
    print("\n🧪 TESTE 3: Persistência do Cache")
    print("=" * 50)
    
    config = load_config()
    
    # Primeira instância do cache
    with CacheManager(config['cache']) as cache1:
        # Armazenar dados
        crypto_data = PriceData(
            symbol="BTCUSDT",
            price=108500.00,
            currency="USD",
            source=DataSource.BINANCE,
            quality=DataQuality.EXCELLENT,
            change_24h=2500.00,
            change_percent_24h=2.36
        )
        
        cache1.set(
            key="BTCUSDT_price",
            data=crypto_data,
            data_type=DataType.CRYPTO,
            expires_in=3600,  # 1 hora
            source=DataSource.BINANCE,
            quality=DataQuality.EXCELLENT
        )
        
        print("✅ Dados de cripto armazenados no cache persistente")
    
    # Segunda instância do cache (deve carregar dados da primeira)
    with CacheManager(config['cache']) as cache2:
        # Tentar recuperar dados
        data = cache2.get("BTCUSDT_price")
        if data:
            print(f"✅ Dados recuperados do cache persistente: {data.symbol} = $ {data.price}")
        else:
            print("❌ Falha ao recuperar dados do cache persistente")

def test_cache_performance():
    """Testa performance do cache"""
    print("\n🧪 TESTE 4: Performance do Cache")
    print("=" * 50)
    
    config = load_config()
    
    with CacheManager(config['cache']) as cache:
        # Armazenar múltiplos itens
        symbols = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBAS3.SA", "^BVSP"]
        
        for i, symbol in enumerate(symbols):
            price_data = PriceData(
                symbol=symbol,
                price=30.0 + i * 5.0,
                currency="BRL",
                source=DataSource.YAHOO_FINANCE,
                quality=DataQuality.GOOD
            )
            
            cache.set(
                key=f"{symbol}_price",
                data=price_data,
                data_type=DataType.STOCK,
                expires_in=600,
                source=DataSource.YAHOO_FINANCE,
                quality=DataQuality.GOOD
            )
        
        print(f"✅ {len(symbols)} itens armazenados")
        
        # Teste de velocidade de acesso
        start_time = time.time()
        
        for symbol in symbols:
            data = cache.get(f"{symbol}_price")
        
        end_time = time.time()
        access_time = (end_time - start_time) * 1000  # em milissegundos
        
        print(f"✅ Tempo de acesso a {len(symbols)} itens: {access_time:.2f}ms")
        print(f"✅ Tempo médio por acesso: {access_time/len(symbols):.2f}ms")
        
        # Estatísticas finais
        stats = cache.get_stats()
        print(f"✅ Estatísticas finais:")
        print(f"   - Hit rate: {stats['hit_rate']}%")
        print(f"   - Total de requisições: {stats['total_requests']}")
        print(f"   - Itens em memória: {stats['memory_size']}")

def main():
    """Função principal"""
    print("🚀 SISTEMA ROBUSTO DE CACHE - TESTES")
    print("=" * 60)
    
    try:
        # Executar testes
        test_cache_basic_operations()
        test_cache_expiration()
        test_cache_persistence()
        test_cache_performance()
        
        print("\n🎉 TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERRO NOS TESTES: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 