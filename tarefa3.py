#!/usr/bin/env python3
"""
Tarefa 3: Criar um dataset personalizado
- Colete dados de múltiplos repositórios
- Salve em um arquivo JSON estruturado
- Gere estatísticas básicas
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
        "issues_abertas": repo_info['open_issues_count'],
        "linguagem": linguagem_principal,
        "descricao": repo_info.get('description'),
        "url": repo_info['html_url']
    }

def gerar_estatisticas(repositorios):
    """Gera estatísticas sobre os repositórios"""
    if not repositorios:
        return None
    
    total_estrelas = sum(r["estrelas"] for r in repositorios)
    total_forks = sum(r["forks"] for r in repositorios)
    
    # Contar distribuição de linguagens
    distribuicao_linguagens = {}
    for repo in repositorios:
        lang = repo["linguagem"]
        distribuicao_linguagens[lang] = distribuicao_linguagens.get(lang, 0) + 1
    
    # Encontrar repo mais estrelado
    repo_mais_estrelado = max(repositorios, key=lambda r: r["estrelas"])["nome_completo"]
    
    return {
        "total_repositorios": len(repositorios),
        "total_estrelas": total_estrelas,
        "media_estrelas": round(total_estrelas / len(repositorios), 2),
        "total_forks": total_forks,
        "media_forks": round(total_forks / len(repositorios), 2),
        "repositorio_mais_estrelado": repo_mais_estrelado,
        "distribuicao_linguagens": distribuicao_linguagens
    }

def main():
    print("=" * 60)
    print("CRIADOR DE DATASET PERSONALIZADO")
    print("=" * 60)
    
    repositorios = []
    
    print("\nDigite os repositórios que deseja analisar (formato: owner/repo)")
    print("Digite 'pronto' quando terminar.\n")
    
    # Dataset padrão com projetos famosos
    dataset_padrao = [
        "numpy/numpy",
        "pandas-dev/pandas",
        "tensorflow/tensorflow",
        "pytorch/pytorch",
        "scikit-learn/scikit-learn"
    ]
    
    print("Ou escolha uma opção:")
    print("1. Usar dataset padrão (numpy, pandas, tensorflow, pytorch, scikit-learn)")
    print("2. Inserir repositórios manualmente")
    
    opcao = input("\nEscolha (1 ou 2): ").strip()
    
    if opcao == "1":
        repos_para_coletar = dataset_padrao
    else:
        repos_para_coletar = []
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
    
    # Gerar estatísticas
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
    
    # Compilar resultado final
    resultado = {
        "_observacao": "Dataset coletado via API do GitHub com dados reais",
        "coletado_em": datetime.now().isoformat(),
        "estatisticas": estatisticas,
        "repositorios": repositorios
    }
    
    # Salvar resultado
    filename = "tarefa3_resultado.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Resultado completo salvo em '{filename}'")

if __name__ == "__main__":
    main()