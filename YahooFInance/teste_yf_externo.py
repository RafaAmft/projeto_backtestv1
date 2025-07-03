import yfinance as yf

ticker = "AAPL"

try:
    df = yf.download(ticker, period="7d", interval="1d", progress=False)
    if df.empty:
        print(f"[ERRO] Nenhum dado retornado para {ticker}.")
    else:
        print(f"[SUCESSO] Dados recebidos para {ticker}:")
        print(df[['Open', 'Close']].head())
except Exception as e:
    print(f"[EXCEÇÃO] Falha ao buscar dados de {ticker}: {e}")
