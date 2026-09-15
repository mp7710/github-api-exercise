#!/usr/bin/env python3
"""
Tarefa 2: Analisar um projeto open-source
- Escolha um repositório famoso (numpy, tensorflow, etc.)
- Extraia: estrelas, forks, issues abertas
- Identifique as linguagens utilizadas
"""

import os
import json
import time
from datetime import datetime, timezone

import requests

API_BASE = "https://api.github.com"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "github-api-exercise",
}
_TOKEN = os.environ.get("GITHUB_TOKEN")
if _TOKEN:
    HEADERS["Authorization"] = f"Bearer {_TOKEN}"


def get(url, params=None):
    """GET com cabeçalhos e tratamento de rate limit."""
    resp = requests.get(url, headers=HEADERS, params=params, timeout=30)
    if resp.status_code == 403 and resp.headers.get("X-RateLimit-Remaining") == "0":
        reset = int(resp.headers.get("X-RateLimit-Reset", "0"))
        espera = max(0, reset - int(time.time()))
        raise RuntimeError(
            f"Limite de requisições atingido. Aguarde ~{espera}s ou "
            f"configure a variável de ambiente GITHUB_TOKEN."
        )
    return resp


def buscar_repositorio(owner, repo):
    """Busca informações do repositório"""
    resp = get(f"{API_BASE}/repos/{owner}/{repo}")
    return resp.json() if resp.status_code == 200 else None


def buscar_linguagens(owner, repo):
    """Busca as linguagens utilizadas no repositório"""
    resp = get(f"{API_BASE}/repos/{owner}/{repo}/languages")
    return resp.json() if resp.status_code == 200 else {}


def contar_via_search(owner, repo, tipo):
    """
    Conta issues OU pull requests abertos usando a Search API.

    A Search API é a forma correta de separar os dois: o endpoint /issues
    do GitHub mistura issues e pull requests na mesma listagem, então contar
    por ele superestima as issues. Aqui usamos 'type:issue' e 'type:pr'
    explicitamente e lemos o campo 'total_count'.
    """
    q = f"repo:{owner}/{repo} type:{tipo} state:open"
    resp = get(f"{API_BASE}/search/issues", params={"q": q, "per_page": 1})
    if resp.status_code == 200:
        return resp.json().get("total_count", 0)
    return None


def main():
    print("=" * 60)
    print("ANALISADOR DE REPOSITÓRIOS OPEN-SOURCE")
    print("=" * 60)
    print("\nExemplos de repositórios populares:")
    print("  - numpy/numpy")
    print("  - pandas-dev/pandas")
    print("  - tensorflow/tensorflow")
    print("  - pytorch/pytorch")
    print("  - scikit-learn/scikit-learn")
    print("  - facebook/react")
    print("  - vuejs/vue")

    repo_input = input("\nDigite o repositório (owner/repo): ").strip()

    if "/" not in repo_input:
        print("❌ Formato inválido! Use: owner/repo")
        return

    owner, repo = repo_input.split("/", 1)

    print(f"\n🔍 Analisando {owner}/{repo}...\n")

    repo_info = buscar_repositorio(owner, repo)

    if not repo_info or "message" in repo_info:
        print(f"❌ Repositório '{owner}/{repo}' não encontrado!")
        return

    print(f"✅ Repositório encontrado!\n")
    print(f"📌 Nome: {repo_info['full_name']}")
    print(f"📝 Descrição: {repo_info.get('description') or 'N/A'}")
    print(f"🌐 URL: {repo_info['html_url']}")
    print(f"⭐ Estrelas: {repo_info['stargazers_count']}")
    print(f"🔀 Forks: {repo_info['forks_count']}")
    print(f"👀 Watchers: {repo_info['watchers_count']}")

    # Issues e PRs abertos, contados separadamente (Search API).
    print(f"\n🔄 Contando issues e pull requests abertos...")
    issues_abertas = contar_via_search(owner, repo, "issue")
    prs_abertos = contar_via_search(owner, repo, "pr")

    # Fallback: se a Search API falhar (ex.: rate limit próprio dela),
    # usamos open_issues_count, lembrando que ele inclui PRs.
    if issues_abertas is None:
        issues_abertas = repo_info.get("open_issues_count")
        print(f"🐛 Issues abertas (inclui PRs, via fallback): {issues_abertas}")
    else:
        print(f"🐛 Issues abertas: {issues_abertas}")
        print(f"🔀 Pull requests abertos: {prs_abertos}")

    print(f"\n🔄 Identificando linguagens...")
    linguagens = buscar_linguagens(owner, repo)

    if linguagens:
        print(f"💻 Linguagens utilizadas:")
        total_bytes = sum(linguagens.values())
        for lang, bytes_count in sorted(linguagens.items(), key=lambda x: x[1], reverse=True):
            percentage = (bytes_count / total_bytes * 100) if total_bytes > 0 else 0
            print(f"   - {lang}: {percentage:.1f}%")
    else:
        print(f"💻 Nenhuma linguagem detectada")

    resultado = {
        "coletado_em": datetime.now(timezone.utc).isoformat(),
        "repositorio": {
            "nome_completo": repo_info['full_name'],
            "url": repo_info['html_url'],
            "descricao": repo_info.get('description'),
            "owner": owner,
            "repo": repo,
        },
        "metricas": {
            "estrelas": repo_info['stargazers_count'],
            "forks": repo_info['forks_count'],
            "watchers": repo_info['watchers_count'],
            "issues_abertas": issues_abertas,
            "pull_requests_abertos": prs_abertos,
        },
        "linguagens": linguagens,
        "informacoes_adicionais": {
            "criado_em": repo_info['created_at'],
            "ultimo_push": repo_info['pushed_at'],
            "license": (repo_info.get('license') or {}).get('name', 'N/A'),
            "topicos": repo_info.get('topics', []),
        },
    }

    with open(f"tarefa2_resultado_{owner}_{repo}.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Resultado salvo em 'tarefa2_resultado_{owner}_{repo}.json'")


if __name__ == "__main__":
    try:
        main()
    except (requests.RequestException, RuntimeError) as e:
        print(f"\n❌ Erro: {e}")
