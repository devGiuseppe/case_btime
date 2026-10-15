from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class RoundInfo:
    """O status atual do round climático (imutável, igual estatística de HUD)."""
    mapa_alvo: str
    hp_termico: Optional[float]
    umidade_spray: Optional[int]
    velocidade_vento_boost: Optional[float]
    bombsite_status: Optional[str]
    timestamp_plant: str  # ISO 8601 com timezone (ex: 2026-10-15T14:30:00-03:00)
    origem_drop: str      # ex: "open-meteo" ou "climatempo"
