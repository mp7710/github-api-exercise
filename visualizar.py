#!/usr/bin/env python3
"""
Bônus: visualizar as estatísticas da Tarefa 3
- Lê tarefa3_resultado.json
- Gráfico de barras com estrelas e forks por repositório
- Paleta segura para daltonismo (Okabe-Ito) e rótulo direto em cada barra
- Salva em visualizacao.png
"""

import json
import sys

import matplotlib

matplotlib.use("Agg")  # gera a imagem sem precisar de janela
import matplotlib.pyplot as plt  # noqa: E402

ARQUIVO = "tarefa3_resultado.json"
SAIDA = "visualizacao.png"
COR_ESTRELAS = "#0072B2"  # azul (Okabe-Ito)
COR_FORKS = "#E69F00"     # laranja (Okabe-Ito)


def formatar(n):
    """12345 -> '12,3 mil'; 1200000 -> '1,2 mi'."""
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f} mi".replace(".", ",")
    if n >= 1_000:
        return f"{n / 1_000:.1f} mil".replace(".", ",")
    return str(n)


def main():
    try:
        with open(ARQUIVO, encoding="utf-8") as f:
            dados = json.load(f)
    except FileNotFoundError:
        print(f"❌ '{ARQUIVO}' não encontrado. Rode primeiro: python tarefa3.py")
        sys.exit(1)

    repos = sorted(dados.get("repositorios", []), key=lambda r: r["estrelas"], reverse=True)
    if not repos:
        print("❌ O dataset não tem repositórios.")
        sys.exit(1)

    nomes = [r["nome_completo"] for r in repos]
    estrelas = [r["estrelas"] for r in repos]
    forks = [r["forks"] for r in repos]

    x = range(len(repos))
    largura = 0.4
    fig, ax = plt.subplots(figsize=(max(8, len(repos) * 1.6), 6))
    barras_e = ax.bar([i - largura / 2 for i in x], estrelas, largura, label="Estrelas", color=COR_ESTRELAS)
    barras_f = ax.bar([i + largura / 2 for i in x], forks, largura, label="Forks", color=COR_FORKS)
    ax.bar_label(barras_e, labels=[formatar(v) for v in estrelas], padding=3, fontsize=9)
    ax.bar_label(barras_f, labels=[formatar(v) for v in forks], padding=3, fontsize=9)

    ax.set_xticks(list(x))
    ax.set_xticklabels(nomes, rotation=30, ha="right")
    ax.set_title("Estrelas e forks por repositório", fontweight="bold")
    ax.yaxis.set_major_formatter(lambda v, _pos: formatar(int(v)))
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(SAIDA, dpi=150)
    print(f"💾 Gráfico salvo em '{SAIDA}'")


if __name__ == "__main__":
    main()
