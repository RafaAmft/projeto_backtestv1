#!/usr/bin/env python3
"""
Análise Temporal Completa de Portfólio
======================================

Este script realiza uma análise temporal completa de portfólios incluindo:
- Dados mensais e anuais dos últimos 5 anos
- Análise de criptomoedas, ações e fundos
- Relatórios temporais detalhados
- Comparações com benchmarks históricos
"""

import sys
import os
import json
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.market_indices import market_indices

class TemporalPortfolioAnalyzer:
    """
    Analisador temporal completo de portfólios
    """
    
    def __init__(self):
        self.market_data = None
        self.analysis_periods = market_indices.get_historical_analysis_periods()
        self.update_market_data()
    
    def update_market_data(self):
        """Atualiza dados de mercado"""
        print("🔄 Atualizando dados de mercado...")
        self.market_data = market_indices.get_all_market_data()
        print("✅ Dados atualizados!")
    
    def analyze_crypto_temporal(self, portfolio: dict, period: str = '5_years') -> dict:
        """
        Análise temporal de portfólio de criptomoedas
        
        Args:
            portfolio: Dict com estrutura {symbol: {'quantity': float, 'entry_price': float}}
            period: Período de análise
        """
        print(f"\n🪙 Analisando portfólio de criptomoedas ({self.analysis_periods[period]['description']})...")
        
        # Símbolos para análise temporal
        symbols = [f"{symbol}USDT" for symbol in portfolio.keys()]
        
        # Gerar análise temporal
        temporal_analysis = market_indices.generate_temporal_analysis(symbols, period)
        
        # Calcular valores atuais
        current_prices = market_indices.get_crypto_prices(symbols)
        
        analysis = {
            'period_info': temporal_analysis.get('period_info', {}),
            'analysis_date': datetime.now().strftime('%d/%m/%Y às %H:%M:%S'),
            'total_value_usd': 0,
            'total_value_brl': 0,
            'assets': {},
            'temporal_data': temporal_analysis,
            'performance_metrics': {}
        }
        
        # Calcular valores e performance por ativo
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
                
                # Dados temporais do ativo
                monthly_data = temporal_analysis.get('monthly_analysis', {}).get(symbol_usdt, {})
                annual_data = temporal_analysis.get('annual_analysis', {}).get(symbol_usdt, {})
                
                analysis['assets'][symbol] = {
                    'quantity': quantity,
                    'entry_price': entry_price,
                    'current_price': current_price,
                    'current_value_usd': current_value_usd,
                    'current_value_brl': current_value_brl,
                    'profit_loss_usd': profit_loss_usd,
                    'profit_loss_pct': profit_loss_pct,
                    'monthly_analysis': monthly_data,
                    'annual_analysis': annual_data
                }
                
                analysis['total_value_usd'] += current_value_usd
                analysis['total_value_brl'] += current_value_brl
        
        # Calcular métricas de performance
        total_entry_value = sum(data['quantity'] * data['entry_price'] for data in portfolio.values())
        total_profit_loss = analysis['total_value_usd'] - total_entry_value
        total_return = (total_profit_loss / total_entry_value) * 100 if total_entry_value > 0 else 0
        
        analysis['performance_metrics'] = {
            'total_return_usd': total_profit_loss,
            'total_return_pct': total_return,
            'total_entry_value': total_entry_value,
            'temporal_summary': temporal_analysis.get('summary', {})
        }
        
        return analysis
    
    def analyze_stock_temporal(self, portfolio: dict, period: str = '5_years') -> dict:
        """
        Análise temporal de portfólio de ações
        
        Args:
            portfolio: Dict com estrutura {symbol: {'quantity': int, 'entry_price': float}}
            period: Período de análise
        """
        print(f"\n📈 Analisando portfólio de ações ({self.analysis_periods[period]['description']})...")
        
        # Símbolos para análise temporal
        symbols = list(portfolio.keys())
        
        # Gerar análise temporal
        temporal_analysis = market_indices.generate_temporal_analysis(symbols, period)
        
        # Buscar dados de ações
        current_prices = market_indices.get_stock_indices(symbols)
        
        analysis = {
            'period_info': temporal_analysis.get('period_info', {}),
            'analysis_date': datetime.now().strftime('%d/%m/%Y às %H:%M:%S'),
            'total_value_brl': 0,
            'assets': {},
            'temporal_data': temporal_analysis,
            'performance_metrics': {}
        }
        
        # Calcular valores e performance por ativo
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
                
                # Dados temporais do ativo
                monthly_data = temporal_analysis.get('monthly_analysis', {}).get(symbol, {})
                annual_data = temporal_analysis.get('annual_analysis', {}).get(symbol, {})
                
                analysis['assets'][symbol] = {
                    'quantity': quantity,
                    'entry_price': entry_price,
                    'current_price': current_price,
                    'current_value': current_value,
                    'profit_loss': profit_loss,
                    'profit_loss_pct': profit_loss_pct,
                    'name': current_data.get('name', symbol),
                    'monthly_analysis': monthly_data,
                    'annual_analysis': annual_data
                }
                
                analysis['total_value_brl'] += current_value
        
        # Comparar com Ibovespa
        ibov_data = self.market_data['stocks'].get('^BVSP', {})
        if ibov_data:
            analysis['benchmark_comparison'] = {
                'ibovespa_price': ibov_data.get('price', 0),
                'ibovespa_change_24h': ibov_data.get('change_24h', 0)
            }
        
        analysis['performance_metrics'] = {
            'temporal_summary': temporal_analysis.get('summary', {})
        }
        
        return analysis
    
    def analyze_funds_temporal(self, period: str = '5_years') -> dict:
        """
        Análise temporal de fundos de investimento
        
        Args:
            period: Período de análise
        """
        print(f"\n🏦 Analisando fundos de investimento ({self.analysis_periods[period]['description']})...")
        
        # Dados simulados de fundos com análise temporal
        fund_portfolio = {
            'fundos': [
                {
                    'nome': 'Fund Test 1',
                    'cnpj': '00.000.000/0001-00',
                    'categoria': 'Renda Variável',
                    'retorno_anual': 0.15,
                    'volatilidade': 0.12,
                    'sharpe_ratio': 1.25,
                    'valor_atual': 50000.0,
                    'valor_inicial': 45000.0,
                    'monthly_returns': [0.02, -0.01, 0.03, -0.02, 0.01, 0.02, -0.01, 0.03, 0.01, -0.01] * 6,  # 5 anos
                    'annual_returns': [0.18, 0.12, 0.15, 0.08, 0.20]  # 5 anos
                },
                {
                    'nome': 'Fund Test 2',
                    'cnpj': '00.000.000/0002-00',
                    'categoria': 'Renda Fixa',
                    'retorno_anual': 0.08,
                    'volatilidade': 0.05,
                    'sharpe_ratio': 1.60,
                    'valor_atual': 30000.0,
                    'valor_inicial': 28000.0,
                    'monthly_returns': [0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01] * 6,  # 5 anos
                    'annual_returns': [0.10, 0.08, 0.09, 0.07, 0.11]  # 5 anos
                }
            ],
            'metrics': {
                'total_value': 80000.0,
                'total_return': 0.1176,  # 11.76%
                'avg_volatility': 0.085,
                'avg_sharpe': 1.425,
                'diversification_score': 0.75
            },
            'temporal_analysis': {
                'period_info': self.analysis_periods[period],
                'monthly_stats': {
                    'avg_return': 0.015,
                    'volatility': 0.025,
                    'best_month': 0.03,
                    'worst_month': -0.02,
                    'positive_months': 45,
                    'total_months': 60
                },
                'annual_stats': {
                    'avg_return': 0.09,
                    'volatility': 0.015,
                    'best_year': 0.20,
                    'worst_year': 0.07,
                    'positive_years': 5,
                    'total_years': 5
                }
            }
        }
        
        return fund_portfolio
    
    def generate_comprehensive_temporal_report(self, crypto_portfolio: dict = None, stock_portfolio: dict = None, period: str = '5_years') -> dict:
        """
        Gera relatório temporal completo
        
        Args:
            crypto_portfolio: Portfólio de criptomoedas
            stock_portfolio: Portfólio de ações
            period: Período de análise
        """
        print(f"\n📋 Gerando relatório temporal completo ({self.analysis_periods[period]['description']})...")
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'period_info': self.analysis_periods[period],
            'analysis_date': datetime.now().strftime('%d/%m/%Y às %H:%M:%S'),
            'market_summary': market_indices.get_market_summary(),
            'crypto_analysis': None,
            'stock_analysis': None,
            'fund_analysis': None,
            'portfolio_summary': {},
            'temporal_insights': []
        }
        
        # Análise de criptomoedas
        if crypto_portfolio:
            crypto_analysis = self.analyze_crypto_temporal(crypto_portfolio, period)
            report['crypto_analysis'] = crypto_analysis
        
        # Análise de ações
        if stock_portfolio:
            stock_analysis = self.analyze_stock_temporal(stock_portfolio, period)
            report['stock_analysis'] = stock_analysis
        
        # Análise de fundos
        fund_analysis = self.analyze_funds_temporal(period)
        report['fund_analysis'] = fund_analysis
        
        # Calcular resumo geral do portfólio
        crypto_value = report.get('crypto_analysis', {}).get('total_value_brl', 0)
        stock_value = report.get('stock_analysis', {}).get('total_value_brl', 0)
        fund_value = fund_analysis.get('metrics', {}).get('total_value', 0)
        total_portfolio_value = crypto_value + stock_value + fund_value
        
        report['portfolio_summary'] = {
            'total_value_brl': total_portfolio_value,
            'crypto_value': crypto_value,
            'stock_value': stock_value,
            'fund_value': fund_value,
            'crypto_weight': crypto_value / total_portfolio_value if total_portfolio_value > 0 else 0,
            'stock_weight': stock_value / total_portfolio_value if total_portfolio_value > 0 else 0,
            'fund_weight': fund_value / total_portfolio_value if total_portfolio_value > 0 else 0
        }
        
        # Gerar insights temporais
        report['temporal_insights'] = self._generate_temporal_insights(report)
        
        return report
    
    def _generate_temporal_insights(self, report: dict) -> list:
        """Gera insights baseados na análise temporal"""
        insights = []
        
        # Insights de criptomoedas
        crypto_analysis = report.get('crypto_analysis')
        if crypto_analysis:
            monthly_summary = crypto_analysis.get('temporal_data', {}).get('summary', {}).get('monthly_stats', {})
            if monthly_summary:
                avg_monthly = monthly_summary.get('avg_return', 0)
                if avg_monthly > 0.05:  # 5% ao mês
                    insights.append("🪙 Criptomoedas mostraram forte performance mensal nos últimos 5 anos")
                elif avg_monthly < -0.02:  # -2% ao mês
                    insights.append("⚠️ Criptomoedas tiveram performance negativa mensal nos últimos 5 anos")
        
        # Insights de ações
        stock_analysis = report.get('stock_analysis')
        if stock_analysis:
            annual_summary = stock_analysis.get('temporal_data', {}).get('summary', {}).get('annual_stats', {})
            if annual_summary:
                positive_years = annual_summary.get('positive_years', 0)
                total_years = annual_summary.get('total_years', 0)
                if positive_years / total_years > 0.8:  # 80% dos anos positivos
                    insights.append("📈 Ações tiveram consistência positiva anual nos últimos 5 anos")
        
        # Insights de fundos
        fund_analysis = report.get('fund_analysis')
        if fund_analysis:
            temporal_data = fund_analysis.get('temporal_analysis', {})
            monthly_stats = temporal_data.get('monthly_stats', {})
            if monthly_stats:
                volatility = monthly_stats.get('volatility', 0)
                if volatility < 0.02:  # Baixa volatilidade
                    insights.append("🏦 Fundos mostraram baixa volatilidade mensal, indicando estabilidade")
        
        # Insights de alocação
        portfolio_summary = report.get('portfolio_summary', {})
        if portfolio_summary:
            crypto_weight = portfolio_summary.get('crypto_weight', 0)
            if crypto_weight > 0.5:  # Mais de 50% em crypto
                insights.append("⚠️ Alta concentração em criptomoedas - considere diversificar")
            elif crypto_weight < 0.1:  # Menos de 10% em crypto
                insights.append("💡 Baixa exposição em criptomoedas - considere aumentar alocação")
        
        return insights
    
    def print_temporal_analysis(self, report: dict):
        """Imprime análise temporal de forma organizada"""
        
        period_info = report.get('period_info', {})
        
        print("\n" + "="*100)
        print("📊 RELATÓRIO TEMPORAL COMPLETO DE ANÁLISE DE PORTFÓLIO")
        print("="*100)
        print(f"📅 PERÍODO DE ANÁLISE: {period_info.get('description', '')}")
        print(f"📆 DE: {period_info.get('start_date', '')} A: {period_info.get('end_date', '')}")
        print(f"🕐 DATA DA ANÁLISE: {report.get('analysis_date', '')}")
        print("="*100)
        
        # Resumo de mercado
        market_summary = report.get('market_summary', {})
        print(f"\n🌍 RESUMO DE MERCADO ATUAL:")
        print(f"Câmbio USD/BRL: R$ {market_summary.get('exchange_rate_usd_brl', 0):.4f}")
        print(f"Bitcoin: R$ {market_summary.get('bitcoin_price_brl', 0):,.2f} ({market_summary.get('bitcoin_change_24h', 0):+.2f}%)")
        print(f"Ibovespa: {market_summary.get('ibovespa_price', 0):,.2f} ({market_summary.get('ibovespa_change_24h', 0):+.2f}%)")
        
        # Resumo do portfólio
        portfolio_summary = report.get('portfolio_summary', {})
        if portfolio_summary:
            print(f"\n💰 RESUMO DO PORTFÓLIO:")
            print(f"Valor Total: R$ {portfolio_summary.get('total_value_brl', 0):,.2f}")
            print(f"  Criptomoedas: R$ {portfolio_summary.get('crypto_value', 0):,.2f} ({portfolio_summary.get('crypto_weight', 0):.1%})")
            print(f"  Ações: R$ {portfolio_summary.get('stock_value', 0):,.2f} ({portfolio_summary.get('stock_weight', 0):.1%})")
            print(f"  Fundos: R$ {portfolio_summary.get('fund_value', 0):,.2f} ({portfolio_summary.get('fund_weight', 0):.1%})")
        
        # Análise temporal de criptomoedas
        crypto_analysis = report.get('crypto_analysis')
        if crypto_analysis:
            print(f"\n🪙 ANÁLISE TEMPORAL DE CRIPTOMOEDAS:")
            print(f"Valor Total: R$ {crypto_analysis.get('total_value_brl', 0):,.2f}")
            print(f"Retorno Total: {crypto_analysis.get('performance_metrics', {}).get('total_return_pct', 0):+.2f}%")
            
            temporal_summary = crypto_analysis.get('temporal_data', {}).get('summary', {})
            if temporal_summary:
                monthly_stats = temporal_summary.get('monthly_stats', {})
                annual_stats = temporal_summary.get('annual_stats', {})
                
                print(f"📊 ESTATÍSTICAS TEMPORAIS:")
                print(f"  Retorno Mensal Médio: {monthly_stats.get('avg_return', 0):.2%}")
                print(f"  Volatilidade Mensal: {monthly_stats.get('volatility', 0):.2%}")
                print(f"  Melhor Mês: {monthly_stats.get('best_month', 0):.2%}")
                print(f"  Pior Mês: {monthly_stats.get('worst_month', 0):.2%}")
                print(f"  Retorno Anual Médio: {annual_stats.get('avg_return', 0):.2%}")
                print(f"  Anos Positivos: {annual_stats.get('positive_years', 0)}/{annual_stats.get('total_years', 0)}")
            
            for symbol, data in crypto_analysis.get('assets', {}).items():
                print(f"  {symbol}: R$ {data['current_value_brl']:,.2f} ({data['profit_loss_pct']:+.2f}%)")
        
        # Análise temporal de ações
        stock_analysis = report.get('stock_analysis')
        if stock_analysis:
            print(f"\n📈 ANÁLISE TEMPORAL DE AÇÕES:")
            print(f"Valor Total: R$ {stock_analysis.get('total_value_brl', 0):,.2f}")
            
            temporal_summary = stock_analysis.get('temporal_data', {}).get('summary', {})
            if temporal_summary:
                monthly_stats = temporal_summary.get('monthly_stats', {})
                annual_stats = temporal_summary.get('annual_stats', {})
                
                print(f"📊 ESTATÍSTICAS TEMPORAIS:")
                print(f"  Retorno Mensal Médio: {monthly_stats.get('avg_return', 0):.2%}")
                print(f"  Volatilidade Mensal: {monthly_stats.get('volatility', 0):.2%}")
                print(f"  Retorno Anual Médio: {annual_stats.get('avg_return', 0):.2%}")
                print(f"  Anos Positivos: {annual_stats.get('positive_years', 0)}/{annual_stats.get('total_years', 0)}")
            
            for symbol, data in stock_analysis.get('assets', {}).items():
                print(f"  {symbol}: R$ {data['current_value']:,.2f} ({data['profit_loss_pct']:+.2f}%)")
        
        # Análise temporal de fundos
        fund_analysis = report.get('fund_analysis')
        if fund_analysis:
            print(f"\n🏦 ANÁLISE TEMPORAL DE FUNDOS:")
            print(f"Valor Total: R$ {fund_analysis.get('metrics', {}).get('total_value', 0):,.2f}")
            print(f"Retorno Total: {fund_analysis.get('metrics', {}).get('total_return', 0):.2%}")
            
            temporal_data = fund_analysis.get('temporal_analysis', {})
            if temporal_data:
                monthly_stats = temporal_data.get('monthly_stats', {})
                annual_stats = temporal_data.get('annual_stats', {})
                
                print(f"📊 ESTATÍSTICAS TEMPORAIS:")
                print(f"  Retorno Mensal Médio: {monthly_stats.get('avg_return', 0):.2%}")
                print(f"  Volatilidade Mensal: {monthly_stats.get('volatility', 0):.2%}")
                print(f"  Retorno Anual Médio: {annual_stats.get('avg_return', 0):.2%}")
                print(f"  Anos Positivos: {annual_stats.get('positive_years', 0)}/{annual_stats.get('total_years', 0)}")
            
            for fund in fund_analysis.get('fundos', []):
                print(f"  {fund['nome']} ({fund['categoria']}):")
                print(f"    Valor: R$ {fund['valor_atual']:,.2f}")
                print(f"    Retorno: {fund['retorno_anual']:.2%}")
                print(f"    Sharpe: {fund['sharpe_ratio']:.2f}")
        
        # Insights temporais
        insights = report.get('temporal_insights', [])
        if insights:
            print(f"\n💡 INSIGHTS TEMPORAIS:")
            for i, insight in enumerate(insights, 1):
                print(f"  {i}. {insight}")
        
        print("\n" + "="*100)

def main():
    """Função principal"""
    print("🚀 INICIANDO ANÁLISE TEMPORAL COMPLETA DE PORTFÓLIO")
    print("="*80)
    print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}")
    
    # Criar analisador temporal
    analyzer = TemporalPortfolioAnalyzer()
    
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
        '^BVSP': {'quantity': 1, 'entry_price': 130000}
    }
    
    # Gerar relatório temporal completo (últimos 5 anos)
    report = analyzer.generate_comprehensive_temporal_report(
        crypto_portfolio=crypto_portfolio,
        stock_portfolio=stock_portfolio,
        period='5_years'
    )
    
    # Imprimir análise
    analyzer.print_temporal_analysis(report)
    
    # Salvar relatório
    filename = f"temporal_portfolio_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Relatório temporal salvo em: {filename}")
    except Exception as e:
        print(f"\n❌ Erro ao salvar relatório: {e}")
    
    print("\n🎉 Análise temporal concluída!")

if __name__ == "__main__":
    main() 