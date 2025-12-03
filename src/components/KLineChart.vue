<template>
  <div class="kline">
    <canvas ref="canvas" height="260"></canvas>
    <div class="axis" v-if="candles && candles.length">
      <span>{{ candles[0].date }}</span>
      <span>{{ candles[candles.length - 1].date }}</span>
    </div>
    <p v-else class="empty">暂无 K 线数据</p>
  </div>
</template>

<script>
export default {
  name: 'KLineChart',
  props: {
    candles: {
      type: Array,
      default: () => []
    }
  },
  mounted () {
    this.draw()
  },
  watch: {
    candles: {
      handler () {
        this.$nextTick(this.draw)
      },
      deep: true
    }
  },
  methods: {
    draw () {
      const canvas = this.$refs.canvas
      if (!canvas || !this.candles.length) return

      const ctx = canvas.getContext('2d')
      const rect = canvas.getBoundingClientRect()
      const width = rect.width || 720
      canvas.width = width
      const height = canvas.height

      ctx.clearRect(0, 0, width, height)

      const padding = { top: 16, right: 16, bottom: 20, left: 16 }
      const innerWidth = width - padding.left - padding.right
      const innerHeight = height - padding.top - padding.bottom

      const highs = this.candles.map(item => item.high)
      const lows = this.candles.map(item => item.low)
      const max = Math.max(...highs)
      const min = Math.min(...lows)
      const range = max - min || 1

      const candleWidth = Math.min(22, innerWidth / this.candles.length - 6)
      const step = innerWidth / this.candles.length

      // guide lines
      ctx.strokeStyle = 'rgba(148, 163, 184, 0.2)'
      ctx.lineWidth = 1
      ctx.setLineDash([4, 6])
      ctx.beginPath()
      ctx.moveTo(padding.left, padding.top)
      ctx.lineTo(padding.left, height - padding.bottom)
      ctx.moveTo(width - padding.right, padding.top)
      ctx.lineTo(width - padding.right, height - padding.bottom)
      ctx.stroke()
      ctx.setLineDash([])

      // closing line for quick glance
      ctx.beginPath()
      this.candles.forEach((item, index) => {
        const x = padding.left + index * step + step / 2
        const y = padding.top + (1 - (item.close - min) / range) * innerHeight
        if (index === 0) {
          ctx.moveTo(x, y)
        } else {
          ctx.lineTo(x, y)
        }
      })
      ctx.strokeStyle = 'rgba(94, 234, 212, 0.9)'
      ctx.lineWidth = 2
      ctx.stroke()

      // candles
      this.candles.forEach((item, index) => {
        const centerX = padding.left + index * step + step / 2
        const highY = padding.top + (1 - (item.high - min) / range) * innerHeight
        const lowY = padding.top + (1 - (item.low - min) / range) * innerHeight
        const openY = padding.top + (1 - (item.open - min) / range) * innerHeight
        const closeY = padding.top + (1 - (item.close - min) / range) * innerHeight
        const color = item.close >= item.open ? '#4ade80' : '#fca5a5'

        ctx.strokeStyle = color
        ctx.lineWidth = 2
        ctx.beginPath()
        ctx.moveTo(centerX, highY)
        ctx.lineTo(centerX, lowY)
        ctx.stroke()

        const rectY = Math.min(openY, closeY)
        const rectHeight = Math.abs(closeY - openY) || 2
        ctx.fillStyle = color
        ctx.strokeStyle = color
        ctx.lineWidth = 1.5
        ctx.fillRect(centerX - candleWidth / 2, rectY, candleWidth, rectHeight)
        ctx.strokeRect(centerX - candleWidth / 2, rectY, candleWidth, rectHeight)
      })
    }
  }
}
</script>

<style scoped>
.kline {
  background: rgba(15, 23, 42, 0.7);
  border-radius: 12px;
  padding: 4px;
  border: 1px solid rgba(148, 163, 184, 0.08);
}

canvas {
  width: 100%;
  display: block;
}

.axis {
  display: flex;
  justify-content: space-between;
  color: #94a3b8;
  font-size: 12px;
  margin-top: 4px;
}

.empty {
  text-align: center;
  color: #94a3b8;
  margin: 12px 0 0;
}
</style>
