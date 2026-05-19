<template>
  <div class="verification-page animate-fade-in">
    <div class="page-header">
      <h2 class="heading-md">Cook Verification</h2>
      <p class="text-sm text-muted">Review submitted cook registration details and complete approval workflow</p>
    </div>

    <div class="filter-row" style="margin-top:16px">
      <button
        v-for="tab in tabs"
        :key="tab"
        class="tab-btn"
        :class="{ active: activeTab === tab }"
        @click="activeTab = tab"
      >
        {{ tab }}
      </button>
    </div>

    <div v-if="loading" class="card-glass" style="padding:20px; margin-top:16px; border-radius:var(--radius-lg)">
      <div class="text-sm text-muted">Loading verification applications...</div>
    </div>

    <div v-else-if="!selectedApp" class="app-list" style="margin-top:20px">
      <div class="app-card card-glass" v-for="app in filtered" :key="app.id" @click="openDetail(app)">
        <div class="app-header">
          <div class="app-avatar">{{ app.initials }}</div>
          <div class="app-info">
            <div class="fw-600">{{ app.name }}</div>
            <div class="text-xs text-muted">{{ app.specialization || 'Not provided' }} &middot; {{ app.experience || 'Not provided' }}</div>
          </div>
          <span class="badge" :class="'badge-' + app.status">{{ app.status }}</span>
        </div>
        <div class="app-meta">
          <span><AppIcon name="map-pin" :size="13" /> {{ app.city || 'N/A' }}</span>
          <span><AppIcon name="calendar" :size="13" /> Applied {{ app.applied || 'N/A' }}</span>
          <span><AppIcon name="clock" :size="13" /> {{ app.years }} yrs exp</span>
          <span><AppIcon name="check" :size="13" /> {{ app.checks_completed }}/{{ app.checks_total }} checks</span>
        </div>
      </div>

      <div v-if="filtered.length === 0" class="card-glass" style="padding:24px; border-radius:var(--radius-lg)">
        <div class="text-sm text-muted">No applications in this status.</div>
      </div>
    </div>

    <div v-else class="detail-view" style="margin-top:20px">
      <button class="btn btn-outline btn-sm" @click="closeDetail" style="margin-bottom:16px">
        <AppIcon name="arrow-left" :size="14" /> Back to list
      </button>

      <div class="card-glass" style="padding:28px;border-radius:var(--radius-lg)">
        <div v-if="detailLoading" class="text-sm text-muted">Loading cook details...</div>

        <template v-else-if="selectedDetail">
          <div class="detail-header">
            <div class="app-avatar lg">{{ selectedApp.initials }}</div>
            <div class="detail-head-text">
              <h3 class="heading-sm">{{ selectedDetail.name }}</h3>
              <div class="text-sm text-muted">{{ selectedDetail.specialization || 'Not provided' }} &middot; {{ selectedDetail.city || 'N/A' }}</div>
              <div class="text-xs text-muted" style="margin-top:4px">
                Status: <strong>{{ selectedDetail.status_label }}</strong> &middot; Applied: {{ formatDate(selectedDetail.applied_at) }}
              </div>
            </div>
            <span class="badge" :class="'badge-' + selectedDetail.status_label">{{ selectedDetail.status_label }}</span>
          </div>

          <div class="section-grid" style="margin-top:20px">
            <div class="section-card">
              <div class="section-title">Cook Profile</div>
              <div class="kv-list">
                <div class="kv-row"><span>Name</span><span>{{ selectedDetail.name || 'N/A' }}</span></div>
                <div class="kv-row"><span>Email</span><span>{{ selectedDetail.email || 'N/A' }}</span></div>
                <div class="kv-row"><span>Phone</span><span>{{ selectedDetail.phone || 'N/A' }}</span></div>
                <div class="kv-row"><span>Address</span><span>{{ selectedDetail.address || 'N/A' }}</span></div>
                <div class="kv-row"><span>Experience Type</span><span>{{ selectedDetail.experience_type || 'N/A' }}</span></div>
                <div class="kv-row"><span>Years Experience</span><span>{{ selectedDetail.years_experience ?? 0 }}</span></div>
                <div class="kv-row"><span>Travel Radius</span><span>{{ selectedDetail.travel_radius_km ?? 0 }} km</span></div>
              </div>
            </div>

            <div class="section-card">
              <div class="section-title">Submitted Documents</div>
              <div class="kv-list">
                <div class="kv-row" v-for="doc in documentRows" :key="doc.label">
                  <span>{{ doc.label }}</span>
                  <span class="doc-value">{{ doc.value_masked || 'Not uploaded' }}</span>
                  <span class="doc-state" :class="doc.provided ? 'ok' : 'missing'">{{ doc.provided ? 'Uploaded' : 'Missing' }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="section-card" style="margin-top:16px">
            <div class="section-title">Verification Checklist</div>
            <div class="checklist-section" v-for="section in checklistSections" :key="section.key">
              <div class="checklist-title">{{ section.title }}</div>
              <div class="checklist-items">
                <div class="checklist-item" v-for="item in section.items" :key="item.label">
                  <span>{{ item.label }}</span>
                  <span class="item-badge" :class="item.ok ? 'good' : 'bad'">{{ item.ok ? 'Pass' : 'Missing' }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="section-card" style="margin-top:16px">
            <div class="section-title">Manager Remarks</div>
            <textarea
              class="input"
              rows="3"
              v-model="managerNote"
              placeholder="Add review remarks, document mismatch notes, or decision rationale"
            ></textarea>

            <div class="action-row" style="margin-top:16px">
              <button class="btn btn-outline" @click="submitAction('send_for_verification')">Send for registration verification</button>
              <button class="btn btn-outline" style="color:var(--color-error);border-color:var(--color-error)" @click="submitAction('reject')">Reject Application</button>
              <button class="btn btn-primary" @click="submitAction('approve')">Approve Registration</button>
            </div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppIcon from '@/components/AppIcon.vue'
import { managerApi } from '@/services/api.js'

const activeTab = ref('All')
const tabs = ['All', 'Pending', 'Approved', 'Rejected']
const selectedApp = ref(null)
const selectedDetail = ref(null)
const applications = ref([])
const loading = ref(true)
const detailLoading = ref(false)
const managerNote = ref('')

function mapStatus(raw) {
  if (raw === 'approved') return 'Approved'
  if (raw === 'rejected') return 'Rejected'
  return 'Pending'
}

function mapApplication(c) {
  const name = c.name || 'Cook'
  return {
    id: c.id,
    name,
    initials: name.split(' ').map((w) => w[0]).join('').slice(0, 2).toUpperCase(),
    specialization: c.specialization || '',
    experience: c.experience_type || '',
    city: c.city || '',
    years: c.years_experience || 0,
    applied: c.applied_at ? new Date(c.applied_at).toLocaleDateString('en-IN') : '',
    status: mapStatus(c.verification_status),
    checks_completed: c.checks_completed || 0,
    checks_total: c.checks_total || 0,
  }
}

async function loadApplications() {
  loading.value = true
  try {
    const [pending, approved, rejected] = await Promise.all([
      managerApi.getVerifications('pending'),
      managerApi.getVerifications('approved'),
      managerApi.getVerifications('rejected'),
    ])

    const merged = [...(pending || []), ...(approved || []), ...(rejected || [])]
    const seen = new Set()
    applications.value = merged
      .filter((c) => {
        if (seen.has(c.id)) return false
        seen.add(c.id)
        return true
      })
      .map(mapApplication)
  } catch (e) {
    console.error('Failed to load verifications', e)
  } finally {
    loading.value = false
  }
}

onMounted(loadApplications)

const filtered = computed(() =>
  activeTab.value === 'All' ? applications.value : applications.value.filter(a => a.status === activeTab.value)
)

async function openDetail(app) {
  selectedApp.value = app
  detailLoading.value = true
  try {
    selectedDetail.value = await managerApi.getVerificationDetail(app.id)
  } catch (e) {
    console.error('Failed to load verification detail', e)
    selectedDetail.value = null
  } finally {
    detailLoading.value = false
  }
}

function closeDetail() {
  selectedApp.value = null
  selectedDetail.value = null
  managerNote.value = ''
}

const documentRows = computed(() => {
  const docs = selectedDetail.value?.documents || {}
  return Object.keys(docs).map((k) => ({ key: k, ...docs[k] }))
})

const checklistSections = computed(() => selectedDetail.value?.checklist || [])

function formatDate(v) {
  if (!v) return 'N/A'
  try {
    return new Date(v).toLocaleDateString('en-IN')
  } catch {
    return 'N/A'
  }
}

async function submitAction(action) {
  if (!selectedApp.value) return
  if (action === 'reject' && managerNote.value.trim().length < 5) {
    alert('Please provide a short rejection reason (minimum 5 characters).')
    return
  }
  try {
    await managerApi.verifyAction(selectedApp.value.id, {
      action,
      reason: managerNote.value.trim() || undefined,
    })
    closeDetail()
    await loadApplications()
  } catch (e) {
    alert(e.message || 'Action failed')
  }
}
</script>

<style scoped>
.verification-page { width: 100%; }

.filter-row { display: flex; gap: 8px; flex-wrap: wrap; }
.tab-btn { padding: 8px 18px; border-radius: var(--radius-full); font-size: 0.813rem; font-weight: 500; background: var(--color-bg-alt); color: var(--color-text-secondary); border: 1px solid var(--color-border); cursor: pointer; transition: all var(--transition-fast); }
.tab-btn.active { background: var(--color-primary); color: #fff; border-color: var(--color-primary); }

.app-list { display: flex; flex-direction: column; gap: 14px; }
.app-card { padding: 20px; border-radius: var(--radius-lg); cursor: pointer; transition: transform var(--transition-fast); }
.app-card:hover { transform: translateY(-2px); }

.app-header { display: flex; align-items: center; gap: 14px; }
.app-avatar { width: 44px; height: 44px; border-radius: 50%; background: var(--color-primary-light); color: var(--color-primary-dark); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.813rem; flex-shrink: 0; }
.app-avatar.lg { width: 56px; height: 56px; font-size: 1rem; }
.app-info { flex: 1; }

.app-meta { display: flex; gap: 16px; margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--color-border-light); }
.app-meta span { display: flex; align-items: center; gap: 5px; font-size: 0.75rem; color: var(--color-text-light); }

.badge-Pending { background: #FEF3C7; color: #D97706; }
.badge-Approved { background: #D1FAE5; color: #059669; }
.badge-Rejected { background: #FEE2E2; color: #DC2626; }
[class*="badge-"] { padding: 3px 10px; border-radius: var(--radius-full); font-size: 0.688rem; font-weight: 600; }

.detail-header { display: flex; align-items: flex-start; gap: 16px; }
.detail-head-text { flex: 1; }

.section-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.section-card {
  padding: 16px;
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-light);
  background: var(--color-bg-alt);
}

.section-title {
  font-size: 0.85rem;
  font-weight: 700;
  margin-bottom: 10px;
}

.kv-list { display: flex; flex-direction: column; gap: 8px; }

.kv-row {
  display: grid;
  grid-template-columns: 1.2fr 1.4fr auto;
  gap: 10px;
  align-items: center;
  border-bottom: 1px solid var(--color-border-light);
  padding-bottom: 8px;
}

.kv-row > span:first-child { font-size: 0.75rem; color: var(--color-text-light); }
.kv-row > span:nth-child(2) { font-size: 0.82rem; font-weight: 600; }

.doc-value {
  overflow-wrap: anywhere;
}

.doc-state {
  font-size: 0.68rem;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: var(--radius-full);
}

.doc-state.ok { background: #D1FAE5; color: #059669; }
.doc-state.missing { background: #FEE2E2; color: #DC2626; }

.checklist-section { margin-bottom: 14px; }
.checklist-title { font-size: 0.8rem; font-weight: 700; margin-bottom: 8px; }
.checklist-items { display: flex; flex-direction: column; gap: 8px; }

.checklist-item {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  border-bottom: 1px solid var(--color-border-light);
  padding-bottom: 8px;
}

.item-badge {
  font-size: 0.68rem;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: var(--radius-full);
}

.item-badge.good { background: #D1FAE5; color: #059669; }
.item-badge.bad { background: #FEE2E2; color: #DC2626; }

.btn-sm { padding: 6px 16px; font-size: 0.813rem; }
.action-row { display: flex; gap: 12px; justify-content: flex-end; }

@media (max-width: 900px) {
  .section-grid { grid-template-columns: 1fr; }
}

@media (max-width: 640px) {
  .app-meta { flex-wrap: wrap; gap: 10px; }
  .detail-header { flex-direction: column; }
  .kv-row { grid-template-columns: 1fr; gap: 4px; }
  .action-row { flex-wrap: wrap; justify-content: flex-start; }
}
</style>
