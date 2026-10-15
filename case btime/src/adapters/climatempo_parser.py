import re
from typing import Optional
from bs4 import BeautifulSoup
from src.domain.errors import ErroNoHudParser

# Seis seletores cravados igual mira de AWP na pixel
SELETOR_HP_TEMP = ".parameter-temperature .value"
SELETOR_UMIDADE = ".parameter-humidity .value"
SELETOR_VENTO = ".parameter-wind .value"
SELETOR_CONDICAO = ".parameter-condition .value"

def parse_html_da_match(html_bruto: str) -> dict:
    """Função pura para extrair as infos do HTML do Climatempo."""
    if not html_bruto or not html_bruto.strip():
        raise ErroNoHudParser("O HTML veio vazio, parece disconectou do servidor.")

    soup = BeautifulSoup(html_bruto, "html.parser")

    tag_temp = soup.select_one(SELETOR_HP_TEMP)
    tag_hum = soup.select_one(SELETOR_UMIDADE)
    tag_vento = soup.select_one(SELETOR_VENTO)
    tag_cond = soup.select_one(SELETOR_CONDICAO)

    if not tag_temp:
        raise ErroNoHudParser("Não achei a tag da temperatura no HTML. O layout mudou na atualização de patch.")

    return {
        "hp_termico": _tratar_float(tag_temp.text, -30.0, 60.0),
        "umidade_spray": _tratar_int(tag_hum.text if tag_hum else None, 0, 100),
        "velocidade_vento_boost": _tratar_float(tag_vento.text if tag_vento else None, 0.0, 300.0),
        "bombsite_status": tag_cond.text.strip() if tag_cond else None
    }

def _tratar_float(texto: Optional[str], minimo: float, maximo: float) -> Optional[float]:
    if not texto:
        return None
    match = re.search(r"[-+]?\d+(?:[\.,]\d+)?", texto)
    if not match:
        return None
    valor = float(match.group().replace(",", "."))
    if not (minimo <= valor <= maximo):
        raise ErroNoHudParser(f"Valor numérico fora dos limites do mapa ({minimo} a {maximo}): {valor}")
    return valor

def _tratar_int(texto: Optional[str], minimo: int, maximo: int) -> Optional[int]:
    val_float = _tratar_float(texto, float(minimo), float(maximo))
    return int(val_float) if val_float is not None else None
