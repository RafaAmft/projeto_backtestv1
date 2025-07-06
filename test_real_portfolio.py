#!/usr/bin/env python3
"""
Teste Real de Análise de Portfólio
==================================

Este script permite testar a análise com CNPJs reais de fundos e ativos específicos
fornecidos pelo usuário.
"""

import sys
import os
import json
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.market_indices import market_indices
from examples.temporal_portfolio_analysis import TemporalPortfolioAnalyzer

class RealPortfolioTester:
    """
    Testador de portfólio real com dados fornecidos pelo usuário
    """
    
    def __init__(self):
        self.analyzer = TemporalPortfolioAnalyzer()
        self.test_data = {
            'funds': [],
            'crypto': {},
            'stocks': {},
            'period': '5_years'
        }
    
    def add_real_fund(self, cnpj: str, name: str, category: str, current_value: float, entry_value: float):
        """
        Adiciona um fundo real à análise
        
        Args:
            cnpj: CNPJ do fundo
            name: Nome do fundo
            category: Categoria (Renda Fixa, Renda Variável, etc.)
            current_value: Valor atual investido
            entry_value: Valor inicial investido
        """
        fund = {
            'cnpj': cnpj,
            'nome': name,
            'categoria': category,
            'valor_atual': current_value,
            'valor_inicial': entry_value,
            'retorno_total': ((current_value - entry_value) / entry_value) * 100 if entry_value > 0 else 0
        }
        
        self.test_data['funds'].append(fund)
        print(f"✅ Fundo adicionado: {name} (CNPJ: {cnpj})")
    
    def add_real_crypto(self, symbol: str, quantity: float, entry_price: float):
        """
        Adiciona uma criptomoeda real à análise
        
        Args:
            symbol: Símbolo da cripto (ex: BTC, ETH)
            quantity: Quantidade
            entry_price: Preço de entrada em USD
        """
        self.test_data['crypto'][symbol] = {
            'quantity': quantity,
            'entry_price': entry_price
        }
        print(f"✅ Criptomoeda adicionada: {symbol} ({quantity} unidades a ${entry_price})")
    
    def add_real_stock(self, symbol: str, quantity: int, entry_price: float):
        """
        Adiciona uma ação real à análise
        
        Args:
            symbol: Símbolo da ação (ex: PETR4.SA, VALE3.SA)
            quantity: Quantidade de ações
            entry_price: Preço de entrada em BRL
        """
        self.test_data['stocks'][symbol] = {
            'quantity': quantity,
            'entry_price': entry_price
        }
        print(f"✅ Ação adicionada: {symbol} ({quantity} ações a R$ {entry_price})")
    
    def set_analysis_period(self, period: str):
        """
        Define o período de análise
        
        Args:
            period: '1_month', '3_months', '6_months', '1_year', '3_years', '5_years'
        """
        self.test_data['period'] = period
        print(f"✅ Período de análise definido: {period}")
    
    def run_real_analysis(self) -> dict:
        """
        Executa análise real do portfólio
        """
        print("\n" + "="*80)
        print("🚀 INICIANDO ANÁLISE REAL DE PORTFÓLIO")
        print("="*80)
        print(f"📅 Data/Hora: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}")
        print(f"⏱️ Período: {self.test_data['period']}")
        print("="*80)
        
        # Preparar dados para análise
        crypto_portfolio = self.test_data['crypto'] if self.test_data['crypto'] else None
        stock_portfolio = self.test_data['stocks'] if self.test_data['stocks'] else None
        
        # Gerar relatório temporal
        report = self.analyzer.generate_comprehensive_temporal_report(
            crypto_portfolio=crypto_portfolio,
            stock_portfolio=stock_portfolio,
            period=self.test_data['period']
        )
        
        # Adicionar análise de fundos reais
        if self.test_data['funds']:
            fund_analysis = self._analyze_real_funds()
            report['real_fund_analysis'] = fund_analysis
            
            # Atualizar resumo do portfólio
            fund_value = sum(fund['valor_atual'] for fund in self.test_data['funds'])
            total_value = report['portfolio_summary']['total_value_brl'] + fund_value
            
            report['portfolio_summary']['fund_value'] = fund_value
            report['portfolio_summary']['total_value_brl'] = total_value
            report['portfolio_summary']['fund_weight'] = fund_value / total_value if total_value > 0 else 0
        
        return report
    
    def _analyze_real_funds(self) -> dict:
        """
        Analisa fundos reais fornecidos pelo usuário
        """
        print(f"\n🏦 Analisando {len(self.test_data['funds'])} fundos reais...")
        
        total_value = sum(fund['valor_atual'] for fund in self.test_data['funds'])
        total_entry = sum(fund['valor_inicial'] for fund in self.test_data['funds'])
        total_return = ((total_value - total_entry) / total_entry) * 100 if total_entry > 0 else 0
        
        # Calcular métricas por categoria
        categories = {}
        for fund in self.test_data['funds']:
            cat = fund['categoria']
            if cat not in categories:
                categories[cat] = {'count': 0, 'total_value': 0, 'total_return': 0}
            
            categories[cat]['count'] += 1
            categories[cat]['total_value'] += fund['valor_atual']
            categories[cat]['total_return'] += fund['retorno_total']
        
        # Calcular médias por categoria
        for cat in categories:
            count = categories[cat]['count']
            categories[cat]['avg_return'] = categories[cat]['total_return'] / count if count > 0 else 0
            categories[cat]['weight'] = categories[cat]['total_value'] / total_value if total_value > 0 else 0
        
        analysis = {
            'total_funds': len(self.test_data['funds']),
            'total_value': total_value,
            'total_entry_value': total_entry,
            'total_return_pct': total_return,
            'funds': self.test_data['funds'],
            'categories': categories,
            'diversification_score': len(categories) / 3 if len(categories) <= 3 else 1.0,  # Score de 0-1
            'analysis_date': datetime.now().strftime('%d/%m/%Y às %H:%M:%S')
        }
        
        return analysis
    
    def print_real_analysis(self, report: dict):
        """
        Imprime análise real de forma organizada
        """
        print("\n" + "="*100)
        print("📊 RELATÓRIO REAL DE ANÁLISE DE PORTFÓLIO")
        print("="*100)
        
        # Informações do período
        period_info = report.get('period_info', {})
        print(f"📅 PERÍODO DE ANÁLISE: {period_info.get('description', '')}")
        print(f"📆 DE: {period_info.get('start_date', '')} A: {period_info.get('end_date', '')}")
        print(f"🕐 DATA DA ANÁLISE: {report.get('analysis_date', '')}")
        print("="*100)
        
        # Resumo do portfólio
        portfolio_summary = report.get('portfolio_summary', {})
        if portfolio_summary:
            print(f"\n💰 RESUMO DO PORTFÓLIO REAL:")
            print(f"Valor Total: R$ {portfolio_summary.get('total_value_brl', 0):,.2f}")
            
            crypto_value = portfolio_summary.get('crypto_value', 0)
            stock_value = portfolio_summary.get('stock_value', 0)
            fund_value = portfolio_summary.get('fund_value', 0)
            
            if crypto_value > 0:
                print(f"  Criptomoedas: R$ {crypto_value:,.2f} ({portfolio_summary.get('crypto_weight', 0):.1%})")
            if stock_value > 0:
                print(f"  Ações: R$ {stock_value:,.2f} ({portfolio_summary.get('stock_weight', 0):.1%})")
            if fund_value > 0:
                print(f"  Fundos: R$ {fund_value:,.2f} ({portfolio_summary.get('fund_weight', 0):.1%})")
        
        # Análise de fundos reais
        fund_analysis = report.get('real_fund_analysis')
        if fund_analysis:
            print(f"\n🏦 ANÁLISE DE FUNDOS REAIS:")
            print(f"Total de Fundos: {fund_analysis['total_funds']}")
            print(f"Valor Total: R$ {fund_analysis['total_value']:,.2f}")
            print(f"Retorno Total: {fund_analysis['total_return_pct']:+.2f}%")
            print(f"Score de Diversificação: {fund_analysis['diversification_score']:.2f}/1.0")
            
            # Por categoria
            categories = fund_analysis.get('categories', {})
            if categories:
                print(f"\n📊 ANÁLISE POR CATEGORIA:")
                for cat, data in categories.items():
                    print(f"  {cat}:")
                    print(f"    Quantidade: {data['count']} fundos")
                    print(f"    Valor Total: R$ {data['total_value']:,.2f}")
                    print(f"    Retorno Médio: {data['avg_return']:+.2f}%")
                    print(f"    Peso no Portfólio: {data['weight']:.1%}")
            
            # Detalhes dos fundos
            print(f"\n📋 DETALHES DOS FUNDOS:")
            for fund in fund_analysis['funds']:
                print(f"  {fund['nome']} ({fund['categoria']}):")
                print(f"    CNPJ: {fund['cnpj']}")
                print(f"    Valor Atual: R$ {fund['valor_atual']:,.2f}")
                print(f"    Valor Inicial: R$ {fund['valor_inicial']:,.2f}")
                print(f"    Retorno: {fund['retorno_total']:+.2f}%")
        
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
                print(f"  Retorno Anual Médio: {annual_stats.get('avg_return', 0):.2%}")
                print(f"  Anos Positivos: {annual_stats.get('positive_years', 0)}/{annual_stats.get('total_years', 0)}")
        
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
        
        # Insights
        insights = report.get('temporal_insights', [])
        if insights:
            print(f"\n💡 INSIGHTS DA ANÁLISE:")
            for i, insight in enumerate(insights, 1):
                print(f"  {i}. {insight}")
        
        print("\n" + "="*100)

def main():
    """Função principal com exemplo de uso"""
    print("🧪 TESTE REAL DE ANÁLISE DE PORTFÓLIO")
    print("="*60)
    print("Este teste permite analisar um portfólio real com seus dados!")
    print("="*60)
    
    # Criar testador
    tester = RealPortfolioTester()
    
    # Exemplo: Adicionar fundos reais (você pode modificar estes dados)
    print("\n📋 ADICIONANDO FUNDOS REAIS:")
    tester.add_real_fund(
        cnpj="16916060000199",
        name="CAIXA INDEXA OURO FI FINANCEIRO MULTIMERCADO LP RL",
        category="Multimercado",
        current_value=50000.0,
        entry_value=45000.0
    )
    
    tester.add_real_fund(
        cnpj="00000000000191",
        name="FUNDO EXEMPLO RENDA FIXA",
        category="Renda Fixa",
        current_value=30000.0,
        entry_value=28000.0
    )
    
    # Exemplo: Adicionar criptomoedas reais
    print("\n🪙 ADICIONANDO CRIPTOMOEDAS REAIS:")
    tester.add_real_crypto("BTC", 0.1, 45000)  # 0.1 BTC comprado a $45.000
    tester.add_real_crypto("ETH", 2.0, 2800)   # 2 ETH comprados a $2.800
    
    # Exemplo: Adicionar ações reais
    print("\n📈 ADICIONANDO AÇÕES REAIS:")
    tester.add_real_stock("PETR4.SA", 100, 30.0)  # 100 ações PETR4 a R$ 30
    tester.add_real_stock("VALE3.SA", 50, 70.0)   # 50 ações VALE3 a R$ 70
    
    # Definir período de análise
    tester.set_analysis_period('5_years')
    
    # Executar análise real
    report = tester.run_real_analysis()
    
    # Imprimir resultados
    tester.print_real_analysis(report)
    
    # Salvar relatório
    filename = f"real_portfolio_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Relatório real salvo em: {filename}")
    except Exception as e:
        print(f"\n❌ Erro ao salvar relatório: {e}")
    
    print("\n🎉 Teste real concluído!")
    print("\n💡 Para usar seus próprios dados, modifique os valores no script:")
    print("   - CNPJs dos fundos")
    print("   - Quantidades e preços de entrada das criptomoedas")
    print("   - Quantidades e preços de entrada das ações")

if __name__ == "__main__":
    main() 