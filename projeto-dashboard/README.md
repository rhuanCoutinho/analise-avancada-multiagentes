# Dashboard de vendas da papelaria

Painel estático feito com HTML, CSS e JavaScript, sem backend, banco de dados ou dependências externas para funcionar. O CSV de entrada é `papelaria_limpa.csv`, na pasta raiz do projeto; ele não é alterado.

## Preparar os dados (PowerShell, na pasta raiz)

```powershell
.\.venv\Scripts\python.exe .\projeto-dashboard\preparar_dados.py
```

O script usa pandas, confere colunas, ausências, IDs, tipos e se `valor_venda` bate com quantidade × preço; exporta `projeto-dashboard/site/data/vendas.json`. A fonte limpa já contém `valor_venda`; a análise valida o campo e usa o valor recalculado. Não remove nem altera linhas.

## Testes

Execute a suíte em `projeto-dashboard/tests/` da pasta raiz:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s .\projeto-dashboard\tests -v
```

## Abrir localmente

Gere os dados antes e, na pasta raiz, inicie um servidor HTTP estático:

```powershell
py -m http.server 8000 --directory .\projeto-dashboard\site
```

Abra `http://localhost:8000` no navegador. Para hospedar como site estático, publique o conteúdo da pasta `projeto-dashboard/site/` (ela é a raiz publicável).

## Base, definições e limitações

- Cada linha de `papelaria_limpa.csv` representa uma venda; `id_venda` identifica a venda. A coluna `quantidade` conta unidades de produto, não vendas.
- A limpeza já foi feita antes deste projeto e está registrada em `resumo.md`: removeram-se somente linhas totalmente idênticas, apararam-se espaços nas cidades, padronizaram-se as categorias e os pagamentos vazios foram marcados como `Não informado`. O CSV original `vendas_papelaria.csv` foi preservado.
- O preparo deste projeto não repete essa limpeza nem descarta linhas. Ele valida a base limpa e interrompe se encontrar campos ausentes, IDs repetidos ou divergência em `valor_venda`.
- `valor_venda` é calculado como `quantidade × preco_unitario`. O valor total vendido é a soma dessa coluna; quantidade de vendas é a contagem de linhas; ticket médio é total vendido dividido por essa contagem (zero quando não há resultados).
- Os gráficos mostram a soma do valor vendido por cidade e categoria. Os dois filtros atualizam juntos os indicadores, os gráficos e a tabela.
- Valor vendido é valor bruto registrado, não lucro. A base não contém custos nem despesas e a conferência é interna aos arquivos fornecidos, sem validação contábil externa.
