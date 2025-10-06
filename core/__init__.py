"""
Módulo core - Funcionalidades principais do sistema de análise financeira

Versão: 1.1.0
Data: 06/10/2025
"""

# Importar versão do projeto
import sys
from pathlib import Path

# Adicionar diretório raiz ao path para importar __version__
root_dir = Path(__file__).parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

try:
    from __version__ import __version__, __title__, __author__
except ImportError:
    __version__ = "1.1.0"
    __title__ = "Sistema de Análise de Portfólios"
    __author__ = "Rafael Augusto Masson Fontes"

# Imports principais
from .market_indices import MarketIndicesManager, market_indices

__all__ = [
    'MarketIndicesManager', 
    'market_indices',
    '__version__',
    '__title__',
    '__author__',
] 