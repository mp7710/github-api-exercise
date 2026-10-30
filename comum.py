"""Acesso à API do GitHub usado pelas três tarefas (cabeçalhos, token e limites)."""

import os
import time
from datetime import datetime

import requests

API_BASE = "https://api.github.com"

# Cabeçalhos recomendados pelo GitHub. Com GITHUB_TOKEN o limite sobe de ~60 para ~5000 requisições/hora.
HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "github-api-exercise",
}
_TOKEN = os.environ.get("GITHUB_TOKEN")
if _TOKEN:
    HEADERS["Authorization"] = f"Bearer {_TOKEN}"


def _espera(resp):
    """Segundos até o limite voltar (Retry-After ou X-RateLimit-Reset)."""
    if resp.headers.get("Retry-After"):
        return int(resp.headers["Retry-After"])
    reset = int(resp.headers.get("X-RateLimit-Reset", "0") or 0)
    return max(0, reset - int(time.time()))


def get(url, params=None):
    """GET com cabeçalhos; transforma limite de requisições e falta de internet em mensagens claras."""
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
    except requests.ConnectionError:
        raise RuntimeError("Sem conexão com a internet (ou api.github.com fora do ar). Tente de novo.")
    except requests.Timeout:
        raise RuntimeError("O GitHub demorou demais para responder. Tente de novo.")
    limite = resp.status_code == 429 or (
        resp.status_code == 403
        and (resp.headers.get("X-RateLimit-Remaining") == "0" or resp.headers.get("Retry-After"))
    )
    if limite:
        espera = _espera(resp)
        volta = datetime.fromtimestamp(time.time() + espera).strftime("%H:%M:%S")
        dica = "" if _TOKEN else " Para ter ~5000/hora, configure a variável GITHUB_TOKEN (veja o README)."
        raise RuntimeError(f"Limite de requisições do GitHub atingido. Volta às {volta} (~{espera}s).{dica}")
    return resp
