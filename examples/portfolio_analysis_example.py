#!/usr/bin/env python3
"""
Exemplo de uso da classe MarketIndicesManager em análises de portfólio
=====================================================================

Este script demonstra como usar a classe MarketIndicesManager para:
1. Atualizar valores de portfólio em tempo real
2. Calcular métricas de risco
3. Comparar com benchmarks
4. Gerar relatórios automatizados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.market_indices import market_indices
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class PortfolioAnalyzer:
    """Classe para análise de portfólios usando MarketIndicesManager"""
    
    def __init__(self):
        self.market_data = None
        self.update_market_data()
    
    def update_market_data(self):
        """Atualiza dados de mercado"""
        print("🔄 Atualizando dados de mercado...")
        self.market_data = market_indices.get_all_market_data()
        print("✅ Dados atualizados!")
    
    def analyze_crypto_portfolio(self, portfolio: dict) -> dict:
        """
        Analisa um portfólio de criptomoedas
        
        Args:
            portfolio: Dict com estrutura {symbol: {'quantity': float, 'entry_price': float}}
        """
        print(f"\n📊 Analisando portfólio de criptomoedas...")
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'total_value_usd': 0,
            'total_value_brl': 0,
            'assets': {},
            'performance': {},
            'risk_metrics': {}
        }
        
        # Buscar preços atuais
        crypto_symbols = [f"{symbol}USDT" for symbol in portfolio.keys()]
        current_prices = market_indices.get_crypto_prices(crypto_symbols)
        
        for symbol, data in portfolio.items():
            symbol_usdt = f"{symbol}USDT"
            current_price = current_prices.get(symbol_usdt, {}).get('price', 0)
            
            if current_price > 0:
                quantity = data['quantity']
                entry_price = data['entry_price']
                
                current_value_usd = quantity * current_price
                entry_value_usd = quantity * entry_price
                profit_loss_usd = current_value_usd - entry_value_usd
                profit_loss_pct = (profit_loss_usd / entry_value_usd) * 100 if entry_value_usd > 0 else 0
                
                current_value_brl = current_value_usd * self.market_data['exchange_rates']['USD_BRL']
                
                analysis['assets'][symbol] = {
                    'quantity': quantity,
                    'entry_price': entry_price,
                    'current_price': current_price,
                    'current_value_usd': current_value_usd,
                    'current_value_brl': current_value_brl,
                    'profit_loss_usd': profit_loss_usd,
                    'profit_loss_pct': profit_loss_pct
                }
                
                analysis['total_value_usd'] += current_value_usd
                analysis['total_value_brl'] += current_value_brl
        
        # Calcular métricas de performance
        total_entry_value = sum(data['quantity'] * data['entry_price'] for data in portfolio.values())
        total_profit_loss = analysis['total_value_usd'] - total_entry_value
        total_return = (total_profit_loss / total_entry_value) * 100 if total_entry_value > 0 else 0
        
        analysis['performance'] = {
            'total_return_usd': total_profit_loss,
            'total_return_pct': total_return,
            'total_entry_value': total_entry_value
        }
        
        return analysis
    
    def analyze_stock_portfolio(self, portfolio: dict) -> dict:
        """
        Analisa um portfólio de ações
        
        Args:
            portfolio: Dict com estrutura {symbol: {'quantity': int, 'entry_price': float}}
        """
        print(f"\n📈 Analisando portfólio de ações...")
        
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'total_value_brl': 0,
            'assets': {},
            'performance': {},
            'benchmark_comparison': {}
        }
        
        # Buscar dados de ações
        stock_symbols = list(portfolio.keys())
        current_prices = market_indices.get_stock_indices(stock_symbols)
        
        for symbol, data in portfolio.items():
            current_data = current_prices.get(symbol, {})
            current_price = current_data.get('price', 0)
            
            if current_price > 0:
                quantity = data['quantity']
                entry_price = data['entry_price']
                
                current_value = quantity * current_price
                entry_value = quantity * entry_price
                profit_loss = current_value - entry_value
                profit_loss_pct = (profit_loss / entry_value) * 100 if entry_value > 0 else 0
                
                analysis['assets'][symbol] = {
                    'quantity': quantity,
                    'entry_price': entry_price,
                    'current_price': current_price,
                    'current_value': current_value,
                    'profit_loss': profit_loss,
                    'profit_loss_pct': profit_loss_pct,
                    'name': current_data.get('name', symbol)
                }
                
                analysis['total_value_brl'] += current_value
        
        # Comparar com Ibovespa
        ibov_data = self.market_data['stocks'].get('^BVSP', {})
        if ibov_data:
            analysis['benchmark_comparison'] = {
                'ibovespa_price': ibov_data.get('price', 0),
                'ibovespa_change_24h': ibov_data.get('change_24h', 0)
            }
        
        return analysis
    
    def calculate_risk_metrics(self, portfolio_analysis: dict) -> dict:
        """Calcula métricas de risco do portfólio"""
        
        # Simular volatilidade baseada no tipo de ativo
        crypto_volatility = 0.25  # 25% volatilidade típica de crypto
        stock_volatility = 0.15   # 15% volatilidade típica de ações
        
        total_value = portfolio_analysis.get('total_value_brl', 0)
        
        # Calcular Sharpe Ratio (simulado)
        risk_free_rate = 0.12  # CDI
        portfolio_return = portfolio_analysis.get('performance', {}).get('total_return_pct', 0) / 100
        
        # Assumir volatilidade média ponderada
        avg_volatility = (crypto_volatility + stock_volatility) / 2
        sharpe_ratio = (portfolio_return - risk_free_rate) / avg_volatility if avg_volatility > 0 else 0
        
        risk_metrics = {
            'volatility': avg_volatility,
            'sharpe_ratio': sharpe_ratio,
            'var_95': total_value * avg_volatility * 1.645,  # Value at Risk 95%
            'max_drawdown': -0.20,  # Simulado
            'beta': 1.2  # Simulado
        }
        
        return risk_metrics
    
    def generate_comprehensive_report(self, crypto_portfolio: dict = None, stock_portfolio: dict = None) -> dict:
        """Gera relatório completo de análise"""
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'market_summary': market_indices.get_market_summary(),
            'crypto_analysis': None,
            'stock_analysis': None,
            'risk_metrics': {},
            'recommendations': []
        }
        
        # Análise de criptomoedas
        if crypto_portfolio:
            crypto_analysis = self.analyze_crypto_portfolio(crypto_portfolio)
            report['crypto_analysis'] = crypto_analysis
            report['risk_metrics']['crypto'] = self.calculate_risk_metrics(crypto_analysis)
        
        # Análise de ações
        if stock_portfolio:
            stock_analysis = self.analyze_stock_portfolio(stock_portfolio)
            report['stock_analysis'] = stock_analysis
            report['risk_metrics']['stocks'] = self.calculate_risk_metrics(stock_analysis)
        
        # Gerar recomendações
        report['recommendations'] = self.generate_recommendations(report)
        
        return report
    
    def generate_recommendations(self, report: dict) -> list:
        """Gera recomendações baseadas na análise"""
        recommendations = []
        
        # Verificar diversificação
        crypto_value = report.get('crypto_analysis', {}).get('total_value_brl', 0)
        stock_value = report.get('stock_analysis', {}).get('total_value_brl', 0)
        total_value = crypto_value + stock_value
        
        if total_value > 0:
            crypto_weight = crypto_value / total_value
            stock_weight = stock_value / total_value
            
            if crypto_weight > 0.7:
                recommendations.append("⚠️ Alta concentração em criptomoedas. Considere diversificar com ações.")
            
            if stock_weight > 0.8:
                recommendations.append("⚠️ Alta concentração em ações. Considere diversificar com criptomoedas.")
        
        # Verificar performance
        crypto_return = report.get('crypto_analysis', {}).get('performance', {}).get('total_return_pct', 0)
        if crypto_return < -10:
            recommendations.append("📉 Performance negativa em criptomoedas. Revise sua estratégia.")
        
        # Verificar câmbio
        usd_brl = report.get('market_summary', {}).get('exchange_rate_usd_brl', 0)
        if usd_brl > 5.5:
            recommendations.append("💱 Dólar em alta. Considere hedge cambial.")
        
        return recommendations
    
    def print_analysis(self, report: dict):
        """Imprime análise de forma organizada"""
        
        print("\n" + "="*80)
        print("📊 RELATÓRIO COMPLETO DE ANÁLISE DE PORTFÓLIO")
        print("="*80)
        
        # Resumo de mercado
        market_summary = report.get('market_summary', {})
        print(f"\n🌍 RESUMO DE MERCADO:")
        print(f"Câmbio USD/BRL: R$ {market_summary.get('exchange_rate_usd_brl', 0):.4f}")
        print(f"Bitcoin: R$ {market_summary.get('bitcoin_price_brl', 0):,.2f} ({market_summary.get('bitcoin_change_24h', 0):+.2f}%)")
        print(f"Ibovespa: {market_summary.get('ibovespa_price', 0):,.2f} ({market_summary.get('ibovespa_change_24h', 0):+.2f}%)")
        
        # Análise de criptomoedas
        crypto_analysis = report.get('crypto_analysis')
        if crypto_analysis:
            print(f"\n🪙 ANÁLISE DE CRIPTOMOEDAS:")
            print(f"Valor Total: R$ {crypto_analysis.get('total_value_brl', 0):,.2f}")
            print(f"Retorno Total: {crypto_analysis.get('performance', {}).get('total_return_pct', 0):+.2f}%")
            
            for symbol, data in crypto_analysis.get('assets', {}).items():
                print(f"  {symbol}: R$ {data['current_value_brl']:,.2f} ({data['profit_loss_pct']:+.2f}%)")
        
        # Análise de ações
        stock_analysis = report.get('stock_analysis')
        if stock_analysis:
            print(f"\n📈 ANÁLISE DE AÇÕES:")
            print(f"Valor Total: R$ {stock_analysis.get('total_value_brl', 0):,.2f}")
            
            for symbol, data in stock_analysis.get('assets', {}).items():
                print(f"  {symbol}: R$ {data['current_value']:,.2f} ({data['profit_loss_pct']:+.2f}%)")
        
        # Métricas de risco
        risk_metrics = report.get('risk_metrics', {})
        if risk_metrics:
            print(f"\n⚠️ MÉTRICAS DE RISCO:")
            for asset_type, metrics in risk_metrics.items():
                print(f"  {asset_type.title()}:")
                print(f"    Volatilidade: {metrics.get('volatility', 0):.1%}")
                print(f"    Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}")
                print(f"    VaR 95%: R$ {metrics.get('var_95', 0):,.2f}")
        
        # Recomendações
        recommendations = report.get('recommendations', [])
        if recommendations:
            print(f"\n💡 RECOMENDAÇÕES:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        
        print("\n" + "="*80)

def main():
    """Função principal com exemplo de uso"""
    
    print("🚀 INICIANDO EXEMPLO DE ANÁLISE DE PORTFÓLIO")
    print("="*60)
    
    # Criar analisador
    analyzer = PortfolioAnalyzer()
    
    # Exemplo de portfólio de criptomoedas
    crypto_portfolio = {
        'BTC': {'quantity': 0.1, 'entry_price': 45000},
        'ETH': {'quantity': 2.0, 'entry_price': 2800},
        'BNB': {'quantity': 5.0, 'entry_price': 300},
        'SOL': {'quantity': 20.0, 'entry_price': 100}
    }
    
    # Exemplo de portfólio de ações
    stock_portfolio = {
        'PETR4.SA': {'quantity': 100, 'entry_price': 30.0},
        'VALE3.SA': {'quantity': 50, 'entry_price': 70.0},
        '^BVSP': {'quantity': 1, 'entry_price': 130000}  # ETF do Ibovespa
    }
    
    # Gerar relatório completo
    report = analyzer.generate_comprehensive_report(
        crypto_portfolio=crypto_portfolio,
        stock_portfolio=stock_portfolio
    )
    
    # Imprimir análise
    analyzer.print_analysis(report)
    
    # Salvar relatório
    filename = f"portfolio_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Relatório salvo em: {filename}")
    except Exception as e:
        print(f"\n❌ Erro ao salvar relatório: {e}")
    
    print("\n🎉 Exemplo concluído!")

if __name__ == "__main__":
    main() 