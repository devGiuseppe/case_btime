class CSBaseError(Exception):
    """Exceção base para qualquer round perdido no domínio."""
    pass

class EconFailedError(CSBaseError):
    """Deu ruim na compra (rede, timeout ou erro 5xx do servidor da Valve)."""
    pass

class BanidoDaMatchmakingError(CSBaseError):
    """Tomou ban de 7 dias (403, 429, Captcha ou anti-cheat pegou o bot)."""
    pass

class ErroNoHudParser(CSBaseError):
    """O HUD mudou de lugar ou veio corrompido, impossível ler o placar."""
    pass
