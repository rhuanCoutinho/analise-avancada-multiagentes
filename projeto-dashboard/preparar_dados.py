"""Valida a fonte limpa e gera os dados locais consumidos pelo dashboard."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


PASTA_PROJETO = Path(__file__).resolve().parent
ARQUIVO_FONTE = PASTA_PROJETO.parent / "papelaria_limpa.csv"
ARQUIVO_SAIDA = PASTA_PROJETO / "site" / "data" / "vendas.json"

COLUNAS_OBRIGATORIAS = [
    "id_venda",
    "data",
    "cidade",
    "categoria",
    "produto",
    "quantidade",
    "preco_unitario",
    "forma_pagamento",
    "valor_venda",
]


def preparar_dados() -> dict:
    """Confere a fonte existente e retorna registros JSON serializáveis."""
    if not ARQUIVO_FONTE.is_file():
        raise FileNotFoundError(f"CSV de origem não encontrado: {ARQUIVO_FONTE}")

    dados = pd.read_csv(ARQUIVO_FONTE, encoding="utf-8-sig")
    faltantes = sorted(set(COLUNAS_OBRIGATORIAS) - set(dados.columns))
    if faltantes:
        raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(faltantes)}")
    if dados[COLUNAS_OBRIGATORIAS].isna().any().any():
        colunas = dados[COLUNAS_OBRIGATORIAS].columns[
            dados[COLUNAS_OBRIGATORIAS].isna().any()
        ].tolist()
        raise ValueError(f"Há valores ausentes nas colunas: {', '.join(colunas)}")
    if dados["id_venda"].duplicated().any():
        raise ValueError("A fonte limpa contém id_venda repetido; nenhuma linha foi removida.")

    for coluna in ("quantidade", "preco_unitario", "valor_venda"):
        dados[coluna] = pd.to_numeric(dados[coluna], errors="raise")
    if not pd.api.types.is_integer_dtype(dados["quantidade"]):
        if not np.equal(dados["quantidade"] % 1, 0).all():
            raise ValueError("A coluna quantidade contém valores não inteiros.")
        dados["quantidade"] = dados["quantidade"].astype("int64")

    datas = pd.to_datetime(dados["data"], format="%Y-%m-%d", errors="raise")
    if (dados["quantidade"] <= 0).any() or (dados["preco_unitario"] < 0).any():
        raise ValueError("Quantidade deve ser positiva e preço unitário não pode ser negativo.")

    # A fonte limpa já contém valor_venda. Conferimos esse campo com a
    # multiplicação independente e exportamos o valor recalculado pelo pandas.
    valores_calculados = dados["quantidade"] * dados["preco_unitario"]
    if not np.isclose(
        dados["valor_venda"].to_numpy(dtype=float),
        valores_calculados.to_numpy(dtype=float),
        rtol=0,
        atol=0.005,
    ).all():
        raise ValueError("Há divergência entre valor_venda e quantidade × preco_unitario.")

    exportar = dados[COLUNAS_OBRIGATORIAS].copy()
    exportar["data"] = datas.dt.strftime("%Y-%m-%d")
    exportar["quantidade"] = exportar["quantidade"].astype("int64")
    exportar["preco_unitario"] = exportar["preco_unitario"].astype(float)
    exportar["valor_venda"] = valores_calculados.round(2).astype(float)

    return {
        "fonte": "papelaria_limpa.csv",
        "definicao_venda": "Uma linha válida da fonte corresponde a uma venda.",
        "quantidade_vendas": int(len(exportar)),
        "total_vendido": round(float(exportar["valor_venda"].sum()), 2),
        "vendas": exportar.to_dict(orient="records"),
    }


def main() -> None:
    pacote = preparar_dados()
    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)
    ARQUIVO_SAIDA.write_text(
        json.dumps(pacote, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    total_pt_br = f"{pacote['total_vendido']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    print(f"Fonte conferida: {ARQUIVO_FONTE}")
    print(f"Vendas: {pacote['quantidade_vendas']}")
    print(f"Total vendido recalculado: R$ {total_pt_br}")
    print(f"Dados estáticos gerados: {ARQUIVO_SAIDA}")


if __name__ == "__main__":
    main()
