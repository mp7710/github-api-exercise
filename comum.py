"""Código compartilhado pelas três tarefas: cabeçalhos, GET com tratamento de limite e nomes de arquivo."""

import os
import re
import time

import requests

API_BASE = "https://api.github.com"

# Cabeçalhos recomendados pelo GitHub. Se GITHUB_TOKEN existir, elevamos o
# limite de ~60 para ~5000 requisições/hora.
HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "github-api-exercise",
}
_TOKEN = os.environ.get("GITHUB_TOKEN")
if _TOKEN:
    HEADERS["Authorization"] = f"Bearer {_TOKEN}"


class ErroAPI(RuntimeError):
    """Falha da API do GitHub que impede um resultado completo."""


def get(url, params=None):
    """GET com cabeçalhos e tratamento de rate limit (primário e secundário)."""
    resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
    limite_primario = resp.status_code == 403 and resp.headers.get("X-RateLimit-Remaining") == "0"
    if limite_primario or resp.status_code == 429:
        if resp.headers.get("Retry-After", "").isdigit():
            espera = int(resp.headers["Retry-After"])
        else:
            reset = int(resp.headers.get("X-RateLimit-Reset", "0"))
            espera = max(0, reset - int(time.time()))
        raise ErroAPI(
            f"Limite de requisições atingido. Aguarde ~{espera}s ou "
            f"configure a variável de ambiente GITHUB_TOKEN."
        )
    return resp


def nome_seguro(texto):
    """Transforma qualquer texto num pedaço de nome de arquivo (sem barras nem caracteres estranhos)."""
    return re.sub(r"[^A-Za-z0-9._-]+", "_", texto).strip("._") or "sem_nome"


def ler_owner_repo(texto):
    """'owner/repo' -> ('owner', 'repo'); None se o formato estiver errado."""
    partes = texto.strip().strip("/").split("/")
    if len(partes) != 2 or not all(partes):
        return None
    return partes[0], partes[1]
