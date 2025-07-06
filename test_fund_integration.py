#!/usr/bin/env python3
"""
Teste de Integração para Análise de Fundos
Testa a integração da análise de fundos no sistema principal de análise de portfólio
"""

import sys
import os
import json
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from examples.portfolio_analysis_example import PortfolioAnalyzer

def test_fund_integration():
    """Testa a integração completa da análise de fundos"""
    print("=" * 60)
    print("TESTE DE INTEGRAÇÃO - ANÁLISE DE FUNDOS")
    print("=" * 60)
    print(f"📅 PERÍODO DE TESTE: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}")
    print(f"⏱️  DURAÇÃO: Teste pontual (dados simulados)")
    print("=" * 60)
    
    try:
        # Criar instância do analisador
        analyzer = PortfolioAnalyzer()
        
        # Testar análise de fundos
        print("\n1. Testando análise de fundos...")
        fund_data = analyzer.analyze_funds()
        
        if fund_data:
            print("✅ Análise de fundos executada com sucesso")
            print(f"   - Fundos analisados: {len(fund_data['fundos'])}")
            print(f"   - Métricas calculadas: {list(fund_data['metrics'].keys())}")
        else:
            print("❌ Falha na análise de fundos")
            return False
        
        # Testar geração de relatório unificado
        print("\n2. Testando geração de relatório unificado...")
        unified_report = analyzer.generate_unified_report()
        
        if unified_report:
            print("✅ Relatório unificado gerado com sucesso")
            print(f"   - Seções incluídas: {list(unified_report.keys())}")
            
            # Verificar se a seção de fundos está presente
            if 'fundos' in unified_report:
                print("✅ Seção de fundos incluída no relatório")
            else:
                print("❌ Seção de fundos não encontrada no relatório")
                return False
        else:
            print("❌ Falha na geração do relatório unificado")
            return False
        
        # Testar salvamento do relatório
        print("\n3. Testando salvamento do relatório...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_fund_integration_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(unified_report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Relatório salvo em: {filename}")
        
        # Mostrar resumo do relatório
        print("\n4. Resumo do relatório gerado:")
        print("-" * 40)
        
        if 'criptomoedas' in unified_report:
            crypto_count = len(unified_report['criptomoedas'].get('ativos', []))
            print(f"   Criptomoedas: {crypto_count} ativos")
        
        if 'acoes' in unified_report:
            stocks_count = len(unified_report['acoes'].get('ativos', []))
            print(f"   Ações: {stocks_count} ativos")
        
        if 'fundos' in unified_report:
            funds_count = len(unified_report['fundos'].get('fundos', []))
            print(f"   Fundos: {funds_count} fundos")
        
        if 'recomendacoes' in unified_report:
            recommendations_count = len(unified_report['recomendacoes'])
            print(f"   Recomendações: {recommendations_count} itens")
        
        print("\n✅ Teste de integração concluído com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro durante o teste: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_fund_metrics():
    """Testa especificamente as métricas de fundos"""
    print("\n" + "=" * 60)
    print("TESTE ESPECÍFICO - MÉTRICAS DE FUNDOS")
    print("=" * 60)
    print(f"📅 PERÍODO DE TESTE: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}")
    print(f"⏱️  DURAÇÃO: Teste pontual (dados simulados)")
    print("=" * 60)
    
    try:
        analyzer = PortfolioAnalyzer()
        
        # Testar cálculo de métricas de risco
        print("\n1. Testando cálculo de métricas de risco...")
        
        # Dados simulados de um fundo
        fund_returns = [0.02, -0.01, 0.03, -0.02, 0.01, 0.02, -0.01, 0.03, 0.01, -0.01]
        
        # Calcular métricas
        volatility = np.std(fund_returns) * np.sqrt(252)  # Anualizada
        sharpe_ratio = np.mean(fund_returns) / np.std(fund_returns) * np.sqrt(252)
        max_drawdown = calculate_max_drawdown(fund_returns)
        
        print(f"   Volatilidade anualizada: {volatility:.4f}")
        print(f"   Sharpe Ratio: {sharpe_ratio:.4f}")
        print(f"   Máximo Drawdown: {max_drawdown:.4f}")
        
        print("✅ Métricas calculadas com sucesso")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de métricas: {str(e)}")
        return False

def calculate_max_drawdown(returns):
    """Calcula o máximo drawdown de uma série de retornos"""
    cumulative = np.cumprod(1 + np.array(returns))
    running_max = np.maximum.accumulate(cumulative)
    drawdown = (cumulative - running_max) / running_max
    return np.min(drawdown)

def test_fund_data_validation():
    """Testa a validação de dados de fundos"""
    print("\n" + "=" * 60)
    print("TESTE DE VALIDAÇÃO - DADOS DE FUNDOS")
    print("=" * 60)
    print(f"📅 PERÍODO DE TESTE: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}")
    print(f"⏱️  DURAÇÃO: Teste pontual (dados simulados)")
    print("=" * 60)
    
    try:
        # Dados simulados para teste
        test_funds = [
            {
                'nome': 'Fund Test 1',
                'cnpj': '00.000.000/0001-00',
                'retorno_anual': 0.15,
                'volatilidade': 0.12,
                'sharpe_ratio': 1.25,
                'categoria': 'Renda Variável'
            },
            {
                'nome': 'Fund Test 2',
                'cnpj': '00.000.000/0002-00',
                'retorno_anual': 0.08,
                'volatilidade': 0.05,
                'sharpe_ratio': 1.60,
                'categoria': 'Renda Fixa'
            }
        ]
        
        print(f"   Fundos para validação: {len(test_funds)}")
        
        # Validar dados
        for i, fund in enumerate(test_funds, 1):
            print(f"\n   Fundo {i}: {fund['nome']}")
            print(f"      CNPJ: {fund['cnpj']}")
            print(f"      Retorno: {fund['retorno_anual']:.2%}")
            print(f"      Volatilidade: {fund['volatilidade']:.2%}")
            print(f"      Sharpe: {fund['sharpe_ratio']:.2f}")
            print(f"      Categoria: {fund['categoria']}")
        
        print("\n✅ Validação de dados concluída")
        return True
        
    except Exception as e:
        print(f"❌ Erro na validação: {str(e)}")
        return False

if __name__ == "__main__":
    print("Iniciando testes de integração de fundos...")
    
    # Executar todos os testes
    tests = [
        test_fund_integration,
        test_fund_metrics,
        test_fund_data_validation
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Erro no teste {test.__name__}: {str(e)}")
            results.append(False)
    
    # Resumo final
    print("\n" + "=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nTestes aprovados: {passed}/{total}")
    
    if passed == total:
        print("🎉 Todos os testes passaram!")
        print("✅ A integração de fundos está funcionando corretamente")
    else:
        print("⚠️  Alguns testes falharam")
        print("❌ Verifique os erros acima e corrija os problemas")
    
    print("\nTeste concluído!") 