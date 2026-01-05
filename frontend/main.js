let limitups = [];
let currentSort = { key: 'fd_amount', asc: false };
let chart, candleSeries, volumeSeries;

async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error('请求失败');
  return res.json();
}

function renderKPIs(data) {
  const s = data.sentiment || {};
  const kpis = [
    { label: '涨停家数', value: s.total_limitups || 0 },
    { label: '连板家数', value: s.consecutive_count || 0 },
    { label: '最高板', value: s.highest_consecutive || '-' },
    { label: '炸板率', value: (s.open_fail_rate || 0) + '%' },
    { label: '晋级率', value: s.progress_rate != null ? s.progress_rate + '%' : '待刷新' },
    { label: '断板率', value: s.break_rate != null ? s.break_rate + '%' : '待刷新' },
  ];
  const html = kpis.map(k => `<div class="kpi"><div class="label">${k.label}</div><div class="value">${k.value}</div></div>`).join('');
  document.getElementById('kpiContainer').innerHTML = html;
}

function renderThemes(data) {
  const list = data.themes || [];
  const html = list.map(t => `<li><span>${t.name}</span><span>${t.count}家 / 分数 ${t.score}</span></li>`).join('');
  document.getElementById('themeList').innerHTML = html || '<li>暂无数据</li>';
}

function formatNumber(n) { return n ? (n / 10000).toFixed(2) : '-'; }

function renderTable(data) {
  const tbody = document.querySelector('#limitTable tbody');
  tbody.innerHTML = '';
  data.forEach(item => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${item.ts_code}</td>
      <td>${item.name}</td>
      <td>${(item.pct_chg || 0).toFixed(2)}</td>
      <td>${item.consecutive || 1}</td>
      <td>${formatNumber(item.fd_amount)}</td>
      <td>${formatNumber(item.amount)}</td>
      <td>${item.first_time || '-'}</td>
      <td>${item.last_time || '-'}</td>
      <td>${item.open_times || 0}</td>
      <td>${item.industry || ''}<br/><span class="badge">${item.reason || ''}</span></td>
      <td>${item.lhb_flag ? '<span class="badge">是</span>' : '否'}</td>
      <td>${item.hot_money_flag ? '<span class="badge hot">游资</span>' : '否'}</td>
    `;
    tr.addEventListener('click', () => loadDetail(item.ts_code, item.name));
    tbody.appendChild(tr);
  });
}

function applyFilters() {
  const keyword = document.getElementById('searchInput').value.trim();
  const cons = document.getElementById('consecutiveFilter').value;
  const hot = document.getElementById('hotMoneyFilter').value;
  let data = [...limitups];
  if (keyword) {
    data = data.filter(i => (i.ts_code && i.ts_code.includes(keyword)) || (i.name && i.name.includes(keyword)) || (i.reason && i.reason.includes(keyword)));
  }
  if (cons) {
    const n = Number(cons);
    data = data.filter(i => (i.consecutive || 1) >= n);
  }
  if (hot === 'hot') {
    data = data.filter(i => i.hot_money_flag);
  } else if (hot === 'lhb') {
    data = data.filter(i => i.lhb_flag);
  }
  data.sort((a, b) => {
    const key = currentSort.key;
    const va = a[key] || 0;
    const vb = b[key] || 0;
    return currentSort.asc ? va - vb : vb - va;
  });
  renderTable(data);
}

async function loadData() {
  const date = document.getElementById('dateInput').value || 'auto';
  const data = await fetchJSON(`/api/limitups?date=${date}`);
  limitups = data.items || [];
  renderKPIs(data);
  renderThemes(data);
  applyFilters();
}

async function loadDetail(ts_code, name) {
  const date = document.getElementById('dateInput').value || 'auto';
  const data = await fetchJSON(`/api/stock/${ts_code}?date=${date}`);
  const info = data.info;
  const lhb = data.lhb || [];
  const holder = document.getElementById('detailInfo');
  const lhbHtml = lhb.length ? lhb.map(i => `<div><strong>${i.reason}</strong> 买${formatNumber(i.buy)} 卖${formatNumber(i.sell)} 净${formatNumber(i.net)}</div>`).join('') : '<div>龙虎榜：暂无或权限不足</div>';
  holder.innerHTML = `
    <div><strong>${info.name}</strong> (${info.ts_code})</div>
    <div>行业：${info.industry || '-'} | 概念：${info.reason || '-'}</div>
    <div>封板：${info.first_time || '-'} / 最后：${info.last_time || '-'} | 炸板：${info.open_times || 0}</div>
    <div>封单：${formatNumber(info.fd_amount)}万 | 成交：${formatNumber(info.amount)}万</div>
    <div>连板：${info.consecutive || 1}</div>
    ${lhbHtml}
  `;
  document.getElementById('detailTitle').innerText = `${name} 详情`;
  drawChart(data.kline || []);
}

function drawChart(bars) {
  const container = document.getElementById('chart');
  if (!chart) {
    chart = LightweightCharts.createChart(container, { height: container.clientHeight, layout: { textColor: '#333', background: { color: '#fff' } } });
    candleSeries = chart.addCandlestickSeries();
    volumeSeries = chart.addHistogramSeries({ priceFormat: { type: 'volume' }, priceScaleId: '' });
    volumeSeries.priceScale().setScaleMargins({ top: 0.8, bottom: 0 });
  }
  const candles = bars.map(b => ({ time: b.trade_date, open: b.open, high: b.high, low: b.low, close: b.close }));
  const vols = bars.map(b => ({ time: b.trade_date, value: b.vol, color: '#4b7bec' }));
  candleSeries.setData(candles);
  volumeSeries.setData(vols);
  chart.timeScale().fitContent();
}

function bindEvents() {
  document.getElementById('searchInput').addEventListener('input', applyFilters);
  document.getElementById('consecutiveFilter').addEventListener('change', applyFilters);
  document.getElementById('hotMoneyFilter').addEventListener('change', applyFilters);
  document.getElementById('refreshBtn').addEventListener('click', () => loadData().catch(alert));
  document.querySelectorAll('#limitTable th[data-sort]').forEach(th => {
    th.addEventListener('click', () => {
      const key = th.dataset.sort;
      if (currentSort.key === key) {
        currentSort.asc = !currentSort.asc;
      } else {
        currentSort.key = key;
        currentSort.asc = false;
      }
      applyFilters();
    });
  });
}

bindEvents();
loadData().catch(err => alert('加载失败: ' + err.message));
