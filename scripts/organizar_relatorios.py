#!/usr/bin/env python3
"""
Script para Organizar Relatórios - Pasta Centralizada
=====================================================

Este script cria a pasta 'relatorios/' e organiza todos os relatórios
de forma profissional para o GitHub.
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path
import glob

class RelatoriosOrganizer:
    """Organizador de relatórios para GitHub"""
    
    def __init__(self):
        self.root_dir = Path(".")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Pasta principal de relatórios
        self.relatorios_dir = Path("relatorios")
        
        # Subpastas organizadas
        self.subdirs = {
            'carteira_ideal': self.relatorios_dir / "carteira_ideal",
            'portfolio': self.relatorios_dir / "portfolio", 
            'cache': self.relatorios_dir / "cache",
            'executivo': self.relatorios_dir / "executivo",
            'testes': self.relatorios_dir / "testes",
            'graficos': self.relatorios_dir / "graficos"
        }
        
        # Criar estrutura
        self._create_structure()
    
    def _create_structure(self):
        """Cria a estrutura de pastas"""
        print("📁 Criando estrutura de relatórios...")
        
        # Criar pasta principal
        self.relatorios_dir.mkdir(exist_ok=True)
        print(f"✅ Pasta principal criada: {self.relatorios_dir}")
        
        # Criar subpastas
        for name, dir_path in self.subdirs.items():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Subpasta criada: {dir_path}")
    
    def organize_reports(self):
        """Organiza todos os relatórios"""
        print("\n📋 ORGANIZANDO RELATÓRIOS")
        print("=" * 50)
        
        # 1. Relatórios de Carteira Ideal
        self._move_carteira_ideal_reports()
        
        # 2. Relatórios de Portfolio
        self._move_portfolio_reports()
        
        # 3. Relatórios de Cache
        self._move_cache_reports()
        
        # 4. Relatórios Executivos
        self._move_executive_reports()
        
        # 5. Relatórios de Testes
        self._move_test_reports()
        
        # 6. Gráficos
        self._move_graphics()
        
        print("\n✅ Organização concluída!")
        self._create_readme()
        self._print_summary()
    
    def _move_carteira_ideal_reports(self):
        """Move relatórios de carteira ideal"""
        print("\n🎯 Movendo relatórios de Carteira Ideal...")
        
        patterns = [
            "relatorio_carteira_ideal_*.txt",
            "relatorio_carteira_ideal_*.json"
        ]
        
        for pattern in patterns:
            files = glob.glob(pattern)
            for file_path in files:
                src = Path(file_path)
                if src.exists():
                    dst = self.subdirs['carteira_ideal'] / src.name
                    try:
                        shutil.move(str(src), str(dst))
                        print(f"  ✅ {src.name} → carteira_ideal/")
                    except Exception as e:
                        print(f"  ❌ Erro ao mover {src.name}: {e}")
    
    def _move_portfolio_reports(self):
        """Move relatórios de portfolio"""
        print("\n📊 Movendo relatórios de Portfolio...")
        
        patterns = [
            "relatorio_portfolio_*.txt",
            "relatorio_portfolio_*.json"
        ]
        
        for pattern in patterns:
            files = glob.glob(pattern)
            for file_path in files:
                src = Path(file_path)
                if src.exists():
                    dst = self.subdirs['portfolio'] / src.name
                    try:
                        shutil.move(str(src), str(dst))
                        print(f"  ✅ {src.name} → portfolio/")
                    except Exception as e:
                        print(f"  ❌ Erro ao mover {src.name}: {e}")
    
    def _move_cache_reports(self):
        """Move relatórios de cache"""
        print("\n💾 Movendo relatórios de Cache...")
        
        # Mover arquivos da pasta relatorios_cache
        cache_source = Path("relatorios_cache")
        if cache_source.exists():
            for file_path in cache_source.glob("*"):
                if file_path.is_file():
                    dst = self.subdirs['cache'] / file_path.name
                    try:
                        shutil.move(str(file_path), str(dst))
                        print(f"  ✅ {file_path.name} → cache/")
                    except Exception as e:
                        print(f"  ❌ Erro ao mover {file_path.name}: {e}")
    
    def _move_executive_reports(self):
        """Move relatórios executivos"""
        print("\n📋 Movendo relatórios Executivos...")
        
        patterns = [
            "relatorio_executivo_*.txt",
            "relatorio_executivo_*.json"
        ]
        
        for pattern in patterns:
            files = glob.glob(pattern)
            for file_path in files:
                src = Path(file_path)
                if src.exists():
                    dst = self.subdirs['executivo'] / src.name
                    try:
                        shutil.move(str(src), str(dst))
                        print(f"  ✅ {src.name} → executivo/")
                    except Exception as e:
                        print(f"  ❌ Erro ao mover {src.name}: {e}")
    
    def _move_test_reports(self):
        """Move relatórios de testes"""
        print("\n🧪 Movendo relatórios de Testes...")
        
        patterns = [
            "test_report_*.json",
            "teste_*.json",
            "yahoo_connection_test.json"
        ]
        
        for pattern in patterns:
            files = glob.glob(pattern)
            for file_path in files:
                src = Path(file_path)
                if src.exists():
                    dst = self.subdirs['testes'] / src.name
                    try:
                        shutil.move(str(src), str(dst))
                        print(f"  ✅ {src.name} → testes/")
                    except Exception as e:
                        print(f"  ❌ Erro ao mover {src.name}: {e}")
    
    def _move_graphics(self):
        """Move gráficos"""
        print("\n📈 Movendo gráficos...")
        
        patterns = ["*.png", "*.jpg", "*.jpeg"]
        
        for pattern in patterns:
            files = glob.glob(pattern)
            for file_path in files:
                src = Path(file_path)
                if src.exists() and src.is_file():
                    dst = self.subdirs['graficos'] / src.name
                    try:
                        shutil.move(str(src), str(dst))
                        print(f"  ✅ {src.name} → graficos/")
                    except Exception as e:
                        print(f"  ❌ Erro ao mover {src.name}: {e}")
    
    def _create_readme(self):
        """Cria README para a pasta de relatórios"""
        readme_content = f"""# 📋 Relatórios do Projeto

Esta pasta contém todos os relatórios gerados pelo sistema de análise financeira.

## 📁 Estrutura

### 🎯 `carteira_ideal/`
Relatórios da carteira ideal diversificada:
- `relatorio_carteira_ideal_YYYYMMDD_HHMMSS.txt` - Relatório completo em texto
- `relatorio_carteira_ideal_YYYYMMDD_HHMMSS.json` - Dados estruturados

### 📊 `portfolio/`
Relatórios de análise de portfólios:
- `relatorio_portfolio_YYYYMMDD_HHMMSS.txt` - Análise de portfólio

### 💾 `cache/`
Relatórios do sistema de cache:
- Relatórios de performance do cache
- Testes de integração
- Métricas de hit rate

### 📋 `executivo/`
Relatórios executivos:
- Resumos para tomada de decisão
- Métricas consolidadas
- Análises de risco

### 🧪 `testes/`
Relatórios de testes:
- Testes de APIs
- Validações de dados
- Relatórios de qualidade

### 📈 `graficos/`
Gráficos e visualizações:
- Evolução de carteiras
- Análises de performance
- Dashboards

## 🌐 Links Públicos

Após fazer push para o GitHub, os relatórios ficam disponíveis em:
- **Carteira Ideal**: https://github.com/RafaAmft/projeto_backtestv1/blob/main/relatorios/carteira_ideal/
- **Portfolio**: https://github.com/RafaAmft/projeto_backtestv1/blob/main/relatorios/portfolio/
- **Cache**: https://github.com/RafaAmft/projeto_backtestv1/blob/main/relatorios/cache/
- **Executivo**: https://github.com/RafaAmft/projeto_backtestv1/blob/main/relatorios/executivo/
- **Testes**: https://github.com/RafaAmft/projeto_backtestv1/blob/main/relatorios/testes/
- **Gráficos**: https://github.com/RafaAmft/projeto_backtestv1/blob/main/relatorios/graficos/

## 📅 Última Organização

Organizado em: {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}

## 🚀 Como Usar

1. **Visualizar relatórios**: Acesse os links do GitHub acima
2. **Baixar relatórios**: Clique em "Raw" no GitHub para download
3. **Gerar novos relatórios**: Execute os scripts correspondentes
4. **Organizar automaticamente**: Execute este script novamente

## 📊 Estatísticas

- **Total de relatórios**: {self._count_total_reports()}
- **Última atualização**: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
- **Versão**: 1.0

---
*Relatórios gerados automaticamente pelo Sistema de Análise Financeira*
"""
        
        readme_path = self.relatorios_dir / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"📄 README criado: {readme_path}")
    
    def _count_total_reports(self):
        """Conta total de relatórios"""
        total = 0
        for subdir in self.subdirs.values():
            if subdir.exists():
                total += len(list(subdir.glob("*")))
        return total
    
    def _print_summary(self):
        """Imprime resumo da organização"""
        print("\n📊 RESUMO DA ORGANIZAÇÃO:")
        print("=" * 30)
        
        for name, dir_path in self.subdirs.items():
            if dir_path.exists():
                file_count = len(list(dir_path.glob("*")))
                print(f"📁 {name}: {file_count} arquivos")
        
        total = self._count_total_reports()
        print(f"\n📋 Total: {total} relatórios organizados")
        
        print(f"\n🌐 Links públicos disponíveis após push:")
        print(f"   https://github.com/RafaAmft/projeto_backtestv1/blob/main/relatorios/")

def main():
    """Função principal"""
    print("📋 ORGANIZADOR DE RELATÓRIOS PARA GITHUB")
    print("=" * 50)
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    organizer = RelatoriosOrganizer()
    
    # Confirmar antes de organizar
    print("\n⚠️ ATENÇÃO: Este script irá mover relatórios para a pasta 'relatorios/'")
    print("Arquivos que serão organizados:")
    print("- Relatórios de carteira ideal")
    print("- Relatórios de portfolio")
    print("- Relatórios de cache")
    print("- Relatórios executivos")
    print("- Relatórios de testes")
    print("- Gráficos")
    
    response = input("\nContinuar? (s/N): ").strip().lower()
    if response != 's':
        print("❌ Operação cancelada")
        return
    
    # Executar organização
    organizer.organize_reports()
    
    print("\n🎉 Organização concluída com sucesso!")
    print("📁 Relatórios organizados em: relatorios/")
    print("🌐 Faça push para o GitHub para gerar os links públicos!")

if __name__ == "__main__":
    main() 