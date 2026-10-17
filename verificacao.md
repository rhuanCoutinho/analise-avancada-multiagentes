# Verificação da análise de vendas da papelaria

## Avaliação geral: pronta para compartilhar com ressalva

Os cálculos conferidos são consistentes entre o CSV original, a cópia limpa, o resumo e a lógica de agregação em `graficos.py`. A ressalva necessária é que `valor_venda` representa valor bruto vendido, **não lucro**. A conferência usou somente os arquivos locais e `.venv/Scripts/python.exe`; não foram usados bancos de dados ou fontes externas.

## O que foi verificado

- Li `vendas_papelaria.csv`, `papelaria_limpa.csv`, `resumo.md` e `graficos.py`.
- Recalculei os valores a partir de `quantidade × preco_unitario` na cópia limpa usando aritmética decimal, independentemente do campo `valor_venda` gravado.
- Conferi cada linha limpa contra o `valor_venda` armazenado: **nenhuma divergência**.
- Reconstruí a cópia esperada a partir do original, repetindo somente a remoção de linhas idênticas e as normalizações documentadas; comparei todas as 180 linhas e todos os campos com a cópia limpa: **coincidem**.
- Conferi contagem de linhas, IDs, duplicatas, totais por dimensão, espaços, categorias e pagamentos.
- Inspecionei a origem, a métrica e a agregação usados pelo código dos gráficos.

## Recontagem e recálculo

| Medida | Resultado conferido |
|---|---:|
| Linhas no original | 182 |
| Linhas exatas duplicadas removidas | 2 (`V0010` e `V0020`) |
| Vendas na cópia limpa | 180 |
| IDs distintos na cópia limpa | 180 |
| Soma de `quantidade` (unidades de produto) | 548 |
| Total recalculado de `valor_venda` | **R$ 20.059,00** |

“Quantidade de vendas” foi interpretada como contagem de vendas/linhas após remover duplicatas: **180 vendas**. A soma da coluna `quantidade` é outra medida: **548 unidades de produtos**.

### Total por categoria

| Categoria | Valor vendido recalculado |
|---|---:|
| Acessórios | R$ 10.517,00 |
| Livros | R$ 7.438,00 |
| Papelaria | R$ 2.104,00 |
| **Soma das categorias** | **R$ 20.059,00** |

A soma por categoria coincide com o total geral.

### Total por cidade

| Cidade | Valor vendido recalculado |
|---|---:|
| Campinas | R$ 8.578,00 |
| Santos | R$ 6.937,50 |
| Sorocaba | R$ 4.543,50 |
| **Soma das cidades** | **R$ 20.059,00** |

A soma por cidade também coincide com o total geral.

## Qualidade e consistência dos arquivos

- No original, confirmei 2 linhas exatas repetidas; `V0010` e `V0020` têm duas ocorrências cada.
- Confirmei 6 cidades com espaços nas bordas, 3 categorias grafadas como `acessórios` em minúsculas e 4 pagamentos vazios.
- Na cópia limpa, confirmei 180 IDs únicos, nenhuma cidade com espaços nas bordas, nenhuma forma de pagamento vazia e somente as categorias `Livros`, `Papelaria` e `Acessórios`.
- Não encontrei campos vazios fora de `forma_pagamento`, nem quantidade ou preço unitário zero/negativo no original.
- O número de linhas, as alterações descritas e os totais apresentados em `resumo.md` são compatíveis com a conferência.

## Código e gráficos

`graficos.py` lê `papelaria_limpa.csv`, converte `valor_venda` para numérico e agrupa essa métrica por `categoria` e `cidade` com soma. Portanto, usa a base limpa correta e a métrica adequada aos gráficos de valor vendido. O código define o limite inferior do eixo vertical como zero e rotula o eixo em reais.

## Conclusões revisadas e ressalvas

- Acessórios tem o maior valor vendido entre as categorias; Campinas, entre as cidades. Os valores recalculados sustentam essas comparações descritivas.
- Os totais não informam margem, custo, despesas ou lucro. Não se deve chamar o valor vendido de lucro.
- A verificação é interna aos arquivos fornecidos; não houve confronto com registros contábeis externos.
