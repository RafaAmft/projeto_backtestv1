# 📊 Sistema de Análise Financeira e Auditoria

Sistema completo para análise de portfólios, auditoria de fundos e monitoramento de mercado em tempo real.

## 🚀 Funcionalidades

- **APIs Integradas**: Binance, Yahoo Finance, CVM
- **Análise de Portfólios**: Criptomoedas, ações, fundos
- **Dados em Tempo Real**: Cotações, índices, câmbio
- **Relatórios Automatizados**: Performance, benchmarks, métricas
- **Cache Inteligente**: Otimização de requisições
- **Formato Brasileiro**: Datas e valores no padrão nacional

## 📦 Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/projeto-final.git
cd projeto-final

# Instale as dependências
pip install -r requirements.txt
```

## 🔧 Configuração

1. **Configure as APIs** (opcional):
   - Binance API (para dados avançados de criptomoedas)
   - Yahoo Finance (funciona sem chave)

2. **Execute o teste inicial**:
```bash
python examples/portfolio_analysis_example.py
```

## 📚 Uso Básico

```python
from core.market_indices import market_indices

# Buscar cotação do dólar
rates = market_indices.get_exchange_rate()
print(f"USD/BRL: R$ {rates['USD_BRL']:.4f}")

# Buscar preços de criptomoedas
crypto = market_indices.get_crypto_prices()
print(f"Bitcoin: R$ {crypto['BTCUSDT']['price_brl']:,.2f}")

# Análise completa de mercado
summary = market_indices.get_enhanced_market_summary()
```

## 🏗️ Estrutura do Projeto

```
├── core/                    # Núcleo do sistema
│   └── market_indices.py   # Gerenciador principal
├── apis/                   # Integrações com APIs
│   ├── binance_api.py     # API Binance
│   ├── yahoo_api.py       # API Yahoo Finance
│   └── cvm_api.py         # API CVM
├── examples/               # Exemplos de uso
├── tests/                  # Testes automatizados
└── docs/                   # Documentação
```

## 📊 Exemplos de Uso

### Análise de Portfólio
```bash
# Teste de rentabilidade
python BInance/test_cripto_portfolio.py

# Análise avançada
python test_enhanced_market_data.py
```

### Dados Históricos
```python
# Dados do dólar (30 dias)
usd_history = market_indices.get_historical_exchange_rate(30)

# Dados do Bitcoin
btc_history = market_indices.get_historical_crypto_data('BTC', 30)
```

## 🔍 Funcionalidades Avançadas

- **Benchmarks Automáticos**: Comparação com índices de mercado
- **Métricas de Risco**: Volatilidade, drawdown, Sharpe ratio
- **Indicadores de Mercado**: Índice medo/ganância, sentimento
- **Cache Inteligente**: 5 minutos de cache para otimização
- **Tratamento de Erros**: Fallback automático para APIs

## 📈 Relatórios Gerados

- `portfolio_analysis_*.json`: Análise de portfólios
- `market_data_*.json`: Dados de mercado
- `crypto_portfolio_report.json`: Relatório de criptomoedas

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
- GitHub: [@seu-usuario](https://github.com/seu-usuario)
- LinkedIn: [Seu Perfil](https://linkedin.com/in/seu-perfil)

## 🙏 Agradecimentos

- APIs: Binance, Yahoo Finance, CVM
- Bibliotecas: yfinance, pandas, requests
- Comunidade Python

---

⭐ **Se este projeto te ajudou, considere dar uma estrela!** 