#!/usr/bin/env python3
"""
Script para buscar preços de mercado em tempo real
- Criptomoedas: preços de abertura em BRL
- Ações: últimos preços de fechamento em BRL
"""

import yfinance as yf
import requests
from datetime import datetime
import time

def get_usd_brl_rate():
    """Busca cotação USD/BRL via API do Banco Central"""
    try:
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados/ultimos/1?formato=json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return float(data[0]['valor'])
        else:
            # Fallback para cotação fixa se API falhar
            return 5.42
    except:
        return 5.42

def get_crypto_prices():
    """Busca preços de abertura das criptomoedas em USD e converte para BRL"""
    cryptos = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD', 'AVAX-USD']
    usd_brl = get_usd_brl_rate()
    
    print("🪙 PREÇOS DE ABERTURA - CRIPTOMOEDAS (BRL)")
    print("=" * 60)
    
    for crypto in cryptos:
        try:
            ticker = yf.Ticker(crypto)
            # Busca dados dos últimos 2 dias para pegar abertura de hoje
            hist = ticker.history(period="2d")
            
            if len(hist) >= 2:
                # Preço de abertura de hoje
                open_price_usd = float(hist.iloc[-1]['Open'])
                # Preço atual
                current_price_usd = float(hist.iloc[-1]['Close'])
                # Variação do dia
                daily_change = ((current_price_usd - open_price_usd) / open_price_usd) * 100
                
                # Conversão para BRL
                open_price_brl = open_price_usd * usd_brl
                current_price_brl = current_price_usd * usd_brl
                
                symbol = crypto.replace('-USD', '')
                print(f"{symbol:>6}: Abertura R$ {open_price_brl:>10.2f} | "
                      f"Atual R$ {current_price_brl:>10.2f} | "
                      f"Var: {daily_change:>+6.2f}%")
                
        except Exception as e:
            print(f"Erro ao buscar {crypto}: {e}")
    
    print(f"\n💱 Cotação USD/BRL: R$ {usd_brl:.4f}")
    print()

def get_stock_prices():
    """Busca últimos preços de fechamento das ações em BRL"""
    stocks = ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'WEGE3.SA', 'LREN3.SA']
    
    print("📈 ÚLTIMOS PREÇOS DE FECHAMENTO - AÇÕES (BRL)")
    print("=" * 60)
    
    for stock in stocks:
        try:
            ticker = yf.Ticker(stock)
            hist = ticker.history(period="5d")
            
            if len(hist) > 0:
                # Último preço de fechamento
                last_close = float(hist.iloc[-1]['Close'])
                # Preço de abertura do último dia
                last_open = float(hist.iloc[-1]['Open'])
                # Variação do último dia
                daily_change = ((last_close - last_open) / last_open) * 100
                
                symbol = stock.replace('.SA', '')
                print(f"{symbol:>6}: Fechamento R$ {last_close:>10.2f} | "
                      f"Abertura R$ {last_open:>10.2f} | "
                      f"Var: {daily_change:>+6.2f}%")
                
        except Exception as e:
            print(f"Erro ao buscar {stock}: {e}")
    
    print()

def generate_portfolio_data():
    """Gera dados formatados para uso no painel Streamlit"""
    print("📋 DADOS FORMATADOS PARA O PAINEL STREAMLIT")
    print("=" * 60)
    
    # Criptomoedas
    cryptos = ['BTC-USD', 'ETH-USD', 'SOL-USD', 'BNB-USD', 'AVAX-USD']
    usd_brl = get_usd_brl_rate()
    
    print("🪙 CRIPTOMOEDAS (Preços de Abertura em BRL):")
    for crypto in cryptos:
        try:
            ticker = yf.Ticker(crypto)
            hist = ticker.history(period="2d")
            
            if len(hist) >= 2:
                open_price_usd = float(hist.iloc[-1]['Open'])
                open_price_brl = open_price_usd * usd_brl
                symbol = crypto.replace('-USD', '')
                print(f"  '{symbol}': {open_price_brl:.2f},")
                
        except Exception as e:
            print(f"  # Erro {crypto}: {e}")
    
    print("\n📈 AÇÕES (Últimos Preços de Fechamento em BRL):")
    stocks = ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'WEGE3.SA', 'LREN3.SA']
    
    for stock in stocks:
        try:
            ticker = yf.Ticker(stock)
            hist = ticker.history(period="5d")
            
            if len(hist) > 0:
                last_close = float(hist.iloc[-1]['Close'])
                symbol = stock.replace('.SA', '')
                print(f"  '{symbol}': {last_close:.2f},")
                
        except Exception as e:
            print(f"  # Erro {stock}: {e}")
    
    print("\n💡 INSTRUÇÕES:")
    print("1. Copie os valores acima para o painel Streamlit")
    print("2. Para criptomoedas, use os preços de abertura como 'Preço de Entrada'")
    print("3. Para ações, use os preços de fechamento como 'Preço Atual'")
    print("4. Defina as quantidades conforme seu portfólio")

def main():
    print("🚀 SISTEMA DE BUSCA DE PREÇOS DE MERCADO")
    print("=" * 60)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Busca preços
    get_crypto_prices()
    get_stock_prices()
    
    # Gera dados formatados
    generate_portfolio_data()
    
    print("✅ Busca concluída!")

if __name__ == "__main__":
    main() 