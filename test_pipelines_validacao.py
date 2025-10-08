#!/usr/bin/env python3
"""
Sistema de Validação Rigorosa dos Pipelines de Dados
====================================================

Este script testa SE os dados estão REALMENTE funcionando ou apenas
passando por "vista grossa" com valores simulados.

Autor: Sistema de Análise de Portfólios
Versão: 1.0.0
Data: 2025-10-07
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import numpy as np
from dataclasses import dataclass, asdict
from enum import Enum

# Imports do projeto
from core.market_indices_fixed import MarketIndicesManager
from dashboard.portfolio_collector_v3 import PortfolioDataCollectorV3
from apis.binance_api import BinanceMercadoAPI
from apis.yahoo_api import YahooFinanceAPI

class QualidadeDados(Enum):
    """Níveis de qualidade de dados"""
    EXCELENTE = "EXCELENTE"  # Dados reais, atualizados, completos
    BOM = "BOM"  # Dados reais mas com algumas lacunas
    REGULAR = "REGULAR"  # Dados parcialmente reais
    RUIM = "RUIM"  # Dados muito incompletos
    SIMULADO = "SIMULADO"  # Dados claramente simulados
    FALHOU = "FALHOU"  # Pipeline falhou completamente

@dataclass
class ResultadoValidacao:
    """Resultado de uma validação de pipeline"""
    pipeline: str
    qualidade: QualidadeDados
    dados_reais: bool
    dados_atualizados: bool
    completude: float  # 0.0 a 1.0
    latencia_ms: float
    erros: List[str]
    avisos: List[str]
    metricas: Dict[str, Any]
    timestamp: str

class ValidadorPipelines:
    """Validador rigoroso de pipelines de dados"""
    
    def __init__(self):
        self.resultados: List[ResultadoValidacao] = []
        self.market_manager = None
        self.portfolio_collector = None
        self.binance_api = None
        self.yahoo_api = None
        
        print("[*] INICIANDO VALIDACAO RIGOROSA DOS PIPELINES DE DADOS")
        print("=" * 70)
        print()
    
    def validar_todos_pipelines(self) -> Dict[str, Any]:
        """Valida todos os pipelines de dados"""
        print("[*] Executando validacoes de todos os pipelines...\n")
        
        # 1. Pipeline de Índices de Mercado
        print("[1] Validando Pipeline de Indices de Mercado...")
        resultado_mercado = self._validar_pipeline_mercado()
        self.resultados.append(resultado_mercado)
        self._imprimir_resultado(resultado_mercado)
        print()
        
        # 2. Pipeline de Criptomoedas
        print("[2] Validando Pipeline de Criptomoedas...")
        resultado_crypto = self._validar_pipeline_crypto()
        self.resultados.append(resultado_crypto)
        self._imprimir_resultado(resultado_crypto)
        print()
        
        # 3. Pipeline de Ações
        print("[3] Validando Pipeline de Acoes...")
        resultado_acoes = self._validar_pipeline_acoes()
        self.resultados.append(resultado_acoes)
        self._imprimir_resultado(resultado_acoes)
        print()
        
        # 4. Pipeline de Fundos de Investimento
        print("[4] Validando Pipeline de Fundos de Investimento...")
        resultado_fundos = self._validar_pipeline_fundos()
        self.resultados.append(resultado_fundos)
        self._imprimir_resultado(resultado_fundos)
        print()
        
        # 5. Pipeline de Câmbio
        print("[5] Validando Pipeline de Cambio...")
        resultado_cambio = self._validar_pipeline_cambio()
        self.resultados.append(resultado_cambio)
        self._imprimir_resultado(resultado_cambio)
        print()
        
        # 6. Pipeline de Dados Históricos
        print("[6] Validando Pipeline de Dados Historicos...")
        resultado_historico = self._validar_pipeline_historico()
        self.resultados.append(resultado_historico)
        self._imprimir_resultado(resultado_historico)
        print()
        
        # Gerar relatório consolidado
        return self._gerar_relatorio_consolidado()
    
    def _validar_pipeline_mercado(self) -> ResultadoValidacao:
        """Valida pipeline de índices de mercado"""
        inicio = time.time()
        erros = []
        avisos = []
        metricas = {}
        
        try:
            if self.market_manager is None:
                self.market_manager = MarketIndicesManager()
            
            # Testar obtenção de dados
            dados = self.market_manager.get_all_market_data(force_update=True)
            latencia = (time.time() - inicio) * 1000
            
            # Validação 1: Dados existem?
            if not dados or not isinstance(dados, dict):
                erros.append("Nenhum dado de mercado retornado")
                return self._criar_resultado_falha("Pipeline Índices Mercado", latencia, erros)
            
            # Validação 2: Dados são REAIS ou SIMULADOS?
            dados_reais = self._verificar_dados_reais_mercado(dados)
            if not dados_reais:
                erros.append("Dados parecem ser simulados/hardcoded")
            
            # Validação 3: Dados estão atualizados?
            dados_atualizados = self._verificar_atualizacao_mercado(dados)
            if not dados_atualizados:
                avisos.append("Dados podem estar desatualizados")
            
            # Validação 4: Completude dos dados
            completude = self._calcular_completude_mercado(dados)
            metricas['completude'] = completude
            metricas['total_indices'] = len(dados.get('stocks', {}))
            metricas['indices_validos'] = sum(1 for d in dados.get('stocks', {}).values() if isinstance(d, dict) and d.get('price', 0) > 0)
            
            # Validação 5: Variabilidade dos dados (detectar valores fixos)
            variabilidade = self._verificar_variabilidade(dados)
            if variabilidade < 0.01:
                avisos.append("Dados têm baixa variabilidade - podem ser fixos")
            metricas['variabilidade'] = variabilidade
            
            # Determinar qualidade
            if not dados_reais:
                qualidade = QualidadeDados.SIMULADO
            elif completude >= 0.9 and dados_atualizados and len(erros) == 0:
                qualidade = QualidadeDados.EXCELENTE
            elif completude >= 0.7 and len(erros) == 0:
                qualidade = QualidadeDados.BOM
            elif completude >= 0.5:
                qualidade = QualidadeDados.REGULAR
            else:
                qualidade = QualidadeDados.RUIM
            
            return ResultadoValidacao(
                pipeline="Pipeline Índices Mercado",
                qualidade=qualidade,
                dados_reais=dados_reais,
                dados_atualizados=dados_atualizados,
                completude=completude,
                latencia_ms=latencia,
                erros=erros,
                avisos=avisos,
                metricas=metricas,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            latencia = (time.time() - inicio) * 1000
            erros.append(f"Exceção: {str(e)}")
            return self._criar_resultado_falha("Pipeline Índices Mercado", latencia, erros)
    
    def _validar_pipeline_crypto(self) -> ResultadoValidacao:
        """Valida pipeline de criptomoedas"""
        inicio = time.time()
        erros = []
        avisos = []
        metricas = {}
        
        try:
            if self.market_manager is None:
                self.market_manager = MarketIndicesManager()
            
            # Testar Binance API diretamente
            if self.binance_api is None:
                self.binance_api = BinanceMercadoAPI()
            
            # Teste 1: Obter preços via MarketManager
            cryptos = self.market_manager.get_crypto_prices()
            
            # Teste 2: Obter preços diretamente da Binance
            btc_ticker = self.binance_api.get_preco("BTCUSDT")
            
            latencia = (time.time() - inicio) * 1000
            
            # Validação 1: Dados existem?
            if not cryptos:
                erros.append("Nenhum dado de criptomoeda retornado")
                return self._criar_resultado_falha("Pipeline Criptomoedas", latencia, erros)
            
            # Validação 2: Comparar dados de duas fontes
            if not btc_ticker or 'price' not in btc_ticker:
                avisos.append("Binance API não retornou dados")
            else:
                preco_binance = float(btc_ticker.get('price', 0))
                preco_manager = cryptos.get('BTC', {}).get('price', 0)
                
                if preco_binance > 0 and preco_manager > 0:
                    diferenca_percentual = abs(preco_binance - preco_manager) / preco_binance * 100
                    metricas['diferenca_fontes_pct'] = diferenca_percentual
                    
                    if diferenca_percentual > 5:
                        avisos.append(f"Diferença entre fontes: {diferenca_percentual:.2f}%")
            
            # Validação 3: Dados são REAIS?
            dados_reais = self._verificar_dados_reais_crypto(cryptos)
            if not dados_reais:
                erros.append("Dados de cripto parecem simulados")
            
            # Validação 4: Preços estão em range razoável?
            for symbol, data in cryptos.items():
                if not isinstance(data, dict):
                    continue
                preco = data.get('price', 0)
                if preco == 0:
                    avisos.append(f"{symbol}: preço zero")
                elif symbol in ['BTC', 'BTCUSDT'] and (preco < 10000 or preco > 150000):
                    avisos.append(f"{symbol}: preço fora do range esperado ({preco})")
            
            # Validação 5: Completude (aceitar símbolos com e sem USDT)
            criptos_esperadas = ['BTC', 'ETH', 'BNB', 'USDT']
            # Verificar se existe BTC ou BTCUSDT, ETH ou ETHUSDT, etc.
            encontradas = 0
            for cripto_base in criptos_esperadas:
                # Verificar versão simples e com USDT
                if cripto_base in cryptos and cryptos[cripto_base].get('price', 0) > 0:
                    encontradas += 1
                elif f"{cripto_base}USDT" in cryptos and cryptos[f"{cripto_base}USDT"].get('price', 0) > 0:
                    encontradas += 1
            completude = encontradas / len(criptos_esperadas)
            
            metricas['completude'] = completude
            metricas['total_cryptos'] = len(cryptos)
            metricas['cryptos_com_preco'] = sum(1 for d in cryptos.values() if d.get('price', 0) > 0)
            
            # Determinar qualidade
            if not dados_reais:
                qualidade = QualidadeDados.SIMULADO
            elif completude >= 0.9 and len(erros) == 0:
                qualidade = QualidadeDados.EXCELENTE
            elif completude >= 0.7:
                qualidade = QualidadeDados.BOM
            elif completude >= 0.5:
                qualidade = QualidadeDados.REGULAR
            else:
                qualidade = QualidadeDados.RUIM
            
            return ResultadoValidacao(
                pipeline="Pipeline Criptomoedas",
                qualidade=qualidade,
                dados_reais=dados_reais,
                dados_atualizados=True,
                completude=completude,
                latencia_ms=latencia,
                erros=erros,
                avisos=avisos,
                metricas=metricas,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            latencia = (time.time() - inicio) * 1000
            erros.append(f"Exceção: {str(e)}")
            return self._criar_resultado_falha("Pipeline Criptomoedas", latencia, erros)
    
    def _validar_pipeline_acoes(self) -> ResultadoValidacao:
        """Valida pipeline de ações"""
        inicio = time.time()
        erros = []
        avisos = []
        metricas = {}
        
        try:
            if self.market_manager is None:
                self.market_manager = MarketIndicesManager()
            
            # Testar com ações reais da carteira
            acoes_teste = ['PETR4.SA', 'VALE3.SA', 'BBAS3.SA']
            dados_acoes = self.market_manager.get_stock_indices(symbols=acoes_teste)
            
            latencia = (time.time() - inicio) * 1000
            
            # Validação 1: Dados existem?
            if not dados_acoes:
                erros.append("Nenhum dado de ação retornado")
                return self._criar_resultado_falha("Pipeline Ações", latencia, erros)
            
            # Validação 2: Dados são REAIS?
            dados_reais = self._verificar_dados_reais_acoes(dados_acoes)
            if not dados_reais:
                erros.append("Dados de ações parecem simulados")
            
            # Validação 3: Preços estão atualizados?
            dados_atualizados = True
            for symbol, data in dados_acoes.items():
                timestamp = data.get('timestamp')
                if timestamp:
                    try:
                        data_cotacao = datetime.fromisoformat(timestamp)
                        idade_horas = (datetime.now() - data_cotacao).total_seconds() / 3600
                        if idade_horas > 48:  # Mais de 2 dias
                            avisos.append(f"{symbol}: cotação com {idade_horas:.1f}h de atraso")
                            dados_atualizados = False
                    except:
                        pass
            
            # Validação 4: Completude
            completude = len(dados_acoes) / len(acoes_teste)
            metricas['completude'] = completude
            metricas['acoes_solicitadas'] = len(acoes_teste)
            metricas['acoes_retornadas'] = len(dados_acoes)
            metricas['acoes_com_preco'] = sum(1 for d in dados_acoes.values() if d.get('price', 0) > 0)
            
            # Validação 5: Ranges de preços razoáveis
            for symbol, data in dados_acoes.items():
                preco = data.get('price', 0)
                if preco == 0:
                    avisos.append(f"{symbol}: preço zero")
                elif preco < 0:
                    erros.append(f"{symbol}: preço negativo ({preco})")
                elif preco < 1 or preco > 1000:
                    avisos.append(f"{symbol}: preço fora do range típico ({preco})")
            
            # Determinar qualidade
            if not dados_reais:
                qualidade = QualidadeDados.SIMULADO
            elif completude == 1.0 and dados_atualizados and len(erros) == 0:
                qualidade = QualidadeDados.EXCELENTE
            elif completude >= 0.8 and len(erros) == 0:
                qualidade = QualidadeDados.BOM
            elif completude >= 0.5:
                qualidade = QualidadeDados.REGULAR
            else:
                qualidade = QualidadeDados.RUIM
            
            return ResultadoValidacao(
                pipeline="Pipeline Ações",
                qualidade=qualidade,
                dados_reais=dados_reais,
                dados_atualizados=dados_atualizados,
                completude=completude,
                latencia_ms=latencia,
                erros=erros,
                avisos=avisos,
                metricas=metricas,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            latencia = (time.time() - inicio) * 1000
            erros.append(f"Exceção: {str(e)}")
            return self._criar_resultado_falha("Pipeline Ações", latencia, erros)
    
    def _validar_pipeline_fundos(self) -> ResultadoValidacao:
        """Valida pipeline de fundos de investimento"""
        inicio = time.time()
        erros = []
        avisos = []
        metricas = {}
        
        try:
            if self.portfolio_collector is None:
                self.portfolio_collector = PortfolioDataCollectorV3()
            
            # Testar com um fundo real da carteira ideal
            # CNPJ do BTG Pactual Absoluto FIC FIM (exemplo)
            cnpj_teste = "00.066.670/0001-00"
            
            # Buscar slug
            slug, url = self.portfolio_collector.buscar_slug_fundo(cnpj_teste)
            
            if not slug:
                avisos.append("Não foi possível encontrar slug do fundo teste")
                # Tentar com fundo do mapeamento
                try:
                    with open('mapeamento_fundos.json', 'r', encoding='utf-8') as f:
                        mapeamento = json.load(f)
                    
                    # Pegar primeiro fundo do mapeamento
                    if mapeamento.get('mapeamento_fundos'):
                        primeiro_cnpj = list(mapeamento['mapeamento_fundos'].keys())[0]
                        slug = mapeamento['mapeamento_fundos'][primeiro_cnpj]['slug']
                        cnpj_teste = primeiro_cnpj
                except:
                    pass
            
            if slug:
                # Extrair dados do fundo
                dados_fundo = self.portfolio_collector.extrair_dados_fundo(slug, cnpj_teste)
                
                latencia = (time.time() - inicio) * 1000
                
                if dados_fundo:
                    # Validação 1: Dados existem?
                    rentabilidades = dados_fundo.get('rentabilidades', {})
                    
                    if not rentabilidades:
                        erros.append("Nenhuma rentabilidade encontrada")
                        return self._criar_resultado_falha("Pipeline Fundos", latencia, erros)
                    
                    # Validação 2: Dados são REAIS?
                    dados_reais = self._verificar_dados_reais_fundos(rentabilidades)
                    if not dados_reais:
                        erros.append("Dados de fundos parecem simulados")
                    
                    # Validação 3: Dados históricos suficientes?
                    anos_dados = len(rentabilidades)
                    meses_total = sum(len(meses) for meses in rentabilidades.values())
                    
                    metricas['anos_dados'] = anos_dados
                    metricas['meses_total'] = meses_total
                    
                    if anos_dados < 1:
                        avisos.append("Menos de 1 ano de dados históricos")
                    
                    # Validação 4: Completude (12 meses por ano)
                    meses_esperados = anos_dados * 12
                    completude = min(meses_total / max(meses_esperados, 1), 1.0)
                    metricas['completude'] = completude
                    
                    # Validação 5: Valores de rentabilidade razoáveis?
                    valores_suspeitos = 0
                    for ano, meses in rentabilidades.items():
                        for mes, valor in meses.items():
                            # Rentabilidade mensal entre -50% e +50% é razoável
                            if abs(valor) > 0.5:
                                valores_suspeitos += 1
                                avisos.append(f"Rentabilidade suspeita em {ano}/{mes}: {valor*100:.2f}%")
                    
                    metricas['valores_suspeitos'] = valores_suspeitos
                    
                    # Determinar qualidade
                    if not dados_reais:
                        qualidade = QualidadeDados.SIMULADO
                    elif completude >= 0.8 and anos_dados >= 2 and len(erros) == 0:
                        qualidade = QualidadeDados.EXCELENTE
                    elif completude >= 0.6 and anos_dados >= 1:
                        qualidade = QualidadeDados.BOM
                    elif meses_total >= 6:
                        qualidade = QualidadeDados.REGULAR
                    else:
                        qualidade = QualidadeDados.RUIM
                    
                    return ResultadoValidacao(
                        pipeline="Pipeline Fundos",
                        qualidade=qualidade,
                        dados_reais=dados_reais,
                        dados_atualizados=True,
                        completude=completude,
                        latencia_ms=latencia,
                        erros=erros,
                        avisos=avisos,
                        metricas=metricas,
                        timestamp=datetime.now().isoformat()
                    )
                else:
                    erros.append("Falha ao extrair dados do fundo")
                    return self._criar_resultado_falha("Pipeline Fundos", latencia, erros)
            else:
                latencia = (time.time() - inicio) * 1000
                erros.append("Não foi possível obter slug de nenhum fundo")
                return self._criar_resultado_falha("Pipeline Fundos", latencia, erros)
            
        except Exception as e:
            latencia = (time.time() - inicio) * 1000
            erros.append(f"Exceção: {str(e)}")
            return self._criar_resultado_falha("Pipeline Fundos", latencia, erros)
    
    def _validar_pipeline_cambio(self) -> ResultadoValidacao:
        """Valida pipeline de câmbio"""
        inicio = time.time()
        erros = []
        avisos = []
        metricas = {}
        
        try:
            if self.market_manager is None:
                self.market_manager = MarketIndicesManager()
            
            # Testar obtenção de taxas de câmbio
            dados = self.market_manager.get_all_market_data(force_update=True)
            exchange_rates = dados.get('exchange_rates', {})
            
            latencia = (time.time() - inicio) * 1000
            
            # Validação 1: Dados existem?
            if not exchange_rates:
                erros.append("Nenhuma taxa de câmbio retornada")
                return self._criar_resultado_falha("Pipeline Câmbio", latencia, erros)
            
            # Validação 2: USD/BRL está presente?
            usd_brl = exchange_rates.get('USD_BRL', 0)
            if usd_brl == 0:
                erros.append("Taxa USD/BRL não encontrada")
            elif usd_brl < 4.0 or usd_brl > 7.0:
                avisos.append(f"Taxa USD/BRL fora do range esperado: {usd_brl}")
            
            metricas['USD_BRL'] = usd_brl
            
            # Validação 3: Dados são REAIS?
            dados_reais = self._verificar_dados_reais_cambio(exchange_rates)
            if not dados_reais:
                erros.append("Dados de câmbio parecem simulados/fixos")
            
            # Validação 4: Completude
            taxas_esperadas = ['USD_BRL', 'EUR_BRL', 'GBP_BRL']
            encontradas = sum(1 for t in taxas_esperadas if t in exchange_rates and exchange_rates[t] > 0)
            completude = encontradas / len(taxas_esperadas)
            
            metricas['completude'] = completude
            metricas['total_taxas'] = len(exchange_rates)
            
            # Determinar qualidade
            if not dados_reais:
                qualidade = QualidadeDados.SIMULADO
            elif completude == 1.0 and len(erros) == 0:
                qualidade = QualidadeDados.EXCELENTE
            elif completude >= 0.6:
                qualidade = QualidadeDados.BOM
            elif usd_brl > 0:
                qualidade = QualidadeDados.REGULAR
            else:
                qualidade = QualidadeDados.RUIM
            
            return ResultadoValidacao(
                pipeline="Pipeline Câmbio",
                qualidade=qualidade,
                dados_reais=dados_reais,
                dados_atualizados=True,
                completude=completude,
                latencia_ms=latencia,
                erros=erros,
                avisos=avisos,
                metricas=metricas,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            latencia = (time.time() - inicio) * 1000
            erros.append(f"Exceção: {str(e)}")
            return self._criar_resultado_falha("Pipeline Câmbio", latencia, erros)
    
    def _validar_pipeline_historico(self) -> ResultadoValidacao:
        """Valida pipeline de dados históricos"""
        inicio = time.time()
        erros = []
        avisos = []
        metricas = {}
        
        try:
            if self.market_manager is None:
                self.market_manager = MarketIndicesManager()
            
            # Testar dados históricos de BTC usando Binance API diretamente
            hist_btc = {}
            try:
                if self.binance_api is None:
                    from apis.binance_api import BinanceMercadoAPI
                    self.binance_api = BinanceMercadoAPI()
                
                df_btc = self.binance_api.get_historical_data('BTCUSDT')
                if not df_btc.empty:
                    hist_btc = {
                        'dates': df_btc.index.strftime('%Y-%m-%d').tolist()[-30:],
                        'prices': df_btc['close'].tolist()[-30:]
                    }
            except Exception as e:
                avisos.append(f"Erro ao buscar histórico BTC: {e}")
            
            # Testar dados históricos de ação usando Yahoo Finance diretamente
            hist_petr4 = {}
            try:
                import yfinance as yf
                ticker = yf.Ticker('PETR4.SA')
                df_petr4 = ticker.history(period='1mo')
                if not df_petr4.empty:
                    hist_petr4 = {
                        'dates': df_petr4.index.strftime('%Y-%m-%d').tolist(),
                        'prices': df_petr4['Close'].tolist()
                    }
            except Exception as e:
                avisos.append(f"Erro ao buscar histórico PETR4: {e}")
            
            latencia = (time.time() - inicio) * 1000
            
            # Validação 1: Dados existem?
            if not hist_btc and not hist_petr4:
                erros.append("Nenhum dado histórico retornado")
                return self._criar_resultado_falha("Pipeline Histórico", latencia, erros)
            
            # Validação 2: BTC - dados suficientes?
            if hist_btc:
                datas_btc = hist_btc.get('dates', [])
                precos_btc = hist_btc.get('prices', [])
                
                metricas['btc_dias'] = len(datas_btc)
                metricas['btc_precos'] = len(precos_btc)
                
                if len(precos_btc) < 20:
                    avisos.append(f"BTC: apenas {len(precos_btc)} dias de dados (esperado ~30)")
                
                # Verificar se há variação nos preços (não são todos iguais)
                if len(precos_btc) > 1:
                    std_btc = np.std(precos_btc)
                    if std_btc < 100:  # BTC deveria ter variação de pelo menos $100
                        avisos.append(f"BTC: baixa variabilidade nos preços (std={std_btc:.2f})")
            else:
                avisos.append("Dados históricos de BTC não disponíveis")
            
            # Validação 3: PETR4 - dados suficientes?
            if hist_petr4:
                datas_petr4 = hist_petr4.get('dates', [])
                precos_petr4 = hist_petr4.get('prices', [])
                
                metricas['petr4_dias'] = len(datas_petr4)
                metricas['petr4_precos'] = len(precos_petr4)
                
                if len(precos_petr4) < 20:
                    avisos.append(f"PETR4: apenas {len(precos_petr4)} dias de dados")
                
                # Verificar variação
                if len(precos_petr4) > 1:
                    std_petr4 = np.std(precos_petr4)
                    if std_petr4 < 0.1:
                        avisos.append(f"PETR4: baixa variabilidade nos preços (std={std_petr4:.2f})")
            else:
                avisos.append("Dados históricos de PETR4 não disponíveis")
            
            # Validação 4: Completude
            dias_esperados = 30
            dias_btc = len(hist_btc.get('dates', [])) if hist_btc else 0
            dias_petr4 = len(hist_petr4.get('dates', [])) if hist_petr4 else 0
            
            completude = ((dias_btc + dias_petr4) / (dias_esperados * 2))
            metricas['completude'] = min(completude, 1.0)
            
            # Validação 5: Dados são reais?
            dados_reais = True
            if hist_btc and len(hist_btc.get('prices', [])) > 1:
                # Verificar se não são todos valores iguais ou sequenciais óbvios
                precos = hist_btc['prices']
                if len(set(precos)) == 1:
                    dados_reais = False
                    erros.append("BTC: todos os preços históricos são iguais")
            
            if hist_petr4 and len(hist_petr4.get('prices', [])) > 1:
                precos = hist_petr4['prices']
                if len(set(precos)) == 1:
                    dados_reais = False
                    erros.append("PETR4: todos os preços históricos são iguais")
            
            # Determinar qualidade
            if not dados_reais:
                qualidade = QualidadeDados.SIMULADO
            elif completude >= 0.8 and len(erros) == 0:
                qualidade = QualidadeDados.EXCELENTE
            elif completude >= 0.6:
                qualidade = QualidadeDados.BOM
            elif completude >= 0.3:
                qualidade = QualidadeDados.REGULAR
            else:
                qualidade = QualidadeDados.RUIM
            
            return ResultadoValidacao(
                pipeline="Pipeline Histórico",
                qualidade=qualidade,
                dados_reais=dados_reais,
                dados_atualizados=True,
                completude=completude,
                latencia_ms=latencia,
                erros=erros,
                avisos=avisos,
                metricas=metricas,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            latencia = (time.time() - inicio) * 1000
            erros.append(f"Exceção: {str(e)}")
            return self._criar_resultado_falha("Pipeline Histórico", latencia, erros)
    
    def _verificar_dados_reais_mercado(self, dados: Dict) -> bool:
        """Verifica se dados de mercado são reais ou simulados"""
        if not dados:
            return False
        
        # Verificar se há variação nos preços das ações
        stocks = dados.get('stocks', {})
        if not stocks:
            return False
        
        precos = [d.get('price', 0) for d in stocks.values() if isinstance(d, dict) and d.get('price', 0) > 0]
        if len(precos) < 2:
            return len(precos) == 1  # OK se tiver pelo menos 1
        
        # Calcular coeficiente de variação
        std = np.std(precos)
        mean = np.mean(precos)
        cv = std / mean if mean > 0 else 0
        
        # Se variação for muito baixa, podem ser dados fixos
        return cv > 0.01
    
    def _verificar_atualizacao_mercado(self, dados: Dict) -> bool:
        """Verifica se dados de mercado estão atualizados"""
        # Verificar timestamps
        agora = datetime.now()
        for key, value in dados.items():
            if isinstance(value, dict) and 'timestamp' in value:
                try:
                    ts = datetime.fromisoformat(value['timestamp'])
                    idade_horas = (agora - ts).total_seconds() / 3600
                    if idade_horas > 24:  # Mais de 24 horas
                        return False
                except:
                    pass
        return True
    
    def _calcular_completude_mercado(self, dados: Dict) -> float:
        """Calcula completude dos dados de mercado"""
        indices_esperados = ['^BVSP', '^GSPC', '^IXIC']
        stocks = dados.get('stocks', {})
        encontrados = sum(1 for idx in indices_esperados if idx in stocks and isinstance(stocks[idx], dict) and stocks[idx].get('price', 0) > 0)
        return encontrados / len(indices_esperados)
    
    def _verificar_variabilidade(self, dados: Dict) -> float:
        """Verifica variabilidade dos dados"""
        valores = []
        
        # Extrair preços de stocks
        stocks = dados.get('stocks', {})
        for value in stocks.values():
            if isinstance(value, dict):
                preco = value.get('price', 0)
                if preco > 0:
                    valores.append(preco)
        
        # Extrair preços de crypto
        crypto = dados.get('crypto', {})
        for value in crypto.values():
            if isinstance(value, dict):
                preco = value.get('price', 0)
                if preco > 0:
                    valores.append(preco)
        
        if len(valores) < 2:
            return 0.0
        
        return np.std(valores) / np.mean(valores) if np.mean(valores) > 0 else 0.0
    
    def _verificar_dados_reais_crypto(self, cryptos: Dict) -> bool:
        """Verifica se dados de cripto são reais"""
        # BTC nunca deve ser zero e deve estar em range razoável
        # Aceitar tanto 'BTC' quanto 'BTCUSDT' como chave
        btc_price = cryptos.get('BTC', {}).get('price', 0) or cryptos.get('BTCUSDT', {}).get('price', 0)
        if btc_price == 0 or btc_price < 10000 or btc_price > 150000:
            return False
        
        # Verificar se há variação entre diferentes criptos
        precos = [d.get('price', 0) for d in cryptos.values() if isinstance(d, dict) and d.get('price', 0) > 0]
        if len(precos) < 2:
            return False
        
        # Preços não podem ser todos iguais
        if len(set(precos)) == 1:
            return False
        
        return True
    
    def _verificar_dados_reais_acoes(self, acoes: Dict) -> bool:
        """Verifica se dados de ações são reais"""
        if not acoes:
            return False
        
        # Verificar se preços são diferentes entre si
        precos = [d.get('price', 0) for d in acoes.values() if d.get('price', 0) > 0]
        if len(precos) < 2:
            return len(precos) == 1  # OK se tiver pelo menos 1
        
        # Preços não podem ser todos iguais
        if len(set(precos)) == 1:
            return False
        
        return True
    
    def _verificar_dados_reais_fundos(self, rentabilidades: Dict) -> bool:
        """Verifica se dados de fundos são reais"""
        if not rentabilidades:
            return False
        
        # Coletar todos os valores de rentabilidade
        valores = []
        for ano, meses in rentabilidades.items():
            valores.extend(meses.values())
        
        if len(valores) < 3:
            return len(valores) > 0  # OK se tiver pelo menos algum
        
        # Valores não podem ser todos iguais
        if len(set(valores)) == 1:
            return False
        
        # Verificar se há variação razoável
        std = np.std(valores)
        return std > 0.001  # Pelo menos 0.1% de variação
    
    def _verificar_dados_reais_cambio(self, exchange_rates: Dict) -> bool:
        """Verifica se dados de câmbio são reais"""
        usd_brl = exchange_rates.get('USD_BRL', 0)
        
        # USD/BRL deve estar em range razoável
        if usd_brl < 4.0 or usd_brl > 7.0:
            return False
        
        # Verificar se não é valor redondo óbvio (ex: 5.0, 5.5)
        if usd_brl == round(usd_brl, 1):
            return False
        
        return True
    
    def _criar_resultado_falha(self, pipeline: str, latencia: float, erros: List[str]) -> ResultadoValidacao:
        """Cria resultado de falha"""
        return ResultadoValidacao(
            pipeline=pipeline,
            qualidade=QualidadeDados.FALHOU,
            dados_reais=False,
            dados_atualizados=False,
            completude=0.0,
            latencia_ms=latencia,
            erros=erros,
            avisos=[],
            metricas={},
            timestamp=datetime.now().isoformat()
        )
    
    def _imprimir_resultado(self, resultado: ResultadoValidacao):
        """Imprime resultado da validação"""
        # Símbolos baseados na qualidade (ASCII-safe para Windows)
        symbol_map = {
            QualidadeDados.EXCELENTE: "[OK]",
            QualidadeDados.BOM: "[+]",
            QualidadeDados.REGULAR: "[~]",
            QualidadeDados.RUIM: "[-]",
            QualidadeDados.SIMULADO: "[!]",
            QualidadeDados.FALHOU: "[X]"
        }
        
        symbol = symbol_map.get(resultado.qualidade, "[?]")
        
        print(f"   {symbol} Qualidade: {resultado.qualidade.value}")
        print(f"   [D] Dados Reais: {'Sim' if resultado.dados_reais else 'NAO'}")
        print(f"   [A] Atualizados: {'Sim' if resultado.dados_atualizados else 'Nao'}")
        print(f"   [C] Completude: {resultado.completude:.1%}")
        print(f"   [T] Latencia: {resultado.latencia_ms:.0f}ms")
        
        if resultado.erros:
            print(f"   [ERROS]:")
            for erro in resultado.erros:
                print(f"      - {erro}")
        
        if resultado.avisos:
            print(f"   [AVISOS]:")
            for aviso in resultado.avisos[:3]:  # Mostrar apenas 3 primeiros
                print(f"      - {aviso}")
        
        if resultado.metricas:
            print(f"   [METRICAS]: {list(resultado.metricas.keys())}")
    
    def _gerar_relatorio_consolidado(self) -> Dict[str, Any]:
        """Gera relatório consolidado de todas as validações"""
        print("\n" + "="*70)
        print("RELATORIO CONSOLIDADO DE VALIDACAO DOS PIPELINES")
        print("="*70)
        print()
        
        # Estatísticas gerais
        total_pipelines = len(self.resultados)
        pipelines_funcionais = sum(1 for r in self.resultados if r.qualidade != QualidadeDados.FALHOU)
        pipelines_com_dados_reais = sum(1 for r in self.resultados if r.dados_reais)
        pipelines_excelentes = sum(1 for r in self.resultados if r.qualidade == QualidadeDados.EXCELENTE)
        pipelines_simulados = sum(1 for r in self.resultados if r.qualidade == QualidadeDados.SIMULADO)
        
        print(f"[T] Total de Pipelines Testados: {total_pipelines}")
        print(f"[OK] Pipelines Funcionais: {pipelines_funcionais}/{total_pipelines}")
        print(f"[R] Pipelines com Dados REAIS: {pipelines_com_dados_reais}/{total_pipelines}")
        print(f"[E] Pipelines Excelentes: {pipelines_excelentes}/{total_pipelines}")
        print(f"[S] Pipelines com Dados Simulados: {pipelines_simulados}/{total_pipelines}")
        print()
        
        # Tabela resumo
        print("RESUMO POR PIPELINE:")
        print("-" * 70)
        print(f"{'Pipeline':<25} {'Qualidade':<12} {'Reais':<8} {'Completo':<10}")
        print("-" * 70)
        
        for resultado in self.resultados:
            nome = resultado.pipeline.replace("Pipeline ", "")
            qualidade = resultado.qualidade.value[:10]
            reais = "SIM" if resultado.dados_reais else "NÃO"
            completude = f"{resultado.completude:.1%}"
            
            print(f"{nome:<25} {qualidade:<12} {reais:<8} {completude:<10}")
        
        print("-" * 70)
        print()
        
        # Avaliação final
        print("AVALIACAO FINAL:")
        print("-" * 70)
        
        if pipelines_simulados > 0:
            print(f"[X] CRITICO: {pipelines_simulados} pipeline(s) usando dados SIMULADOS!")
            print("   Os calculos da carteira NAO sao confiaveis.")
            print()
        
        if pipelines_com_dados_reais == total_pipelines:
            print("[OK] EXCELENTE: Todos os pipelines usam dados REAIS!")
        elif pipelines_com_dados_reais >= total_pipelines * 0.7:
            print("[+] BOM: Maioria dos pipelines usa dados reais.")
        else:
            print("[-] RUIM: Muitos pipelines NAO usam dados reais!")
        
        print()
        
        completude_media = sum(r.completude for r in self.resultados) / len(self.resultados)
        print(f"[C] Completude Media: {completude_media:.1%}")
        
        latencia_media = sum(r.latencia_ms for r in self.resultados) / len(self.resultados)
        print(f"[T] Latencia Media: {latencia_media:.0f}ms")
        
        print()
        print("="*70)
        
        # Gerar relatório JSON
        relatorio = {
            'timestamp': datetime.now().isoformat(),
            'versao': '1.0.0',
            'estatisticas': {
                'total_pipelines': total_pipelines,
                'pipelines_funcionais': pipelines_funcionais,
                'pipelines_com_dados_reais': pipelines_com_dados_reais,
                'pipelines_excelentes': pipelines_excelentes,
                'pipelines_simulados': pipelines_simulados,
                'completude_media': completude_media,
                'latencia_media_ms': latencia_media
            },
            'resultados': [asdict(r) for r in self.resultados]
        }
        
        # Salvar relatório
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"relatorio_validacao_pipelines_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(relatorio, f, indent=2, ensure_ascii=False)
        
        print(f"[SAVE] Relatorio detalhado salvo em: {filename}")
        print()
        
        return relatorio


def main():
    """Função principal"""
    print()
    print("=" + "="*68 + "=")
    print("|" + " "*15 + "VALIDACAO RIGOROSA DOS PIPELINES" + " "*21 + "|")
    print("|" + " "*68 + "|")
    print("|" + " "*10 + "Sistema de Verificacao de Dados Reais vs Simulados" + " "*7 + "|")
    print("=" + "="*68 + "=")
    print()
    
    validador = ValidadorPipelines()
    relatorio = validador.validar_todos_pipelines()
    
    # Análise final
    pipelines_simulados = relatorio['estatisticas']['pipelines_simulados']
    pipelines_reais = relatorio['estatisticas']['pipelines_com_dados_reais']
    total = relatorio['estatisticas']['total_pipelines']
    
    print()
    print("CONCLUSAO:")
    print("="*70)
    
    if pipelines_simulados == 0 and pipelines_reais == total:
        print("[OK] TODOS OS PIPELINES ESTAO USANDO DADOS REAIS!")
        print("   O sistema esta configurado corretamente.")
        print("   Os calculos da carteira sao confiaveis.")
        return 0
    elif pipelines_simulados > 0:
        print("[X] ATENCAO: Foram detectados pipelines com DADOS SIMULADOS!")
        print(f"   {pipelines_simulados}/{total} pipeline(s) nao estao funcionando corretamente.")
        print("   Os calculos da carteira NAO sao confiaveis.")
        print()
        print("RECOMENDACAO:")
        print("   1. Verifique as configuracoes das APIs")
        print("   2. Confirme que as credenciais estao corretas")
        print("   3. Teste a conectividade com as APIs externas")
        print("   4. Revise o codigo que usa valores hardcoded")
        return 1
    else:
        print("[~] PARCIAL: Alguns pipelines estao funcionando, mas nao todos.")
        print(f"   {pipelines_reais}/{total} pipeline(s) com dados reais.")
        print("   Revise os pipelines com problemas.")
        return 1


if __name__ == "__main__":
    # Forçar UTF-8 no Windows
    import sys
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n[X] Validacao interrompida pelo usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n[X] Erro fatal: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

