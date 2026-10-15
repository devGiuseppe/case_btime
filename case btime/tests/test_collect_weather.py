from src.application.collect_weather import ExecutarMatchCasoDeUso
from src.domain.models import RoundInfo

class MockFetcherBot:
    def pegar_info_clima(self, cidade_mapa: str) -> RoundInfo:
        return RoundInfo(
            mapa_alvo=cidade_mapa,
            hp_termico=20.0,
            umidade_spray=50,
            velocidade_vento_boost=10.0,
            bombsite_status="Limpo",
            timestamp_plant="2026-10-15T10:00:00-03:00",
            origem_drop="mock-bot"
        )

class MockRepositoryInventario:
    def __init__(self):
        self.salvos = []
    def salvar_no_inventario(self, round_info: RoundInfo) -> None:
        self.salvos.append(round_info)

def test_caso_de_uso_executar_match():
    fetcher = MockFetcherBot()
    repo = MockRepositoryInventario()
    use_case = ExecutarMatchCasoDeUso(fetcher, repo)

    resultado = use_case.executar_match("Inferno")

    assert resultado.mapa_alvo == "Inferno"
    assert len(repo.salvos) == 1
    assert repo.salvos[0].origem_drop == "mock-bot"
