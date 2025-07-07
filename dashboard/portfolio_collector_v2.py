#!/usr/bin/env python3
"""
Painel Streamlit - Coletor de Dados de Portfólio (Versão 2.0)
=============================================================

Versão melhorada com:
- Scraping corrigido com múltiplas estratégias
- Logs detalhados para debug
- Modo de teste forçado
- Melhor tratamento de erros
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
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import logging

# Configuração da página
st.set_page_config(
    page_title="Coletor de Portfólio Financeiro v2.0",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Adicionar caminhos do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

class PortfolioDataCollectorV2:
    """Classe melhorada para coletar dados de portfólio"""
    
    def __init__(self):
        try:
            self.market_data = MarketIndicesManager()
            self.portfolio_analyzer = PortfolioAnalyzer()
            self.temporal_analyzer = TemporalPortfolioAnalyzer()
            self.cache_manager = get_cache_manager()
            
            # Configurar logging
            logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
            self.logger = logging.getLogger("PortfolioCollectorV2")
            
        except Exception as e:
            st.error(f"Erro ao inicializar módulos: {e}")
    
    def buscar_slug_fundo(self, cnpj: str) -> Tuple[Optional[str], Optional[str]]:
        """Busca o slug do fundo no Mais Retorno"""
        def formatar_cnpj(cnpj_str):
            cnpj = ''.join(filter(str.isdigit, str(cnpj_str)))
            if len(cnpj) != 14:
                return cnpj
            return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
        
        query = f"site:maisretorno.com/fundo {formatar_cnpj(cnpj)}"
        url = f"https://duckduckgo.com/?q={query}"
        
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        
        try:
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            time.sleep(2)
            
            links = driver.find_elements(By.XPATH, "//a[contains(@href, 'maisretorno.com/fundo')]")
            for link in links:
                href = link.get_attribute("href")
                if "maisretorno.com/fundo/" in href:
                    slug = href.split("/")[-1]
                    return slug, href
            return None, None
        except Exception as e:
            self.logger.error(f"Erro na busca do slug: {e}")
            return None, None
        finally:
            try:
                driver.quit()
            except:
                pass
    
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
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            time.sleep(5)  # Aumentar tempo de espera
            
            # Salvar HTML para debug
            debug_file = f"debug_{slug}.html"
            with open(debug_file, "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            self.logger.info(f"[DEBUG] HTML salvo em {debug_file}")
            
            soup = BeautifulSoup(driver.page_source, "html.parser")
            
            # Extrair nome do fundo
            nome_element = soup.find('h1') or soup.find('title')
            nome_fundo = nome_element.get_text().strip() if nome_element else "Fundo não identificado"
            self.logger.info(f"[SCRAPING] Nome do fundo: {nome_fundo}")
            
            dados = {
                'nome': nome_fundo,
                'cnpj': cnpj,
                'slug': slug,
                'url': url,
                'rentabilidades': {},
                'ultima_atualizacao': datetime.now().isoformat()
            }
            
            # Múltiplas estratégias para encontrar a tabela de rentabilidade
            tabela = None
            estrategia_usada = "Nenhuma"
            
            # Estratégia 1: Buscar por título específico
            titulo = soup.find(lambda tag: tag.name in ['h2', 'h3', 'h4'] and 'Rentabilidade' in tag.text)
            if titulo:
                self.logger.info(f"[SCRAPING] Título encontrado: {titulo.text}")
                tabela = titulo.find_next('table')
                if tabela:
                    estrategia_usada = "Título"
                    self.logger.info("✅ Tabela encontrada via título")
            
            # Estratégia 2: Buscar por classe específica
            if not tabela:
                tabela = soup.find('table', class_=lambda x: x and 'rentabilidade' in x.lower())
                if tabela:
                    estrategia_usada = "Classe"
                    self.logger.info("✅ Tabela encontrada via classe")
            
            # Estratégia 3: Buscar por ID específico
            if not tabela:
                tabela = soup.find('table', id=lambda x: x and 'rentabilidade' in x.lower())
                if tabela:
                    estrategia_usada = "ID"
                    self.logger.info("✅ Tabela encontrada via ID")
            
            # Estratégia 4: Buscar qualquer tabela com dados de rentabilidade
            if not tabela:
                tabelas = soup.find_all('table')
                self.logger.info(f"[SCRAPING] Total de tabelas encontradas: {len(tabelas)}")
                
                for i, tab in enumerate(tabelas):
                    texto_tabela = tab.get_text().lower()
                    if any(palavra in texto_tabela for palavra in ['jan', 'fev', 'mar', 'abr', 'mai', 'jun']):
                        tabela = tab
                        estrategia_usada = f"Conteúdo (tabela {i+1})"
                        self.logger.info(f"✅ Tabela encontrada via conteúdo (tabela {i+1})")
                        break
            
            # Estratégia 5: Buscar por div com dados de rentabilidade
            if not tabela:
                divs = soup.find_all('div')
                divs_com_rentabilidade = [d for d in divs if 'rentabilidade' in d.get_text().lower()]
                self.logger.info(f"[SCRAPING] Divs com 'rentabilidade': {len(divs_com_rentabilidade)}")
                
                for div in divs_com_rentabilidade:
                    tabela = div.find('table')
                    if tabela:
                        estrategia_usada = "Div"
                        self.logger.info("✅ Tabela encontrada via div")
                        break
            
            if tabela:
                self.logger.info(f"[SCRAPING] Processando tabela usando estratégia: {estrategia_usada}")
                linhas = tabela.find_all("tr")
                self.logger.info(f"[SCRAPING] Encontradas {len(linhas)} linhas na tabela")
                
                for i, tr in enumerate(linhas):
                    tds = tr.find_all(["td", "th"])
                    linha = [td.get_text(strip=True) for td in tds]
                    
                    # Log da primeira linha para debug
                    if i == 0:
                        self.logger.info(f"[DEBUG] Cabeçalho: {linha}")
                    
                    if i == 0 or not linha or not linha[0].isdigit():
                        continue
                    
                    ano = int(linha[0])
                    dados['rentabilidades'][ano] = {}
                    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
                    
                    self.logger.info(f"[SCRAPING] Processando ano {ano}: {linha}")
                    
                    # Processa cada mês
                    for i, month in enumerate(meses):
                        if i < len(linha) - 2:  # -2 para pular 'No ano' e 'Acumulado'
                            value_str = linha[i + 2]  # +2 para pular 'ANO' e nome do fundo
                            value = parse_value(value_str)
                            if value is not None:
                                dados['rentabilidades'][ano][month] = value / 100  # Converte para decimal
                                self.logger.info(f"[SCRAPING] {ano}/{month}: {value/100:.4f}")
            else:
                self.logger.warning(f"[SCRAPING] Tabela de rentabilidade não encontrada para {slug}")
                # Salvar informações sobre o que foi encontrado
                with open(f"debug_{slug}_info.txt", "w", encoding="utf-8") as f:
                    f.write(f"URL: {url}\n")
                    f.write(f"Nome: {nome_fundo}\n")
                    f.write(f"Tabelas encontradas: {len(soup.find_all('table'))}\n")
                    f.write(f"Divs com 'rentabilidade': {len([d for d in soup.find_all('div') if 'rentabilidade' in d.get_text().lower()])}\n")
                    f.write(f"Estratégia usada: {estrategia_usada}\n")
            
            # Salvar dados no cache
            if not force_debug:
                self.cache_manager.save_fund_data(cnpj, dados)
                self.logger.info(f"[SCRAPING] Dados extraídos e salvos para {cnpj}")
            
            return dados
            
        except Exception as e:
            self.logger.error(f"[SCRAPING] Erro ao extrair dados do fundo: {e}")
            st.error(f"Erro ao extrair dados do fundo: {e}")
            return None
        finally:
            try:
                driver.quit()
            except:
                pass

def main():
    """Função principal do painel v2.0"""
    
    st.markdown('<h1 class="main-header">📊 Coletor de Dados de Portfólio Financeiro v2.0</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    **Versão 2.0 - Melhorias implementadas:**
    - ✅ Scraping corrigido com múltiplas estratégias
    - ✅ Logs detalhados para debug
    - ✅ Modo de teste forçado
    - ✅ Melhor tratamento de erros
    
    **Tipos de ativos suportados:**
    - 🏦 **Fundos de Investimento** (5 fundos) - Busca automática por CNPJ
    - 📈 **Ações** (5 ações) - Dados em tempo real
    - 🪙 **Criptomoedas** (5 criptos) - Dados em tempo real
    - 💰 **Renda Fixa** (2 ativos) - Dados simulados
    """)
    
    # Inicializar coletor
    collector = PortfolioDataCollectorV2()
    
    # Sidebar para configurações
    st.sidebar.markdown("## ⚙️ Configurações v2.0")
    
    # Modo debug
    modo_debug = st.sidebar.checkbox("🐛 Modo Debug (Força novo scraping)")
    
    # Período de análise
    periodo_analise = st.sidebar.selectbox(
        "Período de Análise",
        ["1_ano", "3_anos", "5_anos"],
        format_func=lambda x: {
            "1_ano": "1 Ano",
            "3_anos": "3 Anos", 
            "5_anos": "5 Anos"
        }[x]
    )
    
    # Data de referência
    data_referencia = st.sidebar.date_input(
        "Data de Referência",
        value=datetime.now().date(),
        max_value=datetime.now().date()
    )
    
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
                    
                    # Gerar relatório (usar função existente)
                    from dashboard.portfolio_collector import gerar_relatorio_completo
                    relatorio = gerar_relatorio_completo(portfolio_data, collector)
                    
                    # Salvar relatório
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"relatorio_portfolio_v2_{timestamp}.txt"
                    
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(relatorio)
                    
                    # Mostrar relatório
                    st.markdown('<div class="success-message">', unsafe_allow_html=True)
                    st.success(f"✅ Relatório v2.0 gerado com sucesso! Salvo como: {filename}")
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

if __name__ == "__main__":
    main() 