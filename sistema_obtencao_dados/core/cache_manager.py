#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerenciador de Cache Robusto
Cache em memória + persistente com backup automático
"""

import json
import os
import shutil
import threading
import time
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List
from pathlib import Path
import logging
import hashlib
import pickle
import gzip

from ..models.data_models import CacheEntry, DataType, DataSource, DataQuality

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Gerenciador de cache robusto com múltiplas camadas
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Inicializa o gerenciador de cache
        
        Args:
            config: Configurações do cache
        """
        self.config = config
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.persistent_cache_dir = Path(config['persistent']['directory'])
        self.backup_dir = self.persistent_cache_dir / "backups"
        
        # Criar diretórios se não existirem
        self.persistent_cache_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurações
        self.max_memory_size = config['memory']['max_size']
        self.cleanup_interval = config['memory']['cleanup_interval']
        self.backup_enabled = config['persistent']['backup_enabled']
        self.backup_interval = config['persistent']['backup_interval']
        
        # Threading
        self.lock = threading.RLock()
        self._cleanup_thread = None
        self._backup_thread = None
        self._running = False
        
        # Estatísticas
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'backups': 0,
            'last_backup': None
        }
        
        # Iniciar threads de manutenção
        self._start_maintenance_threads()
        
        # Carregar cache persistente
        self._load_persistent_cache()
        
        logger.info(f"Cache Manager inicializado - Memória: {self.max_memory_size} itens")
    
    def _start_maintenance_threads(self):
        """Inicia threads de manutenção do cache"""
        self._running = True
        
        # Thread de limpeza
        self._cleanup_thread = threading.Thread(
            target=self._cleanup_worker,
            daemon=True,
            name="CacheCleanup"
        )
        self._cleanup_thread.start()
        
        # Thread de backup
        if self.backup_enabled:
            self._backup_thread = threading.Thread(
                target=self._backup_worker,
                daemon=True,
                name="CacheBackup"
            )
            self._backup_thread.start()
        
        logger.info("Threads de manutenção do cache iniciadas")
    
    def _cleanup_worker(self):
        """Worker para limpeza automática do cache"""
        while self._running:
            try:
                time.sleep(self.cleanup_interval)
                self._cleanup_expired_entries()
            except Exception as e:
                logger.error(f"Erro na limpeza do cache: {e}")
    
    def _backup_worker(self):
        """Worker para backup automático do cache"""
        while self._running:
            try:
                time.sleep(self.backup_interval)
                self._create_backup()
            except Exception as e:
                logger.error(f"Erro no backup do cache: {e}")
    
    def _cleanup_expired_entries(self):
        """Remove entradas expiradas do cache"""
        with self.lock:
            current_time = datetime.now()
            expired_keys = []
            
            # Verificar cache em memória
            for key, entry in self.memory_cache.items():
                if entry.is_expired():
                    expired_keys.append(key)
            
            # Remover entradas expiradas
            for key in expired_keys:
                del self.memory_cache[key]
                self.stats['deletes'] += 1
            
            # Limpar cache persistente expirado
            self._cleanup_persistent_cache()
            
            if expired_keys:
                logger.info(f"Removidas {len(expired_keys)} entradas expiradas do cache")
    
    def _cleanup_persistent_cache(self):
        """Limpa entradas expiradas do cache persistente"""
        try:
            for cache_file in self.persistent_cache_dir.glob("*.json"):
                if cache_file.name == "cache_index.json":
                    continue
                
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        entry_data = json.load(f)
                    
                    entry = CacheEntry.from_dict(entry_data)
                    if entry.is_expired():
                        cache_file.unlink()
                        logger.debug(f"Removido arquivo de cache expirado: {cache_file.name}")
                
                except Exception as e:
                    logger.warning(f"Erro ao processar arquivo de cache {cache_file}: {e}")
        
        except Exception as e:
            logger.error(f"Erro na limpeza do cache persistente: {e}")
    
    def _create_backup(self):
        """Cria backup do cache persistente"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"cache_backup_{timestamp}.tar.gz"
            
            # Criar arquivo tar.gz com todos os arquivos de cache
            with open(backup_file, 'wb') as f:
                with gzip.open(f, 'wt') as gz:
                    for cache_file in self.persistent_cache_dir.glob("*.json"):
                        if cache_file.name == "cache_index.json":
                            continue
                        
                        try:
                            with open(cache_file, 'r', encoding='utf-8') as cf:
                                content = cf.read()
                                gz.write(f"{cache_file.name}\n")
                                gz.write(content)
                                gz.write("\n")
                        except Exception as e:
                            logger.warning(f"Erro ao incluir {cache_file} no backup: {e}")
            
            self.stats['backups'] += 1
            self.stats['last_backup'] = datetime.now()
            
            # Manter apenas os últimos 5 backups
            self._cleanup_old_backups()
            
            logger.info(f"Backup do cache criado: {backup_file}")
        
        except Exception as e:
            logger.error(f"Erro ao criar backup do cache: {e}")
    
    def _cleanup_old_backups(self):
        """Remove backups antigos, mantendo apenas os últimos 5"""
        try:
            backup_files = sorted(self.backup_dir.glob("cache_backup_*.tar.gz"))
            if len(backup_files) > 5:
                for old_backup in backup_files[:-5]:
                    old_backup.unlink()
                    logger.debug(f"Backup antigo removido: {old_backup}")
        
        except Exception as e:
            logger.error(f"Erro ao limpar backups antigos: {e}")
    
    def _load_persistent_cache(self):
        """Carrega cache persistente na memória"""
        try:
            index_file = self.persistent_cache_dir / "cache_index.json"
            if not index_file.exists():
                return
            
            with open(index_file, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            
            # Carregar apenas entradas não expiradas
            loaded_count = 0
            for key, entry_data in index_data.items():
                try:
                    entry = CacheEntry.from_dict(entry_data)
                    if not entry.is_expired():
                        self.memory_cache[key] = entry
                        loaded_count += 1
                except Exception as e:
                    logger.warning(f"Erro ao carregar entrada do cache: {e}")
            
            logger.info(f"Cache persistente carregado: {loaded_count} entradas")
        
        except Exception as e:
            logger.error(f"Erro ao carregar cache persistente: {e}")
    
    def _save_persistent_cache(self):
        """Salva cache em memória no disco"""
        try:
            # Salvar entradas individuais
            for key, entry in self.memory_cache.items():
                cache_file = self.persistent_cache_dir / f"{self._hash_key(key)}.json"
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(entry.to_dict(), f, ensure_ascii=False, indent=2)
            
            # Salvar índice
            index_data = {key: entry.to_dict() for key, entry in self.memory_cache.items()}
            index_file = self.persistent_cache_dir / "cache_index.json"
            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, ensure_ascii=False, indent=2)
        
        except Exception as e:
            logger.error(f"Erro ao salvar cache persistente: {e}")
    
    def _hash_key(self, key: str) -> str:
        """Gera hash para o nome do arquivo de cache"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """
        Obtém valor do cache
        
        Args:
            key: Chave do cache
            
        Returns:
            Valor do cache ou None se não encontrado/expirado
        """
        with self.lock:
            if key in self.memory_cache:
                entry = self.memory_cache[key]
                
                if entry.is_expired():
                    del self.memory_cache[key]
                    self.stats['misses'] += 1
                    return None
                
                # Atualizar estatísticas de acesso
                entry.access_count += 1
                entry.last_accessed = datetime.now()
                
                self.stats['hits'] += 1
                return entry.data
            
            self.stats['misses'] += 1
            return None
    
    def set(self, key: str, data: Any, data_type: DataType, 
            expires_in: Optional[int] = None, source: DataSource = DataSource.UNKNOWN,
            quality: DataQuality = DataQuality.UNKNOWN) -> None:
        """
        Armazena valor no cache
        
        Args:
            key: Chave do cache
            data: Dados a serem armazenados
            data_type: Tipo dos dados
            expires_in: Tempo de expiração em segundos
            source: Fonte dos dados
            quality: Qualidade dos dados
        """
        with self.lock:
            # Calcular tempo de expiração
            expires_at = None
            if expires_in:
                expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            # Criar entrada do cache
            entry = CacheEntry(
                key=key,
                data=data,
                data_type=data_type,
                timestamp=datetime.now(),
                expires_at=expires_at,
                source=source,
                quality=quality
            )
            
            # Verificar se há espaço no cache
            if len(self.memory_cache) >= self.max_memory_size:
                self._evict_least_used()
            
            # Armazenar no cache
            self.memory_cache[key] = entry
            self.stats['sets'] += 1
            
            # Salvar no cache persistente
            self._save_persistent_cache()
    
    def _evict_least_used(self):
        """Remove a entrada menos usada do cache (LRU)"""
        if not self.memory_cache:
            return
        
        # Encontrar entrada com menor contador de acesso
        least_used_key = min(
            self.memory_cache.keys(),
            key=lambda k: self.memory_cache[k].access_count
        )
        
        del self.memory_cache[least_used_key]
        logger.debug(f"Entrada removida do cache (LRU): {least_used_key}")
    
    def delete(self, key: str) -> bool:
        """
        Remove entrada do cache
        
        Args:
            key: Chave a ser removida
            
        Returns:
            True se removido, False se não encontrado
        """
        with self.lock:
            if key in self.memory_cache:
                del self.memory_cache[key]
                self.stats['deletes'] += 1
                
                # Remover do cache persistente
                cache_file = self.persistent_cache_dir / f"{self._hash_key(key)}.json"
                if cache_file.exists():
                    cache_file.unlink()
                
                self._save_persistent_cache()
                return True
            
            return False
    
    def clear(self) -> None:
        """Limpa todo o cache"""
        with self.lock:
            self.memory_cache.clear()
            
            # Limpar cache persistente
            for cache_file in self.persistent_cache_dir.glob("*.json"):
                cache_file.unlink()
            
            logger.info("Cache completamente limpo")
    
    def exists(self, key: str) -> bool:
        """
        Verifica se chave existe no cache
        
        Args:
            key: Chave a ser verificada
            
        Returns:
            True se existe e não expirou
        """
        with self.lock:
            if key in self.memory_cache:
                entry = self.memory_cache[key]
                if entry.is_expired():
                    del self.memory_cache[key]
                    return False
                return True
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtém estatísticas do cache
        
        Returns:
            Dicionário com estatísticas
        """
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                **self.stats,
                'total_requests': total_requests,
                'hit_rate': round(hit_rate, 2),
                'memory_size': len(self.memory_cache),
                'max_memory_size': self.max_memory_size,
                'memory_usage_percent': round(len(self.memory_cache) / self.max_memory_size * 100, 2)
            }
    
    def get_keys(self, pattern: Optional[str] = None) -> List[str]:
        """
        Obtém lista de chaves no cache
        
        Args:
            pattern: Padrão para filtrar chaves (opcional)
            
        Returns:
            Lista de chaves
        """
        with self.lock:
            keys = list(self.memory_cache.keys())
            
            if pattern:
                import fnmatch
                keys = [k for k in keys if fnmatch.fnmatch(k, pattern)]
            
            return keys
    
    def shutdown(self):
        """Desliga o gerenciador de cache"""
        self._running = False
        
        # Aguardar threads terminarem
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=5)
        
        if self._backup_thread and self._backup_thread.is_alive():
            self._backup_thread.join(timeout=5)
        
        # Salvar cache final
        self._save_persistent_cache()
        
        logger.info("Cache Manager desligado")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown() 