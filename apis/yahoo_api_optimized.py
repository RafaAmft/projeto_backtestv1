#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Yahoo Finance API Otimizada
Resolve problemas de rate limiting usando requests direto
"""

import requests
import time
import json
from datetime import datetime
from typing import Dict, List, Optional, Union

class YahooFinanceOptimized:
    """Classe otimizada para Yahoo Finance que evita rate limiting"""
    
    def __init__(self, delay_between_requests: float = 2.0):
        """
        Inicializa o cliente Yahoo Finance otimizado
        
        Args:
            delay_between_requests: Delay em segundos entre requisições
        """
        self.delay = delay_between_requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def get_stock_price(self, symbol: str) -> Optional[float]:
        """
        Obtém o preço atual de uma ação
        
        Args:
            symbol: Símbolo da ação (ex: 'PETR4.SA', 'AAPL')
            
        Returns:
            Preço atual ou None se erro
        """
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
            
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if 'chart' in data and 'result' in data['chart'] and data['chart']['result']:
                    result = data['chart']['result'][0]
                    if 'meta' in result and 'regularMarketPrice' in result['meta']:
                        return result['meta']['regularMarketPrice']
            
            elif response.status_code == 429:
                print(f"⚠️ Rate limit atingido para {symbol}. Aguardando 10 segundos...")
                time.sleep(10)
                return self.get_stock_price(symbol)  # Retry
                
            return None
            
        except Exception as e:
            print(f"❌ Erro ao buscar {symbol}: {e}")
            return None
    
    def get_multiple_prices(self, symbols: List[str]) -> Dict[str, float]:
        """
        Obtém preços de múltiplas ações com delays adequados
        
        Args:
            symbols: Lista de símbolos
            
        Returns:
            Dicionário com símbolo -> preço
        """
        results = {}
        
        for i, symbol in enumerate(symbols):
            print(f"🔄 Buscando {symbol}... ({i+1}/{len(symbols)})")
            
            price = self.get_stock_price(symbol)
            if price:
                results[symbol] = price
                print(f"✅ {symbol}: ${price:.2f}")
            else:
                print(f"❌ {symbol}: Erro")
            
            # Delay entre requisições (exceto na última)
            if i < len(symbols) - 1:
                print(f"⏳ Aguardando {self.delay} segundos...")
                time.sleep(self.delay)
        
        return results
    
    def get_market_data(self, symbol: str) -> Optional[Dict]:
        """
        Obtém dados completos do mercado para um símbolo
        
        Args:
            symbol: Símbolo da ação
            
        Returns:
            Dicionário com dados do mercado ou None
        """
        try:
            url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}"
            params = {
                'modules': 'financialData,quoteType,defaultKeyStatistics,assetProfile,summaryDetail',
                'formatted': 'false'
            }
            
            response = self.session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                print(f"⚠️ Rate limit atingido para {symbol}. Aguardando 15 segundos...")
                time.sleep(15)
                return self.get_market_data(symbol)  # Retry
                
            return None
            
        except Exception as e:
            print(f"❌ Erro ao buscar dados de mercado para {symbol}: {e}")
            return None

def test_yahoo_optimized():
    """Teste da classe otimizada"""
    print("🧪 TESTE YAHOO FINANCE OTIMIZADO")
    print("=" * 50)
    
    yahoo = YahooFinanceOptimized(delay_between_requests=3.0)
    
    # Teste ações brasileiras
    symbols_br = ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA']
    print("🇧🇷 Testando ações brasileiras...")
    
    prices = yahoo.get_multiple_prices(symbols_br)
    
    print(f"\n📊 Resultados: {len(prices)}/{len(symbols_br)} ações obtidas")
    for symbol, price in prices.items():
        print(f"  {symbol}: R$ {price:.2f}")
    
    return len(prices) > 0

if __name__ == "__main__":
    test_yahoo_optimized() 