import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List
from src.domain.models import RoundInfo
from src.domain.errors import BanidoDaMatchmakingError, EconFailedError, ErroNoHudParser
from src.ports.weather_fetcher import PlayerBuyInterface
from src.adapters.html_strategies import TáticaScraping, TáticaPistolRequests, TáticaFullBuySelenium
from src.adapters.climatempo_parser import parse_html_da_match

logger = logging.getLogger(__name__)

class ClimatempoScraperRusher(PlayerBuyInterface):
    """Adapter de Scraping escalonando táticas (Requests -> Selenium)."""

    MAPA_SLUGS = {
        "sao paulo": "558/saopaulo-sp",
        "rio de janeiro": "321/riodejaneiro-rj"
    }

    def __init__(self, tatica_arsenal: List[TáticaScraping] = None):
        self.tatica_arsenal = tatica_arsenal or [TáticaPistolRequests(), TáticaFullBuySelenium()]

    def pegar_info_clima(self, cidade_mapa: str) -> RoundInfo:
        cidade_key = cidade_mapa.lower().strip()
        slug_formatado = self.MAPA_SLUGS.get(cidade_key, f"558/{cidade_key.replace(' ', '')}-sp")
        url_climatempo = f"https://www.climatempo.com.br/previsao-do-tempo/agora/cidade/{slug_formatado}"

        ultimo_erro = None

        # Escada tática: tenta a leve, se der ruim, compra a pesada
        for tática in self.tatica_arsenal:
            nome_tática = tática.__class__.__name__
            logger.info(f"Tentando scout/tática {nome_tática} para o mapa {cidade_mapa}...")
            try:
                html_recebido = tática.catar_html(url_climatempo)
                dados_parsed = parse_html_da_match(html_recebido)

                timestamp_agora = datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat()
                return RoundInfo(
                    mapa_alvo=cidade_mapa,
                    hp_termico=dados_parsed["hp_termico"],
                    umidade_spray=dados_parsed["umidade_spray"],
                    velocidade_vento_boost=dados_parsed["velocidade_vento_boost"],
                    bombsite_status=dados_parsed["bombsite_status"],
                    timestamp_plant=timestamp_agora,
                    origem_drop="climatempo"
                )
            except (BanidoDaMatchmakingError, EconFailedError) as err:
                logger.warning(f"Tática {nome_tática} falhou: {str(err)}. Mudando de estratégia...")
                ultimo_erro = err
            except ErroNoHudParser as err:
                logger.error(f"Erro de parsing crítico na tática {nome_tática}: {str(err)}")
                raise

        raise BanidoDaMatchmakingError(f"Todas as táticas falharam para o mapa '{cidade_mapa}'. Último erro: {str(ultimo_erro)}")
