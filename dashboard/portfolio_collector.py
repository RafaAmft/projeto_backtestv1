#!/usr/bin/env python3
"""
Painel Streamlit - Coletor de Dados de Portfólio
================================================

Este painel permite coletar dados de diferentes tipos de ativos:
- 5 Ações
- 5 Fundos (com busca por slug)
- 5 Criptomoedas  
- 2 Renda Fixa

E gera relatórios completos em formato TXT para auditoria.
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

# Configuração da página - DEVE SER A PRIMEIRA CHAMADA DO STREAMLIT
st.set_page_config(
    page_title="Coletor de Portfólio Financeiro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Adicionar caminhos do projeto
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar módulos do projeto
try:
    from core.market_indices import MarketIndicesManager
    from examples.portfolio_analysis_example import PortfolioAnalyzer
    from examples.temporal_portfolio_analysis import TemporalPortfolioAnalyzer
    from dashboard.fund_cache_manager import get_cache_manager
except ImportError as e:
    st.error(f"Erro ao importar módulos: {e}")
    st.info("Certifique-se de que todos os arquivos do projeto estão no lugar correto")

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

class PortfolioDataCollector:
    """Classe para coletar dados de portfólio"""
    
    def __init__(self):
        try:
            self.market_data = MarketIndicesManager()
            self.portfolio_analyzer = PortfolioAnalyzer()
            self.temporal_analyzer = TemporalPortfolioAnalyzer()
            self.cache_manager = get_cache_manager()
        except Exception as e:
            st.error(f"Erro ao inicializar módulos: {e}")
        
    def buscar_slug_fundo(self, cnpj: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Busca o slug do fundo no Mais Retorno usando DuckDuckGo
        
        Args:
            cnpj: CNPJ do fundo
            
        Returns:
            Tuple com (slug, link) ou (None, None) se não encontrado
        """
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
            st.error(f"Erro na busca do slug: {e}")
            return None, None
        finally:
            try:
                driver.quit()
            except:
                pass
    
    def extrair_dados_fundo(self, slug: str, cnpj: str) -> Optional[Dict]:
        """
        Extrai dados de rentabilidade do fundo
        Adiciona logs/prints para debug e garante serialização dos dados.
        """
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("extrair_dados_fundo")
        # Primeiro, verificar se já temos os dados em cache
        cached_data = self.cache_manager.get_fund_data(cnpj)
        if cached_data:
            logger.info(f"[CACHE] Dados do fundo {cnpj} recuperados do cache.")
            return cached_data
        url = f"https://maisretorno.com/fundo/{slug}"
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        try:
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            # Salvar HTML para debug
            with open(f"debug_{slug}.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            nome_element = soup.find('h1') or soup.find('title')
            nome_fundo = nome_element.get_text().strip() if nome_element else "Fundo não identificado"
            dados = {
                'nome': nome_fundo,
                'cnpj': cnpj,
                'slug': slug,
                'url': url,
                'rentabilidades': {},
                'ultima_atualizacao': datetime.now().isoformat()
            }
            # Tentar extrair rentabilidades da tabela
            titulo = soup.find(lambda tag: tag.name == 'h2' and 'Rentabilidade histórica' in tag.text)
            tabela = titulo.find_next('table') if titulo else soup.find('table')
            if tabela:
                linhas = tabela.find_all("tr")
                for i, tr in enumerate(linhas):
                    tds = tr.find_all(["td", "th"])
                    linha = [td.get_text(strip=True) for td in tds]
                    if i == 0 or not linha or not linha[0].isdigit():
                        continue
                    ano = int(linha[0])
                    dados['rentabilidades'][ano] = {}
                    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
                    for j, campo in enumerate(linha[2:14]):
                        if j < len(meses):
                            try:
                                valor = float(campo.replace('%', '').replace(',', '.')) / 100
                                dados['rentabilidades'][ano][meses[j]] = float(valor)
                            except Exception as e:
                                logger.warning(f"Erro ao converter valor do mês {meses[j]}: {campo} - {e}")
                                continue
            else:
                logger.warning(f"Tabela de rentabilidade não encontrada para {slug}")
            # Salvar dados no cache
            self.cache_manager.save_fund_data(cnpj, dados)
            logger.info(f"[SCRAPING] Dados extraídos e salvos para {cnpj}")
            return dados
        except Exception as e:
            logger.error(f"Erro ao extrair dados do fundo: {e}")
            st.error(f"Erro ao extrair dados do fundo: {e}")
            return None
        finally:
            try:
                driver.quit()
            except:
                pass

def main():
    """Função principal do painel"""
    
    st.markdown('<h1 class="main-header">📊 Coletor de Dados de Portfólio Financeiro</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    Este painel permite coletar dados de diferentes tipos de ativos e gerar relatórios completos.
    
    **Tipos de ativos suportados:**
    - 🏦 **Fundos de Investimento** (5 fundos) - Busca automática por CNPJ
    - 📈 **Ações** (5 ações) - Dados em tempo real
    - 🪙 **Criptomoedas** (5 criptos) - Dados em tempo real
    - 💰 **Renda Fixa** (2 ativos) - Dados simulados
    """)
    
    # Inicializar coletor
    collector = PortfolioDataCollector()
    
    # Sidebar para configurações
    st.sidebar.markdown("## ⚙️ Configurações")
    
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
                                dados_fundo = collector.extrair_dados_fundo(slug, cnpj)
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
                                    st.rerun()
                                else:
                                    st.error("❌ Erro ao extrair dados do fundo")
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
    
    st.markdown('<h2 class="section-header">🪙 Criptomoedas</h2>', unsafe_allow_html=True)
    
    for i in range(5):
        with st.expander(f"Cripto {i+1}", expanded=(i==0)):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                symbol = st.selectbox(
                    f"Criptomoeda {i+1}",
                    ["BTC", "ETH", "BNB", "SOL", "ADA", "DOT", "LINK", "MATIC", "AVAX", "UNI"],
                    key=f"crypto_{i}"
                )
            
            with col2:
                quantity = st.number_input(
                    f"Quantidade", 
                    min_value=0.0, 
                    value=1.0, 
                    step=0.1,
                    key=f"qtd_crypto_{i}"
                )
            
            with col3:
                entry_price = st.number_input(
                    f"Preço de Entrada (US$)", 
                    min_value=0.0, 
                    value=50000.0, 
                    step=100.0,
                    key=f"preco_crypto_{i}"
                )
            
            if st.button(f"➕ Adicionar Cripto {i+1}", key=f"add_crypto_{i}"):
                if quantity > 0 and entry_price > 0:
                    # Verificar se já existe
                    crypto_existente = next((c for c in st.session_state.crypto_data if c['symbol'] == symbol), None)
                    if crypto_existente:
                        st.error("❌ Esta criptomoeda já foi adicionada!")
                    else:
                        st.session_state.crypto_data.append({
                            'symbol': symbol,
                            'quantity': quantity,
                            'entry_price': entry_price
                        })
                        st.success("✅ Criptomoeda adicionada com sucesso!")
                        st.rerun()
                else:
                    st.error("❌ Preencha todos os campos corretamente")
    
    st.markdown('<h2 class="section-header">💰 Renda Fixa</h2>', unsafe_allow_html=True)
    
    for i in range(2):
        with st.expander(f"Renda Fixa {i+1}", expanded=(i==0)):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                tipo = st.selectbox(
                    f"Tipo {i+1}",
                    ["CDB", "LCI", "LCA", "Tesouro Direto", "Debêntures"],
                    key=f"renda_fixa_{i}"
                )
            
            with col2:
                valor = st.number_input(
                    f"Valor Investido (R$)", 
                    min_value=0.0, 
                    value=10000.0, 
                    step=1000.0,
                    key=f"valor_rf_{i}"
                )
            
            with col3:
                taxa_anual = st.number_input(
                    f"Taxa Anual (%)", 
                    min_value=0.0, 
                    value=12.0, 
                    step=0.1,
                    key=f"taxa_rf_{i}"
                )
            
            if st.button(f"➕ Adicionar Renda Fixa {i+1}", key=f"add_rf_{i}"):
                if valor > 0 and taxa_anual > 0:
                    # Verificar se já existe
                    rf_existente = next((rf for rf in st.session_state.renda_fixa_data if rf['tipo'] == tipo), None)
                    if rf_existente:
                        st.error("❌ Este tipo de renda fixa já foi adicionado!")
                    else:
                        st.session_state.renda_fixa_data.append({
                            'tipo': tipo,
                            'valor': valor,
                            'taxa_anual': taxa_anual / 100
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
                    
                    # Gerar relatório
                    relatorio = gerar_relatorio_completo(portfolio_data, collector)
                    
                    # Salvar relatório
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"relatorio_portfolio_{timestamp}.txt"
                    
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(relatorio)
                    
                    # Mostrar relatório
                    st.markdown('<div class="success-message">', unsafe_allow_html=True)
                    st.success(f"✅ Relatório gerado com sucesso! Salvo como: {filename}")
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

def gerar_relatorio_completo(portfolio_data: Dict, collector: PortfolioDataCollector) -> str:
    """
    Gera relatório completo em formato texto
    
    Args:
        portfolio_data: Dados do portfólio
        collector: Instância do coletor
        
    Returns:
        String com o relatório completo
    """
    timestamp = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
    
    relatorio = f"""
{'='*80}
                    RELATÓRIO DE PORTFÓLIO FINANCEIRO
{'='*80}

📅 Data de Geração: {timestamp}
📊 Período de Análise: {portfolio_data['periodo']}
📅 Data de Referência: {portfolio_data['data_referencia']}

{'='*80}

📋 RESUMO EXECUTIVO
{'-'*40}

🏦 FUNDOS DE INVESTIMENTO: {len(portfolio_data['fundos'])} fundos
📈 AÇÕES: {len(portfolio_data['acoes'])} ações  
🪙 CRIPTOMOEDAS: {len(portfolio_data['crypto'])} criptos
💰 RENDA FIXA: {len(portfolio_data['renda_fixa'])} ativos

{'='*80}

🏦 ANÁLISE DE FUNDOS DE INVESTIMENTO
{'-'*40}
"""
    
    # Análise de fundos
    total_fundos = 0
    for i, fundo in enumerate(portfolio_data['fundos'], 1):
        relatorio += f"""
Fundo {i}: {fundo['dados']['nome']}
CNPJ: {fundo['cnpj']}
Valor Investido: R$ {fundo['valor_investido']:,.2f}
Slug: {fundo['slug']}
URL: {fundo['dados']['url']}

Rentabilidades Disponíveis:
"""
        for ano, dados_ano in fundo['dados']['rentabilidades'].items():
            relatorio += f"  {ano}: {len(dados_ano)} meses de dados\n"
        
        total_fundos += fundo['valor_investido']
        relatorio += "\n"
    
    if not portfolio_data['fundos']:
        relatorio += "Nenhum fundo adicionado.\n"
    
    relatorio += f"Total Investido em Fundos: R$ {total_fundos:,.2f}\n"
    
    # Análise de ações
    relatorio += f"""
{'='*80}

📈 ANÁLISE DE AÇÕES
{'-'*40}
"""
    
    total_acoes = 0
    for i, acao in enumerate(portfolio_data['acoes'], 1):
        valor_investido = acao['quantidade'] * acao['preco_entrada']
        total_acoes += valor_investido
        
        relatorio += f"""
Ação {i}: {acao['codigo']}
Quantidade: {acao['quantidade']:,}
Preço de Entrada: R$ {acao['preco_entrada']:.2f}
Valor Investido: R$ {valor_investido:,.2f}
"""
    
    if not portfolio_data['acoes']:
        relatorio += "Nenhuma ação adicionada.\n"
    
    relatorio += f"Total Investido em Ações: R$ {total_acoes:,.2f}\n"
    
    # Análise de criptomoedas
    relatorio += f"""
{'='*80}

🪙 ANÁLISE DE CRIPTOMOEDAS
{'-'*40}
"""
    
    total_crypto = 0
    for i, crypto in enumerate(portfolio_data['crypto'], 1):
        valor_investido = crypto['quantity'] * crypto['entry_price']
        total_crypto += valor_investido
        
        relatorio += f"""
Cripto {i}: {crypto['symbol']}
Quantidade: {crypto['quantity']:.4f}
Preço de Entrada: US$ {crypto['entry_price']:,.2f}
Valor Investido: US$ {valor_investido:,.2f}
"""
    
    if not portfolio_data['crypto']:
        relatorio += "Nenhuma criptomoeda adicionada.\n"
    
    relatorio += f"Total Investido em Criptos: US$ {total_crypto:,.2f}\n"
    
    # Análise de renda fixa
    relatorio += f"""
{'='*80}

💰 ANÁLISE DE RENDA FIXA
{'-'*40}
"""
    
    total_rf = 0
    for i, rf in enumerate(portfolio_data['renda_fixa'], 1):
        total_rf += rf['valor']
        
        relatorio += f"""
Renda Fixa {i}: {rf['tipo']}
Valor Investido: R$ {rf['valor']:,.2f}
Taxa Anual: {rf['taxa_anual']:.2%}
Rendimento Anual Esperado: R$ {rf['valor'] * rf['taxa_anual']:,.2f}
"""
    
    if not portfolio_data['renda_fixa']:
        relatorio += "Nenhum ativo de renda fixa adicionado.\n"
    
    relatorio += f"Total Investido em Renda Fixa: R$ {total_rf:,.2f}\n"
    
    # Resumo geral
    total_geral = total_fundos + total_acoes + total_rf + (total_crypto * 5.0)  # Assumindo US$ 1 = R$ 5
    
    relatorio += f"""
{'='*80}

📊 RESUMO GERAL DO PORTFÓLIO
{'-'*40}

💰 VALORES TOTAIS:
  Fundos: R$ {total_fundos:,.2f} ({total_fundos/total_geral*100:.1f}%)
  Ações: R$ {total_acoes:,.2f} ({total_acoes/total_geral*100:.1f}%)
  Criptos: R$ {total_crypto*5.0:,.2f} ({total_crypto*5.0/total_geral*100:.1f}%)
  Renda Fixa: R$ {total_rf:,.2f} ({total_rf/total_geral*100:.1f}%)

🎯 VALOR TOTAL DO PORTFÓLIO: R$ {total_geral:,.2f}

{'='*80}

💡 RECOMENDAÇÕES E INSIGHTS
{'-'*40}

1. DIVERSIFICAÇÃO:
   - O portfólio está {'bem diversificado' if len(portfolio_data['fundos']) + len(portfolio_data['acoes']) + len(portfolio_data['crypto']) + len(portfolio_data['renda_fixa']) >= 10 else 'pouco diversificado'}
   - Considere adicionar mais ativos para melhorar a diversificação

2. ALOCAÇÃO POR CLASSE:
   - Renda Variável: {((total_fundos + total_acoes + total_crypto*5.0)/total_geral*100):.1f}%
   - Renda Fixa: {(total_rf/total_geral*100):.1f}%

3. EXPOSIÇÃO INTERNACIONAL:
   - Criptomoedas representam {(total_crypto*5.0/total_geral*100):.1f}% do portfólio
   - Considere adicionar ETFs internacionais para maior diversificação

4. LIQUIDEZ:
   - Ações e criptomoedas oferecem maior liquidez
   - Fundos podem ter prazo de resgate
   - Renda fixa pode ter vencimento específico

{'='*80}

📈 PRÓXIMOS PASSOS SUGERIDOS
{'-'*40}

1. Revisar alocação mensalmente
2. Rebalancear quando necessário
3. Monitorar performance vs benchmarks
4. Considerar estratégias de hedge
5. Avaliar necessidade de seguro

{'='*80}

⚠️ DISCLAIMER
{'-'*40}

Este relatório é gerado automaticamente e não constitui recomendação de investimento.
Consulte sempre um profissional qualificado antes de tomar decisões de investimento.
Os valores e rentabilidades podem variar e não garantem resultados futuros.

{'='*80}

📄 Relatório gerado automaticamente pelo Sistema de Análise Financeira
🕐 {timestamp}
{'='*80}
"""
    
    return relatorio

if __name__ == "__main__":
    main() 