<template>
  <div class="complaints-page animate-fade-in">
    <div class="page-header">
      <h2 class="heading-md">Complaints</h2>
      <p class="text-sm text-muted">Review and resolve customer complaints</p>
    </div>

    <div class="filter-row" style="margin-top:16px">
      <button v-for="tab in tabs" :key="tab" class="tab-btn" :class="{ active: activeTab === tab }" @click="activeTab = tab">
        {{ tab }}
      </button>
    </div>

    <div class="complaints-list" style="margin-top:20px">
      <div class="complaint-card card-glass" v-for="c in filtered" :key="c.id">
        <div class="complaint-header">
          <div>
            <div class="fw-600">{{ c.subject }}</div>
            <div class="text-xs text-muted">Booking #{{ c.bookingId }} &middot; {{ c.date }}</div>
          </div>
          <span class="badge" :class="'badge-' + c.priority">{{ c.priority }}</span>
        </div>
        <div class="complaint-body">
          <div class="parties">
            <div class="party">
              <span class="party-label">Customer</span>
              <span class="party-name">{{ c.customer }}</span>
            </div>
            <div class="party">
              <span class="party-label">Cook</span>
              <span class="party-name">{{ c.cook }}</span>
            </div>
          </div>
          <p class="complaint-text text-sm">{{ c.description }}</p>
        </div>
        <div class="complaint-footer">
          <span class="badge" :class="'status-' + c.status">{{ c.status }}</span>
          <div class="complaint-actions" v-if="c.status === 'Open'">
            <button class="btn btn-sm btn-outline" @click="updateStatus(c, 'Investigating')">Investigate</button>
            <button class="btn btn-sm btn-primary" @click="updateStatus(c, 'Resolved')">Resolve</button>
          </div>
          <div class="complaint-actions" v-else-if="c.status === 'Investigating'">
            <button class="btn btn-sm btn-primary" @click="updateStatus(c, 'Resolved')">Mark Resolved</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { managerApi } from '@/services/api.js'

const activeTab = ref('All')
const tabs = ['All', 'Open', 'Investigating', 'Resolved']
const complaints = ref([])
const loading = ref(true)

async function loadComplaints() {
  loading.value = true
  try {
    const data = await managerApi.getComplaints()
    complaints.value = (data || []).map(c => ({
      ...c,
      subject: c.subject || c.description?.slice(0, 50) || 'Complaint',
      bookingId: c.booking_id ? `BK-${c.booking_id}` : '',
      date: c.created_at ? new Date(c.created_at).toLocaleDateString('en-IN') : '',
      priority: c.priority || 'Medium',
      customer: c.customer_name || 'Customer',
      cook: c.cook_name || 'Cook',
      status: c.status || 'Open'
    }))
  } catch (e) {
    console.error('Failed to load complaints', e)
  } finally {
    loading.value = false
  }
}

onMounted(loadComplaints)

const filtered = computed(() =>
  activeTab.value === 'All' ? complaints.value : complaints.value.filter(c => c.status === activeTab.value)
)

async function updateStatus(complaint, newStatus) {
  try {
    if (newStatus === 'Resolved') {
      await managerApi.resolveComplaint(complaint.id, { status: 'Resolved', resolution_notes: 'Resolved by manager' })
    } else {
      await managerApi.updateComplaint(complaint.id, { status: newStatus })
    }
    await loadComplaints()
  } catch (e) {
    alert(e.message || 'Failed to update complaint')
  }
}
</script>

<style scoped>
.complaints-page { width: 100%; }

.filter-row { display: flex; gap: 8px; flex-wrap: wrap; }
.tab-btn { padding: 8px 18px; border-radius: var(--radius-full); font-size: 0.813rem; font-weight: 500; background: var(--color-bg-alt); color: var(--color-text-secondary); border: 1px solid var(--color-border); cursor: pointer; transition: all var(--transition-fast); }
.tab-btn.active { background: var(--color-primary); color: #fff; border-color: var(--color-primary); }

.complaints-list { display: flex; flex-direction: column; gap: 16px; }

.complaint-card { padding: 22px; border-radius: var(--radius-lg); }
.complaint-header { display: flex; justify-content: space-between; align-items: flex-start; }

.badge-High { background: #FEE2E2; color: #DC2626; }
.badge-Medium { background: #FEF3C7; color: #D97706; }
.badge-Low { background: #DBEAFE; color: #2563EB; }
[class*="badge-"] { padding: 3px 10px; border-radius: var(--radius-full); font-size: 0.688rem; font-weight: 600; }

.complaint-body { margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--color-border-light); }
.parties { display: flex; gap: 24px; margin-bottom: 10px; }
.party-label { font-size: 0.688rem; color: var(--color-text-light); text-transform: uppercase; letter-spacing: 0.04em; display: block; }
.party-name { font-size: 0.875rem; font-weight: 500; }
.complaint-text { color: var(--color-text-secondary); line-height: 1.5; }

.complaint-footer { display: flex; justify-content: space-between; align-items: center; margin-top: 14px; padding-top: 14px; border-top: 1px solid var(--color-border-light); }
.complaint-actions { display: flex; gap: 8px; }

.status-Open { background: #FEE2E2; color: #DC2626; padding: 3px 10px; border-radius: var(--radius-full); font-size: 0.688rem; font-weight: 600; }
.status-Investigating { background: #FEF3C7; color: #D97706; padding: 3px 10px; border-radius: var(--radius-full); font-size: 0.688rem; font-weight: 600; }
.status-Resolved { background: #D1FAE5; color: #059669; padding: 3px 10px; border-radius: var(--radius-full); font-size: 0.688rem; font-weight: 600; }

.btn-sm { padding: 6px 16px; font-size: 0.813rem; }
</style>
