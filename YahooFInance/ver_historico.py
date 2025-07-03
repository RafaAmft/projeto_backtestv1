from yfinance_api import YahooFinanceAPI
from datetime import datetime, timedelta

api = YahooFinanceAPI()

ticker = "AAPL"  # Você pode trocar para PETR4.SA, VALE3.SA etc.
inicio = datetime.now() - timedelta(days=30)

df = api.get_historico(ticker, start=inicio)

print(f"\nHistórico de {ticker} (últimos 30 dias):\n")
print(df.head(10))  # Mostra os 10 primeiros registros
