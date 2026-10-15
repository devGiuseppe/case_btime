import argparse
import logging
import sys
import os

# Adiciona a raiz do projeto ao PYTHONPATH dinamicamente
LOBBY_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if LOBBY_ROOT not in sys.path:
    sys.path.insert(0, LOBBY_ROOT)

from src.adapters.open_meteo_fetcher import OpenMeteoApiRusher
from src.adapters.csv_repository import CsvInventoryRepository
from src.application.collect_weather import ExecutarMatchCasoDeUso
from src.domain.errors import CSBaseError

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def main():
    parser = argparse.ArgumentParser(description="Coleta de clima via API Open-Meteo (Estilo CS)")
    parser.add_argument("--city", type=str, default="São Paulo", help="Nome do mapa/cidade")
    args = parser.parse_args()

    try:
        fetcher = OpenMeteoApiRusher()
        repo = CsvInventoryRepository()
        use_case = ExecutarMatchCasoDeUso(fetcher_provedor=fetcher, repository_inventario=repo)

        resultado = use_case.executar_match(args.city)
        print(f"🔥 ACE! (API): {resultado.mapa_alvo} -> {resultado.hp_termico}°C, {resultado.bombsite_status}")
    except CSBaseError as err:
        logging.error(f"❌ Round perdido por erro de domínio (API): {str(err)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
