#!/usr/bin/env python3
"""
Tarefa 2: Analisar um projeto open-source
- Escolha um repositório famoso (numpy, tensorflow, etc.)
- Extraia: estrelas, forks, issues abertas
- Identifique as linguagens utilizadas
"""

import requests
import json
from datetime import datetime

def buscar_repositorio(owner, repo):
    """Busca informações do repositório"""
    url = f"https://api.github.com/repos/{owner}/{repo}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def buscar_linguagens(owner, repo):
    """Busca as linguagens utilizadas no repositório"""
    url = f"https://api.github.com/repos/{owner}/{repo}/languages"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else {}

def buscar_issues_abertas(owner, repo):
    """Busca issues abertas"""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    params = {"state": "open", "per_page": 1}
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        # Tenta extrair do header Link se houver paginação
        link_header = response.headers.get("Link", "")
        if "last" in link_header:
            # Extrai número da última página
            import re
            match = re.search(r'page=(\d+)>; rel="last"', link_header)
            if match:
                return int(match.group(1))
        return len(response.json())
    return 0

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
    
    # Buscar informações do repositório
    repo_info = buscar_repositorio(owner, repo)
    
    if not repo_info or "message" in repo_info:
        print(f"❌ Repositório '{owner}/{repo}' não encontrado!")
        return
    
    print(f"✅ Repositório encontrado!\n")
    print(f"📌 Nome: {repo_info['full_name']}")
    print(f"📝 Descrição: {repo_info.get('description', 'N/A')}")
    print(f"🌐 URL: {repo_info['html_url']}")
    print(f"⭐ Estrelas: {repo_info['stargazers_count']}")
    print(f"🔀 Forks: {repo_info['forks_count']}")
    print(f"👀 Watchers: {repo_info['watchers_count']}")
    
    # Buscar issues abertas
    print(f"\n🔄 Buscando issues abertas...")
    issues_abertas = buscar_issues_abertas(owner, repo)
    print(f"🐛 Issues abertas: {issues_abertas}")
    
    # Buscar linguagens
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
    
    # Compilar resultado
    resultado = {
        "coletado_em": datetime.now().isoformat(),
        "repositorio": {
            "nome_completo": repo_info['full_name'],
            "url": repo_info['html_url'],
            "descricao": repo_info.get('description'),
            "owner": owner,
            "repo": repo
        },
        "metricas": {
            "estrelas": repo_info['stargazers_count'],
            "forks": repo_info['forks_count'],
            "watchers": repo_info['watchers_count'],
            "issues_abertas": issues_abertas,
            "pull_requests_abertos": repo_info['open_issues_count'] - issues_abertas if repo_info['open_issues_count'] >= issues_abertas else 0
        },
        "linguagens": linguagens,
        "informacoes_adicionais": {
            "criado_em": repo_info['created_at'],
            "ultimo_push": repo_info['pushed_at'],
            "license": repo_info.get('license', {}).get('name', 'N/A') if repo_info.get('license') else 'N/A',
            "topicos": repo_info.get('topics', [])
        }
    }
    
    # Salvar resultado
    with open(f"tarefa2_resultado_{owner}_{repo}.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultado salvo em 'tarefa2_resultado_{owner}_{repo}.json'")

if __name__ == "__main__":
    main()