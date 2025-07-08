#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para gerar relatório do Data Manager em arquivo de texto
"""

import sys
import os
import subprocess
from datetime import datetime

def main():
    """Executa o teste e salva o resultado"""
    
    # Nome do arquivo de saída
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"relatorio_data_manager_{timestamp}.txt"
    
    print(f"Executando teste do Data Manager...")
    print(f"Arquivo de saída: {output_file}")
    
    try:
        # Executar o teste e capturar a saída
        result = subprocess.run(
            [sys.executable, "test_data_manager_integrated.py"],
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        # Salvar resultado em arquivo
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("RELATÓRIO DO DATA MANAGER - TESTE INTEGRADO\n")
            f.write("=" * 60 + "\n")
            f.write(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            # Saída padrão
            if result.stdout:
                f.write("SAÍDA PADRÃO:\n")
                f.write("-" * 30 + "\n")
                f.write(result.stdout)
                f.write("\n")
            
            # Saída de erro
            if result.stderr:
                f.write("SAÍDA DE ERRO:\n")
                f.write("-" * 30 + "\n")
                f.write(result.stderr)
                f.write("\n")
            
            # Código de retorno
            f.write(f"CÓDIGO DE RETORNO: {result.returncode}\n")
        
        print(f"✅ Relatório salvo em: {output_file}")
        
        # Mostrar resumo na tela
        print("\nRESUMO DO TESTE:")
        print("-" * 30)
        if result.stdout:
            lines = result.stdout.split('\n')
            for line in lines:
                if any(keyword in line for keyword in ['✅', '❌', '📊', '🎉']):
                    print(line)
        
    except Exception as e:
        print(f"❌ Erro ao executar teste: {e}")

if __name__ == "__main__":
    main() 