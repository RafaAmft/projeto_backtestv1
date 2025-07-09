#!/usr/bin/env python3
"""
Painel Streamlit - Coletor de Dados de Portfólio (Versão 3.0)
=============================================================

Versão corrigida com:
- Sem loop infinito de cotações
- set_page_config() corrigido
- Scraping funcionando
- Todas as seções (fundos, ações, criptos, renda fixa)
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import sys
from typing import Dict, List, Optional, Tuple
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import logging

# Adicionar caminhos do projeto ANTES de qualquer import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuração da página (APENAS UMA VEZ)
if 'page_config_set' not in st.session_state:
    st.set_page_config(
        page_title="Coletor de Portfólio Financeiro v3.0",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    st.session_state.page_config_set = True

# Importar módulos do projeto
try:
    from core.market_indices_fixed import MarketIndicesManager
    from examples.portfolio_analysis_example import PortfolioAnalyzer
    from examples.temporal_portfolio_analysis import TemporalPortfolioAnalyzer
    from dashboard.fund_cache_manager import get_cache_manager
except ImportError as e:
    st.error(f"Erro ao importar módulos: {e}")

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        color: #2e8b57;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .asset-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #f5c6cb;
    }
    .debug-info {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ffeaa7;
        font-family: monospace;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Inicializar session_state
if 'fundos_data' not in st.session_state:
    st.session_state.fundos_data = []
if 'acoes_data' not in st.session_state:
    st.session_state.acoes_data = []
if 'crypto_data' not in st.session_state:
    st.session_state.crypto_data = []
if 'renda_fixa_data' not in st.session_state:
    st.session_state.renda_fixa_data = []
if 'market_manager' not in st.session_state:
    st.session_state.market_manager = None

def parse_value(value_str):
    """Extrai o valor de rentabilidade de uma string que pode conter múltiplos valores"""
    if not value_str or value_str == '--':
        return None
    
    try:
        # Remove espaços e quebras de linha
        value_str = value_str.strip()
        
        # Se contém '%', extrai o primeiro valor (rentabilidade)
        if '%' in value_str:
            # Divide pela primeira ocorrência de '%' e pega a parte antes
            parts = value_str.split('%', 1)
            rentabilidade_str = parts[0].strip()
            
            # Remove vírgulas e converte para float
            rentabilidade_str = rentabilidade_str.replace(',', '.')
            return float(rentabilidade_str)
        
        # Se não tem '%', tenta converter diretamente
        value_str = value_str.replace(',', '.')
        return float(value_str)
        
    except (ValueError, AttributeError) as e:
        return None

class PortfolioDataCollectorV3:
    """Classe melhorada para coletar dados de portfólio (sem loop infinito)"""
    
    def __init__(self):
        try:
            # Usar singleton pattern para MarketIndicesManager
            if hasattr(st.session_state, 'market_manager') and st.session_state.market_manager is None:
                st.session_state.market_manager = MarketIndicesManager()
            if hasattr(st.session_state, 'market_manager'):
                self.market_data = st.session_state.market_manager
            else:
                self.market_data = MarketIndicesManager()
            self.portfolio_analyzer = PortfolioAnalyzer()
            self.temporal_analyzer = TemporalPortfolioAnalyzer()
            # Inicializar cache_manager sempre, mesmo fora do Streamlit
            try:
                from dashboard.fund_cache_manager import get_cache_manager
                self.cache_manager = get_cache_manager()
            except Exception as e:
                import sys
                print(f"Erro ao importar ou inicializar get_cache_manager: {e}", file=sys.stderr)
                self.cache_manager = None
            # Configurar logging
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
            self.logger = logging.getLogger("PortfolioCollectorV3")
        except Exception as e:
            if hasattr(st, 'error'):
                st.error(f"Erro ao inicializar módulos: {e}")
            else:
                print(f"Erro ao inicializar PortfolioDataCollectorV3: {e}")
    
    def buscar_slug_fundo(self, cnpj: str) -> Tuple[Optional[str], Optional[str]]:
        """Busca o slug do fundo no Mais Retorno com múltiplas estratégias"""
        def formatar_cnpj(cnpj_str):
            cnpj = ''.join(filter(str.isdigit, str(cnpj_str)))
            if len(cnpj) != 14:
                return cnpj
            return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
        
        def buscar_com_query(query):
            url = f"https://duckduckgo.com/?q={query}"
            
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            try:
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                driver.get(url)
                time.sleep(3)  # Aumentar tempo de espera
                
                links = driver.find_elements(By.XPATH, "//a[contains(@href, 'maisretorno.com/fundo')]")
                for link in links:
                    href = link.get_attribute("href")
                    if "maisretorno.com/fundo/" in href:
                        slug = href.split("/")[-1]
                        return slug, href
                return None, None
            except Exception as e:
                self.logger.error(f"Erro na busca com query '{query}': {e}")
                return None, None
            finally:
                try:
                    driver.quit()
                except:
                    pass
        
        # Estratégia 1: Busca direta com CNPJ formatado
        cnpj_formatado = formatar_cnpj(cnpj)
        query1 = f"site:maisretorno.com/fundo {cnpj_formatado}"
        slug, url = buscar_com_query(query1)
        if slug:
            return slug, url
        
        # Estratégia 2: Busca com CNPJ sem formatação
        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
        query2 = f"site:maisretorno.com/fundo {cnpj_limpo}"
        slug, url = buscar_com_query(query2)
        if slug:
            return slug, url
        
        # Estratégia 3: Busca com parte do CNPJ (primeiros 8 dígitos)
        if len(cnpj_limpo) >= 8:
            cnpj_parcial = cnpj_limpo[:8]
            query3 = f"site:maisretorno.com/fundo {cnpj_parcial}"
            slug, url = buscar_com_query(query3)
            if slug:
                return slug, url
        
        # Estratégia 4: Busca com CNPJ em diferentes formatos
        formatos_cnpj = [
            cnpj_formatado,
            cnpj_limpo,
            f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}",
            f"{cnpj_limpo[:2]}{cnpj_limpo[2:5]}{cnpj_limpo[5:8]}{cnpj_limpo[8:12]}{cnpj_limpo[12:]}"
        ]
        
        for formato in formatos_cnpj:
            if formato != cnpj_formatado:  # Evitar repetir a primeira busca
                query = f"site:maisretorno.com/fundo {formato}"
                slug, url = buscar_com_query(query)
                if slug:
                    return slug, url
        
        return None, None
    
    def extrair_dados_fundo(self, slug: str, cnpj: str, force_debug: bool = False) -> Optional[Dict]:
        """
        Extrai dados de rentabilidade do fundo com múltiplas estratégias
        """
        # Se não for debug forçado, verificar cache primeiro
        if not force_debug:
            cached_data = self.cache_manager.get_fund_data(cnpj)
            if cached_data:
                self.logger.info(f"[CACHE] Dados do fundo {cnpj} recuperados do cache.")
                return cached_data
        
        url = f"https://maisretorno.com/fundo/{slug}"
        self.logger.info(f"[SCRAPING] Iniciando scraping para {slug} - {url}")
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
            driver.get(url)
            time.sleep(3)
            
            # Salvar HTML para debug se necessário
            if force_debug:
                with open(f"debug_{slug}.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                self.logger.info(f"[DEBUG] HTML salvo como debug_{slug}.html")
            
            # Múltiplas estratégias para encontrar a tabela
            tabela_encontrada = False
            rentabilidades = {}
            
            # Estratégia 1: Buscar por ID específico
            try:
                tabela = driver.find_element(By.ID, "rentabilidade-mensal")
                tabela_encontrada = True
                self.logger.info("[SCRAPING] Tabela encontrada por ID")
            except:
                pass
            
            # Estratégia 2: Buscar por classe específica
            if not tabela_encontrada:
                try:
                    tabela = driver.find_element(By.CLASS_NAME, "table-rentabilidade")
                    tabela_encontrada = True
                    self.logger.info("[SCRAPING] Tabela encontrada por classe")
                except:
                    pass
            
            # Estratégia 3: Buscar por texto específico
            if not tabela_encontrada:
                try:
                    elementos = driver.find_elements(By.XPATH, "//*[contains(text(), 'Rentabilidade Mensal')]")
                    if elementos:
                        # Procurar tabela próxima ao texto
                        for elemento in elementos:
                            tabela = elemento.find_element(By.XPATH, "./following-sibling::table")
                            if tabela:
                                tabela_encontrada = True
                                self.logger.info("[SCRAPING] Tabela encontrada por texto")
                                break
                except:
                    pass
            
            # Estratégia 4: Buscar qualquer tabela com dados de rentabilidade
            if not tabela_encontrada:
                try:
                    tabelas = driver.find_elements(By.TAG_NAME, "table")
                    for tabela in tabelas:
                        html = tabela.get_attribute("innerHTML")
                        if "Jan" in html and "Fev" in html and "Mar" in html:
                            tabela_encontrada = True
                            self.logger.info("[SCRAPING] Tabela encontrada por conteúdo")
                            break
                except:
                    pass
            
            if tabela_encontrada:
                # Processar dados da tabela
                soup = BeautifulSoup(tabela.get_attribute("innerHTML"), "html.parser")
                linhas = soup.find_all("tr")
                
                for linha in linhas:
                    celulas = linha.find_all(["td", "th"])
                    if len(celulas) >= 14:  # Cabeçalho + 12 meses
                        # Verificar se é linha de dados (contém ano)
                        primeiro_campo = celulas[0].get_text(strip=True)
                        if primeiro_campo.isdigit() and len(primeiro_campo) == 4:  # Ano
                            ano = primeiro_campo
                            rentabilidades[ano] = {}
                            
                            # Meses em ordem
                            meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                                    'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
                            
                            # Processa cada mês
                            for i, month in enumerate(meses):
                                if i < len(celulas) - 2:  # -2 para pular 'No ano' e '12 meses'
                                    valor_celula = celulas[i + 2].get_text(strip=True)
                                    valor_parsed = parse_value(valor_celula)
                                    
                                    if valor_parsed is not None:
                                        rentabilidades[ano][month] = valor_parsed / 100  # Converter para decimal
                                        self.logger.info(f"[SCRAPING] {ano}/{month}: {valor_parsed/100:.4f}")
                
                # Salvar no cache
                dados_fundo = {
                    'cnpj': cnpj,
                    'slug': slug,
                    'rentabilidades': rentabilidades,
                    'timestamp': datetime.now().isoformat()
                }
                
                self.cache_manager.save_fund_data(cnpj, dados_fundo)
                self.logger.info(f"[SCRAPING] Dados salvos no cache para {cnpj}")
                
                return dados_fundo
            else:
                self.logger.error(f"[SCRAPING] Tabela de rentabilidade não encontrada para {slug}")
                return None
                
        except Exception as e:
            self.logger.error(f"[SCRAPING] Erro ao extrair dados: {e}")
            return None
        finally:
            try:
                driver.quit()
            except:
                pass

def main():
    """Função principal do dashboard"""
    st.markdown('<h1 class="main-header">📊 Coletor de Portfólio Financeiro v3.0</h1>', unsafe_allow_html=True)
    
    # Sidebar com configurações
    st.sidebar.markdown("## ⚙️ Configurações")
    
    # Modo debug
    modo_debug = st.sidebar.checkbox("🐛 Modo Debug", value=False, help="Força novo scraping e mostra logs detalhados")
    
    # Período de análise
    periodo_analise = st.sidebar.selectbox(
        "📅 Período de Análise",
        ["12 meses", "24 meses", "36 meses", "60 meses"],
        index=0
    )
    
    # Data de referência
    data_referencia = st.sidebar.date_input(
        "📆 Data de Referência",
        value=datetime.now().date(),
        max_value=datetime.now().date()
    )
    
    # Inicializar coletor (singleton)
    if 'collector' not in st.session_state:
        st.session_state.collector = PortfolioDataCollectorV3()
    
    collector = st.session_state.collector
    
    # Botão para limpar dados
    if st.sidebar.button("🗑️ Limpar Todos os Dados"):
        st.session_state.fundos_data = []
        st.session_state.acoes_data = []
        st.session_state.crypto_data = []
        st.session_state.renda_fixa_data = []
        st.success("✅ Todos os dados foram limpos!")
        st.rerun()
    
    # Estatísticas do cache
    st.sidebar.markdown("## 💾 Cache de Fundos")
    cache_stats = collector.cache_manager.get_cache_stats()
    st.sidebar.markdown(f"📊 Total: {cache_stats['total_funds']}")
    st.sidebar.markdown(f"✅ Válidos: {cache_stats['valid_funds']}")
    st.sidebar.markdown(f"⚠️ Expirados: {cache_stats['expired_funds']}")
    st.sidebar.markdown(f"📁 Tamanho: {cache_stats['cache_size_mb']} MB")
    
    # Botões de gerenciamento do cache
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🧹 Limpar Expirados"):
            removed = collector.cache_manager.clear_expired_cache()
            st.success(f"🗑️ {removed} entradas removidas!")
            st.rerun()
    
    with col2:
        if st.button("🗑️ Limpar Tudo"):
            collector.cache_manager.clear_all_cache()
            st.success("🗑️ Cache limpo!")
            st.rerun()
    
    # Mostrar dados coletados
    if st.session_state.fundos_data or st.session_state.acoes_data or st.session_state.crypto_data or st.session_state.renda_fixa_data:
        st.sidebar.markdown("## 📊 Dados Coletados")
        st.sidebar.markdown(f"🏦 Fundos: {len(st.session_state.fundos_data)}")
        st.sidebar.markdown(f"📈 Ações: {len(st.session_state.acoes_data)}")
        st.sidebar.markdown(f"🪙 Criptos: {len(st.session_state.crypto_data)}")
        st.sidebar.markdown(f"💰 Renda Fixa: {len(st.session_state.renda_fixa_data)}")
    
    # Formulário principal
    st.markdown('<h2 class="section-header">🏦 Fundos de Investimento</h2>', unsafe_allow_html=True)
    
    for i in range(5):
        with st.expander(f"Fundo {i+1}", expanded=(i==0)):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                cnpj = st.text_input(f"CNPJ do Fundo {i+1}", key=f"cnpj_{i}")
            
            with col2:
                valor_investido = st.number_input(
                    f"Valor Investido (R$)", 
                    min_value=0.0, 
                    value=10000.0, 
                    step=1000.0,
                    key=f"valor_fundo_{i}"
                )
            
            with col3:
                if st.button(f"🔍 Buscar {i+1}", key=f"buscar_fundo_{i}"):
                    if cnpj:
                        with st.spinner(f"Buscando dados do fundo {cnpj}..."):
                            slug, link = collector.buscar_slug_fundo(cnpj)
                            if slug:
                                st.success(f"Slug encontrado: {slug}")
                                
                                # Usar modo debug se ativado
                                dados_fundo = collector.extrair_dados_fundo(slug, cnpj, force_debug=modo_debug)
                                
                                if dados_fundo:
                                    # Verificar se já existe
                                    fundo_existente = next((f for f in st.session_state.fundos_data if f['cnpj'] == cnpj), None)
                                    if fundo_existente:
                                        # Atualizar dados existentes
                                        fundo_existente.update({
                                            'slug': slug,
                                            'valor_investido': valor_investido,
                                            'dados': dados_fundo
                                        })
                                        st.success("✅ Dados do fundo atualizados!")
                                    else:
                                        # Adicionar novo fundo
                                        st.session_state.fundos_data.append({
                                            'cnpj': cnpj,
                                            'slug': slug,
                                            'valor_investido': valor_investido,
                                            'dados': dados_fundo
                                        })
                                        st.success("✅ Fundo adicionado com sucesso!")
                                    
                                    # Mostrar informações de debug se ativado
                                    if modo_debug:
                                        meses_encontrados = sum(len(ano_data) for ano_data in dados_fundo['rentabilidades'].values())
                                        st.info(f"🐛 Debug: {meses_encontrados} meses de dados encontrados")
                                        st.info(f"🐛 Debug: Arquivo HTML salvo como debug_{slug}.html")
                                    
                                    st.rerun()
                                else:
                                    st.error("❌ Erro ao extrair dados do fundo")
                                    if modo_debug:
                                        st.info(f"🐛 Debug: Verifique o arquivo debug_{slug}.html para análise")
                            else:
                                st.error("❌ Fundo não encontrado no Mais Retorno")
                    else:
                        st.error("❌ Digite um CNPJ válido")
    
    # Seção de Ações
    st.markdown('<h2 class="section-header">📈 Ações</h2>', unsafe_allow_html=True)
    
    for i in range(5):
        with st.expander(f"Ação {i+1}", expanded=(i==0)):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                codigo = st.text_input(f"Código da Ação {i+1}", key=f"acao_{i}")
            
            with col2:
                quantidade = st.number_input(
                    f"Quantidade", 
                    min_value=0, 
                    value=100, 
                    step=10,
                    key=f"qtd_acao_{i}"
                )
            
            with col3:
                preco_entrada = st.number_input(
                    f"Preço de Entrada (R$)", 
                    min_value=0.0, 
                    value=50.0, 
                    step=0.01,
                    key=f"preco_acao_{i}"
                )
            
            if st.button(f"➕ Adicionar Ação {i+1}", key=f"add_acao_{i}"):
                if codigo and quantidade > 0 and preco_entrada > 0:
                    # Verificar se já existe
                    acao_existente = next((a for a in st.session_state.acoes_data if a['codigo'] == codigo), None)
                    if acao_existente:
                        st.error("❌ Esta ação já foi adicionada!")
                    else:
                        st.session_state.acoes_data.append({
                            'codigo': codigo,
                            'quantidade': quantidade,
                            'preco_entrada': preco_entrada
                        })
                        st.success("✅ Ação adicionada com sucesso!")
                        st.rerun()
                else:
                    st.error("❌ Preencha todos os campos corretamente")
    
    # Seção de Criptomoedas
    st.markdown('<h2 class="section-header">🪙 Criptomoedas</h2>', unsafe_allow_html=True)
    
    for i in range(5):
        with st.expander(f"Cripto {i+1}", expanded=(i==0)):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                codigo = st.text_input(f"Código da Cripto {i+1}", key=f"crypto_{i}")
            
            with col2:
                quantidade = st.number_input(
                    f"Quantidade", 
                    min_value=0.0, 
                    value=1.0, 
                    step=0.1,
                    key=f"qtd_crypto_{i}"
                )
            
            with col3:
                preco_entrada = st.number_input(
                    f"Preço de Entrada (USD)", 
                    min_value=0.0, 
                    value=50000.0, 
                    step=100.0,
                    key=f"preco_crypto_{i}"
                )
            
            if st.button(f"➕ Adicionar Cripto {i+1}", key=f"add_crypto_{i}"):
                if codigo and quantidade > 0 and preco_entrada > 0:
                    # Verificar se já existe
                    crypto_existente = next((c for c in st.session_state.crypto_data if c['codigo'] == codigo), None)
                    if crypto_existente:
                        st.error("❌ Esta cripto já foi adicionada!")
                    else:
                        st.session_state.crypto_data.append({
                            'codigo': codigo,
                            'quantidade': quantidade,
                            'preco_entrada': preco_entrada
                        })
                        st.success("✅ Cripto adicionada com sucesso!")
                        st.rerun()
                else:
                    st.error("❌ Preencha todos os campos corretamente")
    
    # Seção de Renda Fixa
    st.markdown('<h2 class="section-header">💰 Renda Fixa</h2>', unsafe_allow_html=True)
    
    for i in range(5):
        with st.expander(f"Renda Fixa {i+1}", expanded=(i==0)):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                nome = st.text_input(f"Nome do Título {i+1}", key=f"renda_fixa_{i}")
            
            with col2:
                valor_investido = st.number_input(
                    f"Valor Investido (R$)", 
                    min_value=0.0, 
                    value=10000.0, 
                    step=1000.0,
                    key=f"valor_renda_fixa_{i}"
                )
            
            with col3:
                rentabilidade = st.number_input(
                    f"Rentabilidade (% a.a.)", 
                    min_value=0.0, 
                    value=12.0, 
                    step=0.1,
                    key=f"rent_renda_fixa_{i}"
                )
            
            if st.button(f"➕ Adicionar Renda Fixa {i+1}", key=f"add_renda_fixa_{i}"):
                if nome and valor_investido > 0 and rentabilidade >= 0:
                    # Verificar se já existe
                    rf_existente = next((r for r in st.session_state.renda_fixa_data if r['nome'] == nome), None)
                    if rf_existente:
                        st.error("❌ Este título já foi adicionado!")
                    else:
                        st.session_state.renda_fixa_data.append({
                            'nome': nome,
                            'valor_investido': valor_investido,
                            'rentabilidade': rentabilidade
                        })
                        st.success("✅ Renda fixa adicionada com sucesso!")
                        st.rerun()
                else:
                    st.error("❌ Preencha todos os campos corretamente")
    
    # Botão para processar dados
    st.markdown('<h2 class="section-header">🚀 Processar Análise</h2>', unsafe_allow_html=True)
    
    if st.button("📊 Gerar Relatório Completo", type="primary", use_container_width=True):
        if not any([st.session_state.fundos_data, st.session_state.acoes_data, st.session_state.crypto_data, st.session_state.renda_fixa_data]):
            st.error("❌ Adicione pelo menos um ativo para gerar o relatório")
        else:
            with st.spinner("Processando análise completa..."):
                try:
                    # Preparar dados para análise
                    portfolio_data = {
                        'fundos': st.session_state.fundos_data,
                        'acoes': st.session_state.acoes_data,
                        'crypto': st.session_state.crypto_data,
                        'renda_fixa': st.session_state.renda_fixa_data,
                        'periodo': periodo_analise,
                        'data_referencia': data_referencia.isoformat()
                    }
                    
                    # Gerar relatório simples
                    relatorio = gerar_relatorio_simples(portfolio_data, collector)
                    
                    # Salvar relatório
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"relatorio_portfolio_v3_{timestamp}.txt"
                    
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(relatorio)
                    
                    # Mostrar relatório
                    st.markdown('<div class="success-message">', unsafe_allow_html=True)
                    st.success(f"✅ Relatório v3.0 gerado com sucesso! Salvo como: {filename}")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Exibir relatório
                    st.markdown("## 📋 Relatório Gerado")
                    st.text_area("Conteúdo do Relatório", relatorio, height=600)
                    
                    # Download do arquivo
                    st.download_button(
                        label="⬇️ Baixar Relatório TXT",
                        data=relatorio,
                        file_name=filename,
                        mime="text/plain"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Erro ao gerar relatório: {e}")

def gerar_relatorio_simples(portfolio_data: Dict, collector) -> str:
    """Gera um relatório simples do portfólio"""
    relatorio = []
    relatorio.append("=" * 60)
    relatorio.append("📊 RELATÓRIO DE PORTFÓLIO FINANCEIRO v3.0")
    relatorio.append("=" * 60)
    relatorio.append(f"📅 Data de Geração: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    relatorio.append(f"📊 Período de Análise: {portfolio_data['periodo']}")
    relatorio.append(f"📆 Data de Referência: {portfolio_data['data_referencia']}")
    relatorio.append("")
    
    # Resumo dos ativos
    total_fundos = len(portfolio_data['fundos'])
    total_acoes = len(portfolio_data['acoes'])
    total_crypto = len(portfolio_data['crypto'])
    total_renda_fixa = len(portfolio_data['renda_fixa'])
    
    relatorio.append("📈 RESUMO DOS ATIVOS:")
    relatorio.append(f"   🏦 Fundos de Investimento: {total_fundos}")
    relatorio.append(f"   📈 Ações: {total_acoes}")
    relatorio.append(f"   🪙 Criptomoedas: {total_crypto}")
    relatorio.append(f"   💰 Renda Fixa: {total_renda_fixa}")
    relatorio.append("")
    
    # Detalhes dos fundos
    if portfolio_data['fundos']:
        relatorio.append("🏦 FUNDOS DE INVESTIMENTO:")
        relatorio.append("-" * 40)
        for fundo in portfolio_data['fundos']:
            relatorio.append(f"   CNPJ: {fundo['cnpj']}")
            relatorio.append(f"   Slug: {fundo['slug']}")
            relatorio.append(f"   Valor Investido: R$ {fundo['valor_investido']:,.2f}")
            
            # Calcular meses de dados
            meses_total = sum(len(ano_data) for ano_data in fundo['dados']['rentabilidades'].values())
            relatorio.append(f"   Meses de Dados: {meses_total}")
            relatorio.append("")
    
    # Detalhes das ações
    if portfolio_data['acoes']:
        relatorio.append("📈 AÇÕES:")
        relatorio.append("-" * 40)
        for acao in portfolio_data['acoes']:
            valor_total = acao['quantidade'] * acao['preco_entrada']
            relatorio.append(f"   Código: {acao['codigo']}")
            relatorio.append(f"   Quantidade: {acao['quantidade']}")
            relatorio.append(f"   Preço de Entrada: R$ {acao['preco_entrada']:.2f}")
            relatorio.append(f"   Valor Total: R$ {valor_total:,.2f}")
            relatorio.append("")
    
    # Detalhes das criptos
    if portfolio_data['crypto']:
        relatorio.append("🪙 CRIPTOMOEDAS:")
        relatorio.append("-" * 40)
        for crypto in portfolio_data['crypto']:
            valor_total = crypto['quantidade'] * crypto['preco_entrada']
            relatorio.append(f"   Código: {crypto['codigo']}")
            relatorio.append(f"   Quantidade: {crypto['quantidade']}")
            relatorio.append(f"   Preço de Entrada: USD {crypto['preco_entrada']:.2f}")
            relatorio.append(f"   Valor Total: USD {valor_total:,.2f}")
            relatorio.append("")
    
    # Detalhes da renda fixa
    if portfolio_data['renda_fixa']:
        relatorio.append("💰 RENDA FIXA:")
        relatorio.append("-" * 40)
        for rf in portfolio_data['renda_fixa']:
            relatorio.append(f"   Nome: {rf['nome']}")
            relatorio.append(f"   Valor Investido: R$ {rf['valor_investido']:,.2f}")
            relatorio.append(f"   Rentabilidade: {rf['rentabilidade']:.2f}% a.a.")
            relatorio.append("")
    
    relatorio.append("=" * 60)
    relatorio.append("✅ Relatório gerado com sucesso!")
    relatorio.append("=" * 60)
    
    return "\n".join(relatorio)

if __name__ == "__main__":
    main() 