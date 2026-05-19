<template>
  <div class="disputes-page animate-fade-in">
    <div class="page-header">
      <h2 class="heading-md">Disputes</h2>
      <p class="text-sm text-muted">Escalated complaints requiring admin resolution</p>
    </div>

    <div class="filter-row" style="margin-top:16px">
      <button v-for="tab in tabs" :key="tab" class="tab-btn" :class="{ active: activeTab === tab }" @click="activeTab = tab">
        {{ tab }}
      </button>
    </div>

    <div class="disputes-list" style="margin-top:20px">
      <div class="dispute-card card-glass" v-for="d in filtered" :key="d.id">
        <div class="dispute-header">
          <div>
            <div class="dispute-id text-xs text-muted">{{ d.disputeId }}</div>
            <div class="fw-600">{{ d.subject }}</div>
          </div>
          <span class="badge" :class="'priority-' + d.priority">{{ d.priority }}</span>
        </div>

        <div class="dispute-parties">
          <div class="party-block">
            <span class="party-role">Customer</span>
            <span class="party-name">{{ d.customer }}</span>
          </div>
          <div class="vs">vs</div>
          <div class="party-block">
            <span class="party-role">Cook</span>
            <span class="party-name">{{ d.cook }}</span>
          </div>
        </div>

        <p class="text-sm" style="color:var(--color-text-secondary);margin-top:12px">{{ d.description }}</p>

        <div class="dispute-meta">
          <span class="text-xs text-muted">Booking #{{ d.bookingId }}</span>
          <span class="text-xs text-muted">Escalated: {{ d.escalatedDate }}</span>
          <span class="text-xs text-muted">Manager: {{ d.manager }}</span>
        </div>

        <div class="dispute-footer">
          <span class="badge" :class="'status-' + d.status">{{ d.status }}</span>
          <div class="dispute-actions" v-if="d.status === 'Open'">
            <button class="btn btn-sm btn-outline" @click="reviewDispute(d)">Review</button>
          </div>
          <div class="dispute-actions" v-else-if="d.status === 'Under Review'">
            <button class="btn btn-sm btn-outline" style="color:var(--color-error);border-color:var(--color-error)" @click="resolveDispute(d, 'ruled_for_cook')">Rule for Cook</button>
            <button class="btn btn-sm btn-primary" @click="resolveDispute(d, 'ruled_for_customer')">Rule for Customer</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { adminApi } from '@/services/api.js'

const activeTab = ref('All')
const tabs = ['All', 'Open', 'Under Review', 'Resolved']
const disputes = ref([])
const loading = ref(true)

async function loadDisputes() {
  loading.value = true
  try {
    const data = await adminApi.getDisputes()
    disputes.value = (data || []).map(d => ({
      ...d,
      disputeId: `D-${d.id}`,
      subject: d.subject || d.description?.slice(0, 50) || 'Dispute',
      bookingId: d.booking_id ? `BK-${d.booking_id}` : '',
      customer: d.customer_name || 'Customer',
      cook: d.cook_name || 'Cook',
      manager: d.manager_name || 'Manager',
      priority: d.priority || 'Medium',
      escalatedDate: d.created_at ? new Date(d.created_at).toLocaleDateString('en-IN') : '',
      status: d.status === 'open' ? 'Open' : d.status === 'under_review' ? 'Under Review' : d.status?.startsWith('ruled') ? d.status : d.status
    }))
  } catch (e) {
    console.error('Failed to load disputes', e)
  } finally {
    loading.value = false
  }
}

onMounted(loadDisputes)

const filtered = computed(() => {
  if (activeTab.value === 'All') return disputes.value
  if (activeTab.value === 'Resolved') return disputes.value.filter(d => d.status.startsWith('Ruled'))
  return disputes.value.filter(d => d.status === activeTab.value)
})

async function resolveDispute(d, ruling) {
  try {
    await adminApi.resolveDispute(d.id, { ruling, resolution: `${ruling} by admin` })
    await loadDisputes()
  } catch (e) { alert(e.message || 'Failed to resolve') }
}

async function reviewDispute(d) {
  try {
    await adminApi.resolveDispute(d.id, { ruling: 'under_review', resolution: 'Under admin review' })
    await loadDisputes()
  } catch (e) { alert(e.message || 'Failed') }
}
</script>

<style scoped>
.disputes-page { width: 100%; }

.filter-row { display: flex; gap: 8px; flex-wrap: wrap; }
.tab-btn { padding: 8px 18px; border-radius: var(--radius-full); font-size: 0.813rem; font-weight: 500; background: var(--color-bg-alt); color: var(--color-text-secondary); border: 1px solid var(--color-border); cursor: pointer; transition: all var(--transition-fast); }
.tab-btn.active { background: var(--color-primary); color: #fff; border-color: var(--color-primary); }

.disputes-list { display: flex; flex-direction: column; gap: 16px; }

.dispute-card { padding: 24px; border-radius: var(--radius-lg); }
.dispute-header { display: flex; justify-content: space-between; align-items: flex-start; }
.dispute-id { margin-bottom: 2px; }

.priority-Critical { background: #7C3AED; color: #fff; }
.priority-High { background: #FEE2E2; color: #DC2626; }
.priority-Medium { background: #FEF3C7; color: #D97706; }
.priority-Low { background: #DBEAFE; color: #2563EB; }
[class*="priority-"] { padding: 3px 10px; border-radius: var(--radius-full); font-size: 0.688rem; font-weight: 600; }

.dispute-parties { display: flex; align-items: center; gap: 16px; margin-top: 16px; padding: 14px; background: var(--color-bg-alt); border-radius: var(--radius-md); }
.party-block { text-align: center; flex: 1; }
.party-role { display: block; font-size: 0.688rem; color: var(--color-text-light); text-transform: uppercase; letter-spacing: 0.04em; }
.party-name { font-weight: 600; font-size: 0.875rem; }
.vs { font-size: 0.75rem; color: var(--color-text-light); font-weight: 600; }

.dispute-meta { display: flex; gap: 16px; margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--color-border-light); flex-wrap: wrap; }

.dispute-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--color-border-light); }
.dispute-actions { display: flex; gap: 8px; }

.status-Open { background: #FEE2E2; color: #DC2626; }
[class*="status-Under"] { background: #FEF3C7; color: #D97706; }
[class*="status-Ruled"] { background: #D1FAE5; color: #059669; }
[class*="status-"] { padding: 3px 10px; border-radius: var(--radius-full); font-size: 0.688rem; font-weight: 600; }

.btn-sm { padding: 6px 16px; font-size: 0.813rem; }
</style>
