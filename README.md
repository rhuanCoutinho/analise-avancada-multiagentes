# Análise avançada com múltiplos agentes

Repositório com instruções de fluxo de trabalho, skills de análise de dados e os relatórios/documentação do dashboard de vendas da papelaria.

## Conteúdo

- `AGENTS.md`: critérios e etapas para explorar, preparar, visualizar e validar uma análise.
- `.opencode/skills/`: skills `explore-data`, `data-visualization` e `validate-data`.
- `resumo.md` e `verificacao.md`: resultados e validações da análise anterior.
- `projeto-dashboard/`: código do preparo, testes, site estático e relatórios Markdown por papel e rodada.
- `papelaria_limpa.csv` e `vendas_papelaria.csv`: bases usadas para reproduzir e auditar a análise.

## Reproduzir no Windows

No PowerShell, a partir da pasta do repositório:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe .\projeto-dashboard\preparar_dados.py
.\.venv\Scripts\python.exe -m unittest discover -s .\projeto-dashboard\tests -v
py -m http.server 8000 --directory .\projeto-dashboard\site
```

Abra `http://localhost:8000`. Para os testes completos de interface, instale Node.js e Chrome ou Edge. A pasta publicável para hospedagem estática é `projeto-dashboard/site/`.

## Arquivos ignorados

O `.gitignore` exclui ambientes virtuais, caches, notebooks e gráficos gerados. Os relatórios versionados são Markdown; os dados e o código-fonte necessários para reproduzir o dashboard permanecem no repositório.
