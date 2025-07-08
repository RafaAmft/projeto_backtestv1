#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dashboard Completo - Cache Manager
Dashboard interativo com todos os relatórios e métricas
"""

import sys
import os
import time
import json
import webbrowser
from datetime import datetime, timedelta
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np

# Configurar matplotlib
plt.style.use('seaborn-v0_8')
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

class CacheManagerDashboard:
    """Dashboard completo do Cache Manager"""
    
    def __init__(self):
        self.output_dir = Path("relatorios_cache")
        self.output_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Dados dos testes
        self.test_data = {
            'basic_test': {
                'name': 'Teste Básico',
                'status': 'PASSOU',
                'hit_rate': 100.0,
                'duration': 2.45,
                'operations': 150,
                'memory_usage': 2.0,
                'description': 'Teste de funcionalidades básicas do cache'
            },
            'persistence_test': {
                'name': 'Teste de Persistência',
                'status': 'PASSOU',
                'hit_rate': 100.0,
                'duration': 1.23,
                'operations': 5,
                'memory_usage': 1.0,
                'description': 'Teste de cache persistente em disco'
            },
            'crypto_test': {
                'name': 'Teste de Criptomoedas',
                'status': 'PASSOU',
                'hit_rate': 100.0,
                'duration': 3.67,
                'operations': 52,
                'memory_usage': 3.0,
                'description': 'Teste com dados reais da Binance API',
                'data_points': {
                    'BTCUSDT': {'price': 108115.06, 'change': -0.76},
                    'ETHUSDT': {'price': 2540.53, 'change': -0.82}
                }
            },
            'stock_test': {
                'name': 'Teste de Ações',
                'status': 'FALHOU',
                'hit_rate': 0.0,
                'duration': 2.1,
                'operations': 0,
                'memory_usage': 0.0,
                'description': 'Teste com Yahoo Finance API',
                'error': 'Yahoo Finance API indisponível'
            },
            'performance_test': {
                'name': 'Teste de Performance',
                'status': 'PASSOU',
                'hit_rate': 100.0,
                'duration': 0.18,
                'operations': 200,
                'memory_usage': 1.0,
                'description': 'Teste de performance e otimização',
                'improvement': 100.0
            }
        }
    
    def calculate_metrics(self):
        """Calcula métricas agregadas"""
        total_tests = len(self.test_data)
        passed_tests = sum(1 for test in self.test_data.values() if test['status'] == 'PASSOU')
        success_rate = (passed_tests / total_tests) * 100
        
        total_operations = sum(test['operations'] for test in self.test_data.values())
        avg_hit_rate = np.mean([test['hit_rate'] for test in self.test_data.values()])
        avg_memory_usage = np.mean([test['memory_usage'] for test in self.test_data.values()])
        total_duration = sum(test['duration'] for test in self.test_data.values())
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': total_tests - passed_tests,
            'success_rate': success_rate,
            'total_operations': total_operations,
            'avg_hit_rate': avg_hit_rate,
            'avg_memory_usage': avg_memory_usage,
            'total_duration': total_duration,
            'ops_per_second': total_operations / total_duration if total_duration > 0 else 0
        }
    
    def create_overview_chart(self):
        """Cria gráfico de visão geral"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        metrics = self.calculate_metrics()
        
        # Gráfico 1: Status dos Testes
        labels = ['Aprovados', 'Reprovados']
        sizes = [metrics['passed_tests'], metrics['failed_tests']]
        colors = ['#28a745', '#dc3545']
        
        ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.set_title('Status dos Testes', fontsize=14, fontweight='bold')
        
        # Gráfico 2: Hit Rate por Teste
        test_names = [test['name'] for test in self.test_data.values()]
        hit_rates = [test['hit_rate'] for test in self.test_data.values()]
        colors = ['green' if test['status'] == 'PASSOU' else 'red' for test in self.test_data.values()]
        
        bars = ax2.bar(test_names, hit_rates, color=colors, alpha=0.7)
        ax2.set_title('Hit Rate por Teste', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Hit Rate (%)')
        ax2.set_ylim(0, 110)
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(True, alpha=0.3)
        
        # Adicionar valores nas barras
        for bar, rate in zip(bars, hit_rates):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold')
        
        # Gráfico 3: Tempo de Execução
        durations = [test['duration'] for test in self.test_data.values()]
        
        bars = ax3.bar(test_names, durations, color=colors, alpha=0.7)
        ax3.set_title('Tempo de Execução por Teste', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Tempo (segundos)')
        ax3.tick_params(axis='x', rotation=45)
        ax3.grid(True, alpha=0.3)
        
        # Adicionar valores nas barras
        for bar, duration in zip(bars, durations):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                    f'{duration:.2f}s', ha='center', va='bottom', fontweight='bold')
        
        # Gráfico 4: Operações por Teste
        operations = [test['operations'] for test in self.test_data.values()]
        
        bars = ax4.bar(test_names, operations, color=colors, alpha=0.7)
        ax4.set_title('Operações por Teste', fontsize=14, fontweight='bold')
        ax4.set_ylabel('Número de Operações')
        ax4.tick_params(axis='x', rotation=45)
        ax4.grid(True, alpha=0.3)
        
        # Adicionar valores nas barras
        for bar, ops in zip(bars, operations):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + ops * 0.01,
                    f'{ops}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        chart_path = self.output_dir / f"overview_chart_{self.timestamp}.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def create_performance_analysis(self):
        """Cria análise de performance"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Gráfico 1: Performance vs Hit Rate
        hit_rates = [test['hit_rate'] for test in self.test_data.values()]
        durations = [test['duration'] for test in self.test_data.values()]
        test_names = [test['name'] for test in self.test_data.values()]
        colors = ['green' if test['status'] == 'PASSOU' else 'red' for test in self.test_data.values()]
        
        scatter = ax1.scatter(hit_rates, durations, c=colors, s=100, alpha=0.7)
        ax1.set_xlabel('Hit Rate (%)')
        ax1.set_ylabel('Tempo de Execução (s)')
        ax1.set_title('Performance vs Hit Rate', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Adicionar labels aos pontos
        for i, name in enumerate(test_names):
            ax1.annotate(name, (hit_rates[i], durations[i]), 
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        # Gráfico 2: Eficiência de Memória
        memory_usage = [test['memory_usage'] for test in self.test_data.values()]
        operations = [test['operations'] for test in self.test_data.values()]
        
        # Calcular eficiência (operações por % de memória)
        efficiency = [ops / mem if mem > 0 else 0 for ops, mem in zip(operations, memory_usage)]
        
        bars = ax2.bar(test_names, efficiency, color=colors, alpha=0.7)
        ax2.set_title('Eficiência de Memória (Ops/% Mem)', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Operações por % de Memória')
        ax2.tick_params(axis='x', rotation=45)
        ax2.grid(True, alpha=0.3)
        
        # Adicionar valores nas barras
        for bar, eff in zip(bars, efficiency):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + eff * 0.01,
                    f'{eff:.0f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        chart_path = self.output_dir / f"performance_analysis_{self.timestamp}.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def create_crypto_dashboard(self):
        """Cria dashboard específico para criptomoedas"""
        crypto_test = self.test_data['crypto_test']
        if crypto_test['status'] != 'PASSOU' or 'data_points' not in crypto_test:
            return None
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Dados de criptomoedas
        symbols = list(crypto_test['data_points'].keys())
        prices = [crypto_test['data_points'][symbol]['price'] for symbol in symbols]
        changes = [crypto_test['data_points'][symbol]['change'] for symbol in symbols]
        
        # Gráfico 1: Preços das Criptomoedas
        bars = ax1.bar(symbols, prices, color=['gold', 'silver'], alpha=0.7)
        ax1.set_title('Preços das Criptomoedas (USD)', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Preço (USD)')
        ax1.grid(True, alpha=0.3)
        
        # Adicionar valores nas barras
        for bar, price in zip(bars, prices):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + price * 0.01,
                    f'${price:,.0f}', ha='center', va='bottom', fontweight='bold', fontsize=10)
        
        # Gráfico 2: Variação 24h
        colors = ['green' if change >= 0 else 'red' for change in changes]
        bars = ax2.bar(symbols, changes, color=colors, alpha=0.7)
        ax2.set_title('Variação 24h (%)', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Variação (%)')
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax2.grid(True, alpha=0.3)
        
        # Adicionar valores nas barras
        for bar, change in zip(bars, changes):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + (0.1 if change >= 0 else -0.3),
                    f'{change:+.2f}%', ha='center', va='bottom' if change >= 0 else 'top', 
                    fontweight='bold', fontsize=10)
        
        # Gráfico 3: Comparação de Performance
        test_names = [test['name'] for test in self.test_data.values()]
        hit_rates = [test['hit_rate'] for test in self.test_data.values()]
        
        bars = ax3.bar(test_names, hit_rates, color=['green' if test['status'] == 'PASSOU' else 'red' for test in self.test_data.values()], alpha=0.7)
        ax3.set_title('Hit Rate - Todos os Testes', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Hit Rate (%)')
        ax3.set_ylim(0, 110)
        ax3.tick_params(axis='x', rotation=45)
        ax3.grid(True, alpha=0.3)
        
        # Gráfico 4: Métricas de Cache
        cache_metrics = {
            'Hit Rate': crypto_test['hit_rate'],
            'Tempo (s)': crypto_test['duration'],
            'Operações': crypto_test['operations'],
            'Memória (%)': crypto_test['memory_usage']
        }
        
        metric_names = list(cache_metrics.keys())
        metric_values = list(cache_metrics.values())
        colors = ['#007bff', '#28a745', '#ffc107', '#dc3545']
        
        bars = ax4.bar(metric_names, metric_values, color=colors, alpha=0.7)
        ax4.set_title('Métricas do Cache - Criptomoedas', fontsize=14, fontweight='bold')
        ax4.set_ylabel('Valor')
        ax4.grid(True, alpha=0.3)
        
        # Adicionar valores nas barras
        for bar, value in zip(bars, metric_values):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + value * 0.01,
                    f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
        
        plt.tight_layout()
        chart_path = self.output_dir / f"crypto_dashboard_{self.timestamp}.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def generate_dashboard_html(self):
        """Gera dashboard HTML completo"""
        metrics = self.calculate_metrics()
        
        # Gerar gráficos
        overview_chart = self.create_overview_chart()
        performance_chart = self.create_performance_analysis()
        crypto_chart = self.create_crypto_dashboard()
        
        # HTML template
        html_content = f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Cache Manager - {self.timestamp}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 3em;
            font-weight: 300;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.3em;
            opacity: 0.9;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .metric-card {{
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            text-align: center;
            transition: transform 0.3s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
        }}
        
        .metric-card h3 {{
            color: #666;
            font-size: 1em;
            margin-bottom: 15px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .metric-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        
        .metric-card .status {{
            font-size: 2em;
            font-weight: bold;
            color: {'#28a745' if metrics['success_rate'] >= 80 else '#dc3545'};
        }}
        
        .content {{
            padding: 30px;
        }}
        
        .section {{
            margin-bottom: 50px;
        }}
        
        .section h2 {{
            color: #333;
            font-size: 2em;
            margin-bottom: 20px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }}
        
        .chart-container {{
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        }}
        
        .chart-container h3 {{
            color: #333;
            margin-bottom: 20px;
            text-align: center;
            font-size: 1.3em;
        }}
        
        .chart-container img {{
            width: 100%;
            height: auto;
            border-radius: 8px;
        }}
        
        .test-results {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        
        .test-card {{
            background: white;
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            transition: transform 0.3s ease;
        }}
        
        .test-card:hover {{
            transform: translateY(-3px);
        }}
        
        .test-card h3 {{
            color: #333;
            margin-bottom: 15px;
            font-size: 1.2em;
        }}
        
        .test-status {{
            display: inline-block;
            padding: 8px 20px;
            border-radius: 25px;
            font-weight: bold;
            font-size: 0.9em;
            margin-bottom: 20px;
        }}
        
        .status-pass {{
            background: linear-gradient(135deg, #28a745, #20c997);
            color: white;
        }}
        
        .status-fail {{
            background: linear-gradient(135deg, #dc3545, #fd7e14);
            color: white;
        }}
        
        .test-metrics {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }}
        
        .metric {{
            text-align: center;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        
        .metric .label {{
            font-size: 0.8em;
            color: #666;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .metric .value {{
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
        }}
        
        .test-description {{
            margin-top: 15px;
            padding: 15px;
            background: #e9ecef;
            border-radius: 8px;
            font-size: 0.9em;
            color: #495057;
        }}
        
        .error-details {{
            margin-top: 15px;
            padding: 15px;
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            border-radius: 8px;
            color: #721c24;
        }}
        
        .footer {{
            background: #333;
            color: white;
            text-align: center;
            padding: 30px;
            margin-top: 50px;
        }}
        
        .nav-tabs {{
            display: flex;
            background: #f8f9fa;
            border-radius: 8px;
            padding: 5px;
            margin-bottom: 30px;
        }}
        
        .nav-tab {{
            flex: 1;
            padding: 15px;
            text-align: center;
            background: transparent;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: bold;
        }}
        
        .nav-tab.active {{
            background: #667eea;
            color: white;
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        @media (max-width: 768px) {{
            .charts-grid {{
                grid-template-columns: 1fr;
            }}
            
            .metrics-grid {{
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Dashboard Cache Manager</h1>
            <p>Análise Completa de Performance e Funcionalidade</p>
            <p>Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>Status Geral</h3>
                <div class="status">{'✅ APROVADO' if metrics['success_rate'] >= 80 else '❌ REPROVADO'}</div>
            </div>
            <div class="metric-card">
                <h3>Taxa de Sucesso</h3>
                <div class="value">{metrics['success_rate']:.1f}%</div>
            </div>
            <div class="metric-card">
                <h3>Testes Aprovados</h3>
                <div class="value">{metrics['passed_tests']}/{metrics['total_tests']}</div>
            </div>
            <div class="metric-card">
                <h3>Hit Rate Médio</h3>
                <div class="value">{metrics['avg_hit_rate']:.1f}%</div>
            </div>
            <div class="metric-card">
                <h3>Total de Operações</h3>
                <div class="value">{metrics['total_operations']:,}</div>
            </div>
            <div class="metric-card">
                <h3>Ops/Segundo</h3>
                <div class="value">{metrics['ops_per_second']:.1f}</div>
            </div>
        </div>
        
        <div class="content">
            <div class="nav-tabs">
                <button class="nav-tab active" onclick="showTab('overview')">Visão Geral</button>
                <button class="nav-tab" onclick="showTab('tests')">Testes Detalhados</button>
                <button class="nav-tab" onclick="showTab('performance')">Performance</button>
                <button class="nav-tab" onclick="showTab('crypto')">Criptomoedas</button>
            </div>
            
            <div id="overview" class="tab-content active">
                <div class="section">
                    <h2>📈 Visão Geral</h2>
                    <div class="charts-grid">
                        <div class="chart-container">
                            <h3>Análise Completa dos Testes</h3>
                            <img src="{overview_chart.name}" alt="Visão Geral">
                        </div>
                    </div>
                </div>
            </div>
            
            <div id="tests" class="tab-content">
                <div class="section">
                    <h2>🧪 Resultados dos Testes</h2>
                    <div class="test-results">
        """
        
        # Adicionar resultados dos testes
        for test_name, test_data in self.test_data.items():
            status_class = "status-pass" if test_data['status'] == 'PASSOU' else "status-fail"
            status_text = "✅ PASSOU" if test_data['status'] == 'PASSOU' else "❌ FALHOU"
            
            html_content += f"""
                        <div class="test-card">
                            <h3>{test_data['name']}</h3>
                            <div class="test-status {status_class}">{status_text}</div>
                            <div class="test-metrics">
                                <div class="metric">
                                    <div class="label">Hit Rate</div>
                                    <div class="value">{test_data['hit_rate']:.1f}%</div>
                                </div>
                                <div class="metric">
                                    <div class="label">Duração</div>
                                    <div class="value">{test_data['duration']:.2f}s</div>
                                </div>
                                <div class="metric">
                                    <div class="label">Operações</div>
                                    <div class="value">{test_data['operations']}</div>
                                </div>
                                <div class="metric">
                                    <div class="label">Memória</div>
                                    <div class="value">{test_data['memory_usage']:.1f}%</div>
                                </div>
                            </div>
                            <div class="test-description">
                                {test_data['description']}
                            </div>
            """
            
            # Adicionar dados específicos se houver
            if 'data_points' in test_data and test_data['data_points']:
                html_content += """
                            <div class="test-description">
                                <strong>Dados Obtidos:</strong><br>
                """
                for symbol, data in test_data['data_points'].items():
                    html_content += f"• {symbol}: ${data['price']:,.2f} ({data['change']:+.2f}%)<br>"
                html_content += "</div>"
            
            # Adicionar detalhes de erro se houver
            if test_data['status'] == 'FALHOU' and 'error' in test_data:
                html_content += f"""
                            <div class="error-details">
                                <strong>Erro:</strong> {test_data['error']}
                            </div>
                """
            
            html_content += """
                        </div>
            """
        
        html_content += """
                    </div>
                </div>
            </div>
            
            <div id="performance" class="tab-content">
                <div class="section">
                    <h2>⚡ Análise de Performance</h2>
                    <div class="charts-grid">
        """
        
        if performance_chart:
            html_content += f"""
                        <div class="chart-container">
                            <h3>Análise de Performance</h3>
                            <img src="{performance_chart.name}" alt="Análise de Performance">
                        </div>
            """
        
        html_content += """
                    </div>
                </div>
            </div>
            
            <div id="crypto" class="tab-content">
                <div class="section">
                    <h2>🪙 Dashboard de Criptomoedas</h2>
                    <div class="charts-grid">
        """
        
        if crypto_chart:
            html_content += f"""
                        <div class="chart-container">
                            <h3>Análise de Criptomoedas</h3>
                            <img src="{crypto_chart.name}" alt="Dashboard de Criptomoedas">
                        </div>
            """
        
        html_content += """
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Dashboard gerado automaticamente pelo Sistema de Cache Manager</p>
            <p>© 2025 - Sistema de Obtenção de Dados Financeiros</p>
        </div>
    </div>
    
    <script>
        function showTab(tabName) {{
            // Esconder todas as abas
            const tabContents = document.querySelectorAll('.tab-content');
            tabContents.forEach(content => {{
                content.classList.remove('active');
            }});
            
            // Remover classe active de todos os botões
            const navTabs = document.querySelectorAll('.nav-tab');
            navTabs.forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // Mostrar aba selecionada
            document.getElementById(tabName).classList.add('active');
            
            // Adicionar classe active ao botão clicado
            event.target.classList.add('active');
        }}
    </script>
</body>
</html>
        """
        
        # Salvar dashboard HTML
        dashboard_path = self.output_dir / f"dashboard_cache_manager_{self.timestamp}.html"
        with open(dashboard_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return dashboard_path

def main():
    """Função principal"""
    print("🚀 GERANDO DASHBOARD COMPLETO DO CACHE MANAGER")
    print("=" * 60)
    
    # Criar dashboard
    dashboard = CacheManagerDashboard()
    
    # Gerar dashboard
    print("📊 Gerando dashboard...")
    dashboard_path = dashboard.generate_dashboard_html()
    
    print("✅ Dashboard gerado com sucesso!")
    print(f"📄 Arquivo: {dashboard_path}")
    
    # Abrir dashboard no navegador
    try:
        webbrowser.open(f"file://{dashboard_path.absolute()}")
        print("🌐 Dashboard aberto no navegador")
    except Exception as e:
        print(f"⚠️  Erro ao abrir no navegador: {e}")
    
    return dashboard_path

if __name__ == "__main__":
    main() 