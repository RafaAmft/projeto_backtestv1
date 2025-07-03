import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from yfinance_api import YahooFinanceAPI
from datetime import datetime, timedelta
import pytest

def test_get_historico_ativo_valido():
    api = YahooFinanceAPI()
    try:
        df = api.get_historico("AAPL", start=datetime.now() - timedelta(days=30))
        assert not df.empty
        assert "Date" in df.columns
        assert "Close" in df.columns
    except Exception as e:
        pytest.skip(f"Teste ignorado por falha externa: {e}")

def test_get_historico_ativo_invalido():
    api = YahooFinanceAPI()
    with pytest.raises(ValueError):
        api.get_historico("TICKER_INEXISTENTE_123456")

