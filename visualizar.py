#!/usr/bin/env python3
"""Bônus: gráfico de estrelas e forks por repositório a partir do tarefa3_resultado.json."""

import json
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ARQUIVO = "tarefa3_resultado.json"


def main():
    try:
        dados = json.load(open(ARQUIVO, encoding="utf-8"))
    except FileNotFoundError:
        sys.exit(f"❌ '{ARQUIVO}' não encontrado. Rode antes: python tarefa3.py")
    repos = sorted(dados["repositorios"], key=lambda r: r["estrelas"])
    nomes = [r["nome_completo"].split("/")[1] for r in repos]
    y = range(len(repos))
    fig, ax = plt.subplots(figsize=(9, 0.7 * len(repos) + 1.5))
    # azul e laranja: par seguro para daltonismo
    b1 = ax.barh([i + 0.2 for i in y], [r["estrelas"] for r in repos], height=0.4, color="#0072B2", label="Estrelas")
    b2 = ax.barh([i - 0.2 for i in y], [r["forks"] for r in repos], height=0.4, color="#E69F00", label="Forks")
    for barras in (b1, b2):
        ax.bar_label(barras, labels=[f"{int(b.get_width()):,}".replace(",", ".") for b in barras], padding=3, fontsize=8)
    ax.set_yticks(list(y), nomes)
    ax.set_title("Estrelas e forks por repositório")
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(loc="lower right", frameon=False)
    fig.tight_layout()
    fig.savefig("visualizacao.png", dpi=150)
    print("💾 Gráfico salvo em 'visualizacao.png'")


if __name__ == "__main__":
    main()
