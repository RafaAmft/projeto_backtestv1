# 📊 Sistema de Análise de Portfólios

![Version](https://img.shields.io/badge/version-1.1.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![Status](https://img.shields.io/badge/status-production-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)
![Coverage](https://img.shields.io/badge/coverage-70%25-yellow.svg)

**Versão:** 1.1.0 | **Status:** 🟢 **PRONTO PARA PRODUÇÃO** | **Última Atualização:** 06/10/2025

Sistema completo e robusto para análise de portfólios, auditoria de fundos e monitoramento de mercado em tempo real. Integra múltiplas APIs, oferece análise avançada de dados financeiros e gera relatórios automatizados.

> 🆕 **Novidade v1.1.0:** Versionamento semântico, configuração profissional, pre-commit hooks, pytest configurado e guia completo de boas práticas!

## 🚀 Funcionalidades Principais

### 🔧 Core System
- **MarketIndicesManager** - Classe central robusta (1.123 linhas)
- **Cache Inteligente** - 5 minutos com invalidação automática
- **Tratamento de Erros** - Fallbacks automáticos para todas as APIs
- **Logging Detalhado** - Monitoramento completo de operações
- **Conversão Automática** - USD ↔ BRL em tempo real

### 📊 APIs Integradas
- **Binance API** - Criptomoedas em tempo real (8 símbolos)
- **Yahoo Finance** - Ações, índices, commodities (15+ símbolos)
- **Fundos CVM** - Dados processados localmente (CVM) + scraping Mais Retorno
- **Exchange Rate API** - Cotações de câmbio com fallback
- **IBGE API** - Dados econômicos brasileiros

### 📈 Análise Avançada
- **Análise de Portfólios** - Crypto, ações, fundos, renda fixa
- **Métricas de Risco** - Sharpe, Sortino, VaR, Max Drawdown, CAGR
- **Benchmarks** - Comparação com índices de mercado
- **Correlações** - Análise de correlação entre ativos
- **Evolução Temporal** - Análise de 1, 3, 5 anos
- **Carteira Ideal** - Modelo otimizado com 13 ativos

### 🎯 Funcionalidades Específicas
- **Dashboard Streamlit** - Interface web interativa
- **Auditoria de Fundos** - Validação automática via dados processados da CVM e scraping Mais Retorno
- **Relatórios Automatizados** - JSON estruturado e TXT formatado
- **Testes Automatizados** - 15+ testes de validação
- **Sistema de Cache** - Otimização de performance

## ✨ Novidades v1.1.0

### 🎯 Melhorias de Qualidade
- ✅ **Versionamento Semântico** - Sistema de versões profissional
- ✅ **Pre-commit Hooks** - Validação automática de código
- ✅ **Pytest Configurado** - Framework de testes robusto
- ✅ **Guia de Boas Práticas** - 1.300+ linhas de documentação
- ✅ **CHANGELOG.md** - Histórico completo de mudanças
- ✅ **pyproject.toml** - Configurações centralizadas

### 📚 Documentação
- 📄 Template de variáveis de ambiente (`.env.example`)
- 📋 Configuração de testes (`pytest.ini`)
- 🔧 Hooks de qualidade (`.pre-commit-config.yaml`)
- 📖 Guia completo de boas práticas (`boaspraticas.md`)

### 🔒 Segurança
- 🛡️ Bandit e Safety configurados
- 🔐 Sistema de variáveis de ambiente
- ✅ Validação de configurações obrigatórias

[Ver changelog completo](CHANGELOG.md)

---

## 📦 Instalação

```bash
# 1. Clone o repositório
git clone https://github.com/RafaAmft/projeto_backtestv1.git
cd ProjetoFinal

# 2. Crie e ative ambiente virtual (recomendado)
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate

# 3. Atualize pip
pip install --upgrade pip

# 4. Instale as dependências
pip install -r requirements.txt

# 5. Configure variáveis de ambiente (opcional)
cp env.example.txt .env
# Edite .env com suas credenciais

# 6. Execute o teste inicial
python test_carteira_ideal.py

# 7. (Opcional) Instale hooks de desenvolvimento
pip install pre-commit
pre-commit install
```

## 🔧 Configuração

1. **Configure as APIs** (opcional):
   - Binance API (para dados avançados de criptomoedas)
   - Yahoo Finance (funciona sem chave)

2. **Execute o dashboard**:
```bash
python run_dashboard.py
```

## 📚 Uso Básico

### Análise de Mercado
```python
from core.market_indices_fixed import MarketIndicesManager

# Inicializar gerenciador
market_data = MarketIndicesManager()

# Buscar cotação do dólar
rates = market_data.get_exchange_rate()
print(f"USD/BRL: R$ {rates['USD_BRL']:.4f}")

# Buscar preços de criptomoedas
crypto = market_data.get_crypto_prices()
print(f"Bitcoin: R$ {crypto['BTCUSDT']['price_brl']:,.2f}")

# Análise completa de mercado
summary = market_data.get_enhanced_market_summary()
```

### Análise de Portfólio
```python
from examples.portfolio_analysis_example import PortfolioAnalyzer

# Criar analisador
analyzer = PortfolioAnalyzer()

# Analisar carteira ideal
resultado = analyzer.analisar_carteira_ideal()
print(f"Retorno Esperado: {resultado['metricas_risco']['retorno_esperado']:.2%}")
```

### Dashboard Interativo
```bash
# Executar dashboard Streamlit
streamlit run dashboard/portfolio_collector.py
```

## 🏗️ Estrutura do Projeto

```
📁 ProjetoFinal/
├── 🧠 core/                    # ✅ Núcleo do sistema
│   ├── market_indices.py      # Gerenciador principal
│   └── market_indices_fixed.py # Versão otimizada
├── 🔌 apis/                   # ✅ Integrações com APIs
│   ├── binance_api.py        # API Binance
│   ├── yahoo_api.py          # API Yahoo Finance
│   └── cvm_api.py            # Processamento de dados de fundos (CVM local + scraping)
├── 📊 dashboard/              # ✅ Painel interativo
│   ├── portfolio_collector.py # Coletor principal
│   ├── fund_cache_manager.py # Gerenciador de cache
│   └── portfolio_collector_auto.py # Coletor automático
├── 🏦 CNPJ VALIDADO/         # ✅ Auditoria de fundos CVM
│   ├── app.py                # Dashboard Streamlit
│   └── transformados/        # Dados processados
├── 📈 BInance/               # ✅ Análise de criptomoedas
│   ├── binance.py            # Cliente Binance
│   └── test_cripto_portfolio.py # Testes
├── 📊 YahooFInance/          # ✅ Dados de ações
│   └── yfinance_api.py       # Cliente Yahoo Finance
├── 📚 examples/              # ✅ Exemplos de uso
│   ├── portfolio_analysis_example.py # Análise completa
│   └── temporal_portfolio_analysis.py # Análise temporal
├── ⚙️ config/                # ✅ Configuração centralizada
│   └── config.yaml           # Configurações YAML
├── 📄 docs/                  # ✅ Documentação
├── 🧪 test_*.py              # ✅ Testes automatizados
├── 📊 relatorios/            # ✅ Relatórios organizados
├── 📊 cache/                 # ✅ Cache temporário
└── 📊 dados_debug/           # ✅ Dados de debug
```

## 📊 Exemplos de Uso

### Teste da Carteira Ideal
```bash
# Executar análise completa da carteira ideal
python test_carteira_ideal.py

# Gerar relatório TXT
python gerar_relatorio_txt.py
```

### Análise de Criptomoedas
```bash
# Teste de portfólio de criptomoedas
python BInance/test_cripto_portfolio.py

# Análise avançada de mercado
python test_enhanced_market_data.py
```

### Dashboard de Coleta
```bash
# Executar dashboard de coleta de dados
streamlit run dashboard/portfolio_collector.py
```

### Dados Históricos
```python
# Dados do dólar (30 dias)
usd_history = market_data.get_historical_exchange_rate(30)

# Dados do Bitcoin
btc_history = market_data.get_historical_crypto_data('BTC', 30)

# Análise temporal de portfólio
from examples.temporal_portfolio_analysis import TemporalPortfolioAnalyzer
temporal = TemporalPortfolioAnalyzer()
resultado = temporal.analisar_evolucao_temporal()
```

## 📈 Relatórios Gerados

### Relatórios JSON
- `relatorio_carteira_ideal_*.json` - Análise da carteira ideal
- `portfolio_analysis_*.json` - Análise de portfólios
- `market_data_*.json` - Dados de mercado
- `crypto_portfolio_report.json` - Relatório de criptomoedas

### Relatórios TXT
- `relatorio_carteira_ideal_*.txt` - Relatório formatado da carteira ideal
- `relatorio_portfolio_*.txt` - Relatórios de portfólios

## 🎯 Carteira Ideal

O sistema inclui uma **carteira ideal** com 13 ativos distribuídos em 4 classes:

- **💰 Renda Fixa (40%)**: CDB 95% CDI, LCI 90% CDI
- **📈 Ações (30%)**: PETR4, VALE3, BBAS3
- **🪙 Criptomoedas (15%)**: BTC, ETH, USDT, BNB
- **🏦 Fundos Cambiais (15%)**: 5 fundos especializados

**Métricas da Carteira Ideal:**
- Sharpe Ratio: 0.53
- CAGR: 6.71%
- Volatilidade: 11.80%
- Valor Total: R$ 300.000,00

## 🔍 Funcionalidades Avançadas

- **Benchmarks Automáticos**: Comparação com índices de mercado
- **Métricas de Risco**: Volatilidade, drawdown, Sharpe ratio, Sortino
- **Indicadores de Mercado**: Índice medo/ganância, sentimento
- **Cache Inteligente**: 5 minutos de cache para otimização
- **Tratamento de Erros**: Fallback automático para APIs
- **Auditoria de Fundos**: Validação automática via dados processados da CVM e scraping Mais Retorno

## 🧪 Testes

O projeto inclui 15+ testes automatizados:

```bash
# Executar todos os testes
python scripts/run_tests.py

# Testes específicos
python test_carteira_ideal.py
python test_enhanced_market_data.py
python test_fund_integration.py
python test_market_indices_fixed.py
```

## 📊 Métricas de Sucesso

| Métrica | Valor | Status |
|---------|-------|--------|
| APIs Integradas | 6 | ✅ |
| Linhas de Código | 1.123 | ✅ |
| Testes Automatizados | 15+ | ✅ |
| Relatórios Gerados | 20+ | ✅ |
| Tempo de Resposta | < 5s | ✅ |
| Taxa de Erro | < 5% | ✅ |

## 🚀 Próximas Funcionalidades

### 📅 Fase 1: Otimizações (Julho 2025)
- [ ] Refatoração do Core em módulos menores
- [ ] Testes unitários com 90%+ de cobertura
- [ ] Type hints completos
- [ ] Documentação melhorada

### 📅 Fase 2: Expansão (Agosto 2025)
- [ ] Análise técnica (RSI, MACD, indicadores)
- [ ] Renda fixa (Tesouro Direto, CDB)
- [ ] Relatórios avançados (PDF, Excel)

### 📅 Fase 3: IA (Setembro 2025)
- [ ] Machine Learning para previsões
- [ ] Web App completo
- [ ] API REST

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 👨‍💻 Autor

**Seu Nome**
- GitHub: [@RafaAmft](https://github.com/RafaAmft/projeto_backtestv1)
- LinkedIn: [[Meu Perfil](https://www.linkedin.com/in/rafael-augusto-masson-fontes-94228a27a/)]

## 🙏 Agradecimentos

- APIs: Binance, Yahoo Finance, CVM, Exchange Rate, IBGE
- Bibliotecas: yfinance, pandas, requests, streamlit, selenium
- Comunidade Python

## 📚 Documentação Adicional

- [📋 RESUMO_EXECUTIVO.md](RESUMO_EXECUTIVO.md) - Status detalhado do projeto
- [🗺️ ROADMAP.md](ROADMAP.md) - Planejamento de funcionalidades
- [📄 CHECKPOINT_PROJETO.md](CHECKPOINT_PROJETO.md) - Checkpoints do desenvolvimento

---

⭐ **Se este projeto te ajudou, considere dar uma estrela!**

🟢 **Status:** Pronto para produção - Sistema completo e funcional! 
