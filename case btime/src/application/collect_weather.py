import logging
from src.ports.weather_fetcher import PlayerBuyInterface
from src.ports.weather_repository import InventoryStorageInterface
from src.domain.models import RoundInfo

logger = logging.getLogger(__name__)

class ExecutarMatchCasoDeUso:
    """O caso de uso central: puxa o dado do clima e joga direto no inventário CSV."""

    def __init__(self, fetcher_provedor: PlayerBuyInterface, repository_inventario: InventoryStorageInterface):
        self.fetcher_provedor = fetcher_provedor
        self.repository_inventario = repository_inventario

    def executar_match(self, cidade_mapa: str) -> RoundInfo:
        logger.info(f"Iniciando buy round de clima para o mapa/cidade: {cidade_mapa}")
        round_info = self.fetcher_provedor.pegar_info_clima(cidade_mapa)
        self.repository_inventario.salvar_no_inventario(round_info)
        logger.info(f"Drop efetuado com sucesso e salvo no inventário via [{round_info.origem_drop}].")
        return round_info
