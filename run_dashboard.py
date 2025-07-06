#!/usr/bin/env python3
"""
Script para executar o painel Streamlit
"""

import subprocess
import sys
import os

def main():
    """Executa o painel Streamlit"""
    
    # Verificar se o Streamlit está instalado
    try:
        import streamlit
    except ImportError:
        print("❌ Streamlit não está instalado. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
    
    # Verificar se o Selenium está instalado
    try:
        import selenium
    except ImportError:
        print("❌ Selenium não está instalado. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium"])
    
    # Verificar se o BeautifulSoup está instalado
    try:
        import bs4
    except ImportError:
        print("❌ BeautifulSoup não está instalado. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "beautifulsoup4"])
    
    # Executar o painel
    dashboard_path = os.path.join("dashboard", "portfolio_collector.py")
    
    if not os.path.exists(dashboard_path):
        print(f"❌ Arquivo do painel não encontrado: {dashboard_path}")
        return
    
    print("🚀 Iniciando painel Streamlit...")
    print("📊 Acesse: http://localhost:8501")
    print("⏹️  Para parar: Ctrl+C")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            dashboard_path, 
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Painel encerrado pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao executar painel: {e}")

if __name__ == "__main__":
    main() 