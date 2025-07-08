#!/usr/bin/env python3
"""
Script para download de arquivos grandes de dados externos
Evita versionar arquivos grandes no Git usando Git LFS ou storage externo
"""

import os
import requests
import zipfile
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataDownloader:
    """Classe para gerenciar download de arquivos grandes de dados"""
    
    def __init__(self, data_dir: str = "data/external"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Carregar configurações do arquivo JSON
        config_file = Path(__file__).parent / "data_sources.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                self.data_sources = json.load(f)
        else:
            # Configurações padrão se arquivo não existir
            self.data_sources = {
                "fundos_historico": {
                    "url": "https://example.com/fundos_historico_nome_atual.csv",
                    "filename": "fundos_historico_nome_atual.csv",
                    "description": "Dados históricos de fundos de investimento",
                    "size_mb": 170
                },
                "acoes_historico": {
                    "url": "https://example.com/acoes_historico.csv",
                    "filename": "acoes_historico.csv", 
                    "description": "Dados históricos de ações",
                    "size_mb": 50
                }
            }
    
    def download_file(self, source_name: str, force: bool = False) -> bool:
        """
        Download de um arquivo específico
        
        Args:
            source_name: Nome da fonte de dados
            force: Forçar download mesmo se arquivo existir
            
        Returns:
            bool: True se download foi bem-sucedido
        """
        if source_name not in self.data_sources:
            logger.error(f"Fonte de dados '{source_name}' não encontrada")
            return False
            
        source = self.data_sources[source_name]
        file_path = self.data_dir / source["filename"]
        
        # Verificar se arquivo já existe
        if file_path.exists() and not force:
            logger.info(f"Arquivo {source['filename']} já existe. Use --force para re-download")
            return True
            
        logger.info(f"Iniciando download de {source['filename']} ({source['size_mb']}MB)...")
        
        try:
            response = requests.get(source["url"], stream=True)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    
            logger.info(f"Download concluído: {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erro no download: {e}")
            return False
    
    def download_all(self, force: bool = False) -> Dict[str, bool]:
        """
        Download de todos os arquivos configurados
        
        Args:
            force: Forçar download mesmo se arquivo existir
            
        Returns:
            Dict com status de cada download
        """
        results = {}
        
        for source_name in self.data_sources:
            logger.info(f"Processando: {source_name}")
            results[source_name] = self.download_file(source_name, force)
            
        return results
    
    def list_available_sources(self) -> List[str]:
        """Lista todas as fontes de dados disponíveis"""
        return list(self.data_sources.keys())
    
    def get_file_info(self, source_name: str) -> Optional[Dict]:
        """Obtém informações sobre um arquivo específico"""
        if source_name in self.data_sources:
            source = self.data_sources[source_name]
            file_path = self.data_dir / source["filename"]
            
            info = {
                "name": source_name,
                "filename": source["filename"],
                "description": source["description"],
                "size_mb": source["size_mb"],
                "url": source["url"],
                "exists": file_path.exists(),
                "local_path": str(file_path)
            }
            
            if file_path.exists():
                info["local_size_mb"] = round(file_path.stat().st_size / (1024 * 1024), 2)
                
            return info
        return None

def main():
    """Função principal do script"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Download de arquivos grandes de dados")
    parser.add_argument("--source", help="Nome da fonte de dados específica")
    parser.add_argument("--all", action="store_true", help="Download de todos os arquivos")
    parser.add_argument("--force", action="store_true", help="Forçar re-download")
    parser.add_argument("--list", action="store_true", help="Listar fontes disponíveis")
    parser.add_argument("--info", help="Mostrar informações de uma fonte específica")
    
    args = parser.parse_args()
    
    downloader = DataDownloader()
    
    if args.list:
        print("Fontes de dados disponíveis:")
        for source in downloader.list_available_sources():
            info = downloader.get_file_info(source)
            if info:
                status = "✓" if info["exists"] else "✗"
                print(f"  {status} {source}: {info['description']} ({info['size_mb']}MB)")
        return
    
    if args.info:
        info = downloader.get_file_info(args.info)
        if info:
            print(json.dumps(info, indent=2, ensure_ascii=False))
        else:
            print(f"Fonte '{args.info}' não encontrada")
        return
    
    if args.all:
        results = downloader.download_all(args.force)
        print("\nResumo dos downloads:")
        for source, success in results.items():
            status = "✓" if success else "✗"
            print(f"  {status} {source}")
        return
    
    if args.source:
        success = downloader.download_file(args.source, args.force)
        if success:
            print(f"✓ Download de '{args.source}' concluído")
        else:
            print(f"✗ Erro no download de '{args.source}'")
        return
    
    # Se nenhum argumento foi fornecido, mostrar ajuda
    parser.print_help()

if __name__ == "__main__":
    main() 