import random
import time
from abc import ABC, abstractmethod
import requests
from src.domain.errors import EconFailedError, BanidoDaMatchmakingError

class TáticaScraping(ABC):
    @abstractmethod
    def catar_html(self, url_alvo: str) -> str:
        pass

class TáticaPistolRequests(TáticaScraping):
    """Estratégia leve com requisições normais (pistol round rápido)."""

    FAKE_USER_AGENTS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
    }

    def catar_html(self, url_alvo: str) -> str:
        # Delay com jitter simulando compra demorada na base
        time.sleep(random.uniform(0.5, 1.5))
        try:
            sessao = requests.Session()
            resposta = sessao.get(url_alvo, headers=self.FAKE_USER_AGENTS, timeout=8.0)

            if resposta.status_code in (403, 429) or "captcha" in resposta.text.lower():
                raise BanidoDaMatchmakingError(f"Tomou ban / Captcha ativado (Status code: {resposta.status_code}).")

            resposta.raise_for_status()
            return resposta.text

        except requests.RequestException as err:
            raise EconFailedError(f"Falha de rede na tática pistol: {str(err)}") from err

class TáticaFullBuySelenium(TáticaScraping):
    """Estratégia pesada com Selenium Headless (Vai de AWP quando a pistol falha)."""

    def catar_html(self, url_alvo: str) -> str:
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
        except ImportError:
            raise EconFailedError("Selenium não tá instalado no inventário (pip install selenium).")

        opcoes = Options()
        opcoes.add_argument("--headless=new")
        opcoes.add_argument("--disable-gpu")
        opcoes.add_argument("--no-sandbox")
        opcoes.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

        driver_instancia = None
        try:
            driver_instancia = webdriver.Chrome(options=opcoes)
            driver_instancia.get(url_alvo)

            WebDriverWait(driver_instancia, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            html_pagina = driver_instancia.page_source

            if "captcha" in html_pagina.lower():
                raise BanidoDaMatchmakingError("Captcha detectado pelo Selenium no modo Full Buy.")

            return html_pagina
        except Exception as err:
            if isinstance(err, BanidoDaMatchmakingError):
                raise
            raise EconFailedError(f"Erro ao carregar o mapa no Selenium: {str(err)}") from err
        finally:
            if driver_instancia:
                driver_instancia.quit()
