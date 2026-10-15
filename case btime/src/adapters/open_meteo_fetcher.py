import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from src.domain.models import RoundInfo
from src.domain.errors import EconFailedError, ErroNoHudParser
from src.ports.weather_fetcher import PlayerBuyInterface

# Mapeamento dos códigos WMO da API para a linguagem da banirade
WMO_MAPA_VOX = {
    0: "Auskip Limpo (Solzão)",
    1: "Quase sem nuvens", 2: "Nublado leve na B", 3: "Overpass Fechado",
    45: "Fog na Alamedas (Mirage)", 48: "Nevoeiro com geada na A",
    51: "Garoa depistada", 53: "Chuvinha chata no fundo", 55: "Temporal pesado",
    61: "Chuva fraca deeco", 63: "Chuva moderada", 65: "Chuva pesada de rush",
    80: "Pancada rápida", 81: "Chove forte na base", 82: "Temporal do caótico",
    95: "Raio e Trovão (Alerta de Zeus)", 96: "Granizo leve", 99: "Granizo forte (Fudeu)"
}

class OpenMeteoApiRusher(PlayerBuyInterface):
    """Busca os dados direto na API da Open-Meteo como um rush bem sucedido na B."""

    URL_GEOLOC = "https://geocoding-api.open-meteo.com/v1/search"
    URL_PREVISAO = "https://api.open-meteo.com/v1/forecast"

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=4),
        retry=retry_if_exception_type(EconFailedError),
        reraise=True
    )
    def pegar_info_clima(self, cidade_mapa: str) -> RoundInfo:
        try:
            # 1. Achando o bomb/cidade pelo Geocoding
            resp_geo = requests.get(
                self.URL_GEOLOC,
                params={"name": cidade_mapa, "count": 1, "language": "pt"},
                timeout=5.0
            )
            resp_geo.raise_for_status()
            payload_geo = resp_geo.json()

            if not payload_geo.get("results"):
                raise EconFailedError(f"Mapa/Cidade '{cidade_mapa}' não achada no radar da Open-Meteo.")

            alvo = payload_geo["results"][0]
            lat, lon = alvo["latitude"], alvo["longitude"]
            nome_oficial = alvo.get("name", cidade_mapa)

            # 2. Puxando o clima atual (Buy round executado)
            params_hud = {
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
                "timezone": "America/Sao_Paulo"
            }
            resp_clima = requests.get(self.URL_PREVISAO, params=params_hud, timeout=5.0)
            resp_clima.raise_for_status()
            payload_clima = resp_clima.json()

            hud_atual = payload_clima.get("current")
            if not hud_atual:
                raise ErroNoHudParser("A API respondeu mas o HUD 'current' veio vazio, bugou o scoreboard.")

            wmo_code = hud_atual.get("weather_code")
            condicao_str = WMO_MAPA_VOX.get(wmo_code, "Clima misterioso na smoke")
            agora_iso = datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat()

            return RoundInfo(
                mapa_alvo=nome_oficial,
                hp_termico=float(hud_atual.get("temperature_2m")),
                umidade_spray=int(hud_atual.get("relative_humidity_2m")),
                velocidade_vento_boost=float(hud_atual.get("wind_speed_10m")),
                bombsite_status=condicao_str,
                timestamp_plant=agora_iso,
                origem_drop="open-meteo"
            )

        except requests.RequestException as err:
            raise EconFailedError(f"Queda de conexão com o servidor da Valve (Open-Meteo): {str(err)}") from err
        except (ValueError, KeyError, TypeError) as err:
            raise ErroNoHudParser(f"Erro ao parsear o JSON da API: {str(err)}") from err
