#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Provider para Fundos de Investimento
Integra com Cache Manager e usa dados processados da CVM + scraping Mais Retorno
"""

import sys
import os
import time
import logging
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import pandas as pd

# Adicionar diretórios ao path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from ..core.cache_manager import CacheManager
from ..models.data_models import DataType, DataSource, DataQuality

logger = logging.getLogger(__name__)

class FundosProvider:
    """
    Provider para fundos de investimento com cache integrado
    """
    
    def __init__(self, cache_manager: CacheManager, delay_between_requests: float = 2.0):
        """
        Inicializa o provider de fundos
        
        Args:
            cache_manager: Instância do Cache Manager
            delay_between_requests: Delay em segundos entre requisições
        """
        self.cache_manager = cache_manager
        self.delay = delay_between_requests
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Carregar mapeamento de fundos
        self.mapeamento_fundos = self._carregar_mapeamento()
        
        logger.info(f"Fundos Provider inicializado com delay de {self.delay}s")
    
    def _carregar_mapeamento(self) -> Dict:
        """Carrega o mapeamento de fundos"""
        try:
            mapeamento_path = os.path.join(os.path.dirname(__file__), '../../mapeamento_fundos.json')
            with open(mapeamento_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning("Arquivo de mapeamento de fundos não encontrado")
            return {'mapeamento_fundos': {}}
        except Exception as e:
            logger.error(f"Erro ao carregar mapeamento: {e}")
            return {'mapeamento_fundos': {}}
    
    def buscar_slug_fundo(self, cnpj: str) -> Optional[str]:
        """
        Busca o slug de um fundo pelo CNPJ
        
        Args:
            cnpj: CNPJ do fundo
            
        Returns:
            Slug do fundo ou None se não encontrado
        """
        # Formatar CNPJ
        cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
        
        # Verificar no mapeamento
        if cnpj_limpo in self.mapeamento_fundos.get('mapeamento_fundos', {}):
            return self.mapeamento_fundos['mapeamento_fundos'][cnpj_limpo]['slug']
        
        # Buscar no Mais Retorno (fallback)
        return self._buscar_slug_mais_retorno(cnpj_limpo)
    
    def _buscar_slug_mais_retorno(self, cnpj: str) -> Optional[str]:
        """
        Busca slug no Mais Retorno via web scraping
        
        Args:
            cnpj: CNPJ do fundo
            
        Returns:
            Slug do fundo ou None se não encontrado
        """
        try:
            # URL de busca do Mais Retorno
            url = f"https://maisretorno.com/busca?q={cnpj}"
            
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                # Implementar parsing do HTML para extrair slug
                # Por enquanto, retorna None
                logger.info(f"Busca no Mais Retorno para CNPJ {cnpj}")
                return None
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar slug no Mais Retorno: {e}")
            return None
    
    def get_fundo_data(self, cnpj: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """
        Obtém dados de um fundo pelo CNPJ
        
        Args:
            cnpj: CNPJ do fundo
            use_cache: Se deve usar cache
            
        Returns:
            Dados do fundo ou None se erro
        """
        cache_key = f"fundo_data_{cnpj}"
        
        # Tentar cache primeiro
        if use_cache:
            cached_data = self.cache_manager.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit para fundo {cnpj}")
                return cached_data
        
        # Buscar dados reais
        try:
            logger.info(f"Buscando dados do fundo {cnpj}...")
            
            # Buscar slug
            slug = self.buscar_slug_fundo(cnpj)
            if not slug:
                logger.warning(f"Slug não encontrado para CNPJ {cnpj}")
                return None
            
            # Extrair dados do fundo
            dados_fundo = self._extrair_dados_fundo(slug, cnpj)
            
            if dados_fundo:
                # Armazenar no cache
                if use_cache:
                    self.cache_manager.set(
                        key=cache_key,
                        data=dados_fundo,
                        data_type=DataType.FUND,
                        expires_in=3600,  # 1 hora
                        source=DataSource.UNKNOWN,
                        quality=DataQuality.GOOD
                    )
                    logger.debug(f"Dados do fundo {cnpj} armazenados no cache")
                
                return dados_fundo
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar dados do fundo {cnpj}: {e}")
            return None
    
    def _extrair_dados_fundo(self, slug: str, cnpj: str) -> Optional[Dict[str, Any]]:
        """
        Extrai dados de um fundo do Mais Retorno
        
        Args:
            slug: Slug do fundo
            cnpj: CNPJ do fundo
            
        Returns:
            Dados do fundo ou None se erro
        """
        try:
            # URL do fundo no Mais Retorno
            url = f"https://maisretorno.com/fundos/{slug}"
            
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                # Implementar parsing do HTML para extrair dados
                # Por enquanto, retorna dados básicos
                dados_fundo = {
                    'cnpj': cnpj,
                    'slug': slug,
                    'nome': f"Fundo {slug}",
                    'timestamp': datetime.now().isoformat(),
                    'source': 'mais_retorno',
                    'rentabilidades': {},
                    'dados_basicos': {
                        'tipo': 'Fundo de Investimento',
                        'categoria': 'Não especificada',
                        'administrador': 'Não especificado'
                    }
                }
                
                return dados_fundo
            
            elif response.status_code == 429:
                logger.warning(f"Rate limit atingido para fundo {slug}. Aguardando 10 segundos...")
                time.sleep(10)
                return self._extrair_dados_fundo(slug, cnpj)  # Retry
                
            return None
            
        except Exception as e:
            logger.error(f"Erro ao extrair dados do fundo {slug}: {e}")
            return None
    
    def get_multiple_fundos(self, cnpjs: List[str], use_cache: bool = True) -> Dict[str, Any]:
        """
        Obtém dados de múltiplos fundos
        
        Args:
            cnpjs: Lista de CNPJs
            use_cache: Se deve usar cache
            
        Returns:
            Dicionário com dados dos fundos
        """
        results = {}
        
        for i, cnpj in enumerate(cnpjs):
            logger.info(f"Processando fundo {cnpj}... ({i+1}/{len(cnpjs)})")
            
            dados = self.get_fundo_data(cnpj, use_cache)
            if dados:
                results[cnpj] = dados
                logger.info(f"✅ {cnpj}: Dados obtidos")
            else:
                logger.warning(f"❌ {cnpj}: Erro ao obter dados")
            
            # Delay entre requisições (exceto na última)
            if i < len(cnpjs) - 1:
                logger.debug(f"Aguardando {self.delay} segundos...")
                time.sleep(self.delay)
        
        return results
    
    def get_fundos_carteira(self, carteira_fundos: List[Dict], use_cache: bool = True) -> Dict[str, Any]:
        """
        Obtém dados de fundos de uma carteira
        
        Args:
            carteira_fundos: Lista de fundos da carteira
            use_cache: Se deve usar cache
            
        Returns:
            Dados dos fundos da carteira
        """
        logger.info(f"Obtendo dados de {len(carteira_fundos)} fundos da carteira...")
        
        carteira_data = {
            'timestamp': datetime.now().isoformat(),
            'total_fundos': len(carteira_fundos),
            'fundos': {},
            'resumo': {
                'valor_total': 0,
                'fundos_encontrados': 0,
                'fundos_nao_encontrados': 0
            }
        }
        
        for fundo in carteira_fundos:
            cnpj = fundo.get('cnpj')
            valor = fundo.get('valor', 0)
            
            if cnpj:
                dados = self.get_fundo_data(cnpj, use_cache)
                if dados:
                    carteira_data['fundos'][cnpj] = {
                        'dados_fundo': dados,
                        'valor_carteira': valor,
                        'percentual_carteira': 0  # Será calculado depois
                    }
                    carteira_data['resumo']['fundos_encontrados'] += 1
                    carteira_data['resumo']['valor_total'] += valor
                    logger.info(f"✅ {cnpj}: Dados obtidos")
                else:
                    carteira_data['resumo']['fundos_nao_encontrados'] += 1
                    logger.warning(f"❌ {cnpj}: Dados não encontrados")
            
            # Delay entre requisições
            time.sleep(self.delay)
        
        # Calcular percentuais
        valor_total = carteira_data['resumo']['valor_total']
        if valor_total > 0:
            for fundo_data in carteira_data['fundos'].values():
                fundo_data['percentual_carteira'] = (fundo_data['valor_carteira'] / valor_total) * 100
        
        logger.info(f"Carteira processada: {carteira_data['resumo']['fundos_encontrados']}/{len(carteira_fundos)} fundos")
        return carteira_data
    
    def get_fundos_por_categoria(self, categoria: str = None, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Obtém fundos por categoria
        
        Args:
            categoria: Categoria dos fundos (ex: 'Cambial', 'Renda Fixa')
            use_cache: Se deve usar cache
            
        Returns:
            Lista de fundos da categoria
        """
        cache_key = f"fundos_categoria_{categoria or 'todos'}"
        
        # Tentar cache primeiro
        if use_cache:
            cached_data = self.cache_manager.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit para categoria {categoria}")
                return cached_data
        
        # Buscar fundos da categoria
        try:
            logger.info(f"Buscando fundos da categoria: {categoria or 'Todas'}")
            
            # Filtrar fundos do mapeamento por categoria
            fundos_categoria = []
            
            for cnpj, dados in self.mapeamento_fundos.get('mapeamento_fundos', {}).items():
                if not categoria or categoria.lower() in dados.get('categoria', '').lower():
                    fundos_categoria.append({
                        'cnpj': cnpj,
                        'nome': dados.get('nome', ''),
                        'categoria': dados.get('categoria', ''),
                        'slug': dados.get('slug', '')
                    })
            
            # Armazenar no cache
            if use_cache:
                self.cache_manager.set(
                    key=cache_key,
                    data=fundos_categoria,
                    data_type=DataType.FUND,
                    expires_in=7200,  # 2 horas
                    source=DataSource.UNKNOWN,
                    quality=DataQuality.GOOD
                )
            
            logger.info(f"Encontrados {len(fundos_categoria)} fundos na categoria {categoria}")
            return fundos_categoria
            
        except Exception as e:
            logger.error(f"Erro ao buscar fundos da categoria {categoria}: {e}")
            return []

def test_fundos_provider():
    """Teste do provider de fundos"""
    print("🧪 TESTE FUNDOS PROVIDER")
    print("=" * 50)
    
    try:
        # Configuração do cache
        config = {
            'memory': {
                'enabled': True,
                'max_size': 100,
                'cleanup_interval': 300
            },
            'persistent': {
                'enabled': True,
                'storage_type': 'json',
                'directory': 'test_fundos_cache',
                'backup_enabled': False,
                'backup_interval': 3600
            },
            'expiration': {
                'crypto': 60,
                'stock': 300,
                'fund': 3600
            }
        }
        
        # Inicializar Cache Manager
        from sistema_obtencao_dados.core.cache_manager import CacheManager
        from sistema_obtencao_dados.models.data_models import DataType, DataSource, DataQuality
        
        cache_manager = CacheManager(config)
        
        # Inicializar Provider
        provider = FundosProvider(cache_manager, delay_between_requests=2.0)
        
        # Teste 1: Buscar slug de fundo
        print("📊 Teste 1: Buscar slug de fundo...")
        cnpj_teste = "04.305.193/0001-40"  # BB Cambial Euro LP
        slug = provider.buscar_slug_fundo(cnpj_teste)
        print(f"   CNPJ: {cnpj_teste}")
        print(f"   Slug: {slug}")
        
        # Teste 2: Dados de fundo individual
        print("\n📊 Teste 2: Dados de fundo individual...")
        dados_fundo = provider.get_fundo_data(cnpj_teste, use_cache=True)
        if dados_fundo:
            print(f"   ✅ Dados obtidos: {dados_fundo.get('nome', 'N/A')}")
        else:
            print("   ❌ Dados não encontrados")
        
        # Teste 3: Múltiplos fundos
        print("\n📊 Teste 3: Múltiplos fundos...")
        cnpjs_teste = [
            "04.305.193/0001-40",  # BB Cambial Euro LP
            "20.077.065/0001-42",  # Mapfre FI Financeiro Cambial
            "24.633.789/0001-86"   # Sicredi FIF Cambial
        ]
        
        dados_multiplos = provider.get_multiple_fundos(cnpjs_teste, use_cache=True)
        print(f"   Resultados: {len(dados_multiplos)}/{len(cnpjs_teste)} fundos obtidos")
        
        # Teste 4: Fundos por categoria
        print("\n📊 Teste 4: Fundos por categoria...")
        fundos_cambiais = provider.get_fundos_por_categoria("Cambial", use_cache=True)
        print(f"   Fundos cambiais encontrados: {len(fundos_cambiais)}")
        
        # Estatísticas do cache
        stats = cache_manager.get_stats()
        print(f"\n📈 ESTATÍSTICAS DO CACHE:")
        print(f"   Hit Rate: {stats.get('hit_rate', 0):.1f}%")
        print(f"   Hits: {stats['hits']}")
        print(f"   Misses: {stats['misses']}")
        print(f"   Sets: {stats['sets']}")
        
        # Shutdown
        cache_manager.shutdown()
        print("\n✅ Teste concluído com sucesso!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_fundos_provider() 