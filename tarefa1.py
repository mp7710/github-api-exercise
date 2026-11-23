#!/usr/bin/env python3
"""
Tarefa 1: Explorar sua própria conta no GitHub
- Faça uma requisição para /users/{seu_username}
- Liste todos os seus repositórios públicos
- Calcule o total de estrelas acumuladas
"""

import json
from datetime import datetime, timezone

import requests

from comum import API_BASE, ErroAPI, get


def buscar_usuario(username):
    """Busca informações do usuário"""
    resp = get(f"{API_BASE}/users/{username}")
    if resp.status_code == 404:
        return None
    if resp.status_code != 200:
        raise ErroAPI(f"Falha ao buscar usuário (HTTP {resp.status_code}).")
    return resp.json()


def listar_repositorios(username):
    """Lista todos os repositórios públicos do usuário (com paginação)"""
    repos = []
    page = 1
    while True:
        # "owner" = repositórios do próprio usuário (os valores válidos são all, owner e member).
        resp = get(f"{API_BASE}/users/{username}/repos",
                   params={"page": page, "per_page": 100, "type": "owner"})
        if resp.status_code != 200:
            # Não devolve uma lista pela metade como se estivesse completa.
            raise ErroAPI(f"Falha ao listar repositórios (página {page}, HTTP {resp.status_code}).")
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
    if not username or "/" in username:
        print("❌ Username inválido!")
        return

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
    except (requests.RequestException, ErroAPI, OSError) as e:
        print(f"\n❌ Erro: {e}")
