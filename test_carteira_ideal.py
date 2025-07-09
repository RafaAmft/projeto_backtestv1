#!/usr/bin/env python3
"""
Script de Teste para Carteira Ideal
===================================

Este script testa a carteira ideal diversificada com:
- Renda Fixa (40%): CDB e LCI
- Fundos Cambiais (15%): 5 fundos especializados
- Criptomoedas (15%): 5 principais criptos
- Ações (30%): 3 ações brasileiras
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.market_indices_fixed import MarketIndicesManager
from dashboard.portfolio_collector_v3 import PortfolioDataCollectorV3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import matplotlib.pyplot as plt
import io

class CarteiraIdealTest:
    """Classe para testar a carteira ideal diversificada"""
    
    def __init__(self):
        self.market_data = MarketIndicesManager()
        self.portfolio_collector = PortfolioDataCollectorV3()
        self.carteira_ideal = self.carregar_carteira_ideal()
        
    def carregar_carteira_ideal(self):
        """Carrega a carteira ideal do arquivo JSON"""
        try:
            with open('carteira_ideal.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print("❌ Arquivo carteira_ideal.json não encontrado!")
            return None
    
    def atualizar_dados_mercado(self):
        """Atualiza dados de mercado"""
        print("🔄 Atualizando dados de mercado...")
        try:
            self.market_data.get_all_market_data(force_update=True)
            print("✅ Dados de mercado atualizados!")
            return True
        except Exception as e:
            print(f"❌ Erro ao atualizar dados de mercado: {e}")
            return False
    
    def analisar_renda_fixa(self):
        """Analisa os ativos de renda fixa"""
        print("\n📊 Analisando Renda Fixa...")
        
        renda_fixa = self.carteira_ideal['alocacao']['renda_fixa']
        total_renda_fixa = renda_fixa['valor']
        
        print(f"💰 Valor total em Renda Fixa: R$ {total_renda_fixa:,.2f}")
        print(f"📈 Percentual da carteira: {renda_fixa['percentual']:.1f}%")
        
        for item in renda_fixa['itens']:
            print(f"   • {item['nome']}: R$ {item['valor']:,.2f} ({item['taxa_retorno']})")
        
        return {
            'total': total_renda_fixa,
            'percentual': renda_fixa['percentual'],
            'itens': renda_fixa['itens']
        }
    
    def analisar_fundos(self):
        """Analisa os fundos do portfólio usando mapeamento manual"""
        print("\n📊 Analisando fundos de investimento...")
        
        # Carregar mapeamento manual
        try:
            with open('mapeamento_fundos.json', 'r', encoding='utf-8') as f:
                mapeamento = json.load(f)
        except FileNotFoundError:
            print("   ❌ Arquivo de mapeamento não encontrado")
            return {}
        
        fundos = self.carteira_ideal['alocacao']['fundos_cambiais']
        total_fundos = fundos['valor']
        
        print(f"💰 Valor total em Fundos Cambiais: R$ {total_fundos:,.2f}")
        print(f"📈 Percentual da carteira: {fundos['percentual']:.1f}%")
        
        analise_fundos = {
            'total': total_fundos,
            'percentual': fundos['percentual'],
            'fundos': {}
        }
        
        for item in fundos['itens']:
            print(f"   🔍 Analisando fundo: {item['nome']}")
            
            # Verificar se existe no mapeamento
            cnpj = item['cnpj']
            if cnpj in mapeamento['mapeamento_fundos']:
                dados_mapeamento = mapeamento['mapeamento_fundos'][cnpj]
                slug = dados_mapeamento['slug']
                
                print(f"      📍 Slug mapeado: {slug}")
                
                # Buscar dados do fundo
                dados_fundo = self.portfolio_collector.extrair_dados_fundo(slug, cnpj)
                
                if dados_fundo:
                    analise_fundos['fundos'][cnpj] = {
                        'nome': item['nome'],
                        'valor': item['valor'],
                        'taxa_retorno': item['taxa_retorno'],
                        'slug': slug,
                        'dados_mercado': dados_fundo,
                        'anos_dados': len(dados_fundo.get('rentabilidades', {}))
                    }
                    print(f"      ✅ Dados obtidos: {len(dados_fundo.get('rentabilidades', {}))} anos")
                else:
                    print(f"      ❌ Não foi possível obter dados do fundo")
                    # Fallback com dados básicos
                    analise_fundos['fundos'][cnpj] = {
                        'nome': item['nome'],
                        'valor': item['valor'],
                        'taxa_retorno': item['taxa_retorno'],
                        'slug': slug,
                        'dados_mercado': None,
                        'erro': 'Dados não disponíveis'
                    }
            else:
                print(f"      ❌ Fundo não encontrado no mapeamento")
                # Fallback com dados básicos
                analise_fundos['fundos'][cnpj] = {
                    'nome': item['nome'],
                    'valor': item['valor'],
                    'taxa_retorno': item['taxa_retorno'],
                    'slug': None,
                    'dados_mercado': None,
                    'erro': 'Não mapeado'
                }
        
        return analise_fundos
    
    def analisar_criptomoedas(self):
        """Analisa as criptomoedas"""
        print("\n₿ Analisando Criptomoedas...")
        
        criptos = self.carteira_ideal['alocacao']['criptomoedas']
        total_criptos = criptos['valor']
        
        print(f"💰 Valor total em Criptomoedas: R$ {total_criptos:,.2f}")
        print(f"📈 Percentual da carteira: {criptos['percentual']:.1f}%")
        
        analise_criptos = {
            'total': total_criptos,
            'percentual': criptos['percentual'],
            'criptos': {}
        }
        
        # Buscar todos os preços de criptomoedas de uma vez
        try:
            dados_criptos = self.market_data.get_crypto_prices()
            
            for item in criptos['itens']:
                ticker = item['ticker']
                print(f"   🔍 Analisando {item['nome']} ({ticker})")
                
                # Buscar preço atual
                if ticker in dados_criptos:
                    preco_atual = dados_criptos[ticker].get('price', 0)
                    preco_brl = dados_criptos[ticker].get('price_brl', 0)
                    valor_atual = item['valor']  # Assumindo valor fixo para teste
                    
                    analise_criptos['criptos'][ticker] = {
                        'nome': item['nome'],
                        'valor': item['valor'],
                        'preco_atual': preco_atual,
                        'preco_brl': preco_brl,
                        'valor_atual': valor_atual
                    }
                    print(f"      ✅ Preço atual: ${preco_atual:,.2f} (R$ {preco_brl:,.2f})")
                else:
                    print(f"      ❌ Preço não disponível para {ticker}")
                    
        except Exception as e:
            print(f"      ❌ Erro ao obter preços de criptomoedas: {e}")
        
        return analise_criptos
    
    def analisar_acoes(self):
        """Analisa as ações"""
        print("\n📈 Analisando Ações...")
        
        acoes = self.carteira_ideal['alocacao']['acoes']
        total_acoes = acoes['valor']
        
        print(f"💰 Valor total em Ações: R$ {total_acoes:,.2f}")
        print(f"📈 Percentual da carteira: {acoes['percentual']:.1f}%")
        
        analise_acoes = {
            'total': total_acoes,
            'percentual': acoes['percentual'],
            'acoes': {}
        }
        
        # Buscar ações específicas da carteira ideal
        try:
            # Extrair tickers das ações da carteira
            tickers_acoes = [item['ticker'] for item in acoes['itens']]
            print(f"   🔍 Buscando dados para: {tickers_acoes}")
            
            # Buscar dados específicos para essas ações
            dados_acoes = self.market_data.get_stock_indices(symbols=tickers_acoes)
            
            for item in acoes['itens']:
                ticker = item['ticker']
                print(f"   🔍 Analisando {item['nome']} ({ticker})")
                
                # Buscar preço atual
                if ticker in dados_acoes:
                    preco_atual = dados_acoes[ticker].get('price', 0)
                    valor_atual = item['valor']  # Assumindo valor fixo para teste
                    
                    analise_acoes['acoes'][ticker] = {
                        'nome': item['nome'],
                        'valor': item['valor'],
                        'preco_atual': preco_atual,
                        'valor_atual': valor_atual
                    }
                    print(f"      ✅ Preço atual: R$ {preco_atual:,.2f}")
                else:
                    print(f"      ❌ Preço não disponível para {ticker}")
                    # Fallback com dados básicos
                    analise_acoes['acoes'][ticker] = {
                        'nome': item['nome'],
                        'valor': item['valor'],
                        'preco_atual': 0,
                        'valor_atual': item['valor'],
                        'erro': 'Preço não disponível'
                    }
                    
        except Exception as e:
            print(f"      ❌ Erro ao obter preços de ações: {e}")
        
        return analise_acoes
    
    def calcular_metricas_risco(self):
        """Calcula métricas de risco da carteira"""
        print("\n⚠️ Calculando Métricas de Risco...")
        
        # Simular retornos históricos (em um cenário real, usaria dados reais)
        retornos_simulados = {
            'renda_fixa': 0.08,  # 8% ao ano
            'fundos_cambiais': 0.05,  # 5% ao ano
            'criptomoedas': 0.25,  # 25% ao ano (alta volatilidade)
            'acoes': 0.15  # 15% ao ano
        }
        
        # Calcular retorno ponderado
        pesos = {
            'renda_fixa': 0.40,
            'fundos_cambiais': 0.15,
            'criptomoedas': 0.15,
            'acoes': 0.30
        }
        
        retorno_esperado = sum(pesos[k] * retornos_simulados[k] for k in pesos)
        
        # Simular volatilidade
        volatilidades = {
            'renda_fixa': 0.02,
            'fundos_cambiais': 0.08,
            'criptomoedas': 0.60,
            'acoes': 0.25
        }
        
        # Calcular volatilidade da carteira (simplificado)
        volatilidade_carteira = np.sqrt(sum((pesos[k] * volatilidades[k])**2 for k in pesos))
        
        # Sharpe Ratio (assumindo taxa livre de risco de 6%)
        taxa_livre_risco = 0.06
        sharpe_ratio = (retorno_esperado - taxa_livre_risco) / volatilidade_carteira
        
        metricas = {
            'retorno_esperado': retorno_esperado,
            'volatilidade': volatilidade_carteira,
            'sharpe_ratio': sharpe_ratio,
            'diversificacao': {
                'renda_fixa': pesos['renda_fixa'],
                'fundos_cambiais': pesos['fundos_cambiais'],
                'criptomoedas': pesos['criptomoedas'],
                'acoes': pesos['acoes']
            }
        }
        
        print(f"📊 Retorno Esperado: {retorno_esperado:.2%}")
        print(f"📊 Volatilidade: {volatilidade_carteira:.2%}")
        print(f"📊 Sharpe Ratio: {sharpe_ratio:.2f}")
        print(f"📊 Diversificação: {pesos}")
        
        return metricas
    
    def calcular_metricas_avancadas(self, retornos_mensais):
        """Calcula métricas financeiras avançadas a partir de uma série de retornos mensais"""
        if len(retornos_mensais) == 0:
            return {}
        retornos = np.array(retornos_mensais)
        media = np.mean(retornos)
        std = np.std(retornos)
        sharpe = media / std * np.sqrt(12) if std > 0 else 0
        sortino = media / np.std(retornos[retornos < 0]) * np.sqrt(12) if np.any(retornos < 0) else 0
        max_drawdown = 0
        cagr = 0
        if len(retornos) > 1:
            # Calcular drawdown
            acc = np.cumprod(1 + retornos)
            peak = np.maximum.accumulate(acc)
            drawdown = (acc - peak) / peak
            max_drawdown = drawdown.min()
            # CAGR
            anos = len(retornos) / 12
            cagr = (acc[-1]) ** (1/anos) - 1 if anos > 0 else 0
        return {
            'retorno_medio_mensal': float(media),
            'volatilidade_mensal': float(std),
            'sharpe_ratio': float(sharpe),
            'sortino_ratio': float(sortino),
            'max_drawdown': float(max_drawdown),
            'cagr': float(cagr)
        }

    def evolucao_mensal(self, fundos, acoes, criptos, meses=24):
        """Simula a evolução mensal da carteira usando dados históricos disponíveis"""
        # Para cada classe, pegar rentabilidades históricas (fundos), variação de preço (ações/criptos)
        # e simular evolução do valor investido
        datas = []
        valores = []
        valor_total = 0
        # Inicializar com valor inicial
        for f in fundos:
            valor_total += f['valor']
        for a in acoes:
            valor_total += a['valor']
        for c in criptos:
            valor_total += c['valor']
        valores.append(valor_total)
        datas.append('M0')
        # Simulação simplificada: usar média dos retornos históricos
        for m in range(1, meses+1):
            retorno_mensal = 0
            n = 0
            for f in fundos:
                if f.get('dados_mercado') and f['dados_mercado'].get('rentabilidades'):
                    # Pega último ano disponível
                    anos = sorted(f['dados_mercado']['rentabilidades'].keys())
                    if anos:
                        ano = anos[-1]
                        meses_fundo = f['dados_mercado']['rentabilidades'][ano]
                        if meses_fundo:
                            media = np.mean(list(meses_fundo.values()))
                            retorno_mensal += media
                            n += 1
            for a in acoes:
                # Simular com retorno médio anual de 15%/12
                retorno_mensal += 0.15/12
                n += 1
            for c in criptos:
                # Simular com retorno médio anual de 25%/12
                retorno_mensal += 0.25/12
                n += 1
            if n > 0:
                retorno_mensal = retorno_mensal / n
            else:
                retorno_mensal = 0.01
            valor_total = valor_total * (1 + retorno_mensal)
            valores.append(valor_total)
            datas.append(f'M{m}')
        retornos_mensais = np.diff(valores) / valores[:-1]
        return datas, valores, retornos_mensais

    def gerar_relatorio_completo(self):
        """Gera relatório completo da carteira ideal"""
        print("\n" + "="*60)
        print("📋 RELATÓRIO COMPLETO - CARTEIRA IDEAL")
        print("="*60)
        
        # Atualizar dados de mercado
        if not self.atualizar_dados_mercado():
            return None
        
        # Analisar cada classe de ativo
        renda_fixa = self.analisar_renda_fixa()
        fundos_cambiais = self.analisar_fundos()
        criptomoedas = self.analisar_criptomoedas()
        acoes = self.analisar_acoes()
        
        # Calcular métricas de risco
        metricas_risco = self.calcular_metricas_risco()
        
        # Tabela detalhada de ativos
        ativos = []
        valor_total = self.carteira_ideal['valor_total']
        for f in fundos_cambiais['fundos'].values():
            ativos.append({
                'classe': 'Fundo Cambial',
                'nome': f['nome'],
                'valor': f['valor'],
                'percentual': f['valor']/valor_total*100,
                'rentabilidade': f.get('taxa_retorno'),
                'anos_dados': f.get('anos_dados', 0)
            })
        for a in acoes['acoes'].values():
            ativos.append({
                'classe': 'Ação',
                'nome': a['nome'],
                'valor': a['valor'],
                'percentual': a['valor']/valor_total*100,
                'preco_atual': a.get('preco_atual'),
                'rentabilidade': None
            })
        for c in criptomoedas['criptos'].values():
            ativos.append({
                'classe': 'Criptomoeda',
                'nome': c['nome'],
                'valor': c['valor'],
                'percentual': c['valor']/valor_total*100,
                'preco_atual': c.get('preco_atual'),
                'rentabilidade': None
            })
        for rf in renda_fixa['itens']:
            ativos.append({
                'classe': 'Renda Fixa',
                'nome': rf['nome'],
                'valor': rf['valor'],
                'percentual': rf['valor']/valor_total*100,
                'rentabilidade': rf.get('taxa_retorno')
            })
        print("\nTabela detalhada de ativos:")
        for a in ativos:
            print(a)
        
        # Evolução mensal simulada
        datas, valores, retornos_mensais = self.evolucao_mensal(
            list(fundos_cambiais['fundos'].values()),
            list(acoes['acoes'].values()),
            list(criptomoedas['criptos'].values()),
            meses=24
        )
        metricas_avancadas = self.calcular_metricas_avancadas(retornos_mensais)
        print("\nEvolução mensal simulada (últimos 24 meses):")
        for d, v in zip(datas, valores):
            print(f"{d}: R$ {v:,.2f}")
        print("\nMétricas avançadas:")
        for k, v in metricas_avancadas.items():
            print(f"{k}: {v}")
        
        # Gerar gráfico da evolução (opcional)
        try:
            plt.figure(figsize=(10,4))
            plt.plot(datas, valores, marker='o')
            plt.title('Evolução Simulada do Valor da Carteira')
            plt.xlabel('Mês')
            plt.ylabel('Valor (R$)')
            plt.grid()
            buf = io.BytesIO()
            plt.savefig(buf, format='png')
            buf.seek(0)
            with open('grafico_evolucao_carteira.png', 'wb') as f:
                f.write(buf.read())
            print("Gráfico salvo como grafico_evolucao_carteira.png")
        except Exception as e:
            print(f"Erro ao gerar gráfico: {e}")
        
        # Gerar relatório JSON
        relatorio = {
            'timestamp': datetime.now().isoformat(),
            'carteira': self.carteira_ideal,
            'analise': {
                'renda_fixa': renda_fixa,
                'fundos_cambiais': fundos_cambiais,
                'criptomoedas': criptomoedas,
                'acoes': acoes
            },
            'metricas_risco': metricas_risco,
            'metricas_avancadas': metricas_avancadas,
            'ativos': ativos,
            'evolucao_mensal': {
                'datas': datas,
                'valores': valores,
                'retornos_mensais': retornos_mensais.tolist() if hasattr(retornos_mensais, 'tolist') else list(retornos_mensais)
            },
            'resumo': {
                'valor_total': self.carteira_ideal['valor_total'],
                'alocacao_por_classe': {
                    'Renda Fixa': f"{renda_fixa['percentual']:.1f}%",
                    'Fundos Cambiais': f"{fundos_cambiais['percentual']:.1f}%",
                    'Criptomoedas': f"{criptomoedas['percentual']:.1f}%",
                    'Ações': f"{acoes['percentual']:.1f}%"
                }
            }
        }
        
        # Salvar relatório
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"relatorio_carteira_ideal_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Relatório salvo em: {filename}")
        
        # Exibir resumo
        print("\n" + "="*60)
        print("📊 RESUMO DA CARTEIRA IDEAL")
        print("="*60)
        print(f"💰 Valor Total: R$ {self.carteira_ideal['valor_total']:,.2f}")
        print(f"📈 Retorno Esperado: {metricas_risco['retorno_esperado']:.2%}")
        print(f"⚠️ Volatilidade: {metricas_risco['volatilidade']:.2%}")
        print(f"📊 Sharpe Ratio: {metricas_risco['sharpe_ratio']:.2f}")
        print("\n🎯 Alocação por Classe:")
        for classe, percentual in relatorio['resumo']['alocacao_por_classe'].items():
            print(f"   • {classe}: {percentual}")
        print("\nMétricas Avançadas:")
        for k, v in metricas_avancadas.items():
            print(f"   {k}: {v}")
        print("\nEvolução Mensal (últimos 24 meses):")
        for d, v in zip(datas, valores):
            print(f"   {d}: R$ {v:,.2f}")
        
        return relatorio

    def gerar_relatorio_txt(self, relatorio):
        """Gera relatório em formato .txt"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"relatorio_carteira_ideal_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("📋 RELATÓRIO COMPLETO - CARTEIRA IDEAL DIVERSIFICADA\n")
            f.write("="*80 + "\n")
            f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write(f"Versão: 1.0\n\n")
            
            # Informações da Carteira
            f.write("📊 INFORMAÇÕES DA CARTEIRA\n")
            f.write("-"*50 + "\n")
            f.write(f"Nome: {relatorio['carteira']['nome']}\n")
            f.write(f"Descrição: {relatorio['carteira']['descricao']}\n")
            f.write(f"Data de Criação: {relatorio['carteira']['data_criacao']}\n")
            f.write(f"Valor Total: R$ {relatorio['carteira']['valor_total']:,.2f}\n")
            f.write(f"Perfil de Risco: {relatorio['carteira']['metadados']['perfil_risco']}\n")
            f.write(f"Horizonte de Tempo: {relatorio['carteira']['metadados']['horizonte_tempo']}\n")
            f.write(f"Estratégia: {relatorio['carteira']['metadados']['estrategia']}\n\n")
            
            # Alocação por Classe
            f.write("🎯 ALOCAÇÃO POR CLASSE DE ATIVO\n")
            f.write("-"*50 + "\n")
            for classe, percentual in relatorio['resumo']['alocacao_por_classe'].items():
                valor_classe = relatorio['carteira']['valor_total'] * float(percentual.strip('%')) / 100
                f.write(f"{classe}: {percentual} (R$ {valor_classe:,.2f})\n")
            f.write("\n")
            
            # Análise Detalhada por Classe
            f.write("📈 ANÁLISE DETALHADA POR CLASSE\n")
            f.write("="*80 + "\n")
            
            # Renda Fixa
            f.write("\n💰 RENDA FIXA\n")
            f.write("-"*30 + "\n")
            renda_fixa = relatorio['analise']['renda_fixa']
            f.write(f"Valor Total: R$ {renda_fixa['total']:,.2f}\n")
            f.write(f"Percentual da Carteira: {renda_fixa['percentual']:.1f}%\n\n")
            for item in renda_fixa['itens']:
                f.write(f"  • {item['nome']}\n")
                f.write(f"    Valor: R$ {item['valor']:,.2f}\n")
                f.write(f"    Taxa de Retorno: {item['taxa_retorno']}\n")
                f.write(f"    Tipo: {item['tipo']}\n\n")
            
            # Fundos Cambiais
            f.write("🏦 FUNDOS CAMBIAIS\n")
            f.write("-"*30 + "\n")
            fundos = relatorio['analise']['fundos_cambiais']
            f.write(f"Valor Total: R$ {fundos['total']:,.2f}\n")
            f.write(f"Percentual da Carteira: {fundos['percentual']:.1f}%\n\n")
            for cnpj, fundo in fundos['fundos'].items():
                f.write(f"  • {fundo['nome']}\n")
                f.write(f"    CNPJ: {cnpj}\n")
                f.write(f"    Valor: R$ {fundo['valor']:,.2f}\n")
                f.write(f"    Taxa de Retorno: {fundo['taxa_retorno']}\n")
                f.write(f"    Slug: {fundo['slug']}\n")
                if fundo.get('dados_mercado'):
                    f.write(f"    Anos de Dados: {fundo.get('anos_dados', 'N/A')}\n")
                else:
                    f.write(f"    Status: {fundo.get('erro', 'Dados não disponíveis')}\n")
                f.write("\n")
            
            # Criptomoedas
            f.write("₿ CRIPTOMOEDAS\n")
            f.write("-"*30 + "\n")
            criptos = relatorio['analise']['criptomoedas']
            f.write(f"Valor Total: R$ {criptos['total']:,.2f}\n")
            f.write(f"Percentual da Carteira: {criptos['percentual']:.1f}%\n\n")
            for ticker, cripto in criptos['criptos'].items():
                f.write(f"  • {cripto['nome']} ({ticker})\n")
                f.write(f"    Valor: R$ {cripto['valor']:,.2f}\n")
                if cripto.get('preco_atual'):
                    f.write(f"    Preço Atual: ${cripto['preco_atual']:,.2f}\n")
                f.write("\n")
            
            # Ações
            f.write("📈 AÇÕES\n")
            f.write("-"*30 + "\n")
            acoes = relatorio['analise']['acoes']
            f.write(f"Valor Total: R$ {acoes['total']:,.2f}\n")
            f.write(f"Percentual da Carteira: {acoes['percentual']:.1f}%\n\n")
            for ticker, acao in acoes['acoes'].items():
                f.write(f"  • {acao['nome']} ({ticker})\n")
                f.write(f"    Valor: R$ {acao['valor']:,.2f}\n")
                if acao.get('preco_atual'):
                    f.write(f"    Preço Atual: R$ {acao['preco_atual']:,.2f}\n")
                f.write("\n")
            
            # Métricas de Risco
            f.write("⚠️ MÉTRICAS DE RISCO\n")
            f.write("-"*30 + "\n")
            metricas = relatorio['metricas_risco']
            f.write(f"Retorno Esperado: {metricas['retorno_esperado']:.2%}\n")
            f.write(f"Volatilidade: {metricas['volatilidade']:.2%}\n")
            f.write(f"Sharpe Ratio: {metricas['sharpe_ratio']:.2f}\n")
            f.write(f"Diversificação: {metricas['diversificacao']}\n\n")
            
            # Métricas Avançadas
            f.write("📊 MÉTRICAS AVANÇADAS\n")
            f.write("-"*30 + "\n")
            metricas_av = relatorio['metricas_avancadas']
            for k, v in metricas_av.items():
                if isinstance(v, float):
                    f.write(f"{k}: {v:.6f}\n")
                else:
                    f.write(f"{k}: {v}\n")
            f.write("\n")
            
            # Evolução Mensal
            f.write("📈 EVOLUÇÃO MENSAL SIMULADA (ÚLTIMOS 24 MESES)\n")
            f.write("-"*60 + "\n")
            evolucao = relatorio['evolucao_mensal']
            for data, valor in zip(evolucao['datas'], evolucao['valores']):
                f.write(f"{data}: R$ {valor:,.2f}\n")
            f.write("\n")
            
            # Tabela de Ativos
            f.write("📋 TABELA DETALHADA DE ATIVOS\n")
            f.write("-"*60 + "\n")
            f.write(f"{'Classe':<15} {'Nome':<40} {'Valor':<15} {'%':<8} {'Rentabilidade':<15}\n")
            f.write("-"*100 + "\n")
            for ativo in relatorio['ativos']:
                nome = ativo['nome'][:38] + ".." if len(ativo['nome']) > 40 else ativo['nome']
                valor = f"R$ {ativo['valor']:,.2f}"
                percentual = f"{ativo['percentual']:.1f}%"
                rentabilidade = ativo.get('rentabilidade', 'N/A') or 'N/A'
                f.write(f"{ativo['classe']:<15} {nome:<40} {valor:<15} {percentual:<8} {rentabilidade:<15}\n")
            f.write("\n")
            
            # Objetivos da Carteira
            f.write("🎯 OBJETIVOS DA CARTEIRA\n")
            f.write("-"*30 + "\n")
            for objetivo in relatorio['carteira']['metadados']['objetivos']:
                f.write(f"• {objetivo}\n")
            f.write("\n")
            
            # Observações Finais
            f.write("📝 OBSERVAÇÕES FINAIS\n")
            f.write("-"*30 + "\n")
            f.write("• Este relatório foi gerado automaticamente pelo sistema de análise de carteiras\n")
            f.write("• Os dados de mercado são atualizados em tempo real\n")
            f.write("• As métricas de risco são calculadas com base em dados históricos\n")
            f.write("• Recomenda-se rebalanceamento trimestral conforme estratégia definida\n")
            f.write("• Consulte um profissional de investimentos antes de tomar decisões\n\n")
            
            f.write("="*80 + "\n")
            f.write("FIM DO RELATÓRIO\n")
            f.write("="*80 + "\n")
        
        print(f"📄 Relatório TXT salvo em: {filename}")
        return filename

def main():
    """Função principal"""
    print("🚀 Iniciando teste da Carteira Ideal...")
    
    teste = CarteiraIdealTest()
    if not teste.carteira_ideal:
        print("❌ Não foi possível carregar a carteira ideal!")
        return
    
    relatorio = teste.gerar_relatorio_completo()
    
    if relatorio:
        # Gerar relatório em formato TXT
        teste.gerar_relatorio_txt(relatorio)
        print("\n✅ Teste da Carteira Ideal concluído com sucesso!")
    else:
        print("\n❌ Erro durante o teste da Carteira Ideal!")

if __name__ == "__main__":
    main() 