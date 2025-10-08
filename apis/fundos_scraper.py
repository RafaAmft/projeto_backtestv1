#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sistema Otimizado de Scraping de Fundos de Investimento
=======================================================

Versão consolidada e otimizada que:
- Usa Requests + BeautifulSoup (mais leve que Selenium)
- Sistema inteligente de cache de slugs
- Fallback automático para Selenium quando necessário
- Rate limiting e retry inteligente
- Integração com CVMDataProcessor
"""

import json
import os
import time
import logging
import hashlib
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from bs4 import BeautifulSoup
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FundosScraperOptimized:
    """
    Scraper otimizado para dados de fundos do Mais Retorno
    """
    
    def __init__(self, 
                 mapeamento_file: str = "mapeamento_fundos.json",
                 cache_dir: str = "data/cache/funds",
                 delay_between_requests: float = 2.0,
                 use_selenium_fallback: bool = True):
        """
        Inicializa o scraper
        
        Args:
            mapeamento_file: Arquivo de mapeamento CNPJ -> Slug
            cache_dir: Diretório de cache
            delay_between_requests: Delay em segundos entre requisições
            use_selenium_fallback: Se deve usar Selenium como fallback
        """
        self.mapeamento_file = mapeamento_file
        self.cache_dir = cache_dir
        self.delay = delay_between_requests
        self.use_selenium_fallback = use_selenium_fallback
        
        # Criar diretório de cache se não existir
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        
        # Carregar mapeamento de fundos
        self.mapeamento = self._load_mapeamento()
        
        # Carregar cache de slugs
        self.slug_cache_file = os.path.join(cache_dir, "slug_cache.json")
        self.slug_cache = self._load_slug_cache()
        
        # Configurar session HTTP com retry
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
        
        # Estatísticas
        self.stats = {
            'requests_total': 0,
            'requests_success': 0,
            'requests_failed': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'selenium_fallbacks': 0
        }
        
        logger.info(f"FundosScraperOptimized inicializado - Delay: {self.delay}s")
    
    def _load_mapeamento(self) -> Dict:
        """Carrega o mapeamento de fundos"""
        try:
            if os.path.exists(self.mapeamento_file):
                with open(self.mapeamento_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    logger.info(f"✅ Mapeamento carregado: {len(data.get('mapeamento_fundos', {}))} fundos")
                    return data
        except Exception as e:
            logger.error(f"❌ Erro ao carregar mapeamento: {e}")
        return {'mapeamento_fundos': {}, 'fundos_alternativos': {}}
    
    def _save_mapeamento(self):
        """Salva o mapeamento de fundos"""
        try:
            self.mapeamento['ultima_atualizacao'] = datetime.now().strftime('%Y-%m-%d')
            with open(self.mapeamento_file, 'w', encoding='utf-8') as f:
                json.dump(self.mapeamento, f, ensure_ascii=False, indent=2)
            logger.info("✅ Mapeamento salvo")
        except Exception as e:
            logger.error(f"❌ Erro ao salvar mapeamento: {e}")
    
    def _load_slug_cache(self) -> Dict:
        """Carrega o cache de slugs"""
        try:
            if os.path.exists(self.slug_cache_file):
                with open(self.slug_cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"❌ Erro ao carregar cache de slugs: {e}")
        return {}
    
    def _save_slug_cache(self):
        """Salva o cache de slugs"""
        try:
            with open(self.slug_cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.slug_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"❌ Erro ao salvar cache de slugs: {e}")
    
    @staticmethod
    def _normalize_cnpj(cnpj: str) -> str:
        """Normaliza CNPJ removendo formatação"""
        return ''.join(filter(str.isdigit, str(cnpj)))
    
    @staticmethod
    def _format_cnpj(cnpj: str) -> str:
        """Formata CNPJ no padrão XX.XXX.XXX/XXXX-XX"""
        cnpj_clean = FundosScraperOptimized._normalize_cnpj(cnpj)
        if len(cnpj_clean) == 14:
            return f"{cnpj_clean[:2]}.{cnpj_clean[2:5]}.{cnpj_clean[5:8]}/{cnpj_clean[8:12]}-{cnpj_clean[12:]}"
        return cnpj_clean
    
    def buscar_slug(self, cnpj: str, update_cache: bool = True) -> Optional[str]:
        """
        Busca o slug de um fundo pelo CNPJ
        
        Estratégia:
        1. Verifica no mapeamento local
        2. Verifica no cache de slugs
        3. Busca via requests no Mais Retorno
        4. Fallback para Selenium (se habilitado)
        
        Args:
            cnpj: CNPJ do fundo
            update_cache: Se deve atualizar o cache com o resultado
            
        Returns:
            Slug do fundo ou None se não encontrado
        """
        cnpj_clean = self._normalize_cnpj(cnpj)
        cnpj_formatted = self._format_cnpj(cnpj)
        
        # 1. Verificar no mapeamento local
        if cnpj_formatted in self.mapeamento.get('mapeamento_fundos', {}):
            slug = self.mapeamento['mapeamento_fundos'][cnpj_formatted]['slug']
            logger.info(f"✅ Slug encontrado no mapeamento: {slug}")
            self.stats['cache_hits'] += 1
            return slug
        
        # 2. Verificar no cache de slugs
        if cnpj_clean in self.slug_cache:
            cache_entry = self.slug_cache[cnpj_clean]
            cache_date = datetime.fromisoformat(cache_entry.get('timestamp', '2020-01-01'))
            
            # Cache válido por 90 dias
            if datetime.now() - cache_date < timedelta(days=90):
                slug = cache_entry.get('slug')
                logger.info(f"✅ Slug encontrado no cache: {slug}")
                self.stats['cache_hits'] += 1
                return slug
        
        self.stats['cache_misses'] += 1
        
        # 3. Buscar via requests (mais rápido)
        logger.info(f"🔍 Buscando slug para CNPJ {cnpj_formatted}...")
        slug = self._buscar_slug_requests(cnpj_formatted)
        
        # 4. Fallback para Selenium se necessário
        if not slug and self.use_selenium_fallback:
            logger.warning(f"⚠️ Tentando Selenium como fallback para {cnpj_formatted}")
            self.stats['selenium_fallbacks'] += 1
            slug = self._buscar_slug_selenium(cnpj_formatted)
        
        # Atualizar cache se encontrado
        if slug and update_cache:
            self._update_slug_cache(cnpj_clean, slug, cnpj_formatted)
        
        return slug
    
    def _buscar_slug_requests(self, cnpj_formatted: str) -> Optional[str]:
        """Busca slug usando requests (mais rápido)"""
        try:
            # Tentar busca direta
            url = f"https://maisretorno.com/busca?q={cnpj_formatted}"
            
            self.stats['requests_total'] += 1
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Procurar links para fundos
                links = soup.find_all('a', href=True)
                for link in links:
                    href = link['href']
                    if '/fundo/' in href:
                        # Extrair slug
                        slug = href.split('/fundo/')[-1].split('?')[0].split('#')[0]
                        if slug:
                            logger.info(f"✅ Slug encontrado via requests: {slug}")
                            self.stats['requests_success'] += 1
                            return slug
            
            self.stats['requests_failed'] += 1
            return None
            
        except Exception as e:
            logger.error(f"❌ Erro na busca via requests: {e}")
            self.stats['requests_failed'] += 1
            return None
    
    def _buscar_slug_selenium(self, cnpj_formatted: str) -> Optional[str]:
        """Busca slug usando Selenium (fallback)"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            
            # Configurar Selenium headless
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            driver = webdriver.Chrome(options=options)
            
            try:
                # Buscar via DuckDuckGo
                query = f"site:maisretorno.com/fundo {cnpj_formatted}"
                url = f"https://duckduckgo.com/?q={query}"
                
                driver.get(url)
                time.sleep(3)
                
                links = driver.find_elements(By.XPATH, "//a[contains(@href, 'maisretorno.com/fundo')]")
                for link in links:
                    href = link.get_attribute("href")
                    if "maisretorno.com/fundo/" in href:
                        slug = href.split("/fundo/")[-1].split('?')[0]
                        logger.info(f"✅ Slug encontrado via Selenium: {slug}")
                        return slug
                
                return None
            finally:
                driver.quit()
                
        except ImportError:
            logger.error("❌ Selenium não disponível - instale com: pip install selenium webdriver-manager")
            return None
        except Exception as e:
            logger.error(f"❌ Erro na busca via Selenium: {e}")
            return None
    
    def _update_slug_cache(self, cnpj_clean: str, slug: str, cnpj_formatted: str):
        """Atualiza o cache de slugs e mapeamento"""
        # Atualizar cache de slugs
        self.slug_cache[cnpj_clean] = {
            'slug': slug,
            'cnpj_formatted': cnpj_formatted,
            'timestamp': datetime.now().isoformat()
        }
        self._save_slug_cache()
        
        # Atualizar mapeamento se não existir
        if cnpj_formatted not in self.mapeamento.get('mapeamento_fundos', {}):
            if 'mapeamento_fundos' not in self.mapeamento:
                self.mapeamento['mapeamento_fundos'] = {}
            
            self.mapeamento['mapeamento_fundos'][cnpj_formatted] = {
                'slug': slug,
                'url': f"https://maisretorno.com/fundo/{slug}",
                'status': 'auto_descoberto',
                'data_descoberta': datetime.now().strftime('%Y-%m-%d')
            }
            self._save_mapeamento()
            logger.info(f"✅ Novo fundo adicionado ao mapeamento: {cnpj_formatted}")
    
    def extrair_dados_fundo(self, slug: str, cnpj: str) -> Optional[Dict[str, Any]]:
        """
        Extrai dados de rentabilidade de um fundo
        
        Args:
            slug: Slug do fundo no Mais Retorno
            cnpj: CNPJ do fundo
            
        Returns:
            Dicionário com dados do fundo ou None se erro
        """
        url = f"https://maisretorno.com/fundo/{slug}"
        logger.info(f"📊 Extraindo dados de {slug}...")
        
        try:
            self.stats['requests_total'] += 1
            
            # Fazer requisição com delay
            time.sleep(self.delay)
            response = self.session.get(url, timeout=20)
            
            if response.status_code == 429:
                logger.warning("⚠️ Rate limit atingido. Aguardando 10 segundos...")
                time.sleep(10)
                response = self.session.get(url, timeout=20)
            
            if response.status_code != 200:
                logger.error(f"❌ Status code {response.status_code} para {slug}")
                self.stats['requests_failed'] += 1
                return None
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrair nome do fundo
            nome_fundo = "Fundo não identificado"
            title_tag = soup.find('h1')
            if title_tag:
                nome_fundo = title_tag.get_text(strip=True)
            
            # Extrair rentabilidades
            rentabilidades = self._extrair_rentabilidades_html(soup)
            
            if not rentabilidades:
                logger.warning(f"⚠️ Nenhuma rentabilidade encontrada para {slug}")
                # Tentar Selenium se habilitado
                if self.use_selenium_fallback:
                    logger.info("🔄 Tentando extrair com Selenium...")
                    self.stats['selenium_fallbacks'] += 1
                    return self._extrair_dados_selenium(slug, cnpj)
            
            dados_fundo = {
                'cnpj': self._format_cnpj(cnpj),
                'slug': slug,
                'nome': nome_fundo,
                'url': url,
                'rentabilidades': rentabilidades,
                'timestamp': datetime.now().isoformat(),
                'fonte': 'requests'
            }
            
            self.stats['requests_success'] += 1
            logger.info(f"✅ Dados extraídos: {len(rentabilidades)} períodos encontrados")
            
            return dados_fundo
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair dados: {e}")
            self.stats['requests_failed'] += 1
            return None
    
    def _extrair_rentabilidades_html(self, soup: BeautifulSoup) -> Dict[str, Dict[str, float]]:
        """Extrai rentabilidades do HTML"""
        rentabilidades = {}
        
        try:
            # Procurar tabela de rentabilidade
            # Estratégia 1: Por texto "Rentabilidade"
            tabela = None
            for h2 in soup.find_all(['h2', 'h3', 'h4']):
                if 'Rentabilidade' in h2.get_text():
                    tabela = h2.find_next('table')
                    if tabela:
                        break
            
            # Estratégia 2: Primeira tabela com meses
            if not tabela:
                tabelas = soup.find_all('table')
                for t in tabelas:
                    html_table = str(t)
                    if 'Jan' in html_table and 'Fev' in html_table and 'Mar' in html_table:
                        tabela = t
                        break
            
            if not tabela:
                return rentabilidades
            
            # Processar tabela
            linhas = tabela.find_all('tr')
            meses = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 
                    'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez']
            
            for linha in linhas:
                celulas = linha.find_all(['td', 'th'])
                if len(celulas) >= 13:  # Ano + 12 meses
                    primeiro_campo = celulas[0].get_text(strip=True)
                    
                    # Verificar se é linha de ano
                    if primeiro_campo.isdigit() and len(primeiro_campo) == 4:
                        ano = primeiro_campo
                        rentabilidades[ano] = {}
                        
                        # Extrair cada mês
                        for i, mes in enumerate(meses):
                            if i + 1 < len(celulas):
                                valor_texto = celulas[i + 1].get_text(strip=True)
                                valor = self._parse_rentabilidade(valor_texto)
                                if valor is not None:
                                    rentabilidades[ano][mes] = valor
            
        except Exception as e:
            logger.error(f"❌ Erro ao extrair rentabilidades: {e}")
        
        return rentabilidades
    
    @staticmethod
    def _parse_rentabilidade(valor_str: str) -> Optional[float]:
        """Parse valor de rentabilidade"""
        if not valor_str or valor_str in ['--', '-', 'N/A', '']:
            return None
        
        try:
            # Remover % e espaços
            valor_str = valor_str.replace('%', '').strip()
            
            # Pegar apenas o primeiro valor se houver múltiplos
            if '\n' in valor_str:
                valor_str = valor_str.split('\n')[0]
            
            # Substituir vírgula por ponto
            valor_str = valor_str.replace(',', '.')
            
            # Converter para float e dividir por 100 (percentual para decimal)
            return float(valor_str) / 100
            
        except (ValueError, AttributeError):
            return None
    
    def _extrair_dados_selenium(self, slug: str, cnpj: str) -> Optional[Dict[str, Any]]:
        """Extrai dados usando Selenium (fallback)"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            
            driver = webdriver.Chrome(options=options)
            
            try:
                url = f"https://maisretorno.com/fundo/{slug}"
                driver.get(url)
                time.sleep(3)
                
                # Parse com BeautifulSoup
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                
                # Extrair nome
                nome_fundo = "Fundo não identificado"
                title_tag = soup.find('h1')
                if title_tag:
                    nome_fundo = title_tag.get_text(strip=True)
                
                # Extrair rentabilidades
                rentabilidades = self._extrair_rentabilidades_html(soup)
                
                dados_fundo = {
                    'cnpj': self._format_cnpj(cnpj),
                    'slug': slug,
                    'nome': nome_fundo,
                    'url': url,
                    'rentabilidades': rentabilidades,
                    'timestamp': datetime.now().isoformat(),
                    'fonte': 'selenium'
                }
                
                logger.info(f"✅ Dados extraídos via Selenium: {len(rentabilidades)} períodos")
                return dados_fundo
                
            finally:
                driver.quit()
                
        except ImportError:
            logger.error("❌ Selenium não disponível")
            return None
        except Exception as e:
            logger.error(f"❌ Erro ao extrair com Selenium: {e}")
            return None
    
    def processar_multiplos_fundos(self, cnpjs: List[str]) -> Dict[str, Any]:
        """
        Processa múltiplos fundos
        
        Args:
            cnpjs: Lista de CNPJs
            
        Returns:
            Dicionário com resultados
        """
        resultados = {
            'sucesso': [],
            'falha': [],
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"🚀 Processando {len(cnpjs)} fundos...")
        
        for i, cnpj in enumerate(cnpjs, 1):
            logger.info(f"\n{'='*60}")
            logger.info(f"📊 Fundo {i}/{len(cnpjs)}: {cnpj}")
            logger.info(f"{'='*60}")
            
            try:
                # Buscar slug
                slug = self.buscar_slug(cnpj)
                
                if not slug:
                    logger.warning(f"❌ Slug não encontrado para {cnpj}")
                    resultados['falha'].append({
                        'cnpj': cnpj,
                        'erro': 'Slug não encontrado'
                    })
                    continue
                
                # Extrair dados
                dados = self.extrair_dados_fundo(slug, cnpj)
                
                if dados:
                    resultados['sucesso'].append(dados)
                    logger.info(f"✅ {cnpj}: Sucesso")
                else:
                    resultados['falha'].append({
                        'cnpj': cnpj,
                        'slug': slug,
                        'erro': 'Erro ao extrair dados'
                    })
                    logger.warning(f"❌ {cnpj}: Erro ao extrair dados")
                
            except Exception as e:
                logger.error(f"❌ Erro ao processar {cnpj}: {e}")
                resultados['falha'].append({
                    'cnpj': cnpj,
                    'erro': str(e)
                })
        
        # Estatísticas finais
        logger.info(f"\n{'='*60}")
        logger.info("📈 ESTATÍSTICAS FINAIS:")
        logger.info(f"  ✅ Sucesso: {len(resultados['sucesso'])}")
        logger.info(f"  ❌ Falha: {len(resultados['falha'])}")
        logger.info(f"  📊 Taxa de sucesso: {len(resultados['sucesso'])/len(cnpjs)*100:.1f}%")
        logger.info(f"{'='*60}\n")
        
        return resultados
    
    def get_stats(self) -> Dict[str, int]:
        """Retorna estatísticas do scraper"""
        return self.stats.copy()


def test_scraper():
    """Teste do scraper"""
    print("TESTE DO SCRAPER OTIMIZADO")
    print("=" * 60)
    
    # Inicializar scraper
    scraper = FundosScraperOptimized(delay_between_requests=1.0)
    
    # CNPJs de teste do mapeamento
    cnpjs_teste = [
        "04.305.193/0001-40",  # BB Cambial Euro LP
        "20.077.065/0001-42",  # Mapfre
    ]
    
    # Processar fundos
    resultados = scraper.processar_multiplos_fundos(cnpjs_teste)
    
    # Mostrar resultados
    print("\nRESULTADOS:")
    print(f"Sucesso: {len(resultados['sucesso'])}")
    print(f"Falha: {len(resultados['falha'])}")
    
    # Estatísticas
    stats = scraper.get_stats()
    print("\nESTATISTICAS:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    return resultados


if __name__ == "__main__":
    test_scraper()

