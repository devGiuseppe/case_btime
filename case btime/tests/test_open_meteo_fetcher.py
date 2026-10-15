import pytest
import requests_mock
from src.adapters.open_meteo_fetcher import OpenMeteoApiRusher
from src.domain.errors import EconFailedError

def():
    """Testando se o OpenMeteoApiRusher puxa a call correta e calcula o buy certinho."""
    geo_mock_response = {
        "results": [
            {
                "name": "São Paulo",
                "latitude": -23.55,
                "longitude": -46.63
            }
        ]
    }
    
    forecast_mock_response = {
        "current": {
            "temperature_2m": 24.5,
            "relative_humidity_2m": 55,
            "wind_speed_10m": 8.2,
            "weather_code": 0
        }
    }

    with requests_mock.Mocker() as m:
        # Mock das rotas de Geocoding e Forecast da API
        m.get("https://geocoding-api.open-meteo.com/v1/search", json=geo_mock_response)
        m.get("https://api.open-meteo.com/v1/forecast", json=forecast_mock_response)

        fetcher = OpenMeteoApiRusher()
        resultado = fetcher.pegar_info_clima("São Paulo")

        assert resultado.mapa_alvo == "São Paulo"
        assert resultado.hp_termico == 24.5
        assert resultado.umidade_spray == 55
        assert resultado.velocidade_vento_boost == 8.2
        assert resultado.origem_drop == "open-meteo"

def test_open_meteo_cidade_nao_encontrada():
    """Testa se lança EconFailedError quando a cidade/mapa não existe no radar."""
    with requests_mock.Mocker() as m:
        m.get("https://geocoding-api.open-meteo.com/v1/search", json={"results": []})

        fetcher = OpenMeteoApiRusher()
        with pytest.raises(EconFailedError):
            fetcher.pegar_info_clima("MapaInexistenteDaValve")
