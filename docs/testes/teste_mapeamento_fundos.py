#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do Mapeamento de Fundos
Verifica se o mapeamento está sendo carregado corretamente
"""

import sys
import os
import json

# Adicionar diretórios ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'sistema_obtencao_dados'))

from sistema_obtencao_dados.providers.fundos_provider import FundosProvider
from sistema_obtencao_dados.core.cache_manager import CacheManager

def teste_mapeamento():
    """Testa o carregamento do mapeamento de fundos"""
    print("🧪 TESTE DO MAPEAMENTO DE FUNDOS")
    print("=" * 50)
    
    try:
        # 1. Carregar mapeamento diretamente
        print("\n1️⃣ Carregando mapeamento diretamente...")
        mapeamento_path = "mapeamento_fundos.json"
        
        with open(mapeamento_path, 'r', encoding='utf-8') as f:
            mapeamento = json.load(f)
        
        fundos = mapeamento.get('mapeamento_fundos', {})
        print(f"✅ Mapeamento carregado com {len(fundos)} fundos")
        print("📋 CNPJs no mapeamento:")
        for cnpj, dados in fundos.items():
            print(f"   {cnpj}: {dados['nome']}")
        
        # 2. Testar FundosProvider
        print("\n2️⃣ Testando FundosProvider...")
        config = {
            'memory': {'max_size': 100, 'cleanup_interval': 300},
            'persistent': {'directory': 'test_cache', 'backup_enabled': False, 'backup_interval': 3600}
        }
        cache_manager = CacheManager(config)
        provider = FundosProvider(cache_manager)
        
        print(f"✅ Provider inicializado")
        print(f"📋 Mapeamento no provider: {len(provider.mapeamento_fundos.get('mapeamento_fundos', {}))} fundos")
        
        # 3. Testar busca de slugs
        print("\n3️⃣ Testando busca de slugs...")
        cnpjs_teste = [
            "04.305.193/0001-40",
            "20.077.065/0001-42", 
            "24.633.789/0001-86"
        ]
        
        for cnpj in cnpjs_teste:
            print(f"\n🔍 Testando CNPJ: {cnpj}")
            slug = provider.buscar_slug_fundo(cnpj)
            if slug:
                print(f"✅ Slug encontrado: {slug}")
            else:
                print(f"❌ Slug não encontrado")
        
        # 4. Testar dados de fundo
        print("\n4️⃣ Testando dados de fundo...")
        for cnpj in cnpjs_teste:
            print(f"\n🏦 Buscando dados do fundo: {cnpj}")
            dados = provider.get_fundo_data(cnpj)
            if dados:
                print(f"✅ Dados obtidos: {dados.get('nome', 'N/A')}")
            else:
                print(f"❌ Dados não obtidos")
        
        print(f"\n🎉 TESTE CONCLUÍDO!")
        
    except Exception as e:
        print(f"❌ ERRO: {e}")

if __name__ == "__main__":
    teste_mapeamento() 