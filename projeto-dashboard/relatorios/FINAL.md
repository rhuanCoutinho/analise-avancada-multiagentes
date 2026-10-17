# Relatório final — dashboard da papelaria

## Status conjunto: **APROVADO**

Construtor, Tester e Revisor aprovaram a mesma versão. O CSV `papelaria_limpa.csv` foi preservado. A implementação final entrega preparo reproduzível em Python/pandas e um site estático responsivo com três indicadores, gráficos por categoria e cidade, tabela e filtros sincronizados.

## Versão aprovada

Sem commit. SHA-256 dos arquivos relevantes:

| Arquivo | SHA-256 |
|---|---|
| `papelaria_limpa.csv` | `04f66503149bfac2b9a61b2e9d284a6d0f8c87b48d72aebf8d7acc36a7a1a562` |
| `projeto-dashboard/preparar_dados.py` | `a2ff92c3401180723cad4516997ff1af831250052f79413e9aa060581183232b` |
| `projeto-dashboard/README.md` | `8820d18db6fddcc3c1b0ef94b8dfd10a16e44404443a6a8fc0678eb42cb9c84b` |
| `projeto-dashboard/site/index.html` | `a0948e8a0298de3e90f4978e9384716bb83ec03b3d68641636d219e9fd187cc5` |
| `projeto-dashboard/site/styles.css` | `77b5cce1409bd2e36b68e53472812476b67ec4b8e25321ebed65672e64f84276` |
| `projeto-dashboard/site/app.js` | `fc617010cd8062af4251fcd27e07d4615f104e688b49f2ab495307241677fece` |
| `projeto-dashboard/site/data/vendas.json` | `7bc4fb2a36cd16bc083faea1f3f368a06352331baf915ea4e4881c39d7e0240a` |
| `projeto-dashboard/tests/test_dashboard.py` | `7a0b775f40225e28b26a395d614a4abbdb7b14b5e29082484531b6912bd47fb0` |

## Verificações e resultados

- Preparação dos dados concluída: **180 vendas**, total bruto de **R$ 20.059,00**. A definição de venda é uma linha válida; valor vendido não é lucro.
- Suíte executada pelo Tester: **8 testes passaram, 0 falharam, 0 ignorados**. Incluiu recálculo independente com `Decimal`, mini-exemplo conhecido, preservação do CSV, HTTP e recursos, JavaScript, navegador real, filtros, estado vazio, limpar filtros, responsividade e teclado.
- O Revisor recalculou os resultados e conferiu a limpeza desde o CSV original; também executou a suíte: **8 passaram, 0 falharam, 0 ignorados**.
- O problema anterior de requisição 404 de favicon foi corrigido e aprovado no reteste.
- Relatórios dos papéis e evidências: `relatorios/rodada-01/construtor.md`, `tester.md` e `revisor.md`.
- Os arquivos de skills solicitados em `.agents/skills/` não existem neste workspace; a ausência foi registrada pelos agentes. Não há verificação pendente.

## Como abrir

Na pasta raiz do workspace, PowerShell:

```powershell
& .\.venv\Scripts\python.exe .\projeto-dashboard\preparar_dados.py
py -m http.server 8000 --directory .\projeto-dashboard\site
```

Abra `http://localhost:8000`. Para hospedagem estática, publique o conteúdo de `projeto-dashboard/site/`. O passo a passo de testes e execução também está em `projeto-dashboard/README.md`.
