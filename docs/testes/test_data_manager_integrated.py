#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Integrado do Data Manager
Testa todas as funcionalidades do sistema central de dados
"""

import sys
import os
import time
import logging
from datetime import datetime
from pathlib import Path

# Adicionar diretórios ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'sistema_obtencao_dados'))

from sistema_obtencao_dados.core.data_manager import DataManager
from sistema_obtencao_dados.models.data_models import DataType, DataSource, DataQuality

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_data_manager_initialization():
    """Testa inicialização do Data Manager"""
    print("🧪 TESTE 1: Inicialização do Data Manager")
    print("=" * 60)
    
    try:
        # Inicializar Data Manager
        data_manager = DataManager()
        
        print("✅ Data Manager inicializado com sucesso")
        print(f"✅ Providers disponíveis: {list(data_manager.providers.keys())}")
        print(f"✅ Timeout configurado: {data_manager.timeout}s")
        print(f"✅ Fallback habilitado: {data_manager.fallback_config['enabled']}")
        
        return data_manager
        
    except Exception as e:
        print(f"❌ Erro na inicialização: {e}")
        return None

def test_stock_prices(data_manager):
    """Testa obtenção de preços de ações"""
    print("\n🧪 TESTE 2: Preços de Ações")
    print("=" * 60)
    
    symbols = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "^BVSP"]
    
    for symbol in symbols:
        try:
            print(f"\n📈 Buscando {symbol}...")
            
            # Primeira busca (deve ir para API)
            start_time = time.time()
            data = data_manager.get_stock_price(symbol)
            end_time = time.time()
            
            if data:
                print(f"✅ {symbol}: R$ {data.price:.2f}")
                print(f"   Fonte: {data.source.value}")
                print(f"   Qualidade: {data.quality.value}")
                print(f"   Tempo: {(end_time - start_time):.2f}s")
                
                if data.change_24h:
                    print(f"   Variação 24h: {data.change_24h:+.2f} ({data.change_percent_24h:+.2f}%)")
            else:
                print(f"❌ Falha ao obter dados para {symbol}")
            
            # Segunda busca (deve usar cache)
            print(f"🔄 Buscando {symbol} novamente (cache)...")
            start_time = time.time()
            cached_data = data_manager.get_stock_price(symbol)
            end_time = time.time()
            
            if cached_data:
                print(f"✅ Cache hit: R$ {cached_data.price:.2f}")
                print(f"   Tempo cache: {(end_time - start_time):.3f}s")
            else:
                print(f"❌ Falha no cache para {symbol}")
                
        except Exception as e:
            print(f"❌ Erro ao buscar {symbol}: {e}")

def test_crypto_prices(data_manager):
    """Testa obtenção de preços de criptomoedas"""
    print("\n🧪 TESTE 3: Preços de Criptomoedas")
    print("=" * 60)
    
    symbols = ["BTC-USD", "ETH-USD", "BNB-USD"]
    
    for symbol in symbols:
        try:
            print(f"\n🪙 Buscando {symbol}...")
            
            start_time = time.time()
            data = data_manager.get_crypto_price(symbol)
            end_time = time.time()
            
            if data:
                print(f"✅ {symbol}: $ {data.price:,.2f}")
                print(f"   Fonte: {data.source.value}")
                print(f"   Qualidade: {data.quality.value}")
                print(f"   Tempo: {(end_time - start_time):.2f}s")
                
                if data.change_24h:
                    print(f"   Variação 24h: {data.change_24h:+.2f} ({data.change_percent_24h:+.2f}%)")
            else:
                print(f"❌ Falha ao obter dados para {symbol}")
                
        except Exception as e:
            print(f"❌ Erro ao buscar {symbol}: {e}")

def test_exchange_rates(data_manager):
    """Testa obtenção de taxas de câmbio"""
    print("\n🧪 TESTE 4: Taxas de Câmbio")
    print("=" * 60)
    
    pairs = [("USD", "BRL"), ("EUR", "BRL"), ("GBP", "BRL")]
    
    for from_curr, to_curr in pairs:
        try:
            print(f"\n💱 Buscando {from_curr}/{to_curr}...")
            
            start_time = time.time()
            data = data_manager.get_exchange_rate(from_curr, to_curr)
            end_time = time.time()
            
            if data:
                print(f"✅ {from_curr}/{to_curr}: {data.rate:.4f}")
                print(f"   Fonte: {data.source.value}")
                print(f"   Qualidade: {data.quality.value}")
                print(f"   Tempo: {(end_time - start_time):.2f}s")
            else:
                print(f"❌ Falha ao obter taxa para {from_curr}/{to_curr}")
                
        except Exception as e:
            print(f"❌ Erro ao buscar {from_curr}/{to_curr}: {e}")

def test_multiple_stocks(data_manager):
    """Testa obtenção de múltiplas ações em paralelo"""
    print("\n🧪 TESTE 5: Múltiplas Ações (Paralelo)")
    print("=" * 60)
    
    symbols = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "BBAS3.SA", "^BVSP"]
    
    try:
        print(f"📊 Buscando {len(symbols)} ações em paralelo...")
        
        start_time = time.time()
        results = data_manager.get_multiple_stocks(symbols)
        end_time = time.time()
        
        print(f"✅ Tempo total: {(end_time - start_time):.2f}s")
        print(f"✅ Resultados obtidos: {len(results)}/{len(symbols)}")
        
        for symbol, data in results.items():
            print(f"   {symbol}: R$ {data.price:.2f} ({data.source.value})")
            
    except Exception as e:
        print(f"❌ Erro no teste paralelo: {e}")

def test_fund_data(data_manager):
    """Testa obtenção de dados de fundos"""
    print("\n🧪 TESTE 6: Dados de Fundos")
    print("=" * 60)
    
    # CNPJs de fundos reais para teste
    cnpjs = [
        "00.017.024/0001-53",  # Fundo exemplo
        "33.000.167/0001-01",  # Fundo exemplo
        "33.000.167/0001-01"   # Fundo exemplo
    ]
    
    for cnpj in cnpjs:
        try:
            print(f"\n🏦 Buscando fundo {cnpj}...")
            
            start_time = time.time()
            data = data_manager.get_fund_data(cnpj)
            end_time = time.time()
            
            if data:
                print(f"✅ Fundo encontrado")
                print(f"   Nome: {data.get('nome', 'N/A')}")
                print(f"   Slug: {data.get('slug', 'N/A')}")
                print(f"   Fonte: {data.get('source', 'N/A')}")
                print(f"   Tempo: {(end_time - start_time):.2f}s")
            else:
                print(f"❌ Fundo não encontrado")
                
        except Exception as e:
            print(f"❌ Erro ao buscar fundo {cnpj}: {e}")

def test_cache_operations(data_manager):
    """Testa operações de cache"""
    print("\n🧪 TESTE 7: Operações de Cache")
    print("=" * 60)
    
    try:
        # Verificar estatísticas
        stats = data_manager.get_stats()
        
        print("📊 Estatísticas do Sistema:")
        print(f"   Requisições: {stats['data_manager']['requests']}")
        print(f"   Cache hits: {stats['data_manager']['cache_hits']}")
        print(f"   Cache misses: {stats['data_manager']['cache_misses']}")
        print(f"   Erros: {stats['data_manager']['errors']}")
        print(f"   Fallbacks: {stats['data_manager']['fallbacks']}")
        
        # Verificar providers
        print(f"\n🔌 Providers Ativos:")
        for provider, status in stats['providers'].items():
            print(f"   {provider}: {status}")
        
        # Verificar cache
        cache_stats = stats['cache']
        print(f"\n💾 Cache:")
        print(f"   Hits: {cache_stats['hits']}")
        print(f"   Misses: {cache_stats['misses']}")
        print(f"   Sets: {cache_stats['sets']}")
        print(f"   Backups: {cache_stats['backups']}")
        
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas: {e}")

def test_force_refresh(data_manager):
    """Testa forçar atualização ignorando cache"""
    print("\n🧪 TESTE 8: Force Refresh")
    print("=" * 60)
    
    symbol = "PETR4.SA"
    
    try:
        print(f"🔄 Forçando atualização de {symbol}...")
        
        start_time = time.time()
        data = data_manager.get_stock_price(symbol, force_refresh=True)
        end_time = time.time()
        
        if data:
            print(f"✅ Dados atualizados: R$ {data.price:.2f}")
            print(f"   Fonte: {data.source.value}")
            print(f"   Tempo: {(end_time - start_time):.2f}s")
        else:
            print(f"❌ Falha na atualização")
            
    except Exception as e:
        print(f"❌ Erro no force refresh: {e}")

def main():
    """Função principal de teste"""
    print("🚀 TESTE INTEGRADO DO DATA MANAGER")
    print("=" * 60)
    print(f"⏰ Início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Teste 1: Inicialização
    data_manager = test_data_manager_initialization()
    if not data_manager:
        print("❌ Falha na inicialização. Abortando testes.")
        return
    
    try:
        # Teste 2: Preços de ações
        test_stock_prices(data_manager)
        
        # Teste 3: Preços de criptomoedas
        test_crypto_prices(data_manager)
        
        # Teste 4: Taxas de câmbio
        test_exchange_rates(data_manager)
        
        # Teste 5: Múltiplas ações
        test_multiple_stocks(data_manager)
        
        # Teste 6: Dados de fundos
        test_fund_data(data_manager)
        
        # Teste 7: Operações de cache
        test_cache_operations(data_manager)
        
        # Teste 8: Force refresh
        test_force_refresh(data_manager)
        
    finally:
        # Finalizar Data Manager
        print("\n🔄 Finalizando Data Manager...")
        data_manager.shutdown()
        print("✅ Data Manager finalizado")
    
    print(f"\n🎉 TESTES CONCLUÍDOS - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

if __name__ == "__main__":
    main() 