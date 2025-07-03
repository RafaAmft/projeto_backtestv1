# MarketIndicesManager - Classe Centralizada de Dados de Mercado

## 📋 Visão Geral

A classe `MarketIndicesManager` é uma solução centralizada para buscar e gerenciar informações de mercado em tempo real, incluindo criptomoedas, ações, commodities e câmbio. Ela oferece cache inteligente, tratamento de erros robusto e uma interface simples para uso em outros scripts do projeto.

## 🚀 Características Principais

- **Cache Inteligente**: Dados são cacheados por 5 minutos para evitar requisições excessivas
- **Múltiplas Fontes**: Integra Binance API, Yahoo Finance e APIs de câmbio
- **Tratamento de Erros**: Fallbacks automáticos quando APIs falham
- **Conversão Automática**: Valores em USD são automaticamente convertidos para BRL
- **Logging Detalhado**: Logs informativos para debugging e monitoramento

## 📦 Instalação e Uso

### Importação Básica

```python
from core.market_indices import market_indices

# Usar a instância global
exchange_rate = market_indices.get_exchange_rate()
```

### Importação da Classe

```python
from core.market_indices import MarketIndicesManager

# Criar instância própria
my_indices = MarketIndicesManager()
```

## 🔧 Métodos Principais

### 1. Câmbio

```python
# Buscar cotação do dólar e outras moedas
exchange_rates = market_indices.get_exchange_rate()
print(f"USD/BRL: R$ {exchange_rates['USD_BRL']:.4f}")
print(f"EUR/BRL: R$ {exchange_rates['EUR_BRL']:.4f}")
print(f"GBP/BRL: R$ {exchange_rates['GBP_BRL']:.4f}")
```

### 2. Criptomoedas

```python
# Buscar preços de criptomoedas específicas
crypto_data = market_indices.get_crypto_prices(['BTCUSDT', 'ETHUSDT'])

# Ou buscar todas as principais
crypto_data = market_indices.get_crypto_prices()

for symbol, data in crypto_data.items():
    print(f"{symbol}:")
    print(f"  Preço USD: ${data['price']:,.2f}")
    print(f"  Preço BRL: R$ {data['price_brl']:,.2f}")
    print(f"  Variação 24h: {data['change_24h']:+.2f}%")
```

### 3. Índices de Ações

```python
# Buscar dados de índices e ações
stock_data = market_indices.get_stock_indices(['^BVSP', '^GSPC', 'PETR4.SA'])

for symbol, data in stock_data.items():
    print(f"{symbol} ({data.get('name', 'N/A')}):")
    print(f"  Preço: {data['price']:,.2f}")
    print(f"  Variação 24h: {data['change_24h']:+.2f}%")
```

### 4. Commodities

```python
# Buscar preços de commodities
commodity_data = market_indices.get_commodity_prices(['GC=F', 'SI=F'])  # Ouro e Prata

for symbol, data in commodity_data.items():
    print(f"{symbol}: R$ {data['price_brl']:,.2f} ({data['change_24h']:+.2f}%)")
```

### 5. Todos os Dados

```python
# Buscar todos os dados de uma vez
all_data = market_indices.get_all_market_data()

print(f"Câmbio: {all_data['exchange_rates']['USD_BRL']}")
print(f"Criptos: {len(all_data['crypto'])} ativos")
print(f"Ações: {len(all_data['stocks'])} ativos")
print(f"Commodities: {len(all_data['commodities'])} ativos")
```

### 6. Utilitários

```python
# Converter USD para BRL
usd_amount = 1000
brl_amount = market_indices.convert_to_brl(usd_amount)
print(f"${usd_amount} = R$ {brl_amount:,.2f}")

# Calcular valor total de portfólio em BRL
portfolio = {
    'BTCUSDT': {'value_usd': 5000},
    'PETR4.SA': {'value_brl': 10000}
}
total_brl = market_indices.get_portfolio_value_brl(portfolio)
print(f"Portfólio total: R$ {total_brl:,.2f}")

# Salvar dados em arquivo
filename = market_indices.save_market_data()
print(f"Dados salvos em: {filename}")

# Obter resumo de mercado
summary = market_indices.get_market_summary()
print(f"Bitcoin: R$ {summary['bitcoin_price_brl']:,.2f}")
print(f"Ibovespa: {summary['ibovespa_price']:,.2f}")
```

## 📊 Estrutura dos Dados

### Câmbio
```python
{
    'USD_BRL': 5.47,
    'EUR_BRL': 6.45,
    'GBP_BRL': 7.46,
    'timestamp': '2025-07-02T23:18:43.170302'
}
```

### Criptomoedas
```python
{
    'BTCUSDT': {
        'price': 108800.03,
        'price_brl': 595136.16,
        'change_24h': 3.05,
        'volume_24h': 1234567.89,
        'high_24h': 109000.00,
        'low_24h': 107000.00,
        'timestamp': '2025-07-02T23:18:43.170302'
    }
}
```

### Ações/Índices
```python
{
    '^BVSP': {
        'price': 139051.00,
        'price_brl': 139051.00,
        'change_24h': -0.36,
        'volume': 8811900,
        'high_24h': 140000.00,
        'low_24h': 138000.00,
        'name': 'IBOVESPA',
        'timestamp': '2025-07-02T23:18:43.170302'
    }
}
```

## 🔄 Cache e Performance

### Controle de Cache
```python
# Forçar atualização (ignorar cache)
fresh_data = market_indices.get_crypto_prices(force_update=True)

# Verificar se cache é válido
if not market_indices._is_cache_valid("crypto_prices"):
    print("Cache expirado, atualizando...")
```

### Configuração de Cache
```python
# Alterar duração do cache (em segundos)
market_indices.cache_duration = 600  # 10 minutos
```

## 🛠️ Integração com Outros Scripts

### Exemplo: Atualizar Portfólio

```python
from core.market_indices import market_indices

class PortfolioManager:
    def __init__(self):
        self.portfolio = {
            'BTC': {'quantity': 0.5, 'entry_price': 45000},
            'ETH': {'quantity': 2.0, 'entry_price': 2800}
        }
    
    def update_portfolio_values(self):
        # Buscar preços atuais
        crypto_data = market_indices.get_crypto_prices(['BTCUSDT', 'ETHUSDT'])
        
        for symbol, data in self.portfolio.items():
            symbol_usdt = f"{symbol}USDT"
            if symbol_usdt in crypto_data:
                current_price = crypto_data[symbol_usdt]['price']
                current_value = data['quantity'] * current_price
                data['current_value'] = current_value
                data['current_value_brl'] = market_indices.convert_to_brl(current_value)
```

### Exemplo: Análise de Performance

```python
def analyze_performance(portfolio_data):
    # Buscar dados de mercado
    market_summary = market_indices.get_market_summary()
    
    # Comparar com benchmarks
    ibov_change = market_summary['ibovespa_change_24h']
    btc_change = market_summary['bitcoin_change_24h']
    
    # Calcular performance relativa
    for asset, data in portfolio_data.items():
        if asset in ['BTC', 'ETH']:
            # Comparar com Bitcoin
            relative_performance = data['change_24h'] - btc_change
        else:
            # Comparar com Ibovespa
            relative_performance = data['change_24h'] - ibov_change
        
        data['relative_performance'] = relative_performance
```

## 🚨 Tratamento de Erros

A classe inclui tratamento robusto de erros:

```python
try:
    crypto_data = market_indices.get_crypto_prices()
except Exception as e:
    print(f"Erro ao buscar dados: {e}")
    # Usar dados cacheados ou valores padrão
    crypto_data = market_indices.cache.get('crypto_prices', {})
```

## 📈 Logs e Monitoramento

A classe usa logging para monitoramento:

```python
import logging

# Configurar nível de log
logging.basicConfig(level=logging.INFO)

# Os logs incluem:
# - Inicialização da classe
# - Atualizações de dados
# - Erros de API
# - Salvamento de arquivos
```

## 🔧 Configuração Avançada

### Símbolos Personalizados
```python
# Adicionar símbolos personalizados
market_indices.important_symbols['crypto'].extend(['DOGEUSDT', 'LTCUSDT'])
market_indices.important_symbols['stocks'].extend(['AAPL', 'GOOGL'])
```

### APIs Personalizadas
```python
# Configurar APIs alternativas
market_indices.exchange_rate_api = "https://sua-api-de-cambio.com"
market_indices.binance_base_url = "https://api.binance.com/api/v3"
```

## 📝 Exemplos Práticos

### 1. Dashboard de Mercado
```python
def create_market_dashboard():
    summary = market_indices.get_market_summary()
    
    print("=== DASHBOARD DE MERCADO ===")
    print(f"💰 Dólar: R$ {summary['exchange_rate_usd_brl']:.4f}")
    print(f"🪙 Bitcoin: R$ {summary['bitcoin_price_brl']:,.2f}")
    print(f"📈 Ibovespa: {summary['ibovespa_price']:,.2f}")
    print(f"📊 S&P 500: {summary['sp500_price']:,.2f}")
    print(f"🥇 Ouro: R$ {summary['gold_price_brl']:,.2f}")
```

### 2. Alertas de Preço
```python
def check_price_alerts():
    crypto_data = market_indices.get_crypto_prices(['BTCUSDT'])
    btc_price = crypto_data['BTCUSDT']['price']
    
    if btc_price > 110000:
        print("🚨 Bitcoin acima de $110k!")
    elif btc_price < 100000:
        print("📉 Bitcoin abaixo de $100k!")
```

### 3. Relatório Diário
```python
def generate_daily_report():
    all_data = market_indices.get_all_market_data()
    
    report = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'exchange_rate': all_data['exchange_rates']['USD_BRL'],
        'top_crypto': max(all_data['crypto'].items(), 
                         key=lambda x: x[1]['change_24h']),
        'top_stock': max(all_data['stocks'].items(), 
                        key=lambda x: x[1]['change_24h'])
    }
    
    return report
```

## 🤝 Contribuição

Para contribuir com melhorias na classe:

1. Mantenha a compatibilidade com a interface existente
2. Adicione logs informativos para novos métodos
3. Inclua tratamento de erros robusto
4. Atualize esta documentação
5. Teste com diferentes cenários de erro

## 📞 Suporte

Para dúvidas ou problemas:

1. Verifique os logs para identificar erros
2. Teste com `force_update=True` para ignorar cache
3. Verifique conectividade com as APIs
4. Consulte os exemplos na pasta `examples/`

---

**Última atualização**: 2025-07-02
**Versão**: 1.0.0 