<template>
  <div class="mg animate-fade-in">
    <!-- ═══ HEADER with embedded gauges ═══ -->
    <div class="mg-header">
      <div class="mg-header-top">
        <div>
          <h2 class="mg-title">Operations Hub</h2>
          <p class="mg-subtitle">Regional oversight &amp; field ops</p>
        </div>
        <div class="mg-region-tag">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
          {{ regionLabel }}
        </div>
      </div>
      <div class="mg-gauges">
        <div class="mg-gauge" v-for="g in gauges" :key="g.label">
          <svg class="mg-gauge-svg" viewBox="0 0 80 80">
            <circle cx="40" cy="40" r="34" fill="none" stroke="rgba(8,145,178,0.1)" stroke-width="5"/>
            <circle cx="40" cy="40" r="34" fill="none" :stroke="g.color" stroke-width="5"
                    stroke-linecap="round" stroke-dasharray="213.6"
                    :stroke-dashoffset="213.6 - (213.6 * g.pct / 100)"
                    transform="rotate(-90 40 40)"/>
          </svg>
          <div class="mg-gauge-inner">
            <span class="mg-gauge-val">{{ g.value }}</span>
          </div>
          <span class="mg-gauge-label">{{ g.label }}</span>
        </div>
      </div>
    </div>

    <!-- ═══ KANBAN COLUMNS ═══ -->
    <div class="mg-kanban">
      <!-- Verifications Column -->
      <div class="mg-col">
        <div class="mg-col-head">
          <div class="mg-col-dot teal"></div>
          <h3>Verifications</h3>
          <span class="mg-col-count">{{ pendingVerifications.length }}</span>
        </div>
        <div class="mg-col-body">
          <div v-if="pendingVerifications.length" class="mg-col-list">
            <div class="mg-list-item" v-for="v in pendingVerifications.slice(0, 3)" :key="v.id">
              <strong>{{ v.name || 'Cook' }}</strong>
              <span>{{ v.specialization || 'Specialization pending' }}</span>
            </div>
          </div>
          <div v-else class="mg-col-empty">
            <div class="mg-col-lottie" ref="mgrLottieEl"></div>
            <p>All clear</p>
            <router-link to="/manager/verification" class="mg-col-link">Open Queue →</router-link>
          </div>
        </div>
      </div>

      <!-- Complaints Column -->
      <div class="mg-col">
        <div class="mg-col-head">
          <div class="mg-col-dot orange"></div>
          <h3>Complaints</h3>
          <span class="mg-col-count">{{ openComplaints.length }}</span>
        </div>
        <div class="mg-col-body">
          <div v-if="openComplaints.length" class="mg-col-list">
            <div class="mg-list-item" v-for="c in openComplaints.slice(0, 3)" :key="c.id">
              <strong>{{ c.subject || 'Complaint' }}</strong>
              <span>{{ c.priority || 'Medium' }} • {{ c.status || 'Open' }}</span>
            </div>
          </div>
          <div v-else class="mg-col-empty">
            <p>No complaints</p>
            <router-link to="/manager/complaints" class="mg-col-link">View History →</router-link>
          </div>
        </div>
      </div>

      <!-- Cooks Column -->
      <div class="mg-col">
        <div class="mg-col-head">
          <div class="mg-col-dot green"></div>
          <h3>Active Cooks</h3>
          <span class="mg-col-count">{{ activeCooks.length }}</span>
        </div>
        <div class="mg-col-body">
          <div v-if="activeCooks.length" class="mg-col-list">
            <div class="mg-list-item" v-for="cook in activeCooks.slice(0, 3)" :key="cook.id">
              <strong>{{ cook.name || 'Cook' }}</strong>
              <span>{{ Number(cook.rating || 0).toFixed(1) }} ★ • {{ cook.total_jobs || 0 }} jobs</span>
            </div>
          </div>
          <div v-else class="mg-col-empty">
            <p>No cooks assigned</p>
            <router-link to="/manager/cooks" class="mg-col-link">Manage Cooks →</router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ ACTION TILES ═══ -->
    <div class="mg-actions">
      <router-link to="/manager/verification" class="mg-action-tile">
        <div class="mg-action-icon teal-bg">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#fff" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
        </div>
        <span>Verification Queue</span>
      </router-link>
      <router-link to="/manager/cooks" class="mg-action-tile">
        <div class="mg-action-icon green-bg">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#fff" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        </div>
        <span>Manage Cooks</span>
      </router-link>
      <router-link to="/manager/complaints" class="mg-action-tile">
        <div class="mg-action-icon orange-bg">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="#fff" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
        </div>
        <span>Complaints</span>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import lottie from 'lottie-web'
import { managerApi, profileApi } from '@/services/api.js'

const mgrLottieEl = ref(null)
const profile = ref(null)
const pendingVerifications = ref([])
const complaints = ref([])
const cookMetrics = ref([])

onMounted(() => {
  if (mgrLottieEl.value) {
    lottie.loadAnimation({ container: mgrLottieEl.value, renderer: 'svg', loop: true, autoplay: true, path: '/animations/cooking-loader.json' })
  }

  loadDashboard()
})

async function loadDashboard() {
  try {
    const [profileData, verifications, complaintData, cookData] = await Promise.all([
      profileApi.get(),
      managerApi.getPendingVerifications(),
      managerApi.getComplaints(),
      managerApi.getCookMetrics()
    ])

    profile.value = profileData
    pendingVerifications.value = verifications || []
    complaints.value = complaintData || []
    cookMetrics.value = cookData || []

    const approved = cookMetrics.value.filter(c => c.verification_status === 'approved')
    const open = complaints.value.filter(c => ['Open', 'Investigating', 'Escalated'].includes(c.status))
    const avgRating = approved.length
      ? approved.reduce((sum, c) => sum + Number(c.rating || 0), 0) / approved.length
      : 0

    gauges.value[0].value = pendingVerifications.value.length
    gauges.value[0].pct = Math.min(100, pendingVerifications.value.length * 20)

    gauges.value[1].value = approved.length
    gauges.value[1].pct = Math.min(100, approved.length * 10)

    gauges.value[2].value = open.length
    gauges.value[2].pct = Math.min(100, open.length * 20)

    gauges.value[3].value = avgRating.toFixed(1)
    gauges.value[3].pct = Math.min(100, (avgRating / 5) * 100)
  } catch (error) {
    console.error('Failed to load manager dashboard', error)
  }
}

const openComplaints = computed(() => complaints.value.filter(c => ['Open', 'Investigating', 'Escalated'].includes(c.status)))
const activeCooks = computed(() => cookMetrics.value.filter(c => c.verification_status === 'approved'))
const regionLabel = computed(() => profile.value?.address || 'All Regions')

const gauges = ref([
  { label: 'Pending', value: '—', pct: 0, color: '#0891B2' },
  { label: 'Active', value: '—', pct: 0, color: '#2DB67D' },
  { label: 'Open', value: '—', pct: 0, color: '#EF4444' },
  { label: 'Rating', value: '—', pct: 0, color: '#F59E0B' }
])
</script>

<style scoped>
.mg { display: flex; flex-direction: column; gap: 18px; width: 100%; }

/* ═══ HEADER ═══ */
.mg-header {
  border-radius: 20px;
  background: linear-gradient(145deg, #0C4A6E, #0E7490, #0891B2);
  padding: 28px 26px 20px;
  color: #fff;
}
.mg-header-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px; }
.mg-title { font-size: 1.3rem; font-weight: 800; }
.mg-subtitle { font-size: 0.78rem; opacity: 0.65; margin-top: 2px; }
.mg-region-tag {
  display: flex; align-items: center; gap: 6px;
  padding: 6px 14px; border-radius: 100px;
  background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.15);
  font-size: 0.72rem; font-weight: 600;
}

.mg-gauges { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.mg-gauge { display: flex; flex-direction: column; align-items: center; position: relative; }
.mg-gauge-svg { width: 72px; height: 72px; }
.mg-gauge-inner {
  position: absolute; top: 0; left: 50%; transform: translateX(-50%);
  width: 72px; height: 72px;
  display: flex; align-items: center; justify-content: center;
}
.mg-gauge-val { font-size: 1.1rem; font-weight: 800; }
.mg-gauge-label { font-size: 0.65rem; opacity: 0.7; margin-top: 4px; font-weight: 500; }

/* ═══ KANBAN ═══ */
.mg-kanban { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
.mg-col {
  border-radius: 16px;
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border-light);
  overflow: hidden;
}
.mg-col-head {
  display: flex; align-items: center; gap: 8px;
  padding: 14px 18px;
  border-bottom: 1px solid var(--color-border-light);
}
.mg-col-dot { width: 8px; height: 8px; border-radius: 50%; }
.mg-col-dot.teal { background: #0891B2; }
.mg-col-dot.orange { background: #F59E0B; }
.mg-col-dot.green { background: #2DB67D; }
.mg-col-head h3 { font-size: 0.82rem; font-weight: 700; flex: 1; }
.mg-col-count {
  font-size: 0.68rem; font-weight: 700;
  padding: 2px 10px; border-radius: 100px;
  background: var(--color-bg-alt); color: var(--color-text-light);
}
.mg-col-body { padding: 16px; min-height: 120px; }
.mg-col-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.mg-list-item {
  border: 1px solid var(--color-border-light);
  border-radius: 10px;
  padding: 9px 10px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.mg-list-item strong {
  font-size: 0.78rem;
}
.mg-list-item span {
  font-size: 0.7rem;
  color: var(--color-text-light);
}
.mg-col-empty {
  display: flex; flex-direction: column; align-items: center;
  gap: 8px; padding: 16px 8px; text-align: center;
}
.mg-col-lottie { width: 80px; height: 80px; }
.mg-col-empty p { font-size: 0.78rem; color: var(--color-text-light); }
.mg-col-link { font-size: 0.72rem; font-weight: 600; color: #0891B2; }

/* ═══ ACTION TILES ═══ */
.mg-actions { display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }
.mg-action-tile {
  display: flex; align-items: center; gap: 12px;
  padding: 16px 18px;
  border-radius: 14px;
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border-light);
  text-decoration: none; color: var(--color-text);
  font-size: 0.82rem; font-weight: 700;
  transition: all 0.25s ease;
}
.mg-action-tile:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.06); }
.mg-action-icon {
  width: 38px; height: 38px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.teal-bg { background: linear-gradient(135deg, #0891B2, #0E7490); }
.green-bg { background: linear-gradient(135deg, #2DB67D, #1A8F5F); }
.orange-bg { background: linear-gradient(135deg, #F59E0B, #D97706); }

@media (max-width: 768px) {
  .mg-kanban { grid-template-columns: 1fr; }
  .mg-actions { grid-template-columns: 1fr; }
  .mg-gauges { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 480px) {
  .mg-header { padding: 22px 18px 16px; }
  .mg-gauges { gap: 8px; }
  .mg-gauge-svg { width: 60px; height: 60px; }
  .mg-gauge-inner { width: 60px; height: 60px; }
  .mg-gauge-val { font-size: 0.9rem; }
}
</style>
