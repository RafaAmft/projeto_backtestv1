#!/usr/bin/env python3
"""
Gerenciador de Cache para Dados de Fundos de Investimento
========================================================

Este módulo gerencia o cache de dados de rentabilidade dos fundos,
evitando buscas repetidas no Mais Retorno para dados estáticos.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import hashlib

class FundCacheManager:
    """Gerenciador de cache para dados de fundos"""
    
    def __init__(self, cache_dir: str = "data/cache/funds"):
        """
        Inicializa o gerenciador de cache
        
        Args:
            cache_dir: Diretório para armazenar os arquivos de cache
        """
        self.cache_dir = cache_dir
        self.cache_file = os.path.join(cache_dir, "fund_cache.json")
        self.cache_index_file = os.path.join(cache_dir, "cache_index.json")
        
        # Criar diretório se não existir
        os.makedirs(cache_dir, exist_ok=True)
        
        # Carregar cache existente
        self.cache = self._load_cache()
        self.cache_index = self._load_cache_index()
    
    def _load_cache(self) -> Dict:
        """Carrega o cache do arquivo"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erro ao carregar cache: {e}")
        return {}
    
    def _save_cache(self):
        """Salva o cache no arquivo"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar cache: {e}")
    
    def _load_cache_index(self) -> Dict:
        """Carrega o índice do cache"""
        if os.path.exists(self.cache_index_file):
            try:
                with open(self.cache_index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Erro ao carregar índice do cache: {e}")
        return {}
    
    def _save_cache_index(self):
        """Salva o índice do cache"""
        try:
            with open(self.cache_index_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache_index, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar índice do cache: {e}")
    
    def _normalize_cnpj(self, cnpj: str) -> str:
        """Normaliza o CNPJ removendo caracteres especiais"""
        cnpj_clean = ''.join(filter(str.isdigit, str(cnpj)))
        if len(cnpj_clean) == 14:
            return f"{cnpj_clean[:2]}.{cnpj_clean[2:5]}.{cnpj_clean[5:8]}/{cnpj_clean[8:12]}-{cnpj_clean[12:]}"
        return cnpj_clean
    
    def _get_cache_key(self, cnpj: str) -> str:
        """Gera chave única para o cache baseada no CNPJ"""
        normalized_cnpj = self._normalize_cnpj(cnpj)
        return hashlib.md5(normalized_cnpj.encode()).hexdigest()
    
    def get_fund_data(self, cnpj: str) -> Optional[Dict]:
        """
        Busca dados do fundo no cache
        
        Args:
            cnpj: CNPJ do fundo
            
        Returns:
            Dados do fundo se encontrado no cache, None caso contrário
        """
        cache_key = self._get_cache_key(cnpj)
        
        if cache_key in self.cache:
            fund_data = self.cache[cache_key]
            
            # Verificar se o cache ainda é válido (30 dias)
            cache_date = datetime.fromisoformat(fund_data.get('cache_date', '2020-01-01'))
            if datetime.now() - cache_date < timedelta(days=30):
                print(f"✅ Dados do fundo {cnpj} encontrados no cache")
                return fund_data['data']
            else:
                print(f"⚠️ Cache expirado para o fundo {cnpj}")
                # Remover cache expirado
                del self.cache[cache_key]
                self._save_cache()
        
        return None
    
    def save_fund_data(self, cnpj: str, fund_data: Dict):
        """
        Salva dados do fundo no cache
        
        Args:
            cnpj: CNPJ do fundo
            fund_data: Dados do fundo para salvar
        """
        cache_key = self._get_cache_key(cnpj)
        
        cache_entry = {
            'cnpj': self._normalize_cnpj(cnpj),
            'cache_date': datetime.now().isoformat(),
            'data': fund_data
        }
        
        self.cache[cache_key] = cache_entry
        
        # Atualizar índice
        self.cache_index[cnpj] = {
            'cache_key': cache_key,
            'nome': fund_data.get('nome', 'Fundo não identificado'),
            'slug': fund_data.get('slug', ''),
            'cache_date': cache_entry['cache_date']
        }
        
        self._save_cache()
        self._save_cache_index()
        
        print(f"💾 Dados do fundo {cnpj} salvos no cache")
    
    def get_cache_stats(self) -> Dict:
        """
        Retorna estatísticas do cache
        
        Returns:
            Dicionário com estatísticas do cache
        """
        total_funds = len(self.cache)
        valid_funds = 0
        expired_funds = 0
        
        for cache_key, fund_data in self.cache.items():
            cache_date = datetime.fromisoformat(fund_data.get('cache_date', '2020-01-01'))
            if datetime.now() - cache_date < timedelta(days=30):
                valid_funds += 1
            else:
                expired_funds += 1
        
        return {
            'total_funds': total_funds,
            'valid_funds': valid_funds,
            'expired_funds': expired_funds,
            'cache_size_mb': self._get_cache_size_mb()
        }
    
    def _get_cache_size_mb(self) -> float:
        """Calcula o tamanho do cache em MB"""
        try:
            if os.path.exists(self.cache_file):
                size_bytes = os.path.getsize(self.cache_file)
                return round(size_bytes / (1024 * 1024), 2)
        except:
            pass
        return 0.0
    
    def clear_expired_cache(self) -> int:
        """
        Remove cache expirado
        
        Returns:
            Número de entradas removidas
        """
        expired_keys = []
        
        for cache_key, fund_data in self.cache.items():
            cache_date = datetime.fromisoformat(fund_data.get('cache_date', '2020-01-01'))
            if datetime.now() - cache_date >= timedelta(days=30):
                expired_keys.append(cache_key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            self._save_cache()
            print(f"🗑️ Removidas {len(expired_keys)} entradas expiradas do cache")
        
        return len(expired_keys)
    
    def clear_all_cache(self):
        """Remove todo o cache"""
        self.cache = {}
        self.cache_index = {}
        self._save_cache()
        self._save_cache_index()
        print("🗑️ Cache completamente limpo")
    
    def list_cached_funds(self) -> List[Dict]:
        """
        Lista todos os fundos em cache
        
        Returns:
            Lista com informações dos fundos em cache
        """
        funds = []
        
        for cnpj, info in self.cache_index.items():
            cache_date = datetime.fromisoformat(info.get('cache_date', '2020-01-01'))
            is_valid = datetime.now() - cache_date < timedelta(days=30)
            
            funds.append({
                'cnpj': cnpj,
                'nome': info.get('nome', 'Fundo não identificado'),
                'slug': info.get('slug', ''),
                'cache_date': info.get('cache_date'),
                'is_valid': is_valid
            })
        
        return sorted(funds, key=lambda x: x['nome'])
    
    def search_fund_by_name(self, search_term: str) -> List[Dict]:
        """
        Busca fundos por nome
        
        Args:
            search_term: Termo para busca
            
        Returns:
            Lista de fundos que correspondem à busca
        """
        search_term = search_term.lower()
        results = []
        
        for fund in self.list_cached_funds():
            if (search_term in fund['nome'].lower() or 
                search_term in fund['cnpj'].replace('.', '').replace('/', '').replace('-', '')):
                results.append(fund)
        
        return results

# Função utilitária para criar instância global
_cache_manager = None

def get_cache_manager() -> FundCacheManager:
    """Retorna instância global do gerenciador de cache"""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = FundCacheManager()
    return _cache_manager

if __name__ == "__main__":
    # Teste do cache manager
    cache_manager = FundCacheManager()
    
    print("📊 Estatísticas do Cache:")
    stats = cache_manager.get_cache_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n🏦 Fundos em Cache:")
    funds = cache_manager.list_cached_funds()
    for fund in funds:
        status = "✅" if fund['is_valid'] else "⚠️"
        print(f"  {status} {fund['nome']} ({fund['cnpj']})")
    
    if not funds:
        print("  Nenhum fundo em cache") 