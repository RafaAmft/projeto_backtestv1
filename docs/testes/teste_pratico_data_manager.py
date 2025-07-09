#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Prático do Data Manager
Teste simples para verificar se está funcionando
"""

import sys
import os
from datetime import datetime

# Adicionar diretórios ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'sistema_obtencao_dados'))

from sistema_obtencao_dados.core.data_manager import DataManager

def teste_simples():
    """Teste simples do Data Manager"""
    print("🧪 TESTE PRÁTICO DO DATA MANAGER")
    print("=" * 50)
    print(f"⏰ Início: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    try:
        # 1. Inicializar Data Manager
        print("\n1️⃣ Inicializando Data Manager...")
        data_manager = DataManager()
        print("✅ Data Manager inicializado!")
        
        # 2. Testar busca de ação brasileira
        print("\n2️⃣ Testando busca de ação (PETR4.SA)...")
        petrobras = data_manager.get_stock_price("PETR4.SA")
        if petrobras:
            print(f"✅ PETR4.SA: R$ {petrobras.price:.2f}")
            print(f"   Fonte: {petrobras.source.value}")
            print(f"   Qualidade: {petrobras.quality.value}")
        else:
            print("❌ Falha ao buscar PETR4.SA")
        
        # 3. Testar busca de criptomoeda
        print("\n3️⃣ Testando busca de cripto (BTC-USD)...")
        bitcoin = data_manager.get_crypto_price("BTC-USD")
        if bitcoin:
            print(f"✅ BTC-USD: $ {bitcoin.price:,.2f}")
            print(f"   Fonte: {bitcoin.source.value}")
            print(f"   Qualidade: {bitcoin.quality.value}")
        else:
            print("❌ Falha ao buscar BTC-USD")
        
        # 4. Testar cache (segunda busca)
        print("\n4️⃣ Testando cache (segunda busca PETR4.SA)...")
        petrobras_cache = data_manager.get_stock_price("PETR4.SA")
        if petrobras_cache:
            print(f"✅ Cache hit: R$ {petrobras_cache.price:.2f}")
        else:
            print("❌ Falha no cache")
        
        # 5. Testar múltiplas ações
        print("\n5️⃣ Testando múltiplas ações...")
        acoes = ["VALE3.SA", "ITUB4.SA"]
        resultados = data_manager.get_multiple_stocks(acoes)
        print(f"✅ Resultados: {len(resultados)}/{len(acoes)} ações")
        for simbolo, dados in resultados.items():
            print(f"   {simbolo}: R$ {dados.price:.2f}")
        
        # 6. Testar fundos de investimento
        print("\n6️⃣ Testando fundos de investimento...")
        
        # CNPJs de fundos reais do mapeamento
        cnpjs_fundos = [
            "04.305.193/0001-40",  # BB Cambial Euro LP FIC FIF RL
            "20.077.065/0001-42",  # Mapfre FI Financeiro Cambial RL
            "24.633.789/0001-86"   # Sicredi FIF Classe FIC Cambial Dólar LP RL
        ]
        
        fundos_encontrados = 0
        for cnpj in cnpjs_fundos:
            print(f"   🏦 Buscando fundo {cnpj}...")
            try:
                dados_fundo = data_manager.get_fund_data(cnpj)
                if dados_fundo:
                    print(f"   ✅ Fundo encontrado: {dados_fundo.get('nome', 'N/A')}")
                    print(f"      Slug: {dados_fundo.get('slug', 'N/A')}")
                    print(f"      Fonte: {dados_fundo.get('source', 'N/A')}")
                    fundos_encontrados += 1
                else:
                    print(f"   ❌ Fundo não encontrado")
            except Exception as e:
                print(f"   ❌ Erro ao buscar fundo: {e}")
        
        print(f"✅ Fundos encontrados: {fundos_encontrados}/{len(cnpjs_fundos)}")
        
        # 7. Verificar estatísticas
        print("\n7️⃣ Verificando estatísticas...")
        stats = data_manager.get_stats()
        print(f"✅ Requisições: {stats['data_manager']['requests']}")
        print(f"✅ Cache hits: {stats['data_manager']['cache_hits']}")
        print(f"✅ Cache misses: {stats['data_manager']['cache_misses']}")
        print(f"✅ Erros: {stats['data_manager']['errors']}")
        
        # 8. Finalizar
        print("\n8️⃣ Finalizando...")
        data_manager.shutdown()
        print("✅ Data Manager finalizado!")
        
        print(f"\n🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print(f"⏰ Fim: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERRO NO TESTE: {e}")
        return False

if __name__ == "__main__":
    sucesso = teste_simples()
    if sucesso:
        print("\n🚀 Data Manager está funcionando!")
    else:
        print("\n💥 Data Manager com problemas!") 