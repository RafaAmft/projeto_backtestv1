from binance import BinanceMercadoAPI

api = BinanceMercadoAPI()

# Teste 1: preço atual
print("Preço atual do BTCUSDT:")
print(api.get_preco("BTCUSDT"))

# Teste 2: top 5 volumes
print("\nTop 5 volumes de negociação:")
for ativo in api.top_volume(limit=5):
    print(f"{ativo['symbol']}: {ativo['quoteVolume']}")

# Teste 3: histórico de candles
print("\nHistórico de preços do BTC (último ano):")
df = api.get_historical_data("BTCUSDT")
print(df.head())
