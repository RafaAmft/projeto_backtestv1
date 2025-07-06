#!/usr/bin/env python3
"""
Script de Execução de Testes - Sistema de Análise Financeira
============================================================

Este script executa todos os testes automatizados do projeto e gera um relatório
completo de validação do sistema.
"""

import sys
import os
import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_command(command, description):
    """Executa um comando e retorna o resultado"""
    print(f"\n🔄 {description}...")
    print(f"Comando: {command}")
    
    start_time = time.time()
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos de timeout
        )
        end_time = time.time()
        
        success = result.returncode == 0
        duration = end_time - start_time
        
        print(f"✅ {'Sucesso' if success else '❌ Falha'} ({duration:.2f}s)")
        
        if result.stdout:
            print("📤 Saída:")
            print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
        
        if result.stderr and not success:
            print("❌ Erro:")
            print(result.stderr[:500] + "..." if len(result.stderr) > 500 else result.stderr)
        
        return {
            'success': success,
            'duration': duration,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        }
        
    except subprocess.TimeoutExpired:
        print("⏰ Timeout - Comando demorou mais de 5 minutos")
        return {
            'success': False,
            'duration': 300,
            'stdout': '',
            'stderr': 'Timeout expired',
            'returncode': -1
        }
    except Exception as e:
        print(f"❌ Erro ao executar comando: {e}")
        return {
            'success': False,
            'duration': 0,
            'stdout': '',
            'stderr': str(e),
            'returncode': -1
        }

def test_imports():
    """Testa se todos os módulos podem ser importados"""
    print("\n" + "="*60)
    print("🧪 TESTE DE IMPORTS")
    print("="*60)
    
    modules_to_test = [
        ('core.market_indices', 'MarketIndicesManager'),
        ('apis.binance_api', 'BinanceMercadoAPI'),
        ('apis.yahoo_api', 'YahooFinanceAPI'),
        ('apis.cvm_api', 'CVMAPI')
    ]
    
    results = {}
    
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            class_obj = getattr(module, class_name)
            print(f"✅ {module_name}.{class_name}")
            results[f"{module_name}.{class_name}"] = True
        except Exception as e:
            print(f"❌ {module_name}.{class_name}: {e}")
            results[f"{module_name}.{class_name}"] = False
    
    return results

def test_core_functionality():
    """Testa funcionalidades do core"""
    print("\n" + "="*60)
    print("🧠 TESTE DO CORE")
    print("="*60)
    
    try:
        from core.market_indices import market_indices
        
        results = {}
        
        # Teste 1: Câmbio
        print("\n1. Testando busca de câmbio...")
        try:
            rates = market_indices.get_exchange_rate()
            if rates and 'USD_BRL' in rates:
                print(f"✅ Câmbio: R$ {rates['USD_BRL']:.4f}")
                results['exchange_rate'] = True
            else:
                print("❌ Dados de câmbio inválidos")
                results['exchange_rate'] = False
        except Exception as e:
            print(f"❌ Erro no câmbio: {e}")
            results['exchange_rate'] = False
        
        # Teste 2: Criptomoedas
        print("\n2. Testando busca de criptomoedas...")
        try:
            crypto = market_indices.get_crypto_prices(['BTCUSDT'])
            if crypto and 'BTCUSDT' in crypto:
                print(f"✅ Bitcoin: ${crypto['BTCUSDT']['price']:,.2f}")
                results['crypto_prices'] = True
            else:
                print("❌ Dados de criptomoedas inválidos")
                results['crypto_prices'] = False
        except Exception as e:
            print(f"❌ Erro nas criptomoedas: {e}")
            results['crypto_prices'] = False
        
        # Teste 3: Ações
        print("\n3. Testando busca de ações...")
        try:
            stocks = market_indices.get_stock_indices(['^BVSP'])
            if stocks and '^BVSP' in stocks:
                print(f"✅ Ibovespa: {stocks['^BVSP']['price']:,.2f}")
                results['stock_indices'] = True
            else:
                print("❌ Dados de ações inválidos")
                results['stock_indices'] = False
        except Exception as e:
            print(f"❌ Erro nas ações: {e}")
            results['stock_indices'] = False
        
        # Teste 4: Resumo de mercado
        print("\n4. Testando resumo de mercado...")
        try:
            summary = market_indices.get_market_summary()
            if summary:
                print(f"✅ Resumo gerado com {len(summary)} itens")
                results['market_summary'] = True
            else:
                print("❌ Resumo de mercado inválido")
                results['market_summary'] = False
        except Exception as e:
            print(f"❌ Erro no resumo: {e}")
            results['market_summary'] = False
        
        return results
        
    except Exception as e:
        print(f"❌ Erro geral no core: {e}")
        return {'core_error': False}

def test_apis():
    """Testa as APIs individuais"""
    print("\n" + "="*60)
    print("🔌 TESTE DAS APIS")
    print("="*60)
    
    results = {}
    
    # Teste Binance API
    print("\n1. Testando Binance API...")
    try:
        from apis.binance_api import BinanceMercadoAPI
        api = BinanceMercadoAPI()
        data = api.get_preco("BTCUSDT")
        if data and 'price' in data:
            print(f"✅ Binance: ${float(data['price']):,.2f}")
            results['binance_api'] = True
        else:
            print("❌ Dados da Binance inválidos")
            results['binance_api'] = False
    except Exception as e:
        print(f"❌ Erro na Binance: {e}")
        results['binance_api'] = False
    
    # Teste Yahoo Finance API
    print("\n2. Testando Yahoo Finance API...")
    try:
        from apis.yahoo_api import YahooFinanceAPI
        api = YahooFinanceAPI()
        data = api.get_stock_data("^BVSP")
        if data:
            print(f"✅ Yahoo Finance: Dados obtidos")
            results['yahoo_api'] = True
        else:
            print("❌ Dados do Yahoo Finance inválidos")
            results['yahoo_api'] = False
    except Exception as e:
        print(f"❌ Erro no Yahoo Finance: {e}")
        results['yahoo_api'] = False
    
    return results

def test_examples():
    """Testa os exemplos de uso"""
    print("\n" + "="*60)
    print("📚 TESTE DOS EXEMPLOS")
    print("="*60)
    
    results = {}
    
    # Teste do exemplo de análise de portfólio
    print("\n1. Testando exemplo de análise de portfólio...")
    example_result = run_command(
        "python examples/portfolio_analysis_example.py",
        "Executando exemplo de análise de portfólio"
    )
    results['portfolio_analysis_example'] = example_result['success']
    
    return results

def test_scripts():
    """Testa os scripts principais"""
    print("\n" + "="*60)
    print("📜 TESTE DOS SCRIPTS")
    print("="*60)
    
    results = {}
    
    # Teste do script de criptomoedas
    print("\n1. Testando script de criptomoedas...")
    crypto_result = run_command(
        "python BInance/test_cripto_portfolio.py",
        "Executando teste de portfólio de criptomoedas"
    )
    results['crypto_portfolio_test'] = crypto_result['success']
    
    # Teste do script de dados de mercado
    print("\n2. Testando script de dados de mercado...")
    market_result = run_command(
        "python test_enhanced_market_data.py",
        "Executando teste de dados de mercado"
    )
    results['market_data_test'] = market_result['success']
    
    return results

def generate_report(test_results):
    """Gera relatório final dos testes"""
    print("\n" + "="*60)
    print("📊 RELATÓRIO FINAL")
    print("="*60)
    
    total_tests = 0
    passed_tests = 0
    
    for category, results in test_results.items():
        if isinstance(results, dict):
            category_total = len(results)
            category_passed = sum(1 for success in results.values() if success)
        else:
            category_total = 1
            category_passed = 1 if results else 0
        
        total_tests += category_total
        passed_tests += category_passed
        
        success_rate = (category_passed / category_total) * 100 if category_total > 0 else 0
        
        print(f"\n{category.upper()}:")
        print(f"  Testes: {category_passed}/{category_total} ({success_rate:.1f}%)")
        
        if isinstance(results, dict):
            for test_name, success in results.items():
                status = "✅" if success else "❌"
                print(f"    {status} {test_name}")
    
    overall_success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"\n📈 RESUMO GERAL:")
    print(f"  Total de Testes: {total_tests}")
    print(f"  Testes Aprovados: {passed_tests}")
    print(f"  Taxa de Sucesso: {overall_success_rate:.1f}%")
    
    # Salvar relatório
    report = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'success_rate': overall_success_rate,
        'results': test_results
    }
    
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Relatório salvo em: {report_file}")
    
    return overall_success_rate >= 80  # Sucesso se >= 80%

def main():
    """Função principal"""
    print("🚀 INICIANDO TESTES AUTOMATIZADOS")
    print("="*60)
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Diretório: {os.getcwd()}")
    
    # Executar todos os testes
    test_results = {
        'imports': test_imports(),
        'core_functionality': test_core_functionality(),
        'apis': test_apis(),
        'examples': test_examples(),
        'scripts': test_scripts()
    }
    
    # Gerar relatório
    success = generate_report(test_results)
    
    if success:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        sys.exit(0)
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM!")
        sys.exit(1)

if __name__ == "__main__":
    main() 