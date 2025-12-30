<template>
  <div id="app" class="page">
    <header class="topbar">
      <div class="title-block">
        <h1>涨停雷达面板</h1>
        <p class="subtitle">每日一览 A 股涨停股，快速锁定强势题材与龙头</p>
      </div>
      <div class="badge">实时盘后速览</div>
    </header>

    <section class="guide" :class="{ open: showGuide }">
      <div class="guide-title" @click="toggleGuide">
        <div>
          <p class="eyebrow">使用提示</p>
          <h3>如何快速看盘</h3>
        </div>
        <button class="toggle">{{ showGuide ? '收起' : '展开' }}</button>
      </div>
      <div v-if="showGuide" class="guide-body">
        <ul>
          <li><strong>筛选：</strong>顶栏搜索股票/代码/题材，或按行业、游资席位勾选筛选列表。</li>
          <li><strong>查看详情：</strong>点击表格中的任意股票行，右侧同步展示涨停逻辑、龙虎榜与近十日 K 线。</li>
          <li><strong>连板与游资：</strong>统计卡片实时显示连板高度、知名游资席位数量，便于识别情绪龙头。</li>
        </ul>
        <p class="hint">当前为示例数据，接入实盘接口后即可每日打开即用。</p>
      </div>
    </section>

    <section class="summary-grid">
      <div class="card">
        <p class="label">今日涨停数量</p>
        <p class="value">{{ stocks.length }} 只</p>
        <p class="hint">含主板与科创板标的</p>
      </div>
      <div class="card">
        <p class="label">连板高度</p>
        <p class="value">{{ maxConsecutive }} 连板</p>
        <p class="hint">共 {{ consecutiveCount }} 只连板股</p>
      </div>
      <div class="card">
        <p class="label">游资席位</p>
        <p class="value">{{ hotMoneyCount }} 只</p>
        <p class="hint">龙虎榜出现知名游资</p>
      </div>
      <div class="card">
        <p class="label">今年以来平均涨幅</p>
        <p class="value">{{ averageYtd }}%</p>
        <p class="hint">统计所有涨停股</p>
      </div>
    </section>

    <section class="filter-bar">
      <div class="search-box">
        <input
          v-model="keyword"
          type="text"
          placeholder="按股票/代码/概念搜索"
        >
      </div>
      <div class="filter-group">
        <label>行业：</label>
        <select v-model="industry">
          <option value="">全部</option>
          <option v-for="item in industries" :key="item" :value="item">{{ item }}</option>
        </select>
      </div>
      <div class="filter-group">
        <label class="checkbox">
          <input v-model="onlyHotMoney" type="checkbox">
          <span>只看游资席位</span>
        </label>
      </div>
    </section>

    <section class="layout">
      <div class="table-card">
        <div class="table-header">
          <div>
            <h2>涨停列表</h2>
            <p class="hint">点击查看个股详情与 K 线</p>
          </div>
          <span class="badge info">{{ filteredStocks.length }} / {{ stocks.length }}</span>
        </div>
        <div class="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>股票</th>
                <th>涨幅</th>
                <th>行业</th>
                <th>涨停原因</th>
                <th>连板</th>
                <th>今年涨幅</th>
                <th>游资席位</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="stock in filteredStocks"
                :key="stock.ticker"
                @click="selectStock(stock)"
                :class="{ active: selectedStock && selectedStock.ticker === stock.ticker }"
              >
                <td>
                  <div class="stock-name">
                    <div class="main">{{ stock.name }}</div>
                    <div class="code">{{ stock.ticker }} · {{ stock.board }}</div>
                  </div>
                </td>
                <td><span class="pill gain">+{{ stock.limitChange }}%</span></td>
                <td>{{ stock.industry }}</td>
                <td class="reason">{{ stock.limitReason }}</td>
                <td>
                  <span class="pill" :class="stock.consecutiveCount > 1 ? 'highlight' : 'muted'">
                    {{ stock.consecutiveCount }} 连板
                  </span>
                </td>
                <td>{{ stock.ytdChange }}%</td>
                <td>
                  <span class="pill" :class="stock.hotMoney ? 'alert' : 'muted'">
                    {{ stock.hotMoney ? '有' : '无' }}
                  </span>
                </td>
                <td><button class="link">详情</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="detail-card" v-if="selectedStock">
        <div class="detail-header">
          <div>
            <h2>{{ selectedStock.name }} <span class="code">{{ selectedStock.ticker }}</span></h2>
            <p class="hint">{{ selectedStock.industry }} · {{ selectedStock.board }}</p>
          </div>
          <div class="chips">
            <span class="pill gain">+{{ selectedStock.limitChange }}%</span>
            <span class="pill" :class="selectedStock.consecutiveCount > 1 ? 'highlight' : 'muted'">
              {{ selectedStock.consecutiveCount }} 连板
            </span>
            <span class="pill" :class="selectedStock.hotMoney ? 'alert' : 'muted'">
              {{ selectedStock.hotMoney ? '游资活跃' : '游资未现' }}
            </span>
          </div>
        </div>

        <div class="detail-grid">
          <div class="info-block">
            <p class="label">涨停逻辑</p>
            <p class="value">{{ selectedStock.limitReason }}</p>
            <p class="hint">题材：{{ selectedStock.concepts.join(' / ') }}</p>
          </div>
          <div class="info-block">
            <p class="label">龙虎榜</p>
            <p class="value">{{ selectedStock.hotMoney ? selectedStock.hotDesks : '暂无知名席位' }}</p>
            <p class="hint">成交额 {{ selectedStock.turnover }} · 换手率 {{ selectedStock.turnoverRate }}%</p>
          </div>
          <div class="info-block">
            <p class="label">核心指标</p>
            <ul class="kv-list">
              <li><span>最新价</span><strong>{{ selectedStock.lastPrice }} 元</strong></li>
              <li><span>市值</span><strong>{{ selectedStock.marketCap }}</strong></li>
              <li><span>动态市盈率</span><strong>{{ selectedStock.pe }}</strong></li>
              <li><span>今年涨幅</span><strong>{{ selectedStock.ytdChange }}%</strong></li>
            </ul>
          </div>
        </div>

        <div class="chart-block">
          <div class="chart-title">
            <div>
              <h3>近十日 K 线</h3>
              <p class="hint">含收盘走势与上下影线</p>
            </div>
            <span class="badge info">{{ selectedStock.kline.length }} 日</span>
          </div>
          <KLineChart :candles="selectedStock.kline" />
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import KLineChart from './components/KLineChart.vue'

export default {
  name: 'App',
  components: { KLineChart },
  data () {
    const stocks = [
      {
        name: '宁德时代',
        ticker: '300750',
        board: '创业板',
        industry: '新能源电池',
        limitReason: '磷酸铁锂价格回落 + 订单复苏超预期',
        consecutiveCount: 2,
        limitChange: 10.01,
        ytdChange: 42.6,
        hotMoney: true,
        hotDesks: '中信杭州延安路 / 申万上海临沂路',
        turnover: '68.4 亿',
        turnoverRate: 3.2,
        lastPrice: 210.5,
        marketCap: '9,130 亿',
        pe: 31.2,
        concepts: ['锂电池', '储能', '新能源汽车'],
        kline: [
          { date: '05-02', open: 188, high: 191, low: 183, close: 190 },
          { date: '05-03', open: 191, high: 196, low: 189, close: 195 },
          { date: '05-06', open: 198, high: 204, low: 197, close: 202 },
          { date: '05-07', open: 202, high: 207, low: 199, close: 205 },
          { date: '05-08', open: 206, high: 214, low: 205, close: 210 },
          { date: '05-09', open: 211, high: 217, low: 209, close: 216 },
          { date: '05-10', open: 217, high: 222, low: 214, close: 220 },
          { date: '05-13', open: 222, high: 228, low: 220, close: 227 },
          { date: '05-14', open: 228, high: 233, low: 225, close: 232 },
          { date: '05-15', open: 232, high: 236, low: 229, close: 235 }
        ]
      },
      {
        name: '贵州茅台',
        ticker: '600519',
        board: '主板',
        industry: '白酒',
        limitReason: '内需消费恢复 + 提价预期发酵',
        consecutiveCount: 1,
        limitChange: 10,
        ytdChange: 35.4,
        hotMoney: false,
        hotDesks: '',
        turnover: '112.3 亿',
        turnoverRate: 1.9,
        lastPrice: 1805,
        marketCap: '2.3 万亿',
        pe: 33.6,
        concepts: ['高端白酒', '消费升级'],
        kline: [
          { date: '05-02', open: 1650, high: 1675, low: 1632, close: 1663 },
          { date: '05-03', open: 1670, high: 1704, low: 1662, close: 1698 },
          { date: '05-06', open: 1710, high: 1745, low: 1703, close: 1738 },
          { date: '05-07', open: 1740, high: 1776, low: 1732, close: 1755 },
          { date: '05-08', open: 1760, high: 1802, low: 1751, close: 1796 },
          { date: '05-09', open: 1805, high: 1838, low: 1794, close: 1830 },
          { date: '05-10', open: 1835, high: 1862, low: 1820, close: 1850 },
          { date: '05-13', open: 1860, high: 1890, low: 1851, close: 1882 },
          { date: '05-14', open: 1888, high: 1918, low: 1876, close: 1906 },
          { date: '05-15', open: 1910, high: 1945, low: 1898, close: 1938 }
        ]
      },
      {
        name: '中际旭创',
        ticker: '300308',
        board: '创业板',
        industry: '光模块',
        limitReason: 'AI 算力需求快速增长，800G 订单持续放量',
        consecutiveCount: 3,
        limitChange: 20,
        ytdChange: 98.3,
        hotMoney: true,
        hotDesks: '华鑫上海分公司 / 招商深圳深南东路',
        turnover: '45.8 亿',
        turnoverRate: 8.6,
        lastPrice: 172.4,
        marketCap: '1,250 亿',
        pe: 67.5,
        concepts: ['算力基础设施', '高速光模块', 'CPO'],
        kline: [
          { date: '05-02', open: 128, high: 135, low: 125, close: 134 },
          { date: '05-03', open: 136, high: 141, low: 133, close: 139 },
          { date: '05-06', open: 142, high: 148, low: 141, close: 147 },
          { date: '05-07', open: 150, high: 159, low: 149, close: 158 },
          { date: '05-08', open: 160, high: 168, low: 159, close: 165 },
          { date: '05-09', open: 166, high: 175, low: 165, close: 172 },
          { date: '05-10', open: 173, high: 182, low: 172, close: 179 },
          { date: '05-13', open: 182, high: 190, low: 181, close: 188 },
          { date: '05-14', open: 189, high: 197, low: 187, close: 195 },
          { date: '05-15', open: 196, high: 204, low: 194, close: 203 }
        ]
      },
      {
        name: '隆基绿能',
        ticker: '601012',
        board: '主板',
        industry: '光伏硅片',
        limitReason: '硅料价格回暖 + 海外订单恢复',
        consecutiveCount: 1,
        limitChange: 10.05,
        ytdChange: 21.7,
        hotMoney: false,
        hotDesks: '',
        turnover: '36.1 亿',
        turnoverRate: 4.2,
        lastPrice: 43.8,
        marketCap: '3,160 亿',
        pe: 15.8,
        concepts: ['光伏', 'TOPCon', '绿电'],
        kline: [
          { date: '05-02', open: 33.8, high: 34.2, low: 32.9, close: 34 },
          { date: '05-03', open: 34.2, high: 35, low: 33.8, close: 34.6 },
          { date: '05-06', open: 35.1, high: 36.5, low: 35.1, close: 36.2 },
          { date: '05-07', open: 36.4, high: 37.1, low: 36, close: 36.8 },
          { date: '05-08', open: 36.9, high: 38.3, low: 36.7, close: 37.9 },
          { date: '05-09', open: 38.1, high: 39.4, low: 37.8, close: 38.7 },
          { date: '05-10', open: 38.9, high: 40.2, low: 38.6, close: 39.8 },
          { date: '05-13', open: 40.3, high: 41.7, low: 40.1, close: 41.4 },
          { date: '05-14', open: 41.6, high: 42.8, low: 41.1, close: 42.5 },
          { date: '05-15', open: 42.9, high: 44.1, low: 42.5, close: 43.8 }
        ]
      },
      {
        name: '中远海控',
        ticker: '601919',
        board: '主板',
        industry: '航运港口',
        limitReason: '运价指数反弹 + 红海绕行推升运力需求',
        consecutiveCount: 2,
        limitChange: 10.02,
        ytdChange: 54.1,
        hotMoney: true,
        hotDesks: '华泰深圳益田路 / 国君深圳红荔路',
        turnover: '25.6 亿',
        turnoverRate: 6.2,
        lastPrice: 14.9,
        marketCap: '1,150 亿',
        pe: 9.4,
        concepts: ['航运', '一带一路', '高分红'],
        kline: [
          { date: '05-02', open: 10.8, high: 11.1, low: 10.5, close: 11 },
          { date: '05-03', open: 11.2, high: 11.6, low: 11, close: 11.5 },
          { date: '05-06', open: 11.8, high: 12.4, low: 11.7, close: 12.2 },
          { date: '05-07', open: 12.5, high: 13.1, low: 12.4, close: 13 },
          { date: '05-08', open: 13.2, high: 13.7, low: 13, close: 13.6 },
          { date: '05-09', open: 13.8, high: 14.3, low: 13.6, close: 14.1 },
          { date: '05-10', open: 14.2, high: 14.7, low: 14, close: 14.5 },
          { date: '05-13', open: 14.6, high: 15.2, low: 14.4, close: 15 },
          { date: '05-14', open: 15.1, high: 15.7, low: 14.9, close: 15.6 },
          { date: '05-15', open: 15.7, high: 16.2, low: 15.5, close: 16 }
        ]
      },
      {
        name: '华大智造',
        ticker: '688114',
        board: '科创板',
        industry: '医疗器械',
        limitReason: '国产测序仪渗透率提升 + 创新产品放量',
        consecutiveCount: 1,
        limitChange: 14.9,
        ytdChange: 63.2,
        hotMoney: true,
        hotDesks: '中金北京建国门外大街',
        turnover: '8.3 亿',
        turnoverRate: 13.5,
        lastPrice: 38.6,
        marketCap: '210 亿',
        pe: 52.7,
        concepts: ['创新医疗', '器械国产替代'],
        kline: [
          { date: '05-02', open: 24.6, high: 25.3, low: 24, close: 25.1 },
          { date: '05-03', open: 25.5, high: 26.7, low: 25.3, close: 26.2 },
          { date: '05-06', open: 26.8, high: 28.1, low: 26.6, close: 27.9 },
          { date: '05-07', open: 28.4, high: 29.8, low: 28, close: 29.5 },
          { date: '05-08', open: 30.1, high: 31.4, low: 29.7, close: 30.9 },
          { date: '05-09', open: 31.6, high: 33.1, low: 31.2, close: 32.8 },
          { date: '05-10', open: 33.5, high: 35.2, low: 33.2, close: 34.7 },
          { date: '05-13', open: 35.5, high: 36.9, low: 35, close: 36.4 },
          { date: '05-14', open: 36.8, high: 38.3, low: 36.4, close: 38 },
          { date: '05-15', open: 38.4, high: 40.1, low: 38.1, close: 39.9 }
        ]
      }
    ]

    return {
      stocks,
      keyword: '',
      industry: '',
      onlyHotMoney: false,
      selectedStock: stocks[0],
      showGuide: true
    }
  },
  computed: {
    filteredStocks () {
      return this.stocks.filter(stock => {
        const matchKeyword = this.keyword
          ? [stock.name, stock.ticker, stock.industry, stock.limitReason, stock.concepts.join(' ')].some(value =>
            value.toLowerCase().includes(this.keyword.toLowerCase())
          )
          : true
        const matchIndustry = this.industry ? stock.industry === this.industry : true
        const matchHot = this.onlyHotMoney ? stock.hotMoney : true
        return matchKeyword && matchIndustry && matchHot
      })
    },
    industries () {
      const set = new Set(this.stocks.map(item => item.industry))
      return Array.from(set)
    },
    consecutiveCount () {
      return this.stocks.filter(item => item.consecutiveCount > 1).length
    },
    maxConsecutive () {
      return this.stocks.reduce((max, item) => Math.max(max, item.consecutiveCount), 0)
    },
    averageYtd () {
      if (!this.stocks.length) return 0
      const total = this.stocks.reduce((sum, item) => sum + item.ytdChange, 0)
      return (total / this.stocks.length).toFixed(1)
    },
    hotMoneyCount () {
      return this.stocks.filter(item => item.hotMoney).length
    }
  },
  watch: {
    filteredStocks: {
      immediate: true,
      handler (list) {
        if (!list.length) {
          this.selectedStock = null
          return
        }

        const exists = list.find(item => this.selectedStock && item.ticker === this.selectedStock.ticker)
        if (!exists) {
          this.selectedStock = list[0]
        }
      }
    }
  },
  methods: {
    selectStock (stock) {
      this.selectedStock = stock
    },
    toggleGuide () {
      this.showGuide = !this.showGuide
    }
  }
}
</script>

<style>
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  background: #0f172a;
  font-family: 'Inter', 'PingFang SC', system-ui, -apple-system, sans-serif;
  color: #e2e8f0;
}

#app {
  min-height: 100vh;
}

.page {
  max-width: 1280px;
  margin: 0 auto;
  padding: 32px 20px 80px;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.title-block h1 {
  margin: 0;
  font-size: 28px;
  letter-spacing: 0.5px;
}

.subtitle {
  margin: 8px 0 0;
  color: #94a3b8;
}

.guide {
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(148, 163, 184, 0.12);
  border-radius: 12px;
  padding: 12px 14px;
  margin-bottom: 14px;
  transition: all 0.2s ease;
}

.guide.open {
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.35);
}

.guide-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
}

.guide-title h3 {
  margin: 2px 0 0;
  font-size: 16px;
}

.guide .eyebrow {
  margin: 0;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-size: 12px;
}

.guide .toggle {
  background: rgba(59, 130, 246, 0.12);
  color: #93c5fd;
  border: 1px solid rgba(59, 130, 246, 0.35);
  border-radius: 20px;
  padding: 6px 14px;
  cursor: pointer;
  font-weight: 600;
}

.guide-body {
  margin-top: 10px;
  color: #cbd5e1;
}

.guide-body ul {
  padding-left: 18px;
  margin: 0 0 8px;
  line-height: 1.6;
}

.badge {
  padding: 6px 10px;
  border-radius: 12px;
  background: linear-gradient(135deg, #1d4ed8, #22d3ee);
  color: #e0f2fe;
  font-weight: 600;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 14px;
  margin-bottom: 22px;
}

.card {
  background: linear-gradient(145deg, rgba(30, 41, 59, 0.9), rgba(30, 41, 59, 0.6));
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 12px;
  padding: 14px 16px;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.4);
}

.card .label {
  color: #94a3b8;
  margin: 0;
  font-size: 13px;
}

.card .value {
  margin: 8px 0 4px;
  font-size: 24px;
  font-weight: 700;
  color: #e2e8f0;
}

.card .hint {
  margin: 0;
  color: #64748b;
  font-size: 12px;
}

.filter-bar {
  display: grid;
  grid-template-columns: 1fr auto auto;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: rgba(30, 41, 59, 0.7);
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 12px;
  margin-bottom: 16px;
}

.search-box input {
  width: 100%;
  padding: 12px;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(15, 23, 42, 0.8);
  color: #e2e8f0;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #94a3b8;
}

.filter-group select {
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(15, 23, 42, 0.8);
  color: #e2e8f0;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 6px;
}

.layout {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 16px;
}

.table-card, .detail-card {
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(148, 163, 184, 0.1);
  border-radius: 14px;
  padding: 16px;
  box-shadow: 0 20px 40px rgba(8, 15, 33, 0.45);
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.table-wrapper {
  overflow: auto;
  max-height: 640px;
}

table {
  width: 100%;
  border-collapse: collapse;
  min-width: 780px;
}

th, td {
  padding: 12px 10px;
  text-align: left;
  border-bottom: 1px solid rgba(148, 163, 184, 0.08);
}

th {
  color: #94a3b8;
  font-weight: 600;
  font-size: 12px;
  letter-spacing: 0.5px;
  text-transform: uppercase;
}

td {
  color: #e2e8f0;
  font-size: 14px;
}

tr.active {
  background: rgba(59, 130, 246, 0.08);
  border-left: 3px solid #60a5fa;
}

.stock-name .main {
  font-weight: 700;
}

.stock-name .code {
  color: #94a3b8;
  font-size: 12px;
}

.reason {
  color: #cbd5e1;
}

.pill {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  font-weight: 600;
  font-size: 12px;
  color: #e2e8f0;
}

.pill.gain {
  background: rgba(34, 197, 94, 0.18);
  color: #4ade80;
  border: 1px solid rgba(74, 222, 128, 0.35);
}

.pill.highlight {
  background: rgba(59, 130, 246, 0.18);
  color: #93c5fd;
  border: 1px solid rgba(147, 197, 253, 0.35);
}

.pill.alert {
  background: rgba(248, 113, 113, 0.18);
  color: #fecdd3;
  border: 1px solid rgba(254, 164, 164, 0.35);
}

.pill.muted {
  background: rgba(148, 163, 184, 0.15);
  color: #cbd5e1;
  border: 1px solid rgba(148, 163, 184, 0.25);
}

.link {
  background: none;
  color: #60a5fa;
  border: none;
  cursor: pointer;
  font-weight: 600;
}

.detail-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.detail-header h2 {
  margin: 0;
  font-size: 22px;
}

.detail-header .code {
  color: #94a3b8;
  font-size: 14px;
}

.chips {
  display: flex;
  gap: 8px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.info-block {
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(148, 163, 184, 0.12);
  border-radius: 12px;
  padding: 12px;
}

.info-block .label {
  color: #94a3b8;
  margin: 0;
}

.info-block .value {
  margin: 8px 0 6px;
  font-weight: 700;
  font-size: 16px;
}

.kv-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 6px;
}

.kv-list li {
  display: flex;
  justify-content: space-between;
  color: #cbd5e1;
}

.chart-block {
  margin-top: 16px;
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(148, 163, 184, 0.12);
  border-radius: 12px;
  padding: 12px;
}

.chart-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 6px;
}

.badge.info {
  background: rgba(59, 130, 246, 0.16);
  border: 1px solid rgba(96, 165, 250, 0.4);
  color: #bfdbfe;
}

@media (max-width: 1024px) {
  .layout {
    grid-template-columns: 1fr;
  }

  .detail-card {
    order: -1;
  }
}
</style>
