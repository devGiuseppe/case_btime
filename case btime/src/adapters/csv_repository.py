import csv
import os
from dataclasses import asdict
from src.domain.models import RoundInfo
from src.ports.weather_repository import InventoryStorageInterface

class CsvInventoryRepository(InventoryStorageInterface):
    """Salva os dados coletados direto no inventário (CSV local)."""

    def __init__(self, caminho_inventario: str = "output/weather_history.csv"):
        self.caminho_inventario = caminho_inventario
        self._garantir_lobby_pasta()

    def _garantir_lobby_pasta(self) -> None:
        os.makedirs(os.path.dirname(self.caminho_inventario), exist_ok=True)

    def salvar_no_inventario(self, round_info: RoundInfo) -> None:
        arquivo_ja_existe = os.path.isfile(self.caminho_inventario)
        dados_dict = asdict(round_info)

        # Se faltou dado, deixa vazio no CSV igual round econômico sem kit
        colunas_hud = list(dados_dict.keys())
        for k, v in dados_dict.items():
            if v is None:
                dados_dict[k] = ""

        with open(self.caminho_inventario, mode="a", newline="", encoding="utf-8") as f:
            escritor = csv.DictWriter(f, fieldnames=colunas_hud)
            if not arquivo_ja_existe:
                escritor.writeheader()
            escritor.writerow(dados_dict)
