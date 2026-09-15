#!/usr/bin/env python3
"""
Tarefa 3: Criar um dataset personalizado
- Colete dados de múltiplos repositórios
- Salve em um arquivo JSON estruturado
- Gere estatísticas básicas
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


def coletar_dados_repositorio(owner, repo):
    """Coleta dados completos de um repositório"""
    repo_info = buscar_repositorio(owner, repo)

    if not repo_info or "message" in repo_info:
        return None

    linguagens = buscar_linguagens(owner, repo)
    linguagem_principal = max(linguagens, key=linguagens.get) if linguagens else "N/A"

    return {
        "nome_completo": repo_info['full_name'],
        "estrelas": repo_info['stargazers_count'],
        "forks": repo_info['forks_count'],
        # open_issues_count inclui pull requests (limitação da API do GitHub).
        "issues_abertas": repo_info['open_issues_count'],
        "linguagem": linguagem_principal,
        "descricao": repo_info.get('description'),
        "url": repo_info['html_url'],
    }


def gerar_estatisticas(repositorios):
    """Gera estatísticas sobre os repositórios"""
    if not repositorios:
        return None

    total_estrelas = sum(r["estrelas"] for r in repositorios)
    total_forks = sum(r["forks"] for r in repositorios)

    distribuicao_linguagens = {}
    for repo in repositorios:
        lang = repo["linguagem"]
        distribuicao_linguagens[lang] = distribuicao_linguagens.get(lang, 0) + 1

    repo_mais_estrelado = max(repositorios, key=lambda r: r["estrelas"])["nome_completo"]

    return {
        "total_repositorios": len(repositorios),
        "total_estrelas": total_estrelas,
        "media_estrelas": round(total_estrelas / len(repositorios), 2),
        "total_forks": total_forks,
        "media_forks": round(total_forks / len(repositorios), 2),
        "repositorio_mais_estrelado": repo_mais_estrelado,
        "distribuicao_linguagens": distribuicao_linguagens,
    }


def main():
    print("=" * 60)
    print("CRIADOR DE DATASET PERSONALIZADO")
    print("=" * 60)

    repositorios = []

    dataset_padrao = [
        "numpy/numpy",
        "pandas-dev/pandas",
        "tensorflow/tensorflow",
        "pytorch/pytorch",
        "scikit-learn/scikit-learn",
    ]

    print("\nEscolha uma opção:")
    print("1. Usar dataset padrão (numpy, pandas, tensorflow, pytorch, scikit-learn)")
    print("2. Inserir repositórios manualmente")

    opcao = input("\nEscolha (1 ou 2): ").strip()

    if opcao == "1":
        repos_para_coletar = dataset_padrao
    else:
        repos_para_coletar = []
        print("\nDigite os repositórios (formato: owner/repo). Digite 'pronto' para encerrar.")
        while True:
            repo = input("Repositório (owner/repo) ou 'pronto': ").strip()
            if repo.lower() == "pronto":
                break
            if "/" in repo:
                repos_para_coletar.append(repo)
            else:
                print("❌ Formato inválido! Use: owner/repo")

    if not repos_para_coletar:
        print("Nenhum repositório foi inserido.")
        return

    print(f"\n🔍 Coletando dados de {len(repos_para_coletar)} repositórios...\n")

    for repo_ref in repos_para_coletar:
        if "/" not in repo_ref:
            continue

        owner, repo = repo_ref.split("/", 1)
        print(f"⏳ Analisando {owner}/{repo}...", end=" ")

        dados = coletar_dados_repositorio(owner, repo)

        if dados:
            repositorios.append(dados)
            print(f"✅")
        else:
            print(f"❌ Não encontrado")

    if not repositorios:
        print("Nenhum repositório foi coletado com sucesso.")
        return

    print(f"\n📊 Gerando estatísticas...\n")
    estatisticas = gerar_estatisticas(repositorios)

    print("ESTATÍSTICAS DO DATASET:")
    print(f"  Total de repositórios: {estatisticas['total_repositorios']}")
    print(f"  Total de estrelas: {estatisticas['total_estrelas']}")
    print(f"  Média de estrelas: {estatisticas['media_estrelas']}")
    print(f"  Total de forks: {estatisticas['total_forks']}")
    print(f"  Média de forks: {estatisticas['media_forks']}")
    print(f"  Repositório mais estrelado: {estatisticas['repositorio_mais_estrelado']}")
    print(f"\n  Distribuição de linguagens:")
    for lang, count in estatisticas['distribuicao_linguagens'].items():
        print(f"    - {lang}: {count}")

    resultado = {
        "_observacao": "Dataset coletado via API do GitHub com dados reais. "
                       "'issues_abertas' usa open_issues_count, que inclui PRs.",
        "coletado_em": datetime.now(timezone.utc).isoformat(),
        "estatisticas": estatisticas,
        "repositorios": repositorios,
    }

    filename = "tarefa3_resultado.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Resultado completo salvo em '{filename}'")


if __name__ == "__main__":
    try:
        main()
    except (requests.RequestException, RuntimeError) as e:
        print(f"\n❌ Erro: {e}")
