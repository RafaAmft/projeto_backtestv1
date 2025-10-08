# 🚀 Guia Rápido - Versão 1.1.0

Bem-vindo à versão 1.1.0 do Sistema de Análise de Portfólios! Este guia vai ajudá-lo a aproveitar todas as novas funcionalidades.

---

## 📋 O que mudou da v1.0 para v1.1?

### ✅ **Completamente Configurado**
- Sistema de versionamento profissional
- Arquivos de configuração modernos
- Pre-commit hooks para qualidade
- Testes automatizados configurados

### 📚 **Documentação Completa**
- Guia de boas práticas (1.300+ linhas)
- CHANGELOG detalhado
- Template de variáveis de ambiente

---

## 🎯 Checklist de Migração

Se você já usa a v1.0, siga estes passos:

### 1. **Backup dos Dados**
```bash
# Faça backup antes de atualizar
cp -r data/ data_backup_$(date +%Y%m%d)/
cp -r relatorios/ relatorios_backup_$(date +%Y%m%d)/
```

### 2. **Atualizar Código**
```bash
git pull origin main
# Ou baixe a última versão do GitHub
```

### 3. **Atualizar Dependências**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. **Configurar Ambiente (Novo!)**
```bash
# Copiar template
cp env.example.txt .env

# Editar com suas credenciais
# Windows: notepad .env
# Linux/Mac: nano .env
```

### 5. **Instalar Pre-commit (Opcional)**
```bash
pip install pre-commit
pre-commit install

# Executar uma vez para validar
pre-commit run --all-files
```

### 6. **Executar Testes**
```bash
# Com pytest
pytest

# Ou testes individuais
python test_carteira_ideal.py
```

---

## 🔧 Novos Arquivos de Configuração

### **1. pytest.ini** - Configuração de Testes
```bash
# Executar todos os testes
pytest

# Apenas testes unitários
pytest -m unit

# Apenas testes rápidos (sem APIs externas)
pytest -m "not slow and not api"

# Com relatório de cobertura
pytest --cov=core --cov-report=html
```

### **2. pyproject.toml** - Metadados do Projeto
```bash
# Instalar em modo desenvolvimento
pip install -e .

# Instalar com dependências de dev
pip install -e ".[dev]"
```

### **3. .pre-commit-config.yaml** - Hooks de Qualidade
```bash
# Instalar hooks
pre-commit install

# Executar manualmente
pre-commit run --all-files

# Atualizar versões
pre-commit autoupdate
```

### **4. .env** - Variáveis de Ambiente
```bash
# Criar a partir do template
cp env.example.txt .env

# Editar com suas credenciais
BINANCE_API_KEY=sua_chave_aqui
BINANCE_API_SECRET=seu_segredo_aqui
EXCHANGE_RATE_API_KEY=sua_chave_aqui
```

---

## 📖 Como Usar os Novos Recursos

### **Versionamento no Código**

```python
# Importar versão
from __version__ import __version__, print_version

# Mostrar versão
print(f"Sistema versão: {__version__}")

# Informações completas
print_version()
```

### **Variáveis de Ambiente**

```python
import os
from dotenv import load_dotenv

# Carregar .env
load_dotenv()

# Usar variáveis
api_key = os.getenv("BINANCE_API_KEY")
cache_dir = os.getenv("CACHE_DIR", "data/cache")
log_level = os.getenv("LOG_LEVEL", "INFO")
```

### **Testes Organizados**

```python
# Criar novo teste seguindo as convenções
# tests/test_meu_modulo.py

import pytest
from core.market_indices_fixed import MarketIndicesManager

@pytest.fixture
def market_data():
    """Fixture reutilizável"""
    return MarketIndicesManager()

def test_get_exchange_rate(market_data):
    """Testa obtenção de taxa de câmbio"""
    rates = market_data.get_exchange_rate()
    assert "USD_BRL" in rates
    assert rates["USD_BRL"] > 0
```

---

## 🔒 Segurança Melhorada

### **Antes (v1.0)**
```python
# ❌ Chaves hardcoded no código
BINANCE_API_KEY = "abc123xyz"
```

### **Agora (v1.1)**
```python
# ✅ Usando variáveis de ambiente
import os
from dotenv import load_dotenv

load_dotenv()
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY")

if not BINANCE_API_KEY:
    raise EnvironmentError("BINANCE_API_KEY não configurada")
```

---

## 📊 Qualidade de Código

### **Formatação Automática**

```bash
# Black - formatador
black core/ apis/ dashboard/

# isort - organizar imports
isort core/ apis/ dashboard/

# Flake8 - linter
flake8 core/ apis/ dashboard/

# MyPy - type checking
mypy core/ apis/ dashboard/
```

### **Verificação de Segurança**

```bash
# Bandit - vulnerabilidades
bandit -r core/ apis/ dashboard/

# Safety - dependências vulneráveis
pip install safety
safety check

# Pip-audit (alternativa moderna)
pip install pip-audit
pip-audit
```

---

## 📈 Workflow de Desenvolvimento

### **Fluxo Recomendado**

```bash
# 1. Criar branch para feature
git checkout -b feature/nova-funcionalidade

# 2. Desenvolver
# ... editar código ...

# 3. Formatar código
black core/meu_modulo.py
isort core/meu_modulo.py

# 4. Executar testes
pytest tests/test_meu_modulo.py

# 5. Pre-commit valida tudo automaticamente
git add .
git commit -m "feat: adicionar nova funcionalidade"

# 6. Push
git push origin feature/nova-funcionalidade

# 7. Abrir Pull Request no GitHub
```

---

## 🎓 Recursos de Aprendizado

### **Documentação Incluída**

1. **[boaspraticas.md](boaspraticas.md)** (1.300+ linhas)
   - Git workflow e versionamento
   - Python: nomenclaturas, type hints, logging
   - Testes: pytest, fixtures, mocks
   - Análise de dados financeiros
   - Deploy e CI/CD

2. **[CHANGELOG.md](CHANGELOG.md)**
   - Histórico completo de versões
   - O que mudou em cada release
   - Como migrar entre versões

3. **[CONTRIBUTING.md](CONTRIBUTING.md)**
   - Como contribuir para o projeto
   - Padrões de código
   - Processo de revisão

---

## 🆘 Problemas Comuns

### **"ModuleNotFoundError"**
```bash
# Solução: Reinstalar dependências
pip install -r requirements.txt
```

### **"Permission denied" no .env**
```bash
# Solução: Verificar permissões
chmod 600 .env
```

### **Pre-commit muito lento**
```bash
# Solução: Executar apenas arquivos modificados
pre-commit run
# Ao invés de: pre-commit run --all-files
```

### **Testes falhando**
```bash
# Solução 1: Verificar dependências
pip install pytest pytest-cov pytest-mock

# Solução 2: Verificar variáveis de ambiente
cp env.example.txt .env

# Solução 3: Executar testes individualmente
pytest tests/test_market_indices.py -v
```

---

## 🚀 Próximos Passos

### **Para Usuários**
1. ✅ Explorar o dashboard atualizado
2. ✅ Configurar alertas personalizados
3. ✅ Gerar relatórios customizados

### **Para Desenvolvedores**
1. ✅ Adicionar type hints ao seu código
2. ✅ Aumentar cobertura de testes para 80%+
3. ✅ Contribuir com novas features

### **Planejado para v1.2.0**
- [ ] Docker e docker-compose
- [ ] CI/CD com GitHub Actions
- [ ] Análise técnica (RSI, MACD)
- [ ] Relatórios em PDF
- [ ] API REST

---

## 📞 Suporte

### **Encontrou um bug?**
[Abra uma issue no GitHub](https://github.com/RafaAmft/projeto_backtestv1/issues)

### **Tem uma sugestão?**
[Inicie uma discussão](https://github.com/RafaAmft/projeto_backtestv1/discussions)

### **Precisa de ajuda?**
- 📧 Email: [seu-email@example.com]
- 💬 Discord: [Link do servidor]
- 📱 Telegram: [Link do grupo]

---

## ⭐ Contribua!

Se você gostou da v1.1.0:

1. ⭐ Dê uma estrela no [GitHub](https://github.com/RafaAmft/projeto_backtestv1)
2. 🐛 Reporte bugs que encontrar
3. 💡 Sugira melhorias
4. 🤝 Contribua com código
5. 📢 Compartilhe com outros

---

**Obrigado por usar o Sistema de Análise de Portfólios!** 🎉

**Versão:** 1.1.0  
**Data:** 06/10/2025  
**Autor:** Rafael Augusto Masson Fontes


