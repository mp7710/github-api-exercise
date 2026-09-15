#!/usr/bin/env python3
"""
Tarefa 1: Explorar sua própria conta no GitHub
- Faça uma requisição para /users/{seu_username}
- Liste todos os seus repositórios públicos
- Calcule o total de estrelas acumuladas
"""

import os
import json
import time
from datetime import datetime, timezone

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


def buscar_usuario(username):
    """Busca informações do usuário"""
    resp = get(f"{API_BASE}/users/{username}")
    return resp.json() if resp.status_code == 200 else None


def listar_repositorios(username):
    """Lista todos os repositórios públicos do usuário (com paginação)"""
    repos = []
    page = 1
    while True:
        resp = get(f"{API_BASE}/users/{username}/repos",
                   params={"page": page, "per_page": 100, "type": "public"})
        if resp.status_code != 200:
            break
        data = resp.json()
        if not data:
            break
        repos.extend(data)
        if len(data) < 100:
            break  # última página
        page += 1
    return repos


def calcular_estrelas_totais(repos):
    """Calcula o total de estrelas acumuladas"""
    return sum(repo["stargazers_count"] for repo in repos)


def main():
    username = input("Digite seu username do GitHub: ").strip()

    print(f"\n🔍 Buscando informações do usuário '{username}'...\n")

    usuario = buscar_usuario(username)
    if not usuario:
        print(f"❌ Usuário '{username}' não encontrado!")
        return

    print(f"✅ Usuário encontrado!")
    print(f"   Nome: {usuario.get('name') or 'N/A'}")
    print(f"   Bio: {usuario.get('bio') or 'N/A'}")
    print(f"   Seguidores: {usuario.get('followers')}")
    print(f"   Seguindo: {usuario.get('following')}")
    print(f"   Repositórios públicos: {usuario.get('public_repos')}")

    print(f"\n📚 Listando repositórios públicos...\n")
    repos = listar_repositorios(username)

    if not repos:
        print("Nenhum repositório público encontrado.")
        return

    print(f"Encontrados {len(repos)} repositórios:\n")
    for i, repo in enumerate(repos, 1):
        print(f"{i}. {repo['name']}")
        print(f"   ⭐ Estrelas: {repo['stargazers_count']}")
        print(f"   🔀 Forks: {repo['forks_count']}")
        print(f"   🔗 {repo['html_url']}\n")

    total_estrelas = calcular_estrelas_totais(repos)
    media_estrelas = total_estrelas / len(repos) if repos else 0

    print(f"\n📊 ESTATÍSTICAS:")
    print(f"   Total de repositórios: {len(repos)}")
    print(f"   Total de estrelas: {total_estrelas}")
    print(f"   Média de estrelas por repo: {media_estrelas:.2f}")

    resultado = {
        "coletado_em": datetime.now(timezone.utc).isoformat(),
        "usuario": {
            "username": usuario.get("login"),
            "nome": usuario.get("name"),
            "bio": usuario.get("bio"),
            "seguidores": usuario.get("followers"),
            "seguindo": usuario.get("following"),
            "repositorios_publicos": usuario.get("public_repos"),
        },
        "estatisticas": {
            "total_repositorios": len(repos),
            "total_estrelas": total_estrelas,
            "media_estrelas": round(media_estrelas, 2),
        },
        "repositorios": [
            {
                "nome": repo["name"],
                "url": repo["html_url"],
                "estrelas": repo["stargazers_count"],
                "forks": repo["forks_count"],
                "linguagem": repo.get("language") or "N/A",
            }
            for repo in repos
        ],
    }

    with open("tarefa1_resultado.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Resultado salvo em 'tarefa1_resultado.json'")


if __name__ == "__main__":
    try:
        main()
    except (requests.RequestException, RuntimeError) as e:
        print(f"\n❌ Erro: {e}")
