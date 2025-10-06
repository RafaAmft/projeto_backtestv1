# 📘 Boas Práticas de Código – Cursora AI

**Versão:** 1.1.0  
**Data:** 06/10/2025  
**Status:** Estável

Guia de referência para manter consistência, qualidade e segurança no desenvolvimento em **Python backend** e **análise de dados**.

---

## 📋 Changelog

### [1.1.0] - 2025-10-06
#### Adicionado
- Exemplos práticos de Conventional Commits
- Estrutura de projeto completa e corrigida
- Seção expandida sobre nomenclaturas Python
- Exemplos de testes com pytest (fixtures, mocks, parametrização)
- Complementos para análise de dados financeiros
- Seção completa de CI/CD com GitHub Actions
- Exemplos de Docker e pre-commit hooks
- Validação de dados financeiros

#### Corrigido
- Formatação da estrutura de projeto
- Organização visual do documento

### [1.0.0] - 2025-07-08
- Versão inicial do guia

---

## 🔹 Git Workflow

### Commits Descritivos
- Use [Conventional Commits](https://www.conventionalcommits.org/) para padronização.
- PRs devem ter pelo menos 1 revisão aprovada antes do merge.
- Adote versionamento semântico (**semver**): `major.minor.patch`.
- Nunca commitar `.env`, `venv/`, `__pycache__/` ou dados sensíveis.

### Exemplos de Commits:
```bash
feat: adicionar suporte para fundos imobiliários
fix: corrigir cálculo do Sharpe Ratio
docs: atualizar README com exemplos de uso
refactor: reorganizar estrutura de cache
test: adicionar testes para portfolio_collector
perf: otimizar consultas ao banco de dados
chore: atualizar dependências do projeto
style: formatar código com black
```

### Branch Strategy (GitFlow):
```
main (produção)
  ↑
  └── release/v1.1.0
        ↑
        └── develop (homologação)
              ↑
              ├── feature/nova-funcionalidade
              ├── feature/suporte-fundos-imobiliarios
              └── fix/corrigir-sharpe-ratio
```

### Tags e Versionamento:
```bash
# Criar tag anotada
git tag -a v1.1.0 -m "Versão 1.1.0 - Melhorias e correções"

# Enviar tags para repositório remoto
git push origin v1.1.0

# Listar todas as tags
git tag -l
```

---

## 🔹 Estrutura de Projeto

```
project_root/
├── src/                      # Código fonte principal
│   ├── __init__.py
│   ├── core/                # Lógica de negócio
│   │   ├── __init__.py
│   │   ├── portfolio.py
│   │   └── market_indices.py
│   ├── apis/                # Integrações com APIs externas
│   │   ├── __init__.py
│   │   ├── binance_api.py
│   │   ├── yahoo_api.py
│   │   └── cvm_api.py
│   ├── dashboard/           # Interface e visualização
│   │   ├── __init__.py
│   │   └── portfolio_collector.py
│   └── utils/               # Utilitários e helpers
│       ├── __init__.py
│       └── validators.py
├── tests/                   # Testes automatizados
│   ├── __init__.py
│   ├── unit/               # Testes unitários
│   │   └── test_portfolio.py
│   ├── integration/        # Testes de integração
│   │   └── test_apis.py
│   └── fixtures/           # Dados de teste
│       └── sample_data.json
├── data/                    # Dados (gitignored se sensível)
│   ├── raw/                # Dados brutos originais
│   ├── processed/          # Dados processados
│   └── cache/              # Cache temporário
├── docs/                    # Documentação
│   ├── README.md
│   └── API.md
├── scripts/                 # Scripts auxiliares
│   ├── setup.py
│   └── data_download.py
├── config/                  # Arquivos de configuração
│   ├── config.yaml
│   └── config.example.yaml
├── relatorios/             # Relatórios gerados
│   ├── portfolio/
│   └── executivo/
├── .env.example            # Template de variáveis de ambiente
├── .gitignore
├── .gitattributes
├── requirements.txt        # Dependências Python
├── pyproject.toml          # Configuração do projeto (Poetry/setuptools)
├── README.md               # Documentação principal
├── CHANGELOG.md            # Histórico de mudanças
└── boaspraticas.md         # Este arquivo
```

### Princípios:
- ✅ Código de produção em `src/`
- ✅ Testes separados em `tests/`
- ✅ Dependências sempre declaradas em `requirements.txt` ou `pyproject.toml`
- ✅ Configurações em arquivos separados, nunca hardcoded
- ✅ Dados sensíveis sempre no `.gitignore`

---

## 🔹 Python

### Configuração Básica
- **Versão**: Padronizar Python >= 3.10 (recomendado 3.11+).
- **Estilo**: Seguir [PEP 8](https://peps.python.org/pep-0008/).
- **Tipagem**: Usar `type hints` em funções públicas.
- **Docstrings**: Seguir [PEP 257](https://peps.python.org/pep-0257/).

### Convenções de Nomenclatura
```python
# Classes: PascalCase
class PortfolioAnalyzer:
    pass

# Funções e variáveis: snake_case
def calculate_sharpe_ratio(returns: list) -> float:
    pass

# Constantes: UPPER_SNAKE_CASE
MAX_PORTFOLIO_SIZE = 1000000
API_TIMEOUT = 30

# Métodos privados: prefixo _
def _internal_validation(self):
    pass

# Variáveis privadas de classe: prefixo __
class MyClass:
    __private_attr = "value"
```

### Imports
```python
# Ordem: stdlib → terceiros → locais
import os
import sys
from datetime import datetime

import pandas as pd
import numpy as np
from requests import Session

from src.core.portfolio import Portfolio
from src.utils.validators import validate_cnpj
```
- ✅ Preferir imports absolutos
- ✅ Agrupar imports por categoria
- ✅ Ordenar alfabeticamente dentro de cada grupo

### Type Hints
```python
from typing import List, Dict, Optional, Union
from decimal import Decimal

def calculate_returns(
    prices: List[float],
    period: int = 252,
    annualize: bool = True
) -> Dict[str, float]:
    """Calcula retornos de uma série de preços.
    
    Args:
        prices: Lista de preços históricos
        period: Período para cálculo (padrão: 252 dias úteis)
        annualize: Se True, anualiza os retornos
    
    Returns:
        Dicionário com métricas de retorno
        
    Raises:
        ValueError: Se prices estiver vazio
    """
    if not prices:
        raise ValueError("Lista de preços não pode estar vazia")
    
    # implementação...
    return {"mean": 0.0, "std": 0.0}
```

### Logging (nunca usar print() em produção)
```python
import logging

# Configuração básica
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Uso
logger.debug("Detalhes de debug")
logger.info("Processando carteira: %s", portfolio_name)
logger.warning("Cache desatualizado, recarregando dados")
logger.error("Erro ao buscar dados da API: %s", error)
logger.critical("Falha crítica no sistema")
```

### Tratamento de Erros
```python
# ❌ Evitar genérico
try:
    result = calculate_something()
except Exception as e:
    print(e)

# ✅ Usar exceções específicas
try:
    result = calculate_sharpe_ratio(returns)
except ValueError as e:
    logger.error(f"Dados inválidos para cálculo: {e}")
    raise
except ZeroDivisionError:
    logger.warning("Volatilidade zero detectada, retornando 0")
    return 0.0

# ✅ Criar exceções customizadas
class PortfolioValidationError(Exception):
    """Exceção para erros de validação de carteira"""
    pass

def validate_portfolio(portfolio: Dict) -> None:
    if portfolio['value'] <= 0:
        raise PortfolioValidationError(
            f"Valor da carteira deve ser positivo, recebido: {portfolio['value']}"
        )
```

### Context Managers
```python
# ✅ Sempre usar para gerenciar recursos
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Para conexões de banco
from sqlalchemy import create_engine

engine = create_engine('postgresql://...')
with engine.connect() as conn:
    result = conn.execute(query)
    
# Custom context manager
from contextlib import contextmanager

@contextmanager
def temporary_cache():
    cache = {}
    try:
        yield cache
    finally:
        cache.clear()
```

### Configurações (nunca hardcoded)
```python
import os
from dotenv import load_dotenv

load_dotenv()

# ❌ Nunca fazer isso
API_KEY = "abc123xyz"
DATABASE_URL = "postgresql://user:pass@localhost/db"

# ✅ Usar variáveis de ambiente
API_KEY = os.getenv("API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# ✅ Com valores padrão e validação
API_TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))

if not API_KEY:
    raise EnvironmentError("API_KEY não configurada")
```

### Performance
```python
# ✅ List comprehensions (mais rápido)
squares = [x**2 for x in range(1000)]

# ✅ Generator expressions (economia de memória)
sum_squares = sum(x**2 for x in range(1000000))

# ✅ Use yield para datasets grandes
def read_large_file(file_path: str):
    with open(file_path) as f:
        for line in f:
            yield line.strip()

# ✅ Profiling quando necessário
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
# código a perfilar
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # Top 10 funções mais lentas
```

### Gerenciamento de Dependências
```txt
# requirements.txt - Fixar versões em produção
pandas==2.0.3
numpy==1.24.4
yfinance==0.2.28

# Ou com ranges compatíveis
requests>=2.28.0,<3.0.0  # Aceita patches e minors da v2
scipy~=1.11.0            # Aceita apenas patches (1.11.x)
```

---

## 🔹 Testes

### Configuração
- **Framework**: pytest (recomendado)
- **Nomenclatura**: Arquivos `test_*.py` ou `*_test.py`
- **Cobertura mínima**: 80% (ideal: 90%+)
- **Estrutura**:
  - **Unitários** → Funções isoladas
  - **Integração** → Interação entre módulos
  - **E2E** (end-to-end) → Fluxos completos

### Estrutura Básica de Teste (AAA Pattern)
```python
# tests/unit/test_portfolio.py
import pytest
from src.core.portfolio import Portfolio

def test_calculate_sharpe_ratio():
    """Testa cálculo do Sharpe Ratio"""
    # Arrange (Preparar)
    portfolio = Portfolio(value=100000)
    portfolio.returns = [0.01, 0.02, -0.01, 0.03]
    expected_ratio = 0.53
    
    # Act (Agir)
    result = portfolio.calculate_sharpe_ratio()
    
    # Assert (Verificar)
    assert abs(result - expected_ratio) < 0.01
    assert isinstance(result, float)
```

### Fixtures (Dados Reutilizáveis)
```python
import pytest
from datetime import datetime

@pytest.fixture
def sample_portfolio():
    """Fixture de carteira padrão para testes"""
    return Portfolio(
        value=100000,
        assets=[
            {"name": "PETR4", "value": 40000},
            {"name": "VALE3", "value": 60000}
        ],
        created_at=datetime(2025, 1, 1)
    )

@pytest.fixture
def mock_market_data():
    """Fixture com dados de mercado simulados"""
    return {
        "PETR4": {"price": 32.50, "volume": 1000000},
        "VALE3": {"price": 54.60, "volume": 800000}
    }

def test_portfolio_allocation(sample_portfolio):
    """Usa fixture para testar alocação"""
    allocation = sample_portfolio.get_allocation()
    assert allocation["PETR4"] == 0.4
    assert allocation["VALE3"] == 0.6
```

### Mocking APIs Externas
```python
from unittest.mock import patch, MagicMock
import pytest

@pytest.fixture
def mock_binance_api(monkeypatch):
    """Mock da API Binance"""
    def mock_get_price(symbol):
        prices = {
            "BTCUSDT": 50000.0,
            "ETHUSDT": 3000.0
        }
        return prices.get(symbol, 0.0)
    
    monkeypatch.setattr("src.apis.binance_api.get_price", mock_get_price)

def test_crypto_portfolio_value(mock_binance_api):
    """Testa valor de carteira cripto com API mockada"""
    portfolio = CryptoPortfolio({"BTCUSDT": 1, "ETHUSDT": 10})
    
    expected_value = 50000 + (10 * 3000)  # 80000
    assert portfolio.get_total_value() == expected_value

# Usando @patch decorator
@patch('src.apis.yahoo_api.yfinance.download')
def test_fetch_stock_data(mock_download):
    """Mock do yfinance.download"""
    mock_download.return_value = pd.DataFrame({
        'Close': [32.5, 33.0, 32.8]
    })
    
    data = fetch_stock_data("PETR4.SA")
    assert len(data) == 3
    assert data['Close'].iloc[0] == 32.5
```

### Testes Parametrizados
```python
@pytest.mark.parametrize("value,expected_tier", [
    (10000, "bronze"),
    (100000, "silver"),
    (500000, "gold"),
    (1000000, "platinum"),
])
def test_portfolio_tier(value, expected_tier):
    """Testa classificação de carteira por valor"""
    portfolio = Portfolio(value=value)
    assert portfolio.get_tier() == expected_tier

@pytest.mark.parametrize("returns,expected", [
    ([0.01, 0.02, 0.03], 0.02),  # Média positiva
    ([-0.01, -0.02, -0.03], -0.02),  # Média negativa
    ([0, 0, 0], 0.0),  # Zero
])
def test_average_return(returns, expected):
    """Testa cálculo de retorno médio"""
    result = calculate_average_return(returns)
    assert abs(result - expected) < 0.001
```

### Testando Exceções
```python
def test_negative_portfolio_value_raises_error():
    """Verifica se valor negativo levanta exceção"""
    with pytest.raises(ValueError, match="Valor deve ser positivo"):
        Portfolio(value=-1000)

def test_empty_returns_raises_error():
    """Verifica erro ao calcular Sharpe sem retornos"""
    portfolio = Portfolio(value=100000)
    with pytest.raises(ValueError) as exc_info:
        portfolio.calculate_sharpe_ratio()
    
    assert "retornos vazia" in str(exc_info.value).lower()
```

### Markers (Categorização de Testes)
```python
@pytest.mark.slow
def test_large_dataset_processing():
    """Teste lento com dataset grande"""
    data = load_large_dataset()
    result = process_data(data)
    assert len(result) > 1000000

@pytest.mark.integration
def test_api_integration():
    """Teste de integração com API real"""
    api = BinanceAPI()
    price = api.get_price("BTCUSDT")
    assert price > 0

@pytest.mark.skip(reason="API temporariamente indisponível")
def test_external_api():
    """Teste a ser pulado"""
    pass

# Executar apenas testes rápidos:
# pytest -m "not slow"
# Executar apenas integração:
# pytest -m integration
```

### Cobertura de Código
```bash
# Instalar pytest-cov
pip install pytest-cov

# Executar com relatório de cobertura
pytest --cov=src --cov-report=html --cov-report=term

# Ver relatório detalhado
# Abre: htmlcov/index.html

# Falhar se cobertura < 80%
pytest --cov=src --cov-fail-under=80
```

### Configuração pytest.ini
```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

# Markers customizados
markers =
    slow: marca testes lentos
    integration: testes de integração
    unit: testes unitários
    api: testes que usam APIs externas

# Opções padrão
addopts = 
    --verbose
    --strict-markers
    --cov=src
    --cov-report=term-missing
    --cov-report=html

# Ignorar warnings específicos
filterwarnings =
    ignore::DeprecationWarning
```

---

## 🔹 Análise de Dados

### Ambiente e Dependências
- **Ambientes virtuais**: Sempre usar `venv`, `poetry`, ou `conda`
- **Fixar versões**: Todas as bibliotecas em `requirements.txt`
- **Bibliotecas essenciais**:
  - Manipulação: `pandas`, `polars` (para grandes volumes)
  - Numérico: `numpy`, `scipy`
  - Visualização: `matplotlib`, `seaborn`, `plotly`
  - Banco de dados: `sqlalchemy`, `duckdb`
  - Finanças: `yfinance`, `pandas-datareader`

### Boas Práticas Gerais
```python
import pandas as pd
import numpy as np

# ✅ Sempre manter cópia dos dados originais
df_raw = pd.read_csv('data.csv')
df = df_raw.copy()

# ✅ Normalizar nomes de colunas (snake_case)
df.columns = df.columns.str.lower().str.replace(' ', '_')

# ✅ Definir tipos de dados explicitamente
df = df.astype({
    'data': 'datetime64[ns]',
    'valor': 'float64',
    'ticker': 'string'
})

# ✅ Usar query() para filtros legíveis
df_filtered = df.query('valor > 1000 and ticker == "PETR4"')

# ❌ Evitar loops em pandas
# Ruim:
for idx, row in df.iterrows():
    df.at[idx, 'result'] = row['price'] * row['quantity']

# ✅ Bom: usar vetorização
df['result'] = df['price'] * df['quantity']

# ✅ Para operações complexas, usar apply
df['category'] = df['value'].apply(lambda x: 'high' if x > 1000 else 'low')

# ✅ Ou ainda melhor: np.where ou pd.cut
df['category'] = np.where(df['value'] > 1000, 'high', 'low')
```

### Séries Temporais Financeiras
```python
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ✅ Sempre definir índice temporal
df['data'] = pd.to_datetime(df['data'])
df.set_index('data', inplace=True)
df.sort_index(inplace=True)

# ✅ Reamostrar dados (diário → mensal)
df_monthly = df.resample('M').last()  # Último valor do mês
df_monthly_avg = df.resample('M').mean()  # Média mensal

# ✅ Tratar dados faltantes em séries financeiras
df.fillna(method='ffill', inplace=True)  # Forward fill (propaga último valor)
df.fillna(method='bfill', inplace=True)  # Backward fill

# ✅ Calcular retornos
# Retornos simples
df['return_simple'] = df['price'].pct_change()

# Retornos logarítmicos (mais precisos para análise)
df['return_log'] = np.log(df['price'] / df['price'].shift(1))

# ✅ Retornos acumulados
df['cumulative_return'] = (1 + df['return_simple']).cumprod() - 1

# ✅ Volatilidade móvel (janela de 30 dias)
df['volatility_30d'] = df['return_log'].rolling(window=30).std()

# ✅ Médias móveis
df['sma_50'] = df['price'].rolling(window=50).mean()  # Média simples
df['ema_50'] = df['price'].ewm(span=50).mean()  # Média exponencial
```

### Cálculos Financeiros Essenciais
```python
import numpy as np
import pandas as pd

def calculate_returns(prices: pd.Series) -> pd.Series:
    """Calcula retornos logarítmicos"""
    return np.log(prices / prices.shift(1))

def calculate_volatility(returns: pd.Series, annualize: bool = True) -> float:
    """Calcula volatilidade (anualizada para trading days)"""
    vol = returns.std()
    if annualize:
        vol = vol * np.sqrt(252)  # 252 dias úteis
    return vol

def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.0) -> float:
    """Calcula Sharpe Ratio"""
    excess_returns = returns - risk_free_rate / 252  # Diário
    if returns.std() == 0:
        return 0.0
    return (excess_returns.mean() / excess_returns.std()) * np.sqrt(252)

def calculate_max_drawdown(returns: pd.Series) -> float:
    """Calcula Maximum Drawdown"""
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.cummax()
    drawdown = (cumulative - running_max) / running_max
    return drawdown.min()

def calculate_cagr(prices: pd.Series) -> float:
    """Calcula CAGR (Compound Annual Growth Rate)"""
    n_years = len(prices) / 252  # Assumindo dados diários
    total_return = (prices.iloc[-1] / prices.iloc[0]) - 1
    return (1 + total_return) ** (1 / n_years) - 1

# ✅ Exemplo de uso
returns = calculate_returns(df['price'])
print(f"Volatilidade anualizada: {calculate_volatility(returns):.2%}")
print(f"Sharpe Ratio: {calculate_sharpe_ratio(returns):.2f}")
print(f"Max Drawdown: {calculate_max_drawdown(returns):.2%}")
print(f"CAGR: {calculate_cagr(df['price']):.2%}")
```

### Validação de Dados Financeiros
```python
import pandas as pd
import numpy as np

def validate_financial_data(df: pd.DataFrame) -> None:
    """Valida consistência de dados financeiros"""
    
    # Verificar valores nulos
    null_counts = df.isnull().sum()
    if null_counts.any():
        print(f"⚠️ Valores nulos encontrados:\n{null_counts[null_counts > 0]}")
    
    # Verificar preços negativos
    if 'price' in df.columns:
        negative_prices = (df['price'] < 0).sum()
        assert negative_prices == 0, f"❌ {negative_prices} preços negativos detectados"
    
    # Verificar ordem cronológica
    if df.index.name == 'data' or 'data' in df.columns:
        assert df.index.is_monotonic_increasing, "❌ Datas fora de ordem"
    
    # Verificar outliers extremos (mais de 50% de variação diária)
    if 'return_simple' in df.columns:
        extreme_returns = df[abs(df['return_simple']) > 0.5]
        if len(extreme_returns) > 0:
            print(f"⚠️ {len(extreme_returns)} retornos extremos (>50%) detectados")
    
    print("✅ Validação concluída")

# Exemplo de uso
validate_financial_data(df)
```

### Cache para Dados de Mercado
```python
import functools
from datetime import datetime, timedelta
import pickle
import os

def cache_to_disk(cache_dir: str = 'cache_temp', expiry_hours: int = 24):
    """Decorator para cachear resultados em disco"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Criar chave de cache
            cache_key = f"{func.__name__}_{str(args)}_{str(kwargs)}.pkl"
            cache_path = os.path.join(cache_dir, cache_key)
            
            # Verificar se cache existe e é válido
            if os.path.exists(cache_path):
                age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_path))
                if age < timedelta(hours=expiry_hours):
                    with open(cache_path, 'rb') as f:
                        return pickle.load(f)
            
            # Executar função e cachear resultado
            result = func(*args, **kwargs)
            os.makedirs(cache_dir, exist_ok=True)
            with open(cache_path, 'wb') as f:
                pickle.dump(result, f)
            
            return result
        return wrapper
    return decorator

# Uso
@cache_to_disk(cache_dir='data/cache', expiry_hours=24)
def get_stock_data(ticker: str, start_date: str):
    """Busca dados de ações com cache"""
    import yfinance as yf
    return yf.download(ticker, start=start_date, progress=False)
```

### Visualização de Dados Financeiros
```python
import matplotlib.pyplot as plt
import seaborn as sns

# ✅ Configurar estilo consistente
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def plot_price_and_volume(df: pd.DataFrame, ticker: str):
    """Gráfico de preço e volume"""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    # Preço
    ax1.plot(df.index, df['close'], label='Preço de Fechamento', linewidth=2)
    ax1.fill_between(df.index, df['low'], df['high'], alpha=0.3, label='Min-Max')
    ax1.set_ylabel('Preço (R$)', fontsize=12)
    ax1.set_title(f'{ticker} - Evolução de Preço e Volume', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Volume
    ax2.bar(df.index, df['volume'], alpha=0.7, color='steelblue')
    ax2.set_ylabel('Volume', fontsize=12)
    ax2.set_xlabel('Data', fontsize=12)
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'relatorios/graficos/{ticker}_price_volume.png', dpi=300, bbox_inches='tight')
    plt.show()

def plot_returns_distribution(returns: pd.Series):
    """Histograma de distribuição de retornos"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.hist(returns.dropna(), bins=50, alpha=0.7, edgecolor='black')
    ax.axvline(returns.mean(), color='red', linestyle='--', linewidth=2, label=f'Média: {returns.mean():.2%}')
    ax.axvline(0, color='black', linestyle='-', linewidth=1)
    
    ax.set_xlabel('Retorno', fontsize=12)
    ax.set_ylabel('Frequência', fontsize=12)
    ax.set_title('Distribuição de Retornos', fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
```

### Reprodutibilidade
```python
import numpy as np
import random

# ✅ Fixar seeds para resultados reproduzíveis
RANDOM_SEED = 42

np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)

# Para bibliotecas específicas
import tensorflow as tf
tf.random.set_seed(RANDOM_SEED)

# ✅ Scripts devem rodar do início ao fim
# Estrutura recomendada:
if __name__ == "__main__":
    # 1. Carregar dados
    df = load_data()
    
    # 2. Processar
    df_processed = process_data(df)
    
    # 3. Analisar
    results = analyze_data(df_processed)
    
    # 4. Visualizar
    plot_results(results)
    
    # 5. Salvar
    save_results(results, 'relatorios/analise.json')
```

### Segurança de Dados (LGPD)
```python
import hashlib
import re

def anonimizar_cpf(cpf: str) -> str:
    """Anonimiza CPF para LGPD"""
    return f"***.***.{cpf[-6:]}"

def hash_sensitive_data(data: str) -> str:
    """Cria hash irreversível de dados sensíveis"""
    return hashlib.sha256(data.encode()).hexdigest()

def remover_pii(df: pd.DataFrame) -> pd.DataFrame:
    """Remove informações pessoais identificáveis"""
    pii_columns = ['cpf', 'nome', 'email', 'telefone', 'endereco']
    df_clean = df.drop(columns=[col for col in pii_columns if col in df.columns])
    return df_clean

# ✅ Sempre anonimizar antes de exportar
df_export = remover_pii(df)
df_export.to_csv('dados_anonimizados.csv', index=False)
```

### Performance para Grandes Datasets
```python
# ✅ Para datasets grandes (> 1GB), usar Polars
import polars as pl

# Polars é mais rápido que Pandas para grandes volumes
df_polars = pl.read_csv('large_dataset.csv')
result = df_polars.filter(pl.col('value') > 1000).groupby('category').agg(pl.col('value').mean())

# ✅ Ou usar Dask para processamento paralelo
import dask.dataframe as dd

df_dask = dd.read_csv('large_dataset*.csv')
result = df_dask.groupby('category')['value'].mean().compute()

# ✅ Chunking para leitura de arquivos grandes
for chunk in pd.read_csv('large_file.csv', chunksize=10000):
    process_chunk(chunk)
```

---

## 🔹 Deploy / CI-CD

### Ambientes
- **Development**: Ambiente local com dados de teste
- **Staging/Homologação**: Dados simulados ou anonimizados
- **Production**: Dados reais, monitoramento ativo

### Pipeline Mínimo (CI/CD)
```
1. Lint (Verificar código)
2. Tests (Executar testes)
3. Build (Construir aplicação)
4. Security Scan (Verificar vulnerabilidades)
5. Deploy (Implantar)
```

### GitHub Actions - Exemplo Completo
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  lint:
    name: Lint & Code Quality
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install linting tools
        run: |
          pip install black flake8 isort mypy
      
      - name: Run Black
        run: black --check src/
      
      - name: Run Flake8
        run: flake8 src/ --max-line-length=100
      
      - name: Run isort
        run: isort --check-only src/
      
      - name: Run mypy
        run: mypy src/ --ignore-missing-imports

  test:
    name: Run Tests
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Cache dependencies
        uses: actions/cache@v3
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      
      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov-report=xml --cov-report=term
      
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
      
      - name: Check coverage threshold
        run: |
          pytest --cov=src --cov-fail-under=80

  security:
    name: Security Scan
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Bandit (security linter)
        run: |
          pip install bandit
          bandit -r src/ -f json -o bandit-report.json
      
      - name: Run Safety (dependency check)
        run: |
          pip install safety
          safety check --json

  deploy:
    name: Deploy to Production
    runs-on: ubuntu-latest
    needs: [lint, test, security]
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to server
        run: |
          echo "Deploying to production..."
          # Adicionar comandos de deploy aqui
```

### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.10

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ["--max-line-length=100", "--extend-ignore=E203,W503"]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
      - id: detect-private-key

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: ["-c", "pyproject.toml"]

# Instalar: pip install pre-commit
# Ativar: pre-commit install
# Executar manualmente: pre-commit run --all-files
```

### Docker (Containerização)
```dockerfile
# Dockerfile
FROM python:3.10-slim

# Definir diretório de trabalho
WORKDIR /app

# Variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar usuário não-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expor porta (se aplicável)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import sys; sys.exit(0)"

# Comando para executar a aplicação
CMD ["python", "run_dashboard.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    container_name: portfolio_analyzer
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - API_KEY=${API_KEY}
    volumes:
      - ./data:/app/data
      - ./relatorios:/app/relatorios
    restart: unless-stopped
    networks:
      - app-network

  # Exemplo: adicionar banco de dados
  # postgres:
  #   image: postgres:15
  #   environment:
  #     POSTGRES_DB: portfolio_db
  #     POSTGRES_USER: user
  #     POSTGRES_PASSWORD: ${DB_PASSWORD}
  #   volumes:
  #     - postgres_data:/var/lib/postgresql/data
  #   networks:
  #     - app-network

networks:
  app-network:
    driver: bridge

volumes:
  postgres_data:
```

### Configuração de Ambiente
```bash
# .env.example - Template para variáveis de ambiente
# Copiar para .env e preencher valores reais

# Ambiente
ENVIRONMENT=development  # development, staging, production

# APIs
BINANCE_API_KEY=your_key_here
BINANCE_API_SECRET=your_secret_here
YAHOO_FINANCE_KEY=your_key_here

# Banco de Dados (se aplicável)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Cache
CACHE_EXPIRY_HOURS=24
CACHE_DIR=data/cache

# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=app.log

# Segurança
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=localhost,127.0.0.1
```

```python
# config/settings.py - Carregar configurações
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Configurações da aplicação"""
    
    # Ambiente
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = ENVIRONMENT == "development"
    
    # APIs
    BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")
    BINANCE_API_SECRET = os.getenv("BINANCE_API_SECRET")
    
    # Cache
    CACHE_EXPIRY_HOURS = int(os.getenv("CACHE_EXPIRY_HOURS", "24"))
    CACHE_DIR = os.getenv("CACHE_DIR", "data/cache")
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "app.log")
    
    @classmethod
    def validate(cls):
        """Valida configurações obrigatórias"""
        required = ["BINANCE_API_KEY", "BINANCE_API_SECRET"]
        missing = [key for key in required if not getattr(cls, key)]
        if missing:
            raise EnvironmentError(f"Variáveis obrigatórias não definidas: {', '.join(missing)}")

# Uso
settings = Settings()
settings.validate()
```

### Monitoramento e Logs
```python
# Configuração de logging estruturado
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Formatter para logs em JSON"""
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)

# Configurar
handler = logging.FileHandler('logs/app.json')
handler.setFormatter(JSONFormatter())

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Uso
logger.info("Processando carteira", extra={"portfolio_id": "123", "value": 100000})
```

### Branch Strategy (GitFlow)
```
main (produção)
  ↓
  └── Merges apenas de release/ ou hotfix/
  
release/v1.1.0 (pré-produção)
  ↓
  └── Merges de develop quando features estão prontas
  
develop (homologação)
  ↓
  └── Merges de feature/, fix/, refactor/
  
feature/adicionar-fundos-imobiliarios (desenvolvimento)
feature/melhorar-cache
fix/corrigir-sharpe-ratio
refactor/reorganizar-apis
hotfix/bug-critico (emergência → direto para main)
```

### Checklist de Deploy
```markdown
## Pre-Deploy
- [ ] Todos os testes passando
- [ ] Cobertura de testes >= 80%
- [ ] Lint sem erros
- [ ] Documentação atualizada
- [ ] CHANGELOG.md atualizado
- [ ] Versão incrementada corretamente
- [ ] Variáveis de ambiente configuradas
- [ ] Backup dos dados de produção realizado

## Deploy
- [ ] Build da aplicação executado
- [ ] Testes de integração executados
- [ ] Deploy para staging executado
- [ ] Testes manuais em staging
- [ ] Deploy para produção executado
- [ ] Health checks passando

## Post-Deploy
- [ ] Monitoramento ativo
- [ ] Logs sendo coletados
- [ ] Performance dentro do esperado
- [ ] Funcionalidades principais testadas
- [ ] Rollback plan preparado
- [ ] Stakeholders notificados
```

---

## 📚 Recursos Adicionais

### Ferramentas Recomendadas
- **Lint**: `black`, `flake8`, `isort`, `mypy`
- **Testing**: `pytest`, `pytest-cov`, `pytest-mock`
- **Security**: `bandit`, `safety`, `pip-audit`
- **Docs**: `sphinx`, `mkdocs`
- **Performance**: `cProfile`, `memory_profiler`, `py-spy`

### Links Úteis
- [PEP 8 - Style Guide](https://peps.python.org/pep-0008/)
- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [pytest Documentation](https://docs.pytest.org/)
- [GitHub Actions](https://docs.github.com/actions)

---

## 📝 Notas Finais

Este guia deve ser tratado como um documento vivo, atualizado conforme novas práticas são adotadas e tecnologias evoluem.

**Última atualização:** 06/10/2025  
**Mantenedor:** Equipe de Desenvolvimento  
**Próxima revisão:** 06/01/2026

---
