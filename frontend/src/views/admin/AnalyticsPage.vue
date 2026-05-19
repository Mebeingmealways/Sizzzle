<template>
  <div class="analytics-page animate-fade-in">
    <div class="page-header">
      <h2 class="heading-md">Analytics</h2>
      <p class="text-sm text-muted">Platform-wide metrics and insights</p>
    </div>

    <div class="period-selector" style="margin-top:16px">
      <button v-for="p in periods" :key="p" class="tab-btn" :class="{ active: activePeriod === p }" @click="activePeriod = p">{{ p }}</button>
    </div>

    <!-- KPI Row -->
    <div class="kpi-row" style="margin-top:20px">
      <div class="kpi-card card-glass" v-for="kpi in kpis" :key="kpi.label">
        <div class="kpi-value">{{ kpi.value }}</div>
        <div class="kpi-label">{{ kpi.label }}</div>
        <div class="kpi-change" :class="kpi.direction">{{ kpi.change }}</div>
      </div>
    </div>

    <div class="grid-2" style="margin-top:24px">
      <!-- Bookings by City -->
      <div class="card-glass section">
        <h3 class="heading-sm">Bookings by City</h3>
        <div class="city-list" style="margin-top:16px">
          <div class="city-row" v-for="city in cityData" :key="city.name">
            <span class="text-sm" style="min-width:100px">{{ city.name }}</span>
            <div class="city-bar-wrap">
              <div class="city-bar" :style="{ width: city.pct + '%' }"></div>
            </div>
            <span class="text-sm fw-600">{{ city.bookings }}</span>
          </div>
        </div>
      </div>

      <!-- Top Cuisines -->
      <div class="card-glass section">
        <h3 class="heading-sm">Popular Cuisines</h3>
        <div class="cuisine-list" style="margin-top:16px">
          <div class="cuisine-item" v-for="(c, i) in cuisines" :key="c.name">
            <span class="cuisine-rank">{{ i + 1 }}</span>
            <span class="text-sm" style="flex:1">{{ c.name }}</span>
            <span class="text-sm fw-600">{{ c.orders }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Revenue Trend -->
    <div class="card-glass section" style="margin-top:20px">
      <h3 class="heading-sm">Revenue Trend (6 Months)</h3>
      <div class="trend-chart" style="margin-top:20px">
        <svg viewBox="0 0 600 200" class="line-chart">
          <polyline :points="revenuePoints" fill="none" stroke="var(--color-primary)" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
          <polyline :points="revenueAreaPoints" fill="url(#areaGrad)" opacity="0.15" />
          <defs>
            <linearGradient id="areaGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="var(--color-primary)" />
              <stop offset="100%" stop-color="var(--color-primary)" stop-opacity="0" />
            </linearGradient>
          </defs>
          <circle v-for="(pt, i) in revenuePointsArr" :key="i" :cx="pt[0]" :cy="pt[1]" r="4" fill="var(--color-primary)" />
        </svg>
        <div class="trend-labels">
          <span v-for="m in trendMonths" :key="m">{{ m }}</span>
        </div>
      </div>
    </div>

    <!-- User Growth -->
    <div class="card-glass section" style="margin-top:20px">
      <h3 class="heading-sm">User Growth</h3>
      <div class="growth-stats" style="margin-top:16px">
        <div class="growth-item" v-for="g in growthData" :key="g.label">
          <div class="growth-value">{{ g.value }}</div>
          <div class="growth-label">{{ g.label }}</div>
          <div class="growth-delta" :class="g.direction">{{ g.delta }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { adminApi } from '@/services/api.js'

const activePeriod = ref('This Month')
const periods = ['This Week', 'This Month', 'This Quarter', 'This Year']

const kpis = ref([
  { label: 'Total Bookings', value: '—', change: '', direction: 'up' },
  { label: 'Completion Rate', value: '—', change: '', direction: 'up' },
  { label: 'Cancellation Rate', value: '—', change: '', direction: 'down' }
])

const cityData = ref([])
const cuisines = ref([])
const trendMonths = ref(['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])

const periodMap = {
  'This Week': '7d',
  'This Month': '30d',
  'This Quarter': '90d',
  'This Year': '365d'
}

async function loadAnalytics() {
  try {
    const data = await adminApi.getAnalytics(periodMap[activePeriod.value] || '30d')
    kpis.value = [
      { label: 'Total Bookings', value: String(data.total_bookings || 0), change: `${(data.total_revenue || 0).toFixed(0)} revenue`, direction: 'up' },
      { label: 'Completion Rate', value: `${(data.completion_rate || 0).toFixed(1)}%`, change: `${data.completed_bookings || 0} completed`, direction: 'up' },
      { label: 'Cancellation Rate', value: `${(data.cancellation_rate || 0).toFixed(1)}%`, change: `${data.cancelled_bookings || 0} cancelled`, direction: 'down' }
    ]

    cityData.value = (data.city_breakdown || []).map(c => ({
      name: c.name,
      bookings: c.bookings,
      pct: c.pct
    }))

    cuisines.value = (data.cuisine_breakdown || []).map(c => ({
      name: c.name,
      orders: c.orders
    }))

    revenueValues.value = (data.revenue_trend || []).map(m => Number(m.revenue || 0))
    trendMonths.value = (data.revenue_trend || []).map(m => m.month)

    const growth = data.growth || {}
    growthData.value = [
      {
        label: 'Customers',
        value: String(growth.customers?.value ?? data.total_customers ?? 0),
        delta: `${(growth.customers?.delta_pct ?? 0) >= 0 ? '+' : ''}${(growth.customers?.delta_pct ?? 0).toFixed(1)}%`,
        direction: (growth.customers?.delta_pct ?? 0) >= 0 ? 'up' : 'down'
      },
      {
        label: 'Cooks',
        value: String(growth.cooks?.value ?? data.total_cooks ?? 0),
        delta: `${(growth.cooks?.delta_pct ?? 0) >= 0 ? '+' : ''}${(growth.cooks?.delta_pct ?? 0).toFixed(1)}%`,
        direction: (growth.cooks?.delta_pct ?? 0) >= 0 ? 'up' : 'down'
      },
      {
        label: 'Managers',
        value: String(growth.managers?.value ?? 0),
        delta: `${(growth.managers?.delta_pct ?? 0) >= 0 ? '+' : ''}${(growth.managers?.delta_pct ?? 0).toFixed(1)}%`,
        direction: (growth.managers?.delta_pct ?? 0) >= 0 ? 'up' : 'down'
      },
      {
        label: 'Retention Rate',
        value: `${(growth.retention_rate?.value ?? 0).toFixed(1)}%`,
        delta: `${(growth.retention_rate?.delta_pct ?? 0) >= 0 ? '+' : ''}${(growth.retention_rate?.delta_pct ?? 0).toFixed(1)}%`,
        direction: (growth.retention_rate?.delta_pct ?? 0) >= 0 ? 'up' : 'down'
      }
    ]
  } catch (e) {
    console.error('Analytics load failed', e)
  }
}

onMounted(loadAnalytics)
watch(activePeriod, loadAnalytics)

const revenueValues = ref([82, 101, 124, 148, 162, 184])
const revenuePointsArr = computed(() =>
  revenueValues.value.map((v, i) => [i * 110 + 30, 190 - ((v || 0) / Math.max(...revenueValues.value, 1)) * 150])
)
const revenuePoints = computed(() => revenuePointsArr.value.map(p => p.join(',')).join(' '))
const revenueAreaPoints = computed(() => {
  const pts = [...revenuePointsArr.value]
  return [...pts, [pts[pts.length - 1][0], 190], [pts[0][0], 190]].map(p => p.join(',')).join(' ')
})

const growthData = ref([
  { label: 'Customers', value: '—', delta: '', direction: 'up' },
  { label: 'Cooks', value: '—', delta: '', direction: 'up' },
  { label: 'Managers', value: '—', delta: '', direction: 'up' },
  { label: 'Retention Rate', value: '—', delta: '', direction: 'up' }
])
</script>

<style scoped>
.analytics-page { width: 100%; }

.period-selector { display: flex; gap: 8px; flex-wrap: wrap; }
.tab-btn { padding: 8px 18px; border-radius: var(--radius-full); font-size: 0.813rem; font-weight: 500; background: var(--color-bg-alt); color: var(--color-text-secondary); border: 1px solid var(--color-border); cursor: pointer; transition: all var(--transition-fast); }
.tab-btn.active { background: var(--color-primary); color: #fff; border-color: var(--color-primary); }

.kpi-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 14px; }
.kpi-card { padding: 20px; border-radius: var(--radius-lg); text-align: center; }
.kpi-value { font-size: 1.375rem; font-weight: 700; }
.kpi-label { font-size: 0.75rem; color: var(--color-text-light); margin-top: 2px; }
.kpi-change { font-size: 0.688rem; font-weight: 600; margin-top: 4px; }
.kpi-change.up { color: #059669; }
.kpi-change.down { color: #DC2626; }

.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
@media (max-width: 768px) { .grid-2 { grid-template-columns: 1fr; } }

.section { padding: 24px; border-radius: var(--radius-lg); }

.city-list { display: flex; flex-direction: column; gap: 12px; }
.city-row { display: flex; align-items: center; gap: 12px; }
.city-bar-wrap { flex: 1; height: 8px; background: var(--color-bg-alt); border-radius: var(--radius-full); overflow: hidden; }
.city-bar { height: 100%; background: linear-gradient(90deg, var(--color-primary), var(--color-accent)); border-radius: var(--radius-full); transition: width 0.8s ease; }

.cuisine-list { display: flex; flex-direction: column; gap: 10px; }
.cuisine-item { display: flex; align-items: center; gap: 12px; padding: 10px; background: var(--color-bg-alt); border-radius: var(--radius-md); }
.cuisine-rank { width: 26px; height: 26px; border-radius: 50%; background: var(--color-primary); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 700; }

.line-chart { width: 100%; height: auto; }
.trend-labels { display: flex; justify-content: space-between; padding: 0 20px; margin-top: 4px; }
.trend-labels span { font-size: 0.75rem; color: var(--color-text-light); }

.growth-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 16px; }
.growth-item { text-align: center; padding: 16px; background: var(--color-bg-alt); border-radius: var(--radius-md); }
.growth-value { font-size: 1.5rem; font-weight: 700; color: var(--color-text); }
.growth-label { font-size: 0.75rem; color: var(--color-text-light); margin-top: 2px; }
.growth-delta { font-size: 0.688rem; font-weight: 600; margin-top: 4px; }
.growth-delta.up { color: #059669; }
.growth-delta.down { color: #DC2626; }
</style>
