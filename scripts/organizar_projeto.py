#!/usr/bin/env python3
"""
Script para Organizar o Projeto - Limpeza da Área Comum
=======================================================

Este script organiza os arquivos que estão poluindo a área comum do projeto,
movendo-os para diretórios apropriados.
"""

import os
import shutil
import json
from datetime import datetime
from pathlib import Path
import glob

class ProjetoOrganizer:
    """Organizador do projeto - limpa a área comum"""
    
    def __init__(self):
        self.root_dir = Path(".")
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Diretórios de destino
        self.dirs = {
            'relatorios': Path("relatorios_organizados"),
            'testes': Path("testes_organizados"),
            'dados': Path("data"),
            'debug': Path("arquivos_debug"),
            'cache': Path("relatorios_cache"),
            'graficos': Path("relatorios_cache/graficos"),
            'test_reports': Path("relatorios_cache/test_reports"),
            'yahoo_tests': Path("relatorios_cache/yahoo_tests")
        }
        
        # Criar diretórios se não existirem
        self._create_directories()
    
    def _create_directories(self):
        """Cria diretórios necessários"""
        for dir_path in self.dirs.values():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Diretório criado/verificado: {dir_path}")
    
    def organize_files(self):
        """Organiza todos os arquivos da área comum"""
        print("🧹 INICIANDO ORGANIZAÇÃO DO PROJETO")
        print("=" * 50)
        
        # 1. Mover relatórios JSON
        self._move_json_reports()
        
        # 2. Mover arquivos de teste
        self._move_test_files()
        
        # 3. Mover gráficos
        self._move_graphics()
        
        # 4. Mover arquivos de resultado
        self._move_result_files()
        
        # 5. Mover arquivos de debug
        self._move_debug_files()
        
        # 6. Limpar arquivos vazios
        self._clean_empty_files()
        
        print("\n✅ Organização concluída!")
        self._print_summary()
    
    def _move_json_reports(self):
        """Move relatórios JSON para diretório apropriado"""
        print("\n📄 Movendo relatórios JSON...")
        
        json_patterns = [
            "relatorio_carteira_ideal_*.json",
            "test_report_*.json",
            "yahoo_connection_test.json"
        ]
        
        for pattern in json_patterns:
            files = glob.glob(pattern)
            for file_path in files:
                src = Path(file_path)
                if src.exists():
                    # Determinar destino baseado no nome
                    if "relatorio_carteira_ideal" in file_path:
                        dst = self.dirs['relatorios'] / src.name
                    elif "test_report" in file_path:
                        dst = self.dirs['test_reports'] / src.name
                    elif "yahoo_connection" in file_path:
                        dst = self.dirs['yahoo_tests'] / src.name
                    else:
                        dst = self.dirs['relatorios'] / src.name
                    
                    try:
                        shutil.move(str(src), str(dst))
                        print(f"  ✅ {src.name} → {dst}")
                    except Exception as e:
                        print(f"  ❌ Erro ao mover {src.name}: {e}")
    
    def _move_test_files(self):
        """Move arquivos de teste para diretório apropriado"""
        print("\n🧪 Movendo arquivos de teste...")
        
        test_files = [
            "test_cotacoes_reais_fundos.py"
        ]
        
        for file_name in test_files:
            src = Path(file_name)
            if src.exists():
                dst = self.dirs['testes'] / src.name
                try:
                    shutil.move(str(src), str(dst))
                    print(f"  ✅ {src.name} → {dst}")
                except Exception as e:
                    print(f"  ❌ Erro ao mover {src.name}: {e}")
    
    def _move_graphics(self):
        """Move arquivos gráficos para diretório apropriado"""
        print("\n📊 Movendo gráficos...")
        
        graphics_patterns = [
            "*.png",
            "*.jpg",
            "*.jpeg"
        ]
        
        for pattern in graphics_patterns:
            files = glob.glob(pattern)
            for file_path in files:
                src = Path(file_path)
                if src.exists() and src.is_file():
                    dst = self.dirs['graficos'] / src.name
                    try:
                        shutil.move(str(src), str(dst))
                        print(f"  ✅ {src.name} → {dst}")
                    except Exception as e:
                        print(f"  ❌ Erro ao mover {src.name}: {e}")
    
    def _move_result_files(self):
        """Move arquivos de resultado para diretório apropriado"""
        print("\n📋 Movendo arquivos de resultado...")
        
        result_files = [
            "resultados_mapeamento_fundos.json",
            "resultados_busca_fundos.json",
            "resultados_busca_fundos_avancada.json",
            "audit_report.json",
            "resultado_data_manager.txt"
        ]
        
        for file_name in result_files:
            src = Path(file_name)
            if src.exists():
                dst = self.dirs['dados'] / src.name
                try:
                    shutil.move(str(src), str(dst))
                    print(f"  ✅ {src.name} → {dst}")
                except Exception as e:
                    print(f"  ❌ Erro ao mover {src.name}: {e}")
    
    def _move_debug_files(self):
        """Move arquivos de debug para diretório apropriado"""
        print("\n🐛 Movendo arquivos de debug...")
        
        debug_files = [
            "README_SISTEMA_NOVO.md"
        ]
        
        for file_name in debug_files:
            src = Path(file_name)
            if src.exists():
                dst = self.dirs['debug'] / src.name
                try:
                    shutil.move(str(src), str(dst))
                    print(f"  ✅ {src.name} → {dst}")
                except Exception as e:
                    print(f"  ❌ Erro ao mover {src.name}: {e}")
    
    def _clean_empty_files(self):
        """Remove arquivos vazios"""
        print("\n🧹 Limpando arquivos vazios...")
        
        for file_path in self.root_dir.glob("*"):
            if file_path.is_file() and file_path.stat().st_size == 0:
                try:
                    file_path.unlink()
                    print(f"  🗑️ Removido arquivo vazio: {file_path.name}")
                except Exception as e:
                    print(f"  ❌ Erro ao remover {file_path.name}: {e}")
    
    def _print_summary(self):
        """Imprime resumo da organização"""
        print("\n📊 RESUMO DA ORGANIZAÇÃO:")
        print("=" * 30)
        
        for dir_name, dir_path in self.dirs.items():
            if dir_path.exists():
                file_count = len(list(dir_path.glob("*")))
                print(f"📁 {dir_name}: {file_count} arquivos")
        
        # Contar arquivos na raiz
        root_files = [f for f in self.root_dir.iterdir() if f.is_file()]
        print(f"📁 Raiz: {len(root_files)} arquivos restantes")
        
        print("\n🎯 Arquivos importantes na raiz:")
        important_files = [
            "README.md", "requirements.txt", "run_dashboard.py",
            "carteira_ideal.json", "mapeamento_fundos.json",
            "ROADMAP.md", "RESUMO_EXECUTIVO.md", "CHECKPOINT_PROJETO.md"
        ]
        
        for file_name in important_files:
            if Path(file_name).exists():
                print(f"  ✅ {file_name}")
    
    def create_organization_report(self):
        """Cria relatório da organização"""
        report = {
            "timestamp": self.timestamp,
            "directories_created": [str(d) for d in self.dirs.values()],
            "organization_summary": "Projeto organizado com sucesso"
        }
        
        report_path = self.dirs['relatorios'] / f"organizacao_projeto_{self.timestamp}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 Relatório salvo em: {report_path}")

def main():
    """Função principal"""
    organizer = ProjetoOrganizer()
    
    # Confirmar antes de organizar
    print("⚠️ ATENÇÃO: Este script irá mover arquivos da área comum!")
    print("Arquivos que serão organizados:")
    print("- Relatórios JSON")
    print("- Arquivos de teste")
    print("- Gráficos")
    print("- Arquivos de resultado")
    print("- Arquivos de debug")
    
    response = input("\nContinuar? (s/N): ").strip().lower()
    if response != 's':
        print("❌ Operação cancelada")
        return
    
    # Executar organização
    organizer.organize_files()
    organizer.create_organization_report()
    
    print("\n🎉 Organização concluída com sucesso!")
    print("📁 A área comum agora está mais limpa e organizada!")

if __name__ == "__main__":
    main() 