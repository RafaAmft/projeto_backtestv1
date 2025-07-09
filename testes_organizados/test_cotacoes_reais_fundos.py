#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Cotações Reais dos Fundos - Ano Atual
Busca cotações mensais reais dos fundos da carteira ideal
"""

import sys
import os
import time
import logging
from datetime import datetime
import json

# Adicionar diretórios ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard'))

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_cotacoes_reais_fundos():
    """Teste que busca cotações reais dos fundos"""
    print("🧪 TESTE DE COTAÇÕES REAIS DOS FUNDOS")
    print("=" * 60)
    
    try:
        # Importar o coletor de portfólio que já tem o sistema de scraping
        from dashboard.portfolio_collector_v3 import PortfolioDataCollectorV3
        
        # Inicializar o coletor
        collector = PortfolioDataCollectorV3()
        
        # Carregar mapeamento de fundos
        with open('mapeamento_fundos.json', 'r', encoding='utf-8') as f:
            mapeamento = json.load(f)
        
        # Lista de fundos para testar
        fundos_teste = [
            {
                'cnpj': '04.305.193/0001-40',
                'nome': 'BB Cambial Euro LP FIC FIF RL',
                'slug': 'bb-cambial-euro-lp-fic-fif-rl'
            },
            {
                'cnpj': '20.077.065/0001-42',
                'nome': 'Mapfre FI Financeiro Cambial RL',
                'slug': 'mapfre-fi-financeiro-cambial-rl'
            },
            {
                'cnpj': '24.633.789/0001-86',
                'nome': 'Sicredi FIF Classe FIC Cambial Dólar LP RL',
                'slug': 'sicredi-fif-classe-fic-cambial-dolar-lp-rl'
            }
        ]
        
        print(f"📊 Buscando cotações reais de {len(fundos_teste)} fundos...")
        print(f"📅 Ano atual: {datetime.now().year}")
        print()
        
        resultados = {}
        
        for i, fundo in enumerate(fundos_teste):
            print(f"🔄 Processando fundo {i+1}/{len(fundos_teste)}: {fundo['nome']}")
            print(f"   CNPJ: {fundo['cnpj']}")
            print(f"   Slug: {fundo['slug']}")
            
            try:
                # Buscar dados reais do fundo
                dados_fundo = collector.extrair_dados_fundo(
                    fundo['slug'], 
                    fundo['cnpj'], 
                    force_debug=True
                )
                
                if dados_fundo and 'rentabilidades' in dados_fundo:
                    rentabilidades = dados_fundo['rentabilidades']
                    
                    print(f"   ✅ Dados obtidos!")
                    print(f"   📊 Anos disponíveis: {list(rentabilidades.keys())}")
                    
                    # Mostrar cotações do ano atual
                    ano_atual = str(datetime.now().year)
                    if ano_atual in rentabilidades:
                        cotacoes_ano = rentabilidades[ano_atual]
                        print(f"   📈 Cotações {ano_atual} (mês a mês):")
                        
                        for mes, rentabilidade in sorted(cotacoes_ano.items()):
                            print(f"      {mes}: {rentabilidade:.2f}%")
                        
                        resultados[fundo['cnpj']] = {
                            'nome': fundo['nome'],
                            'slug': fundo['slug'],
                            'dados_obtidos': True,
                            'cotacoes_ano_atual': cotacoes_ano,
                            'total_meses': len(cotacoes_ano)
                        }
                    else:
                        print(f"   ⚠️ Nenhuma cotação disponível para {ano_atual}")
                        resultados[fundo['cnpj']] = {
                            'nome': fundo['nome'],
                            'slug': fundo['slug'],
                            'dados_obtidos': True,
                            'cotacoes_ano_atual': {},
                            'erro': f'Nenhuma cotação para {ano_atual}'
                        }
                else:
                    print(f"   ❌ Erro ao obter dados do fundo")
                    resultados[fundo['cnpj']] = {
                        'nome': fundo['nome'],
                        'slug': fundo['slug'],
                        'dados_obtidos': False,
                        'erro': 'Dados não disponíveis'
                    }
                
            except Exception as e:
                print(f"   ❌ Erro ao processar fundo: {e}")
                resultados[fundo['cnpj']] = {
                    'nome': fundo['nome'],
                    'slug': fundo['slug'],
                    'dados_obtidos': False,
                    'erro': str(e)
                }
            
            # Delay entre requisições
            if i < len(fundos_teste) - 1:
                print(f"   ⏳ Aguardando 3 segundos...")
                time.sleep(3)
            
            print()
        
        # Resumo dos resultados
        print("📊 RESUMO DOS RESULTADOS")
        print("=" * 60)
        
        fundos_com_dados = sum(1 for r in resultados.values() if r['dados_obtidos'])
        fundos_com_cotacoes = sum(1 for r in resultados.values() if r.get('cotacoes_ano_atual'))
        
        print(f"🎯 Fundos processados: {len(fundos_teste)}")
        print(f"✅ Fundos com dados: {fundos_com_dados}")
        print(f"📈 Fundos com cotações do ano atual: {fundos_com_cotacoes}")
        print()
        
        # Detalhes por fundo
        for cnpj, resultado in resultados.items():
            print(f"🏦 {resultado['nome']}")
            print(f"   CNPJ: {cnpj}")
            print(f"   Status: {'✅ Dados obtidos' if resultado['dados_obtidos'] else '❌ Erro'}")
            
            if resultado['dados_obtidos'] and resultado.get('cotacoes_ano_atual'):
                cotacoes = resultado['cotacoes_ano_atual']
                print(f"   📊 Cotações {datetime.now().year}: {len(cotacoes)} meses")
                
                # Calcular média anual
                if cotacoes:
                    media_anual = sum(cotacoes.values()) / len(cotacoes)
                    print(f"   📈 Média anual: {media_anual:.2f}%")
                    
                    # Mostrar melhor e pior mês
                    melhor_mes = max(cotacoes.items(), key=lambda x: x[1])
                    pior_mes = min(cotacoes.items(), key=lambda x: x[1])
                    print(f"   🟢 Melhor mês: {melhor_mes[0]} ({melhor_mes[1]:.2f}%)")
                    print(f"   🔴 Pior mês: {pior_mes[0]} ({pior_mes[1]:.2f}%)")
            elif resultado.get('erro'):
                print(f"   ❌ Erro: {resultado['erro']}")
            
            print()
        
        return fundos_com_dados > 0
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executa o teste de cotações reais"""
    print("🚀 INICIANDO TESTE DE COTAÇÕES REAIS DOS FUNDOS")
    print("=" * 70)
    print(f"⏰ Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success = test_cotacoes_reais_fundos()
    
    print(f"\n⏰ Fim: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if success:
        print("🎉 Teste concluído! Cotações reais obtidas com sucesso.")
    else:
        print("⚠️ Teste falhou. Verificar conectividade e configurações.")

if __name__ == "__main__":
    main() 