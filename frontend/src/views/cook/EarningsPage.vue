<template>
  <div class="earnings-page animate-fade-in">
    <div class="page-header">
      <h2 class="heading-md">Earnings</h2>
      <p class="text-sm text-muted">Track your income and payouts</p>
    </div>

    <div class="summary-row" style="margin-top:20px">
      <div class="summary-card card-glass" v-for="s in summary" :key="s.label">
        <div class="summary-value" :style="{ color: s.color }">{{ s.value }}</div>
        <div class="summary-label">{{ s.label }}</div>
      </div>
    </div>

    <!-- Weekly Chart Placeholder -->
    <div class="card-glass chart-section" style="margin-top:24px">
      <h3 class="heading-sm">Weekly Earnings</h3>
      <div class="bar-chart" style="margin-top:20px">
        <div class="bar-col" v-for="(day, i) in weeklyData" :key="i">
          <div class="bar" :style="{ height: day.pct + '%' }">
            <span class="bar-value">{{ day.amount }}</span>
          </div>
          <span class="bar-label">{{ day.day }}</span>
        </div>
      </div>
    </div>

    <!-- Payout History -->
    <div class="card-glass" style="margin-top:20px; padding:24px; border-radius:var(--radius-lg)">
      <h3 class="heading-sm">Payout History</h3>
      <table class="data-table" style="margin-top:16px">
        <thead>
          <tr><th>Date</th><th>Amount</th><th>Status</th><th>Method</th></tr>
        </thead>
        <tbody>
          <tr v-for="p in payouts" :key="p.id">
            <td>{{ p.date }}</td>
            <td class="fw-600">{{ p.amount }}</td>
            <td><span class="badge" :class="'badge-' + p.status">{{ p.status }}</span></td>
            <td>{{ p.method }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { cookApi } from '@/services/api.js'

const loading = ref(true)
const earningsData = ref(null)

async function loadEarnings() {
  loading.value = true
  try {
    earningsData.value = await cookApi.getEarnings()
  } catch (e) {
    console.error('Failed to load earnings', e)
  } finally {
    loading.value = false
  }
}

onMounted(loadEarnings)

const summary = computed(() => {
  const d = earningsData.value
  if (!d) return []

  const weeklyTotal = (d.weekly_earnings || []).reduce((sum, row) => sum + Number(row.amount || 0), 0)
  const pendingPayout = (d.payouts || [])
    .filter(p => String(p.status || '').toLowerCase() !== 'paid')
    .reduce((sum, p) => sum + Number(p.amount || 0), 0)

  return [
    { label: 'Total Earned', value: `Rs ${(d.total_earned || 0).toLocaleString('en-IN')}`, color: 'var(--color-primary-dark)' },
    { label: 'This Week', value: `Rs ${weeklyTotal.toLocaleString('en-IN')}`, color: 'var(--color-primary)' },
    { label: 'Pending Payout', value: `Rs ${pendingPayout.toLocaleString('en-IN')}`, color: 'var(--color-accent)' },
    { label: 'Total Jobs', value: `${d.total_bookings || 0}`, color: 'var(--color-secondary)' }
  ]
})

const weeklyData = computed(() => {
  const rows = earningsData.value?.weekly_earnings || []
  if (!rows.length) return []
  const max = Math.max(...rows.map(w => Number(w.amount || 0)), 1)
  return rows.map(w => ({
    day: w.day,
    amount: `Rs ${Number(w.amount || 0).toLocaleString('en-IN')}`,
    pct: Math.round((Number(w.amount || 0) / max) * 100)
  }))
})

const payouts = computed(() => {
  const list = earningsData.value?.payouts || []
  return list.map((p) => ({
    id: p.id,
    date: p.date ? new Date(p.date).toLocaleDateString('en-IN') : 'N/A',
    amount: `Rs ${Number(p.amount || 0).toLocaleString('en-IN')}`,
    status: String(p.status || 'paid').toLowerCase() === 'paid' ? 'Completed' : 'Processing',
    method: 'Bank Transfer'
  }))
})
</script>

<style scoped>
.earnings-page {
  width: 100%;
}

.summary-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 14px;
}

.summary-card {
  padding: 20px;
  border-radius: var(--radius-lg);
  text-align: center;
}

.summary-value {
  font-size: 1.375rem;
  font-weight: 700;
}

.summary-label {
  font-size: 0.75rem;
  color: var(--color-text-light);
  margin-top: 4px;
}

.chart-section {
  padding: 24px;
  border-radius: var(--radius-lg);
}

.bar-chart {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  height: 280px;
  padding: 24px 0;
}

.bar-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
  justify-content: flex-end;
  gap: 12px;
}

.bar {
  width: 100%;
  max-width: 52px;
  background: linear-gradient(160deg, #2DB67D 0%, #1A8F5C 100%);
  border-radius: var(--radius-md) var(--radius-md) 0 0;
  position: relative;
  transition: height 0.6s ease;
  min-height: 12px;
  box-shadow: 0 4px 12px rgba(45, 182, 125, 0.25);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 6px;
}

.bar-col:nth-child(odd) .bar {
  background: linear-gradient(160deg, #2DB67D 0%, #1A8F5C 100%);
  box-shadow: 0 4px 12px rgba(45, 182, 125, 0.25);
}

.bar-col:nth-child(even) .bar {
  background: linear-gradient(160deg, #5CCFA0 0%, #2DB67D 100%);
  box-shadow: 0 4px 12px rgba(92, 207, 160, 0.25);
}

.bar-value {
  font-size: 0.7rem;
  font-weight: 700;
  color: #fff;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
  white-space: nowrap;
}

.bar-label {
  font-size: 0.8rem;
  font-weight: 500;
  color: var(--color-text);
  text-align: center;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  text-align: left;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--color-text-light);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 10px 12px;
  border-bottom: 1px solid var(--color-border);
}

.data-table td {
  padding: 12px;
  font-size: 0.875rem;
  border-bottom: 1px solid var(--color-border-light);
}

.badge-Completed { background: #D1FAE5; color: #059669; padding: 3px 10px; border-radius: var(--radius-full); font-size: 0.688rem; font-weight: 600; }
.badge-Processing { background: #FEF3C7; color: #D97706; padding: 3px 10px; border-radius: var(--radius-full); font-size: 0.688rem; font-weight: 600; }
</style>
