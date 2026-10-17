# Tester — rodada 01

## Versão examinada

Sem commit. SHA-256 do produto examinado (iguais aos hashes entregues pelo Construtor):

| Arquivo | SHA-256 |
|---|---|
| `papelaria_limpa.csv` | `04f66503149bfac2b9a61b2e9d284a6d0f8c87b48d72aebf8d7acc36a7a1a562` |
| `projeto-dashboard/preparar_dados.py` | `a2ff92c3401180723cad4516997ff1af831250052f79413e9aa060581183232b` |
| `projeto-dashboard/README.md` | `b9d1eb968c2afd6846d7b6e600edd6b3d93adc659279798497eeaac460266dd2` |
| `projeto-dashboard/site/index.html` | `f0fb2b409a9f6b8421a45bb64805555037d03c3e0afd47b309611effb39c6188` |
| `projeto-dashboard/site/styles.css` | `77b5cce1409bd2e36b68e53472812476b67ec4b8e25321ebed65672e64f84276` |
| `projeto-dashboard/site/app.js` | `fc617010cd8062af4251fcd27e07d4615f104e688b49f2ab495307241677fece` |
| `projeto-dashboard/site/data/vendas.json` | `7bc4fb2a36cd16bc083faea1f3f368a06352331baf915ea4e4881c39d7e0240a` |
| `projeto-dashboard/tests/test_dashboard.py` | `7a0b775f40225e28b26a395d614a4abbdb7b14b5e29082484531b6912bd47fb0` |

## O que foi conferido

- Implementada suíte independente em `projeto-dashboard/tests/test_dashboard.py`; nenhum arquivo do produto foi editado. O CSV foi comparado byte a byte antes/depois da suíte (SHA-256 acima).
- Dados: 180 linhas preservadas em ordem, colunas obrigatórias, valores não ausentes, datas e tipos, IDs sem duplicatas, valores calculados e consistência CSV–JSON. Não há eliminação silenciosa de linhas.
- Agregações refeitas independentemente com `csv` e `Decimal`, além de mini-caso conhecido. Resultado conferido: total `R$ 20.059,00`; categorias Acessórios `R$ 10.517,00`, Livros `R$ 7.438,00`, Papelaria `R$ 2.104,00`; cidades Campinas `R$ 8.578,00`, Santos `R$ 6.937,50`, Sorocaba `R$ 4.543,50`.
- Dashboard em Chrome real: indicadores, agrupamentos dos dois gráficos, linhas/valores da tabela, filtros isolados de cidade e categoria, combinação, estado vazio e reset; verificados ausência de `NaN`/`Infinity` e atualização de foco após reset.
- HTTP local: HTML, CSS, JS e JSON carregados; verificados status 200 para recursos declarados. `node --check` validou a sintaxe JavaScript.
- Responsividade checada em viewports de 1440×900, 390×844 e 320×720; sem overflow horizontal da página, filtros com alvos utilizáveis, rótulos legíveis e tabela rolável. Teclado: tabulação, foco visível, seleção de filtro por seta e ativação do reset com Enter.

## Comandos e evidências

Executado na raiz do workspace, Windows/PowerShell:

```powershell
& .\.venv\Scripts\python.exe -m unittest discover -s .\projeto-dashboard\tests -v
```

Ambiente: Python `3.14.7` (`.venv`), Node `v24.21.0`, Chrome/Chromium headless acessível por Chrome DevTools Protocol. O teste inicia servidor HTTP local temporário; perfil e processos temporários são encerrados pela suíte. Evidência: saída do comando, **8 testes: 7 passaram, 1 falhou**. Os recursos estáticos essenciais retornaram 200; falha reproduzida pelo próprio navegador descrita abaixo.

## Problemas e encaminhamento

- **Construtor — falha:** em carregamento HTTP, o navegador requisita implicitamente `http://127.0.0.1:<porta>/favicon.ico` e recebe **404 File not found**, registrado como erro de rede no console Chrome. Reproduzível em `test_browser_console_and_requested_resources_have_no_errors`. O pedido de teste exige ausência de recursos ausentes/erros no navegador; disponibilizar o favicon ou evitar a requisição e devolver ao Tester para reteste.
- Não foram encontradas divergências nos dados, KPIs, gráficos, tabela, filtros, interação por teclado ou viewports testados.
- A suíte deliberadamente **não** executa `preparar_dados.py`, pois o comando sobrescreveria `site/data/vendas.json` do produto; a validação foi somente de leitura contra CSV e JSON entregues.
- Os arquivos `.agents/skills/{explore-data,data-visualization,validate-data}/SKILL.md` não foram encontrados conforme limitação informada; o Tester não os declara lidos/utilizados.

## Status: **REPROVADO**

O defeito do recurso `/favicon.ico` impede aprovação nesta versão. Depois da correção pelo Construtor, executar novamente a suíte integral e atualizar o relatório em nova rodada, preservando este histórico.

---

## Auditoria e preparação do reteste — snapshot após correção do Construtor

Esta seção complementa o resultado histórico acima. O defeito do favicon foi corrigido pelo Construtor, mas **não foi retestado nesta etapa**. O Construtor ainda está trabalhando nos arquivos do produto; conforme solicitado, não executei a suíte nem naveguei o dashboard. O resultado anterior de 7 aprovados e 1 falho pertence à versão sem a correção, não é evidência da versão atual.

### Versão auditada (sem execução)

Sem commit. SHA-256 observado neste snapshot:

| Arquivo | SHA-256 |
|---|---|
| `papelaria_limpa.csv` | `04f66503149bfac2b9a61b2e9d284a6d0f8c87b48d72aebf8d7acc36a7a1a562` |
| `projeto-dashboard/tests/test_dashboard.py` | `7a0b775f40225e28b26a395d614a4abbdb7b14b5e29082484531b6912bd47fb0` |
| `projeto-dashboard/preparar_dados.py` | `a2ff92c3401180723cad4516997ff1af831250052f79413e9aa060581183232b` |
| `projeto-dashboard/site/index.html` | `a0948e8a0298de3e90f4978e9384716bb83ec03b3d68641636d219e9fd187cc5` |
| `projeto-dashboard/site/styles.css` | `77b5cce1409bd2e36b68e53472812476b67ec4b8e25321ebed65672e64f84276` |
| `projeto-dashboard/site/app.js` | `fc617010cd8062af4251fcd27e07d4615f104e688b49f2ab495307241677fece` |
| `projeto-dashboard/site/data/vendas.json` | `7bc4fb2a36cd16bc083faea1f3f368a06352331baf915ea4e4881c39d7e0240a` |
| `projeto-dashboard/README.md` | `b9d1eb968c2afd6846d7b6e600edd6b3d93adc659279798497eeaac460266dd2` |

### Auditoria de cobertura e decisão sobre mudanças

Li o `AGENTS.md`, o CSV selecionado e a suíte/produto atuais. A suíte já cobre os critérios obrigatórios; **não alterei `tests/test_dashboard.py`**, pois não encontrei lacuna que justificasse acrescentar ou modificar testes sem executar a versão em construção:

- Fonte original: hash antes/depois da classe de dados, colunas obrigatórias, 180 linhas, ausência de campos vazios, IDs únicos e na mesma ordem no JSON, datas, tipos numéricos, finitude e consistência quantidade × preço; valida também a definição documentada de linha/venda.
- Cálculos: agregação independente com `Decimal`, mini-oráculo manual, total e somas por cidade/categoria, comparação da fonte com JSON e dos metadados do payload.
- Página e recursos: contrato de IDs/labels, HTML em português, recursos locais via HTTP, JSON, verificação sintática Node quando disponível e erros/recursos ausentes no console do navegador.
- Interação real: indicadores, ambos os gráficos e tabela comparados com recálculo independente; filtro de cidade, de categoria, combinação, seleção artificial vazia, botão limpar, retorno do foco e ausência visível de `NaN`/`Infinity`.
- Interface: Chrome/Edge headless via CDP, viewports 1440, 390 e 320 px, overflow, dimensões dos filtros, rótulos, rolagem da tabela, tabulação, foco visível, seleção por seta e ativação de limpar por Enter.

Os testes de navegador ficam explicitamente pendentes caso o navegador não esteja disponível quando a suíte for executada; a suíte registra esse caso como skip/bloqueio, não como aprovação. A execução final deve usar o comando documentado no README, registrar a saída integral e confirmar os hashes da versão estável antes de atribuir resultado.

### Execução, pendências e encaminhamento

- Comando da suíte: **não executado**, para evitar testar enquanto o Construtor altera o produto. Evidência desta etapa: auditoria estática dos arquivos e hashes acima; não há evidência nova de execução.
- Dados, HTTP, JavaScript em runtime, filtros, navegador, responsividade e teclado nesta versão: **PENDENTES**.
- Nenhuma alteração no produto ou no arquivo de testes foi feita. Quando o Construtor sinalizar a versão estável, executar a suíte integral; retornar qualquer falha de produto ao Construtor e qualquer bloqueio de ambiente ao coordenador.

## Status desta etapa: **BLOQUEADO — reteste integral PENDENTE**

Não é aprovação da versão corrigida. O resultado histórico **REPROVADO** acima permanece registrado para a versão anterior; este snapshot ainda precisa de execução completa.

---

## Reteste integral da versão estável corrigida

### Versão executada

Sem commit. Hashes verificados antes e depois da suíte; não houve alteração entre as verificações:

| Arquivo | SHA-256 |
|---|---|
| `papelaria_limpa.csv` | `04f66503149bfac2b9a61b2e9d284a6d0f8c87b48d72aebf8d7acc36a7a1a562` |
| `projeto-dashboard/tests/test_dashboard.py` | `7a0b775f40225e28b26a395d614a4abbdb7b14b5e29082484531b6912bd47fb0` |
| `projeto-dashboard/preparar_dados.py` | `a2ff92c3401180723cad4516997ff1af831250052f79413e9aa060581183232b` |
| `projeto-dashboard/README.md` | `8820d18db6fddcc3c1b0ef94b8dfd10a16e44404443a6a8fc0678eb42cb9c84b` |
| `projeto-dashboard/site/index.html` | `a0948e8a0298de3e90f4978e9384716bb83ec03b3d68641636d219e9fd187cc5` |
| `projeto-dashboard/site/styles.css` | `77b5cce1409bd2e36b68e53472812476b67ec4b8e25321ebed65672e64f84276` |
| `projeto-dashboard/site/app.js` | `fc617010cd8062af4251fcd27e07d4615f104e688b49f2ab495307241677fece` |
| `projeto-dashboard/site/data/vendas.json` | `7bc4fb2a36cd16bc083faea1f3f368a06352331baf915ea4e4881c39d7e0240a` |
| `projeto-dashboard/site/favicon.svg` | `baf2f76d2fce8ead5fb6db7d64a84e235dce199435a8fcda54edcf8064b0af4a` |
| `projeto-dashboard/site/favicon.ico` | `5322358f862b59ca76577635fff96db88fdf00b524a4f539449596d96568a2a9` |

### Comando e saída integral

Executado na raiz do workspace, PowerShell, exatamente como documentado no README:

```powershell
& .\.venv\Scripts\python.exe -m unittest discover -s .\projeto-dashboard\tests -v
```

Saída:

```text
test_known_miniature_oracle_and_independent_aggregations (test_dashboard.TestIndependentData.test_known_miniature_oracle_and_independent_aggregations) ... ok
test_original_is_still_byte_identical_at_end_of_data_checks (test_dashboard.TestIndependentData.test_original_is_still_byte_identical_at_end_of_data_checks) ... ok
test_original_schema_values_types_missing_and_duplicates (test_dashboard.TestIndependentData.test_original_schema_values_types_missing_and_duplicates) ... ok
test_browser_console_and_requested_resources_have_no_errors (test_dashboard.TestRealBrowser.test_browser_console_and_requested_resources_have_no_errors) ... ok
test_http_javascript_runtime_responsive_viewports_and_keyboard (test_dashboard.TestRealBrowser.test_http_javascript_runtime_responsive_viewports_and_keyboard) ... ok
test_live_dashboard_filters_empty_reset_and_values (test_dashboard.TestRealBrowser.test_live_dashboard_filters_empty_reset_and_values) ... ok
test_html_contract_assets_and_local_http_resources (test_dashboard.TestStaticSiteAndHTTP.test_html_contract_assets_and_local_http_resources) ... ok
test_javascript_syntax_with_node (test_dashboard.TestStaticSiteAndHTTP.test_javascript_syntax_with_node) ... ok

----------------------------------------------------------------------
Ran 8 tests in 5.232s

OK
```

### Resultados

- **8 testes passaram, 0 falharam, 0 foram ignorados**, em 5,232 s. Os três testes de navegador real foram executados (sem skip), cobrindo Chrome/Chromium headless via DevTools Protocol.
- Fonte original: preservação por SHA-256, colunas, linhas, valores ausentes, IDs/duplicatas, ordem, datas, tipos, finitude e cálculo quantidade × preço conferidos.
- Cálculos: agregações independentes com `Decimal`, mini-oráculo conhecido, total e agrupamentos por cidade/categoria conferidos contra a fonte e o JSON.
- Dashboard: três indicadores, gráficos, tabela, formatação e contagem correspondem aos dados calculados; filtros de cidade e categoria isolados, combinados, estado vazio e limpar foram exercitados. Confirmados estado vazio/mensagem, retorno do foco e ausência visível de `NaN`/`Infinity`.
- HTTP/site: página, CSS, JS, JSON e recursos estáticos locais retornaram sucesso; favicon corrigido; sintaxe JavaScript aprovada pelo Node; console sem erros ou recursos ausentes.
- Interface: interação em navegador real; viewports 1440×900, 390×844 e 320×720 sem overflow horizontal, filtros utilizáveis, rótulos legíveis e tabela rolável. Teclado confirmou tabulação, foco visível, seleção de filtro por seta e ativação do botão limpar por Enter.
- Arquivos do produto não foram alterados pelo Tester. Os hashes antes/depois da execução coincidem.

Problemas encontrados: nenhum. Encaminhamento: seguir para revisão independente; esta aprovação é somente do Tester para os hashes listados e não substitui o parecer do Revisor nem a aprovação conjunta do coordenador.

## Status do Tester após reteste: **APROVADO**
