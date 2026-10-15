import pytest
from src.adapters.climatempo_parser import parse_html_da_match
from src.domain.errors import ErroNoHudParser

def test_parse_html_sucesso():
    html_mock = """
    <html>
        <div class="parameter-temperature"><span class="value">25°</span></div>
        <div class="parameter-humidity"><span class="value">60%</span></div>
        <div class="parameter-wind"><span class="value">12 km/h</span></div>
        <div class="parameter-condition"><span class="value">Sol na B</span></div>
    </html>
    """
    dados = parse_html_da_match(html_mock)
    assert dados["hp_termico"] == 25.0
    assert dados["umidade_spray"] == 60
    assert dados["velocidade_vento_boost"] == 12.0
    assert dados["bombsite_status"] == "Sol na B"

def test_parse_html_sem_temperatura_crash():
    html_mock = "<html><body>AFK na base</body></html>"
    with pytest.raises(ErroNoHudParser):
        parse_html_da_match(html_mock)
