#!/usr/bin/env python3
"""
Tarefa 1: Explorar sua própria conta no GitHub
- Faça uma requisição para /users/{seu_username}
- Liste todos os seus repositórios públicos
- Calcule o total de estrelas acumuladas
"""

import requests
import json
from datetime import datetime

def buscar_usuario(username):
    """Busca informações do usuário"""
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def listar_repositorios(username):
    """Lista todos os repositórios públicos do usuário"""
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{username}/repos"
        params = {"page": page, "per_page": 100}
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            break
            
        data = response.json()
        if not data:
            break
            
        repos.extend(data)
        page += 1
    
    return repos

def calcular_estrelas_totais(repos):
    """Calcula o total de estrelas acumuladas"""
    return sum(repo["stargazers_count"] for repo in repos)

def main():
    username = input("Digite seu username do GitHub: ").strip()
    
    print(f"\n🔍 Buscando informações do usuário '{username}'...\n")
    
    # Tarefa 1: Buscar informações do usuário
    usuario = buscar_usuario(username)
    if not usuario:
        print(f"❌ Usuário '{username}' não encontrado!")
        return
    
    print(f"✅ Usuário encontrado!")
    print(f"   Nome: {usuario.get('name', 'N/A')}")
    print(f"   Bio: {usuario.get('bio', 'N/A')}")
    print(f"   Seguidores: {usuario.get('followers')}")
    print(f"   Seguindo: {usuario.get('following')}")
    print(f"   Repositórios públicos: {usuario.get('public_repos')}")
    
    # Tarefa 2: Listar repositórios
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
    
    # Tarefa 3: Calcular total de estrelas
    total_estrelas = calcular_estrelas_totais(repos)
    media_estrelas = total_estrelas / len(repos) if repos else 0
    
    print(f"\n📊 ESTATÍSTICAS:")
    print(f"   Total de repositórios: {len(repos)}")
    print(f"   Total de estrelas: {total_estrelas}")
    print(f"   Média de estrelas por repo: {media_estrelas:.2f}")
    
    # Salvar resultado em JSON
    resultado = {
        "coletado_em": datetime.now().isoformat(),
        "usuario": {
            "username": usuario.get("login"),
            "nome": usuario.get("name"),
            "bio": usuario.get("bio"),
            "seguidores": usuario.get("followers"),
            "seguindo": usuario.get("following"),
            "repositorios_publicos": usuario.get("public_repos")
        },
        "estatisticas": {
            "total_repositorios": len(repos),
            "total_estrelas": total_estrelas,
            "media_estrelas": round(media_estrelas, 2)
        },
        "repositorios": [
            {
                "nome": repo["name"],
                "url": repo["html_url"],
                "estrelas": repo["stargazers_count"],
                "forks": repo["forks_count"],
                "linguagem": repo.get("language", "N/A")
            }
            for repo in repos
        ]
    }
    
    with open("tarefa1_resultado.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultado salvo em 'tarefa1_resultado.json'")

if __name__ == "__main__":
    main()