"""Gera gráficos de valor vendido por categoria e por cidade."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # geração de PNG sem interface gráfica

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd


PASTA = Path(__file__).resolve().parent
ARQUIVO_DADOS = PASTA / "papelaria_limpa.csv"


def moeda_br(valor):
    """Formata valores no padrão brasileiro, por exemplo R$ 1.234,56."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def criar_grafico(df, dimensao, titulo, nome_arquivo, cor):
    totais = (
        df.groupby(dimensao, as_index=False)["valor_venda"]
        .sum()
        .sort_values("valor_venda", ascending=False)
    )

    fig, ax = plt.subplots(figsize=(8, 5), dpi=150)
    barras = ax.bar(
        totais[dimensao], totais["valor_venda"], color=cor, width=0.65
    )

    ax.set_title(titulo, fontsize=14, fontweight="bold", pad=14)
    ax.set_xlabel(dimensao.capitalize())
    ax.set_ylabel("Valor vendido (R$)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda valor, _: moeda_br(valor)))
    ax.set_ylim(bottom=0, top=max(totais["valor_venda"]) * 1.16)
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    for barra, valor in zip(barras, totais["valor_venda"]):
        ax.annotate(
            moeda_br(valor),
            (barra.get_x() + barra.get_width() / 2, barra.get_height()),
            xytext=(0, 5),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    fig.tight_layout()
    fig.savefig(PASTA / nome_arquivo, bbox_inches="tight")
    plt.close(fig)
    return totais


def main():
    df = pd.read_csv(ARQUIVO_DADOS, encoding="utf-8-sig")
    df["valor_venda"] = pd.to_numeric(df["valor_venda"], errors="raise")

    por_categoria = criar_grafico(
        df,
        "categoria",
        "Valor total vendido por categoria",
        "categorias.png",
        "#4C72B0",
    )
    por_cidade = criar_grafico(
        df,
        "cidade",
        "Valor total vendido por cidade",
        "cidades.png",
        "#DD8452",
    )

    print("Totais por categoria (R$):")
    print(por_categoria.to_string(index=False))
    print("\nTotais por cidade (R$):")
    print(por_cidade.to_string(index=False))
    print("\nGráficos salvos: categorias.png e cidades.png")


if __name__ == "__main__":
    main()
