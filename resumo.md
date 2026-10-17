# Análise e tratamento de `vendas_papelaria.csv`

## Perfil do arquivo original

- **Linhas de dados:** 182 (183 linhas contando o cabeçalho).
- **Colunas:** 8 — `id_venda`, `data`, `cidade`, `categoria`, `produto`, `quantidade`, `preco_unitario` e `forma_pagamento`.
- **Granularidade informada:** uma linha por venda; `id_venda` identifica a venda.
- **Período coberto:** 2026-01-01 a 2026-03-31.

## Problemas encontrados

- **2 linhas duplicadas exatas**, correspondentes às vendas `V0010` e `V0020`. Havia 180 IDs distintos entre 182 linhas.
- **6 cidades com espaços nas bordas** do texto.
- **3 categorias** estavam grafadas como `acessórios` em minúsculas, além das categorias padronizadas.
- **4 valores de forma_pagamento vazios**.
- Não foram encontrados valores vazios nas outras colunas, quantidades/preços negativos ou iguais a zero, nem outros IDs repetidos além das duas vendas duplicadas.

## Tratamento aplicado na cópia

O arquivo original foi preservado. Em `papelaria_limpa.csv`:

1. Removi somente as 2 linhas exatamente repetidas (comparação de todos os campos), mantendo uma ocorrência de cada venda.
2. Retirei espaços no início/fim dos valores de `cidade`.
3. Padronizei a grafia e capitalização de `categoria` para `Livros`, `Papelaria` e `Acessórios`.
4. Substituí valores vazios de `forma_pagamento` por `Não informado`.
5. Acrescentei `valor_venda`, calculado como `quantidade * preco_unitario`.

O resultado tem **180 linhas de dados** e **9 colunas**. A soma de `valor_venda` na cópia limpa é **20.059,00**; a média por venda é **111,44**.

## Execução

Cálculos feitos localmente com `.venv/Scripts/python.exe`, lendo apenas o CSV local. Nenhuma integração com banco de dados foi usada.
