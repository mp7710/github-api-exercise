"""Testes das três tarefas com a API do GitHub falsa (nada sai para a internet)."""

import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest
import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import comum  # noqa: E402
import tarefa1  # noqa: E402
import tarefa2  # noqa: E402
import tarefa3  # noqa: E402


class Resp:
    def __init__(self, status=200, dados=None, headers=None):
        self.status_code, self._dados, self.headers = status, dados, headers or {}

    def json(self):
        return self._dados


def api(rotas):
    """Troca requests.get por uma função que responde pelas rotas dadas."""
    def falso(url, params=None, **kw):
        caminho = url.replace(comum.API_BASE, "")
        pagina = (params or {}).get("page")
        r = rotas.get((caminho, pagina), rotas.get(caminho, Resp(404, {"message": "Not Found"})))
        return r(params) if callable(r) else r
    return patch.object(comum.requests, "get", side_effect=falso)


def repo(nome, estrelas=1):
    return {"full_name": f"dono/{nome}", "stargazers_count": estrelas, "forks_count": 2,
            "open_issues_count": 3, "html_url": "https://github.com/dono/" + nome, "description": None}


def test_usuario_inexistente():
    with api({}):
        assert tarefa1.buscar_usuario("ninguem") is None


def test_paginacao_junta_todas_as_paginas_e_soma_estrelas():
    p1 = [repo(f"r{i}", 1) for i in range(100)]
    p2 = [repo("ultimo", 50)]
    with api({("/users/eu/repos", 1): Resp(200, p1), ("/users/eu/repos", 2): Resp(200, p2)}):
        repos = tarefa1.listar_repositorios("eu")
    assert len(repos) == 101
    assert tarefa1.calcular_estrelas_totais(repos) == 150


def test_repositorio_sem_linguagens_nem_licenca():
    with api({"/repos/dono/vazio": Resp(200, repo("vazio")), "/repos/dono/vazio/languages": Resp(200, {})}):
        dados = tarefa3.coletar_dados_repositorio("dono", "vazio")
    assert dados["linguagem"] == "N/A"


def test_search_separa_issues_de_prs():
    with api({"/search/issues": lambda p: Resp(200, {"total_count": 7 if "type:issue" in p["q"] else 2})}):
        assert tarefa2.contar_via_search("dono", "x", "issue") == 7
        assert tarefa2.contar_via_search("dono", "x", "pr") == 2


def test_estatisticas():
    est = tarefa3.gerar_estatisticas([
        {"nome_completo": "a/a", "estrelas": 10, "forks": 1, "linguagem": "Python"},
        {"nome_completo": "b/b", "estrelas": 30, "forks": 3, "linguagem": "Python"},
    ])
    assert est["media_estrelas"] == 20
    assert est["repositorio_mais_estrelado"] == "b/b"
    assert est["distribuicao_linguagens"] == {"Python": 2}


@pytest.mark.parametrize("status,headers", [
    (403, {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": str(int(time.time()) + 120)}),
    (429, {"Retry-After": "60"}),
    (403, {"Retry-After": "30"}),
])
def test_limite_de_requisicoes_vira_mensagem_clara(status, headers):
    with api({"/users/eu": Resp(status, {}, headers)}):
        with pytest.raises(RuntimeError, match="Limite de requisições"):
            tarefa1.buscar_usuario("eu")


def test_sem_internet():
    with patch.object(comum.requests, "get", side_effect=requests.ConnectionError()):
        with pytest.raises(RuntimeError, match="Sem conexão"):
            tarefa1.buscar_usuario("eu")
