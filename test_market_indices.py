#!/usr/bin/env python3
"""
Script de teste para demonstrar o uso da classe MarketIndicesManager
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.market_indices import market_indices
import json
from datetime import datetime

def test_market_indices():
    """Testa todas as funcionalidades da classe MarketIndicesManager"""
    
    print("=" * 60)
    print("TESTE DA CLASSE MARKET INDICES MANAGER")
    print("=" * 60)
    
    try:
        # 1. Teste de câmbio
        print("\n1. TESTE DE CÂMBIO:")
        print("-" * 30)
        exchange_rates = market_indices.get_exchange_rate()
        print(f"USD/BRL: R$ {exchange_rates['USD_BRL']:.4f}")
        print(f"EUR/BRL: R$ {exchange_rates['EUR_BRL']:.4f}")
        print(f"GBP/BRL: R$ {exchange_rates['GBP_BRL']:.4f}")
        
        # 2. Teste de criptomoedas
        print("\n2. TESTE DE CRIPTOMOEDAS:")
        print("-" * 30)
        crypto_data = market_indices.get_crypto_prices()
        for symbol, data in crypto_data.items():
            print(f"{symbol}:")
            print(f"  Preço USD: ${data['price']:,.2f}")
            print(f"  Preço BRL: R$ {data['price_brl']:,.2f}")
            print(f"  Variação 24h: {data['change_24h']:+.2f}%")
            print()
        
        # 3. Teste de índices de ações
        print("\n3. TESTE DE ÍNDICES DE AÇÕES:")
        print("-" * 30)
        stock_data = market_indices.get_stock_indices()
        for symbol, data in stock_data.items():
            print(f"{symbol} ({data.get('name', 'N/A')}):")
            print(f"  Preço: {data['price']:,.2f}")
            print(f"  Variação 24h: {data['change_24h']:+.2f}%")
            print(f"  Volume: {data['volume']:,.0f}")
            print()
        
        # 4. Teste de commodities
        print("\n4. TESTE DE COMMODITIES:")
        print("-" * 30)
        commodity_data = market_indices.get_commodity_prices()
        for symbol, data in commodity_data.items():
            print(f"{symbol}:")
            print(f"  Preço USD: ${data['price']:,.2f}")
            print(f"  Preço BRL: R$ {data['price_brl']:,.2f}")
            print(f"  Variação 24h: {data['change_24h']:+.2f}%")
            print()
        
        # 5. Teste de resumo de mercado
        print("\n5. RESUMO DE MERCADO:")
        print("-" * 30)
        summary = market_indices.get_market_summary()
        print(f"Câmbio USD/BRL: R$ {summary['exchange_rate_usd_brl']:.4f}")
        print(f"Bitcoin: R$ {summary['bitcoin_price_brl']:,.2f} ({summary['bitcoin_change_24h']:+.2f}%)")
        print(f"Ibovespa: {summary['ibovespa_price']:,.2f} ({summary['ibovespa_change_24h']:+.2f}%)")
        print(f"S&P 500: {summary['sp500_price']:,.2f} ({summary['sp500_change_24h']:+.2f}%)")
        print(f"Ouro: R$ {summary['gold_price_brl']:,.2f} ({summary['gold_change_24h']:+.2f}%)")
        
        # 6. Teste de conversão
        print("\n6. TESTE DE CONVERSÃO:")
        print("-" * 30)
        usd_amount = 1000
        brl_amount = market_indices.convert_to_brl(usd_amount)
        print(f"${usd_amount:,.2f} USD = R$ {brl_amount:,.2f} BRL")
        
        # 7. Teste de todos os dados
        print("\n7. TESTE DE TODOS OS DADOS:")
        print("-" * 30)
        all_data = market_indices.get_all_market_data()
        print(f"Total de criptomoedas: {len(all_data['crypto'])}")
        print(f"Total de índices/ações: {len(all_data['stocks'])}")
        print(f"Total de commodities: {len(all_data['commodities'])}")
        print(f"Timestamp: {all_data['timestamp']}")
        
        # 8. Salvar dados
        print("\n8. SALVANDO DADOS:")
        print("-" * 30)
        filename = market_indices.save_market_data()
        if filename:
            print(f"Dados salvos em: {filename}")
        
        print("\n" + "=" * 60)
        print("TESTE CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()

def test_portfolio_integration():
    """Testa a integração com dados de portfólio"""
    
    print("\n" + "=" * 60)
    print("TESTE DE INTEGRAÇÃO COM PORTFÓLIO")
    print("=" * 60)
    
    # Simular dados de portfólio
    portfolio_data = {
        'BTCUSDT': {
            'quantity': 0.5,
            'value_usd': 25000,
            'weight': 0.4
        },
        'ETHUSDT': {
            'quantity': 2.0,
            'value_usd': 15000,
            'weight': 0.3
        },
        'PETR4.SA': {
            'quantity': 100,
            'value_brl': 30000,
            'weight': 0.3
        }
    }
    
    # Calcular valor total em BRL
    total_brl = market_indices.get_portfolio_value_brl(portfolio_data)
    
    print(f"Valor total do portfólio: R$ {total_brl:,.2f}")
    
    # Atualizar valores com preços atuais
    print("\nValores atualizados:")
    crypto_data = market_indices.get_crypto_prices()
    
    for asset, data in portfolio_data.items():
        if asset in crypto_data:
            current_price_brl = crypto_data[asset]['price_brl']
            current_value = data['quantity'] * current_price_brl
            print(f"{asset}: R$ {current_value:,.2f} (R$ {current_price_brl:,.2f} cada)")
        else:
            print(f"{asset}: R$ {data.get('value_brl', 0):,.2f}")

if __name__ == "__main__":
    test_market_indices()
    test_portfolio_integration() 