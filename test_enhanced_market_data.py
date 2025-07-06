#!/usr/bin/env python3
"""
Teste dos Métodos Avançados - MarketIndicesManager
==================================================

Este script testa os novos métodos com dados históricos e métricas avançadas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.market_indices import market_indices
import json
from datetime import datetime

def test_historical_data():
    """Testa os métodos de dados históricos"""
    
    print("=" * 80)
    print("TESTE DE DADOS HISTÓRICOS")
    print("=" * 80)
    print(f"📅 PERÍODO DE TESTE: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}")
    print(f"⏱️  DURAÇÃO: Últimos 30 dias (dados históricos)")
    print("=" * 80)
    
    try:
        # 1. Teste de dados históricos do dólar
        print("\n1. DADOS HISTÓRICOS DO DÓLAR (30 dias):")
        print("-" * 50)
        usd_history = market_indices.get_historical_exchange_rate(30)
        if usd_history:
            print(f"Taxa atual: R$ {usd_history['current_rate']:.4f}")
            print(f"Taxa máxima: R$ {usd_history['max_rate']:.4f}")
            print(f"Taxa mínima: R$ {usd_history['min_rate']:.4f}")
            print(f"Retorno acumulado: {usd_history['cumulative_return']:.2%}")
            print(f"Volatilidade anualizada: {usd_history['volatility']:.2%}")
            print(f"Total de dias: {len(usd_history['dates'])}")
        else:
            print("❌ Erro ao obter dados históricos do dólar")
        
        # 2. Teste de dados históricos do Bitcoin
        print("\n2. DADOS HISTÓRICOS DO BITCOIN (30 dias):")
        print("-" * 50)
        btc_history = market_indices.get_historical_crypto_data('BTC', 30)
        if btc_history:
            print(f"Preço atual: ${btc_history['current_price']:,.2f}")
            print(f"Preço máximo: ${btc_history['max_price']:,.2f}")
            print(f"Preço mínimo: ${btc_history['min_price']:,.2f}")
            print(f"Retorno acumulado: {btc_history['cumulative_return']:.2%}")
            print(f"Volatilidade anualizada: {btc_history['volatility']:.2%}")
            print(f"Total de dias: {len(btc_history['dates'])}")
        else:
            print("❌ Erro ao obter dados históricos do Bitcoin")
        
        # 3. Teste de dados históricos do Ibovespa
        print("\n3. DADOS HISTÓRICOS DO IBOVESPA (30 dias):")
        print("-" * 50)
        ibov_history = market_indices.get_historical_stock_data('^BVSP', 30)
        if ibov_history:
            print(f"Preço atual: {ibov_history['current_price']:,.2f}")
            print(f"Preço máximo: {ibov_history['max_price']:,.2f}")
            print(f"Preço mínimo: {ibov_history['min_price']:,.2f}")
            print(f"Retorno acumulado: {ibov_history['cumulative_return']:.2%}")
            print(f"Volatilidade anualizada: {ibov_history['volatility']:.2%}")
            print(f"Nome: {ibov_history.get('name', 'N/A')}")
            print(f"Total de dias: {len(ibov_history['dates'])}")
        else:
            print("❌ Erro ao obter dados históricos do Ibovespa")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de dados históricos: {e}")
        return False

def test_benchmark_metrics():
    """Testa o cálculo de métricas dos benchmarks"""
    
    print("\n" + "=" * 80)
    print("TESTE DE MÉTRICAS DOS BENCHMARKS")
    print("=" * 80)
    print(f"📅 PERÍODO DE TESTE: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}")
    print(f"⏱️  DURAÇÃO: Últimos 30 dias (dados históricos)")
    print("=" * 80)
    
    try:
        # Calcular métricas completas dos benchmarks
        print("\n📊 Calculando métricas dos benchmarks (30 dias)...")
        benchmarks = market_indices.calculate_benchmark_metrics(30)
        
        if benchmarks:
            print(f"✅ {len(benchmarks)} benchmarks calculados com sucesso!")
            
            # Mostrar período de análise
            if benchmarks and 'period_info' in list(benchmarks.values())[0]:
                period_info = list(benchmarks.values())[0]['period_info']
                print(f"\n📅 PERÍODO DE ANÁLISE: {period_info['period_description']}")
                print(f"   Data da análise: {period_info['analysis_date']}")
            
            for name, data in benchmarks.items():
                print(f"\n{name} ({data['description']}):")
                print(f"  Retorno Anual: {data['annual_return']:.2%}")
                print(f"  Volatilidade: {data['volatility']:.2%}")
                print(f"  Máximo Drawdown: {data['max_drawdown']:.2%}")
                print(f"  Sharpe Ratio: {data['sharpe_ratio']:.3f}")
                
                if 'current_rate' in data:
                    print(f"  Taxa Atual: {data['current_rate']:.4f}")
                elif 'current_price' in data:
                    print(f"  Preço Atual: {data['current_price']:,.2f}")
        else:
            print("❌ Erro ao calcular métricas dos benchmarks")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de métricas dos benchmarks: {e}")
        return False

def test_enhanced_market_summary():
    """Testa o resumo completo de mercado"""
    
    print("\n" + "=" * 80)
    print("TESTE DE RESUMO COMPLETO DE MERCADO")
    print("=" * 80)
    print(f"📅 PERÍODO DE TESTE: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}")
    print(f"⏱️  DURAÇÃO: Últimos 30 dias (dados históricos)")
    print("=" * 80)
    
    try:
        # Gerar resumo completo
        print("\n📊 Gerando resumo completo de mercado (30 dias)...")
        summary = market_indices.get_enhanced_market_summary(30)
        
        if summary:
            print("✅ Resumo completo gerado com sucesso!")
            
            # Informações do período
            period_info = summary['period_info']
            print(f"\n📅 PERÍODO DE ANÁLISE:")
            print(f"  {period_info['period_description']}")
            print(f"  Data da análise: {period_info['analysis_date']}")
            
            # Dados atuais
            current = summary['current_data']
            print(f"\n🌍 DADOS ATUAIS:")
            print(f"  Dólar: R$ {current['exchange_rate_usd_brl']:.4f}")
            print(f"  Bitcoin: R$ {current['bitcoin_price_brl']:,.2f} ({current['bitcoin_change_24h']:+.2f}%)")
            print(f"  Ibovespa: {current['ibovespa_price']:,.2f} ({current['ibovespa_change_24h']:+.2f}%)")
            print(f"  S&P 500: {current['sp500_price']:,.2f} ({current['sp500_change_24h']:+.2f}%)")
            print(f"  Ouro: R$ {current['gold_price_brl']:,.2f} ({current['gold_change_24h']:+.2f}%)")
            
            # Indicadores de mercado
            indicators = summary['market_indicators']
            print(f"\n📈 INDICADORES DE MERCADO:")
            print(f"  Índice Medo/Ganância: {indicators['fear_greed_index']['value']:.1f} ({indicators['fear_greed_index']['sentiment']})")
            print(f"  Sentimento do Mercado: {indicators['market_sentiment']}")
            print(f"  Regime de Volatilidade: {indicators['volatility_regime']}")
            
            # Correlações
            correlations = summary['correlation_analysis']
            if correlations:
                print(f"\n🔗 CORRELAÇÕES:")
                for pair, corr in correlations.items():
                    print(f"  {pair}: {corr:.3f}")
            
            # Dados históricos do dólar
            usd_history = summary['usd_history']
            if usd_history:
                print(f"\n💱 HISTÓRICO DO DÓLAR:")
                print(f"  Taxa atual: R$ {usd_history['current_rate']:.4f}")
                print(f"  Variação 30 dias: {usd_history['cumulative_return']:.2%}")
                print(f"  Volatilidade: {usd_history['volatility']:.2%}")
            
            return True
        else:
            print("❌ Erro ao gerar resumo completo")
            return False
        
    except Exception as e:
        print(f"❌ Erro no teste de resumo completo: {e}")
        return False

def test_portfolio_analysis():
    """Testa análise de portfólio com dados históricos"""
    
    print("\n" + "=" * 80)
    print("TESTE DE ANÁLISE DE PORTFÓLIO")
    print("=" * 80)
    
    try:
        # Simular portfólio
        portfolio = {
            'BTC': {'quantity': 0.1, 'entry_price': 45000},
            'ETH': {'quantity': 2.0, 'entry_price': 2800},
            'BNB': {'quantity': 5.0, 'entry_price': 300}
        }
        
        print(f"\n📊 Analisando portfólio:")
        for symbol, data in portfolio.items():
            print(f"  {symbol}: {data['quantity']} unidades a ${data['entry_price']:,.2f}")
        
        # Buscar preços atuais
        crypto_data = market_indices.get_crypto_prices(['BTCUSDT', 'ETHUSDT', 'BNBUSDT'])
        
        # Calcular performance
        total_entry_value = 0
        total_current_value = 0
        
        print(f"\n💰 PERFORMANCE ATUAL:")
        for symbol, data in portfolio.items():
            symbol_usdt = f"{symbol}USDT"
            if symbol_usdt in crypto_data:
                current_price = crypto_data[symbol_usdt]['price']
                entry_value = data['quantity'] * data['entry_price']
                current_value = data['quantity'] * current_price
                profit_loss = current_value - entry_value
                profit_loss_pct = (profit_loss / entry_value) * 100
                
                total_entry_value += entry_value
                total_current_value += current_value
                
                print(f"  {symbol}: ${current_value:,.2f} ({profit_loss_pct:+.2f}%)")
        
        # Performance total
        if total_entry_value > 0:
            total_profit_loss = total_current_value - total_entry_value
            total_return = (total_profit_loss / total_entry_value) * 100
            print(f"\n📈 PERFORMANCE TOTAL:")
            print(f"  Valor inicial: ${total_entry_value:,.2f}")
            print(f"  Valor atual: ${total_current_value:,.2f}")
            print(f"  Lucro/Prejuízo: ${total_profit_loss:,.2f} ({total_return:+.2f}%)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na análise de portfólio: {e}")
        return False

def main():
    """Função principal"""
    
    print("🚀 INICIANDO TESTE DOS MÉTODOS AVANÇADOS")
    print("=" * 80)
    
    # Executar testes
    tests = [
        ("Dados Históricos", test_historical_data),
        ("Métricas dos Benchmarks", test_benchmark_metrics),
        ("Resumo Completo de Mercado", test_enhanced_market_summary),
        ("Análise de Portfólio", test_portfolio_analysis)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔄 Executando: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro no teste {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumo dos resultados
    print("\n" + "=" * 80)
    print("RESUMO DOS TESTES")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📊 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 Todos os testes passaram!")
    else:
        print("⚠️ Alguns testes falharam. Verifique os logs acima.")
    
    print("\n" + "=" * 80)

if __name__ == "__main__":
    main() 