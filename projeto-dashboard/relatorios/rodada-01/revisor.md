# Revisor — rodada 01

## Versão examinada

Sem commit. Hashes SHA-256 conferidos nesta revisão:

| Arquivo | SHA-256 |
|---|---|
| `vendas_papelaria.csv` (original) | `bf95b7609e30eb7e3e6a30cfc16e43d9fb5bdfc48a410e49148cceb92e2494ff` |
| `papelaria_limpa.csv` (fonte escolhida) | `04f66503149bfac2b9a61b2e9d284a6d0f8c87b48d72aebf8d7acc36a7a1a562` |
| `projeto-dashboard/preparar_dados.py` | `a2ff92c3401180723cad4516997ff1af831250052f79413e9aa060581183232b` |
| `projeto-dashboard/README.md` | `8820d18db6fddcc3c1b0ef94b8dfd10a16e44404443a6a8fc0678eb42cb9c84b` |
| `projeto-dashboard/site/index.html` | `a0948e8a0298de3e90f4978e9384716bb83ec03b3d68641636d219e9fd187cc5` |
| `projeto-dashboard/site/styles.css` | `77b5cce1409bd2e36b68e53472812476b67ec4b8e25321ebed65672e64f84276` |
| `projeto-dashboard/site/app.js` | `fc617010cd8062af4251fcd27e07d4615f104e688b49f2ab495307241677fece` |
| `projeto-dashboard/site/data/vendas.json` | `7bc4fb2a36cd16bc083faea1f3f368a06352331baf915ea4e4881c39d7e0240a` |
| `projeto-dashboard/tests/test_dashboard.py` | `7a0b775f40225e28b26a395d614a4abbdb7b14b5e29082484531b6912bd47fb0` |

Os hashes do produto correspondem à versão corrigida submetida à suíte final do Tester. As duas fontes CSV estão presentes; o hash de `papelaria_limpa.csv` também coincide com o registrado pelo Construtor e Tester.

## O que examinei e recálculo independente

Examinei `resumo.md`, `verificacao.md`, ambas as fontes CSV, o preparador, JSON, HTML, CSS, JavaScript, README, suíte e os relatórios do Construtor e Tester. Conferi a implementação e não me limitei aos resultados registrados por eles.

- Recriei com Python padrão (`csv`, `Decimal` e `Counter`) a limpeza documentada desde `vendas_papelaria.csv`: 182 linhas; descarte de apenas duas duplicatas de linha integral (`V0010`, `V0020`); aparo de espaços em cidade; padronização de categoria e pagamento vazio; cálculo de quantidade × preço. A reconstrução independente corresponde a todas as 180 linhas de `papelaria_limpa.csv`, sem divergência.
- Recalculei os valores a partir de quantidade × preço, sem usar `valor_venda` como base do cálculo. Resultado: 548 unidades, 180 vendas/linhas, total bruto de **R$ 20.059,00** e média por venda de **R$ 111,44**.
- Agregações independentes: categorias Acessórios **R$ 10.517,00**, Livros **R$ 7.438,00**, Papelaria **R$ 2.104,00**; cidades Campinas **R$ 8.578,00**, Santos **R$ 6.937,50**, Sorocaba **R$ 4.543,50**. Os agrupamentos somam o total geral. JSON: 180 registros; total recalculado independentemente também **R$ 20.059,00**.
- A definição de venda é coerente: uma linha válida equivale a uma venda; `quantidade` mede unidades, não vendas. Indicadores usam total, contagem de linhas filtradas e total/contagem. README e rodapé distinguem expressamente valor bruto de lucro e registram que custos e despesas não estão na base.
- Os dois filtros usam colunas existentes (`cidade`, `categoria`); o código recalcula KPIs, gráficos e tabela a partir do mesmo conjunto filtrado. O estado sem resultados mostra mensagens nos gráficos e tabela, mantém indicadores numéricos finitos e evita divisão por zero. O botão limpar também devolve foco ao primeiro filtro.
- Acessibilidade/responsividade: HTML tem idioma pt-BR, labels associados aos selects, link de pular conteúdo e foco visível; tabela pode rolar horizontalmente. A suíte exercita teclado e tamanhos desktop/celular. Não fiz auditoria especializada com leitor de tela.
- README traz comandos para preparar dados, testar e iniciar HTTP local, e identifica `site/` como raiz publicável. Não encontrei problema metodológico ou conceitual que exija retorno ao Construtor, nem lacuna obrigatória que exija retorno ao Tester.

## Comandos executados e evidências

Na raiz do workspace, PowerShell:

```powershell
Get-FileHash -Algorithm SHA256 .\papelaria_limpa.csv, .\vendas_papelaria.csv, .\projeto-dashboard\preparar_dados.py, .\projeto-dashboard\README.md, .\projeto-dashboard\site\index.html, .\projeto-dashboard\site\styles.css, .\projeto-dashboard\site\app.js, .\projeto-dashboard\site\data\vendas.json, .\projeto-dashboard\site\favicon.svg, .\projeto-dashboard\site\favicon.ico, .\projeto-dashboard\tests\test_dashboard.py
& .\.venv\Scripts\python.exe -m unittest discover -s .\projeto-dashboard\tests -v
```

Também executei um script independente enviado por here-string ao `.venv\Scripts\python.exe -`, usando `csv`, `Decimal`, `Counter` e JSON, lendo as duas fontes e o JSON; não escrevi nem alterei arquivos do produto. Resultados: reconstrução da limpeza **coincidente**; totais e agrupamentos acima; teste integral **8 passaram, 0 falharam, 0 ignorados**, em 4,656 s. A saída integral do teste confirmou os casos de dados, mini-oráculo Decimal, HTTP, sintaxe JavaScript e três testes com Chrome/Chromium real (console/recursos, filtros/estado vazio e responsividade/teclado). Evidência reproduzível: saída dos comandos; suíte em `projeto-dashboard/tests/test_dashboard.py`. A suíte verifica ainda que `papelaria_limpa.csv` permanece com o mesmo SHA-256 antes/depois.

As skills foram consultadas via harness conforme informado para esta revisão; o diretório local `.agents/skills/` e os respectivos `SKILL.md` não existem neste workspace. Não afirmo ter lido cópias locais.

## Problemas e encaminhamento

Nenhum problema encontrado nesta versão. Nenhum encaminhamento necessário ao Construtor ou Tester. A limitação da ausência dos arquivos locais de skills fica registrada acima; não bloqueia a revisão dos cálculos e critérios verificáveis.

## Status: **APROVADO**

Parecer restrito aos hashes listados. Cálculos, metodologia documentada, conceitos, cobertura e evidências da suíte foram conferidos; não há teste obrigatório pendente nesta revisão.
