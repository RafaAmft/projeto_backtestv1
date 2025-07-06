#!/usr/bin/env python3
"""
Teste do Sistema de Cache de Fundos
===================================

Este script testa o sistema de cache para dados de fundos de investimento.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from dashboard.fund_cache_manager import FundCacheManager
from datetime import datetime

def test_cache_system():
    """Testa o sistema de cache"""
    
    print("🧪 TESTE DO SISTEMA DE CACHE DE FUNDOS")
    print("=" * 50)
    
    # Criar instância do cache manager
    cache_manager = FundCacheManager()
    
    # Dados de teste
    test_funds = [
        {
            'cnpj': '00.017.021/0001-53',
            'nome': 'Fundo Teste 1',
            'slug': 'fundo-teste-1',
            'rentabilidades': {
                2024: {'Jan': 0.05, 'Fev': 0.03, 'Mar': 0.07},
                2023: {'Jan': 0.04, 'Fev': 0.06, 'Mar': 0.02}
            }
        },
        {
            'cnpj': '00017021000153',
            'nome': 'Fundo Teste 2',
            'slug': 'fundo-teste-2',
            'rentabilidades': {
                2024: {'Jan': 0.08, 'Fev': 0.05, 'Mar': 0.09},
                2023: {'Jan': 0.06, 'Fev': 0.08, 'Mar': 0.04}
            }
        }
    ]
    
    print("\n1️⃣ TESTE DE SALVAMENTO NO CACHE")
    print("-" * 30)
    
    for fund in test_funds:
        print(f"Salvando fundo: {fund['nome']} ({fund['cnpj']})")
        cache_manager.save_fund_data(fund['cnpj'], fund)
    
    print("\n2️⃣ TESTE DE RECUPERAÇÃO DO CACHE")
    print("-" * 30)
    
    for fund in test_funds:
        print(f"Buscando fundo: {fund['cnpj']}")
        cached_data = cache_manager.get_fund_data(fund['cnpj'])
        if cached_data:
            print(f"✅ Encontrado: {cached_data['nome']}")
        else:
            print(f"❌ Não encontrado")
    
    print("\n3️⃣ TESTE DE NORMALIZAÇÃO DE CNPJ")
    print("-" * 30)
    
    test_cnpjs = [
        '00.017.021/0001-53',
        '00017021000153',
        '00.017.021/0001-53',
        '00017021000153'
    ]
    
    for cnpj in test_cnpjs:
        cached_data = cache_manager.get_fund_data(cnpj)
        if cached_data:
            print(f"✅ CNPJ {cnpj} -> {cached_data['nome']}")
        else:
            print(f"❌ CNPJ {cnpj} -> Não encontrado")
    
    print("\n4️⃣ ESTATÍSTICAS DO CACHE")
    print("-" * 30)
    
    stats = cache_manager.get_cache_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n5️⃣ LISTA DE FUNDOS EM CACHE")
    print("-" * 30)
    
    funds = cache_manager.list_cached_funds()
    for fund in funds:
        status = "✅" if fund['is_valid'] else "⚠️"
        print(f"{status} {fund['nome']} ({fund['cnpj']})")
    
    print("\n6️⃣ TESTE DE BUSCA POR NOME")
    print("-" * 30)
    
    search_results = cache_manager.search_fund_by_name("teste")
    for fund in search_results:
        print(f"🔍 Encontrado: {fund['nome']} ({fund['cnpj']})")
    
    print("\n7️⃣ TESTE DE LIMPEZA DE CACHE")
    print("-" * 30)
    
    # Limpar cache expirado (não deve remover nada pois acabamos de criar)
    removed = cache_manager.clear_expired_cache()
    print(f"Entradas expiradas removidas: {removed}")
    
    print("\n✅ TESTE CONCLUÍDO COM SUCESSO!")
    print("=" * 50)

if __name__ == "__main__":
    test_cache_system() 