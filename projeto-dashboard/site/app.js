(() => {
  'use strict';

  const currency = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' });
  const integer = new Intl.NumberFormat('pt-BR');
  const dateFormat = new Intl.DateTimeFormat('pt-BR', { timeZone: 'UTC' });
  const citySelect = document.querySelector('#filter-city');
  const categorySelect = document.querySelector('#filter-category');
  const clearButton = document.querySelector('#clear-filters');
  const errorBox = document.querySelector('#load-error');
  const tableBody = document.querySelector('#sales-table-body');
  let sales = [];

  const formatDate = (value) => {
    const [year, month, day] = value.split('-').map(Number);
    return dateFormat.format(new Date(Date.UTC(year, month - 1, day)));
  };

  function populateFilter(select, values, placeholder) {
    select.replaceChildren(new Option(placeholder, ''));
    [...new Set(values)].sort((a, b) => a.localeCompare(b, 'pt-BR')).forEach((value) => {
      select.add(new Option(value, value));
    });
  }

  function drawBars(container, groups, emptyMessage) {
    container.replaceChildren();
    if (!groups.length) {
      const message = document.createElement('p');
      message.className = 'chart-empty';
      message.textContent = emptyMessage;
      container.append(message);
      return;
    }
    const largest = Math.max(...groups.map((group) => group.total), 0);
    groups.forEach((group) => {
      const row = document.createElement('div');
      row.className = 'bar-row';
      const label = document.createElement('span');
      label.className = 'bar-label';
      label.textContent = group.name;
      const track = document.createElement('span');
      track.className = 'bar-track';
      track.setAttribute('aria-hidden', 'true');
      const fill = document.createElement('span');
      fill.className = 'bar-fill';
      fill.style.width = `${largest > 0 ? (group.total / largest) * 100 : 0}%`;
      track.append(fill);
      const value = document.createElement('span');
      value.className = 'bar-value';
      value.textContent = currency.format(group.total);
      row.append(label, track, value);
      container.append(row);
    });
  }

  function groupBy(rows, key) {
    const totals = new Map();
    rows.forEach((sale) => totals.set(sale[key], (totals.get(sale[key]) || 0) + sale.valor_venda));
    return [...totals.entries()]
      .map(([name, total]) => ({ name, total }))
      .sort((a, b) => b.total - a.total || a.name.localeCompare(b.name, 'pt-BR'));
  }

  function renderTable(rows) {
    tableBody.replaceChildren();
    if (!rows.length) {
      const tr = document.createElement('tr');
      const td = document.createElement('td');
      td.colSpan = 8;
      td.className = 'table-message';
      td.textContent = 'Nenhuma venda encontrada. Altere ou limpe os filtros para ver resultados.';
      tr.append(td);
      tableBody.append(tr);
      return;
    }
    const fragment = document.createDocumentFragment();
    rows.forEach((sale) => {
      const tr = document.createElement('tr');
      const cells = [
        sale.id_venda,
        formatDate(sale.data),
        sale.cidade,
        sale.categoria,
        sale.produto,
        integer.format(sale.quantidade),
        currency.format(sale.preco_unitario),
        currency.format(sale.valor_venda),
      ];
      cells.forEach((text, index) => {
        const td = document.createElement('td');
        td.textContent = text;
        if (index >= 5) td.className = 'numeric';
        tr.append(td);
      });
      fragment.append(tr);
    });
    tableBody.append(fragment);
  }

  function render() {
    const city = citySelect.value;
    const category = categorySelect.value;
    const filtered = sales.filter((sale) => (!city || sale.cidade === city)
      && (!category || sale.categoria === category));
    const total = filtered.reduce((sum, sale) => sum + sale.valor_venda, 0);
    const count = filtered.length;

    document.querySelector('#kpi-total').textContent = currency.format(total);
    document.querySelector('#kpi-count').textContent = integer.format(count);
    document.querySelector('#kpi-average').textContent = currency.format(count ? total / count : 0);
    document.querySelector('#results-count').textContent = `${integer.format(count)} ${count === 1 ? 'venda encontrada' : 'vendas encontradas'}`;
    drawBars(document.querySelector('#category-chart'), groupBy(filtered, 'categoria'), 'Sem vendas para exibir nesta seleção.');
    drawBars(document.querySelector('#city-chart'), groupBy(filtered, 'cidade'), 'Sem vendas para exibir nesta seleção.');
    renderTable(filtered);
  }

  async function init() {
    try {
      const response = await fetch('./data/vendas.json');
      if (!response.ok) throw new Error(`Falha ao carregar os dados (HTTP ${response.status}).`);
      const payload = await response.json();
      if (!Array.isArray(payload.vendas)) throw new Error('O arquivo de dados não contém a lista de vendas esperada.');
      sales = payload.vendas;
      populateFilter(citySelect, sales.map((sale) => sale.cidade), 'Todas as cidades');
      populateFilter(categorySelect, sales.map((sale) => sale.categoria), 'Todas as categorias');
      render();
    } catch (error) {
      errorBox.hidden = false;
      errorBox.textContent = `${error.message} Gere os dados pelo comando do README e abra o site por um servidor HTTP local.`;
      document.querySelector('#results-count').textContent = 'Dados indisponíveis';
      tableBody.replaceChildren();
      const row = document.createElement('tr');
      const cell = document.createElement('td');
      cell.colSpan = 8;
      cell.className = 'table-message';
      cell.textContent = 'Não foi possível carregar as vendas.';
      row.append(cell);
      tableBody.append(row);
    }
  }

  citySelect.addEventListener('change', render);
  categorySelect.addEventListener('change', render);
  clearButton.addEventListener('click', () => {
    citySelect.value = '';
    categorySelect.value = '';
    render();
    citySelect.focus();
  });

  init();
})();
