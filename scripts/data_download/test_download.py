#!/usr/bin/env python3
"""
Script de teste para o sistema de download de arquivos grandes
"""

import sys
from pathlib import Path

# Adicionar o diretório pai ao path para importar o módulo
sys.path.append(str(Path(__file__).parent))

from download_large_files import DataDownloader

def test_downloader():
    """Testa as funcionalidades do DataDownloader"""
    
    print("=== Teste do Sistema de Download de Arquivos Grandes ===\n")
    
    # Criar instância do downloader
    downloader = DataDownloader()
    
    # Teste 1: Listar fontes disponíveis
    print("1. Fontes de dados disponíveis:")
    sources = downloader.list_available_sources()
    for source in sources:
        info = downloader.get_file_info(source)
        if info:
            status = "✓" if info["exists"] else "✗"
            print(f"   {status} {source}: {info['description']} ({info['size_mb']}MB)")
    print()
    
    # Teste 2: Informações detalhadas de uma fonte
    if sources:
        print("2. Informações detalhadas da primeira fonte:")
        first_source = sources[0]
        info = downloader.get_file_info(first_source)
        if info:
            print(f"   Nome: {info['name']}")
            print(f"   Arquivo: {info['filename']}")
            print(f"   Descrição: {info['description']}")
            print(f"   Tamanho: {info['size_mb']}MB")
            print(f"   URL: {info['url']}")
            print(f"   Existe localmente: {info['exists']}")
            print(f"   Caminho local: {info['local_path']}")
        print()
    
    # Teste 3: Verificar estrutura de diretórios
    print("3. Estrutura de diretórios:")
    data_dir = downloader.data_dir
    print(f"   Diretório de dados: {data_dir}")
    print(f"   Diretório existe: {data_dir.exists()}")
    if data_dir.exists():
        files = list(data_dir.glob("*"))
        if files:
            print("   Arquivos encontrados:")
            for file in files:
                size_mb = file.stat().st_size / (1024 * 1024)
                print(f"     - {file.name} ({size_mb:.2f}MB)")
        else:
            print("   Nenhum arquivo encontrado")
    print()
    
    # Teste 4: Simular download (sem fazer download real)
    print("4. Simulação de download:")
    print("   Para fazer download real, use:")
    print("   python download_large_files.py --source <nome_fonte>")
    print("   python download_large_files.py --all")
    print()
    
    print("=== Teste concluído ===")

if __name__ == "__main__":
    test_downloader() 