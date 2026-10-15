import os
import csv
from src.adapters.csv_repository import CsvInventoryRepository
from src.domain.models import RoundInfo

def test_csv_inventario_save(tmp_path):
    caminho_teste = tmp_path / "inventario_cs.csv"
    repo = CsvInventoryRepository(caminho_inventario=str(caminho_teste))

    round_fake = RoundInfo(
        mapa_alvo="Mirage",
        hp_termico=22.5,
        umidade_spray=70,
        velocidade_vento_boost=5.0,
        bombsite_status="Nublado",
        timestamp_plant="2026-10-15T14:00:00-03:00",
        origem_drop="test-case"
    )

    repo.salvar_no_inventario(round_fake)

    assert os.path.isfile(caminho_teste)
    with open(caminho_teste, mode="r", encoding="utf-8") as f:
        leitor = list(csv.DictReader(f))
        assert len(leitor) == 1
        assert leitor[0]["mapa_alvo"] == "Mirage"
        assert leitor[0]["hp_termico"] == "22.5"
