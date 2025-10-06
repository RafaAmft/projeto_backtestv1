"""
Sistema de Análise de Portfólios - Informações de Versão
"""

__version__ = "1.1.0"
__version_info__ = {
    "major": 1,
    "minor": 1,
    "patch": 0,
    "release": "stable",
    "build": "20251006"
}

__title__ = "Sistema de Análise de Portfólios"
__description__ = "Sistema completo para análise de portfólios, auditoria de fundos e monitoramento de mercado"
__author__ = "Rafael Augusto Masson Fontes"
__author_email__ = "seu-email@example.com"
__license__ = "MIT"
__url__ = "https://github.com/RafaAmft/projeto_backtestv1"

# Compatibilidade
__python_requires__ = ">=3.10"
__status__ = "Production/Stable"

# APIs Integradas
__apis__ = [
    "Binance API",
    "Yahoo Finance",
    "CVM (local + scraping)",
    "Exchange Rate API",
    "IBGE API",
    "Mais Retorno (scraping)"
]

# Funcionalidades Principais
__features__ = [
    "Análise de Portfólios Multi-Ativos",
    "Métricas de Risco Avançadas",
    "Dashboard Interativo (Streamlit)",
    "Sistema de Cache Inteligente",
    "Relatórios Automatizados",
    "Auditoria de Fundos CVM",
    "Análise Temporal",
    "Benchmarking"
]


def get_version():
    """Retorna a versão atual do sistema"""
    return __version__


def get_version_info():
    """Retorna informações detalhadas da versão"""
    return __version_info__


def print_version():
    """Imprime informações de versão formatadas"""
    import sys
    
    # Garantir encoding UTF-8 no Windows
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except (AttributeError, OSError):
            # Python < 3.7 ou stdout não suporta reconfigure
            pass
    
    print(f"{'='*60}")
    print(f"{__title__}")
    print(f"Versão: {__version__} ({__status__})")
    print(f"Build: {__version_info__['build']}")
    print(f"Autor: {__author__}")
    print(f"Python: {__python_requires__}")
    print(f"{'='*60}")
    print(f"\nAPIs Integradas: {len(__apis__)}")
    for api in __apis__:
        print(f"  - {api}")
    print(f"\nFuncionalidades: {len(__features__)}")
    for feature in __features__:
        print(f"  - {feature}")
    print(f"{'='*60}")


if __name__ == "__main__":
    print_version()

