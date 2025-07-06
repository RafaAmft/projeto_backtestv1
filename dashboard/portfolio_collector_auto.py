#!/usr/bin/env python3
"""
Painel Streamlit para Coleta de Dados de Portfólio Financeiro
Versão com busca automática de preços para criptos e ações
"""

import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import re
import yfinance as yf

# Configuração da página
st.set_page_config(
    page_title="📊 Coletor de Portfólio Financeiro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
.main-header {
    text-align: center;
    color: #1f77b4;
    font-size: 2.5rem;
    margin-bottom: 2rem;
    padding: 1rem;
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    border-radius: 10px;
    color: white;
}

.section-header {
    color: #2c3e50;
    border-bottom: 3px solid #3498db;
    padding-bottom: 0.5rem;
    margin-top: 2rem;
}

.success-message {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    border-radius: 5px;
    padding: 1rem;
    margin: 1rem 0;
}

.info-box {
    background-color: #e7f3ff;
    border: 1px solid #b3d9ff;
    border-radius: 5px;
    padding: 1rem;
    margin: 1rem 0;
}

.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    text-align: center;
    margin: 0.5rem 0;
}

.metric-value {
    font-size: 1.5rem;
    font-weight: bold;
}

.metric-label {
    font-size: 0.9rem;
    opacity: 0.9;
}

.price-info {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 5px;
    padding: 0.5rem;
    margin: 0.5rem 0;
    font-size: 0.9rem;
}

.price-up {
    color: #28a745;
}

.price-down {
    color: #dc3545;
}
</style>
""", unsafe_allow_html=True)

# Inicializar session state
if 'fundos_data' not in st.session_state:
    st.session_state.fundos_data = []
if 'acoes_data' not in st.session_state:
    st.session_state.acoes_data = []
if 'crypto_data' not in st.session_state:
    st.session_state.crypto_data = []
if 'renda_fixa_data' not in st.session_state:
    st.session_state.renda_fixa_data = []

class PriceFetcher:
    """Classe para buscar preços em tempo real"""
    
    def __init__(self):
        self.usd_brl_rate = self.get_usd_brl_rate()
    
    def get_usd_brl_rate(self) -> float:
        """Busca cotação USD/BRL via API do Banco Central"""
        try:
            url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1/dados/ultimos/1?formato=json"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return float(data[0]['valor'])
            else:
                return 5.42
        except:
            return 5.42
    
    def get_crypto_price(self, symbol: str) -> Optional[Dict]:
        """Busca preço de abertura da criptomoeda"""
        try:
            ticker = yf.Ticker(f"{symbol}-USD")
            hist = ticker.history(period="2d")
            
            if len(hist) >= 2:
                open_price_usd = float(hist.iloc[-1]['Open'])
                current_price_usd = float(hist.iloc[-1]['Close'])
                daily_change = ((current_price_usd - open_price_usd) / open_price_usd) * 100
                
                # Conversão para BRL
                open_price_brl = open_price_usd * self.usd_brl_rate
                current_price_brl = current_price_usd * self.usd_brl_rate
                
                return {
                    'open_usd': open_price_usd,
                    'current_usd': current_price_usd,
                    'open_brl': open_price_brl,
                    'current_brl': current_price_brl,
                    'daily_change': daily_change,
                    'usd_brl_rate': self.usd_brl_rate
                }
        except Exception as e:
            st.error(f"Erro ao buscar preço da {symbol}: {e}")
            return None
    
    def get_stock_price(self, ticker: str) -> Optional[Dict]:
        """Busca preço de fechamento da ação"""
        try:
            # Adicionar .SA se não estiver presente
            if not ticker.endswith('.SA'):
                ticker = f"{ticker}.SA"
            
            stock_ticker = yf.Ticker(ticker)
            hist = stock_ticker.history(period="5d")
            
            if len(hist) > 0:
                last_close = float(hist.iloc[-1]['Close'])
                last_open = float(hist.iloc[-1]['Open'])
                daily_change = ((last_close - last_open) / last_open) * 100
                
                return {
                    'close_price': last_close,
                    'open_price': last_open,
                    'daily_change': daily_change
                }
        except Exception as e:
            st.error(f"Erro ao buscar preço da {ticker}: {e}")
            return None

class CacheManager:
    """Gerenciador de cache para dados de fundos"""
    
    def __init__(self, cache_dir="data/cache"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_file = os.path.join(cache_dir, "fund_cache.json")
        self.cache_expiry_days = 30
    
    def normalize_cnpj(self, cnpj: str) -> str:
        """Normaliza CNPJ removendo caracteres especiais"""
        return re.sub(r'[^\d]', '', cnpj)
    
    def save_fund_data(self, cnpj: str, data: Dict):
        """Salva dados do fundo no cache"""
        normalized_cnpj = self.normalize_cnpj(cnpj)
        cache_data = self.load_cache()
        
        cache_data[normalized_cnpj] = {
            'data': data,
            'timestamp': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=self.cache_expiry_days)).isoformat()
        }
        
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
    
    def get_fund_data(self, cnpj: str) -> Optional[Dict]:
        """Recupera dados do fundo do cache"""
        normalized_cnpj = self.normalize_cnpj(cnpj)
        cache_data = self.load_cache()
        
        if normalized_cnpj in cache_data:
            entry = cache_data[normalized_cnpj]
            expires_at = datetime.fromisoformat(entry['expires_at'])
            
            if datetime.now() < expires_at:
                return entry['data']
            else:
                # Remover entrada expirada
                del cache_data[normalized_cnpj]
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        return None
    
    def load_cache(self) -> Dict:
        """Carrega dados do cache"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def get_cache_stats(self) -> Dict:
        """Retorna estatísticas do cache"""
        cache_data = self.load_cache()
        total = len(cache_data)
        valid = 0
        expired = 0
        
        for entry in cache_data.values():
            expires_at = datetime.fromisoformat(entry['expires_at'])
            if datetime.now() < expires_at:
                valid += 1
            else:
                expired += 1
        
        # Calcular tamanho do arquivo
        cache_size_mb = 0
        if os.path.exists(self.cache_file):
            cache_size_mb = os.path.getsize(self.cache_file) / (1024 * 1024)
        
        return {
            'total_funds': total,
            'valid_funds': valid,
            'expired_funds': expired,
            'cache_size_mb': f"{cache_size_mb:.2f}"
        }
    
    def clear_expired_cache(self) -> int:
        """Remove entradas expiradas do cache"""
        cache_data = self.load_cache()
        initial_count = len(cache_data)
        
        expired_keys = []
        for cnpj, entry in cache_data.items():
            expires_at = datetime.fromisoformat(entry['expires_at'])
            if datetime.now() >= expires_at:
                expired_keys.append(cnpj)
        
        for key in expired_keys:
            del cache_data[key]
        
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        return initial_count - len(cache_data)
    
    def clear_all_cache(self):
        """Limpa todo o cache"""
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)

class PortfolioDataCollector:
    """Coletor de dados de portfólio financeiro"""
    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.price_fetcher = PriceFetcher()
    
    def buscar_slug_fundo(self, cnpj: str) -> Tuple[Optional[str], Optional[str]]:
        """Busca slug do fundo no Mais Retorno usando DuckDuckGo"""
        try:
            # Formatar CNPJ
            def formatar_cnpj(cnpj_str):
                cnpj_limpo = re.sub(r'[^\d]', '', cnpj_str)
                if len(cnpj_limpo) == 14:
                    return f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"
                return cnpj_str
            
            cnpj_formatado = formatar_cnpj(cnpj)
            
            # Buscar no DuckDuckGo
            query = f"site:maisretorno.com.br {cnpj_formatado}"
            url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Procurar por links do Mais Retorno
                if 'AbstractURL' in data and 'maisretorno.com.br' in data['AbstractURL']:
                    url_fundo = data['AbstractURL']
                    slug = url_fundo.split('/')[-1] if '/' in url_fundo else None
                    return slug, url_fundo
                
                # Procurar em resultados relacionados
                if 'RelatedTopics' in data:
                    for topic in data['RelatedTopics']:
                        if 'FirstURL' in topic and 'maisretorno.com.br' in topic['FirstURL']:
                            url_fundo = topic['FirstURL']
                            slug = url_fundo.split('/')[-1] if '/' in url_fundo else None
                            return slug, url_fundo
            
            return None, None
            
        except Exception as e:
            st.error(f"Erro na busca: {e}")
            return None, None
    
    def extrair_dados_fundo(self, slug: str, cnpj: str) -> Optional[Dict]:
        """Extrai dados do fundo usando Selenium"""
        try:
            # Verificar cache primeiro
            cached_data = self.cache_manager.get_fund_data(cnpj)
            if cached_data:
                return cached_data
            
            # Configurar Selenium
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(30)
            
            url = f"https://maisretorno.com.br/fundos/{slug}"
            driver.get(url)
            
            # Aguardar carregamento
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Extrair dados
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            
            dados = {
                'nome': 'Fundo não encontrado',
                'url': url,
                'rentabilidades': {}
            }
            
            # Tentar extrair nome do fundo
            nome_element = soup.find('h1') or soup.find('title')
            if nome_element:
                dados['nome'] = nome_element.get_text(strip=True)
            
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
                    
                    # Extrair dados mensais (simplificado)
                    meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                            'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
                    
                    for j, campo in enumerate(linha[2:14]):
                        if j < len(meses):
                            try:
                                valor = float(campo.replace('%', '').replace(',', '.')) / 100
                                dados['rentabilidades'][ano][meses[j]] = valor
                            except:
                                continue
            
            # Salvar dados no cache
            self.cache_manager.save_fund_data(cnpj, dados)
            
            return dados
            
        except Exception as e:
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
    - 📈 **Ações** (5 ações) - Preços automáticos em tempo real
    - 🪙 **Criptomoedas** (5 criptos) - Preços automáticos em tempo real
    - 💰 **Renda Fixa** (2 ativos) - % do CDI
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
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                codigo = st.text_input(f"Código da Ação {i+1}", key=f"acao_{i}")
            
            with col2:
                if st.button(f"🔍 Buscar Preço {i+1}", key=f"buscar_acao_{i}"):
                    if codigo:
                        with st.spinner(f"Buscando preço da {codigo}..."):
                            price_data = collector.price_fetcher.get_stock_price(codigo)
                            if price_data:
                                # Atualizar o preço de entrada automaticamente
                                st.session_state[f"preco_acao_{i}"] = price_data['close_price']
                                st.success(f"✅ Preço atualizado: R$ {price_data['close_price']:.2f}")
                                
                                # Mostrar informações do preço
                                change_color = "price-up" if price_data['daily_change'] >= 0 else "price-down"
                                change_symbol = "📈" if price_data['daily_change'] >= 0 else "📉"
                                
                                st.markdown(f"""
                                <div class="price-info">
                                    {change_symbol} <strong>{codigo}</strong><br>
                                    Fechamento: R$ {price_data['close_price']:.2f}<br>
                                    Abertura: R$ {price_data['open_price']:.2f}<br>
                                    Variação: <span class="{change_color}">{price_data['daily_change']:+.2f}%</span>
                                </div>
                                """, unsafe_allow_html=True)
                                st.rerun()
                            else:
                                st.error(f"❌ Erro ao buscar preço da {codigo}")
                    else:
                        st.error("❌ Digite um código válido")
            
            with col3:
                quantidade = st.number_input(
                    f"Quantidade", 
                    min_value=0, 
                    value=100, 
                    step=10,
                    key=f"qtd_acao_{i}"
                )
            
            with col4:
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
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                symbol = st.selectbox(
                    f"Criptomoeda {i+1}",
                    ["BTC", "ETH", "BNB", "SOL", "ADA", "DOT", "LINK", "MATIC", "AVAX", "UNI"],
                    key=f"crypto_{i}"
                )
            
            with col2:
                if st.button(f"🔍 Buscar Preço {i+1}", key=f"buscar_crypto_{i}"):
                    with st.spinner(f"Buscando preço da {symbol}..."):
                        price_data = collector.price_fetcher.get_crypto_price(symbol)
                        if price_data:
                            # Atualizar o preço de entrada automaticamente (preço de abertura em USD)
                            st.session_state[f"preco_crypto_{i}"] = price_data['open_usd']
                            st.success(f"✅ Preço atualizado: US$ {price_data['open_usd']:.2f}")
                            
                            # Mostrar informações do preço
                            change_color = "price-up" if price_data['daily_change'] >= 0 else "price-down"
                            change_symbol = "📈" if price_data['daily_change'] >= 0 else "📉"
                            
                            st.markdown(f"""
                            <div class="price-info">
                                {change_symbol} <strong>{symbol}</strong><br>
                                Abertura: US$ {price_data['open_usd']:.2f} (R$ {price_data['open_brl']:.2f})<br>
                                Atual: US$ {price_data['current_usd']:.2f} (R$ {price_data['current_brl']:.2f})<br>
                                Variação: <span class="{change_color}">{price_data['daily_change']:+.2f}%</span><br>
                                USD/BRL: R$ {price_data['usd_brl_rate']:.4f}
                            </div>
                            """, unsafe_allow_html=True)
                            st.rerun()
                        else:
                            st.error(f"❌ Erro ao buscar preço da {symbol}")
            
            with col3:
                quantity = st.number_input(
                    f"Quantidade", 
                    min_value=0.0, 
                    value=1.0, 
                    step=0.1,
                    key=f"qtd_crypto_{i}"
                )
            
            with col4:
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
    
    # Informação sobre CDI
    st.markdown("""
    <div class="info-box">
    <strong>💡 Sobre a % do CDI:</strong><br>
    • CDI atual ≈ 10.5% ao ano<br>
    • Ex: 95% do CDI = 9.975% ao ano<br>
    • Ex: 110% do CDI = 11.55% ao ano<br>
    • Use o valor percentual que você conseguiu na instituição
    </div>
    """, unsafe_allow_html=True)
    
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
                percentual_cdi = st.number_input(
                    f"% do CDI", 
                    min_value=0.0, 
                    max_value=200.0,
                    value=95.0, 
                    step=0.1,
                    help="Ex: 95.0 = 95% do CDI (CDI atual ≈ 10.5% ao ano)"
                )
            
            if st.button(f"➕ Adicionar Renda Fixa {i+1}", key=f"add_rf_{i}"):
                if valor > 0 and percentual_cdi > 0:
                    # Verificar se já existe
                    rf_existente = next((rf for rf in st.session_state.renda_fixa_data if rf['tipo'] == tipo), None)
                    if rf_existente:
                        st.error("❌ Este tipo de renda fixa já foi adicionado!")
                    else:
                        st.session_state.renda_fixa_data.append({
                            'tipo': tipo,
                            'valor': valor,
                            'percentual_cdi': percentual_cdi / 100  # Converter para decimal
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
        
        # Calcular taxa efetiva baseada no CDI
        percentual_cdi = rf['percentual_cdi'] * 100
        cdi_atual = 10.5  # CDI aproximado atual
        taxa_efetiva = cdi_atual * rf['percentual_cdi']
        
        relatorio += f"""
Renda Fixa {i}: {rf['tipo']}
Valor Investido: R$ {rf['valor']:,.2f}
% do CDI: {percentual_cdi:.1f}%
Taxa Efetiva: {taxa_efetiva:.2f}% ao ano (baseado em CDI de {cdi_atual}%)
"""
    
    if not portfolio_data['renda_fixa']:
        relatorio += "Nenhum ativo de renda fixa adicionado.\n"
    
    relatorio += f"Total Investido em Renda Fixa: R$ {total_rf:,.2f}\n"
    
    # Resumo total
    relatorio += f"""
{'='*80}

📊 RESUMO TOTAL DO PORTFÓLIO
{'-'*40}

🏦 Fundos: R$ {total_fundos:,.2f}
📈 Ações: R$ {total_acoes:,.2f}
🪙 Criptos: US$ {total_crypto:,.2f}
💰 Renda Fixa: R$ {total_rf:,.2f}

Total em Reais: R$ {total_fundos + total_acoes + total_rf:,.2f}
Total em Dólares: US$ {total_crypto:,.2f}

{'='*80}

💡 PRÓXIMOS PASSOS PARA ANÁLISE COMPLETA:
{'-'*40}

1. 📈 Integrar com APIs de preços em tempo real
2. 📊 Calcular rentabilidades históricas
3. 📉 Comparar com benchmarks (CDI, Selic, Ibovespa)
4. 📋 Gerar métricas de risco e retorno
5. 📈 Criar gráficos de evolução temporal

{'='*80}
"""
    
    return relatorio

if __name__ == "__main__":
    main() 