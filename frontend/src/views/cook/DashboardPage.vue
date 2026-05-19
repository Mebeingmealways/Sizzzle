<template>
  <div class="ck animate-fade-in">
    <!-- ═══ DARK BANNER with fire edge ═══ -->
    <div class="ck-banner">
      <div class="ck-banner-lottie" ref="bannerFireEl"></div>
      <div class="ck-banner-content">
        <div class="ck-chef-ring">
          <span>{{ user?.name?.charAt(0) || 'C' }}</span>
        </div>
        <div class="ck-banner-text">
          <h2>Welcome, Chef {{ user?.name?.split(' ')[0] || '' }}</h2>
          <p>Your kitchen awaits</p>
        </div>
        <div class="ck-status-chip" :class="{ online: isOnline }" @click="isOnline = !isOnline">
          <div class="ck-status-dot"></div>
          <span>{{ isOnline ? 'Available' : 'Offline' }}</span>
        </div>
      </div>
    </div>

    <!-- ═══ EARNINGS RING + STATS SIDE ═══ -->
    <div class="ck-earnings-row">
      <div class="ck-ring-card">
        <div class="ck-ring-wrap">
          <svg class="ck-ring-svg" viewBox="0 0 120 120">
            <circle cx="60" cy="60" r="52" fill="none" stroke="rgba(242,115,79,0.12)" stroke-width="8"/>
            <circle cx="60" cy="60" r="52" fill="none" stroke="url(#fireGrad)" stroke-width="8"
                    stroke-linecap="round" stroke-dasharray="327" :stroke-dashoffset="327"
                    transform="rotate(-90 60 60)"/>
            <defs>
              <linearGradient id="fireGrad" x1="0" y1="0" x2="1" y2="1">
                <stop offset="0%" stop-color="#F2734F"/>
                <stop offset="100%" stop-color="#FF9426"/>
              </linearGradient>
            </defs>
          </svg>
          <div class="ck-ring-inner">
            <span class="ck-ring-currency">₹</span>
            <span class="ck-ring-amount">{{ monthlyEarnings }}</span>
          </div>
        </div>
        <p class="ck-ring-label">This Month</p>
        <p class="ck-ring-target">{{ payoutFrequencyLabel }}</p>
      </div>

      <div class="ck-stats-col">
        <div class="ck-stat-card" v-for="m in metrics" :key="m.label">
          <div class="ck-stat-bar" :style="{ background: m.color }"></div>
          <div class="ck-stat-info">
            <span class="ck-stat-val">{{ m.value }}</span>
            <span class="ck-stat-lbl">{{ m.label }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ JOB TIMELINE ═══ -->
    <div class="ck-section">
      <div class="ck-section-head">
        <h3>Upcoming Jobs</h3>
        <router-link to="/cook/jobs" class="ck-link">View all →</router-link>
      </div>
      <div v-if="upcomingJobs.length" class="ck-job-list">
        <div v-for="job in upcomingJobs" :key="job.id" class="ck-job-item">
          <div>
            <strong>{{ job.customer_name || 'Customer' }}</strong>
            <p>{{ formatDate(job.date) }} • {{ job.time_slot || 'N/A' }}</p>
          </div>
          <span class="ck-job-status" :class="job.status">{{ toStatusLabel(job.status) }}</span>
        </div>
      </div>
      <div v-else class="ck-timeline-empty">
        <div class="ck-timeline-line"></div>
        <div class="ck-timeline-node">
          <div class="ck-node-dot"></div>
          <div class="ck-node-content">
            <div class="ck-node-lottie" ref="chefLottieEl"></div>
            <p>No upcoming jobs</p>
            <router-link to="/cook/availability" class="ck-set-avail">Set Availability</router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ QUICK ACCESS STRIP ═══ -->
    <div class="ck-quick">
      <router-link to="/cook/jobs" class="ck-quick-item">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        <span>All Jobs</span>
      </router-link>
      <router-link to="/cook/earnings" class="ck-quick-item">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
        <span>Earnings</span>
      </router-link>
      <router-link to="/cook/availability" class="ck-quick-item">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
        <span>Availability</span>
      </router-link>
      <router-link to="/cook/profile" class="ck-quick-item">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        <span>Profile</span>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import lottie from 'lottie-web'
import { useAuthStore } from '@/stores/auth'
import { cookApi } from '@/services/api'

const auth = useAuthStore()
const user = computed(() => auth.user)
const isOnline = ref(false)
const bannerFireEl = ref(null)
const chefLottieEl = ref(null)
const jobs = ref([])
const earnings = ref(null)

const statusStorageKey = computed(() => `sizzzle_cook_online_${auth.user?.id || 'me'}`)

function toStatusLabel(status) {
  return ({
    pending: 'Pending',
    accepted: 'Accepted',
    in_progress: 'In Progress',
    completed: 'Completed',
    cancelled: 'Cancelled'
  })[status] || status
}

function formatDate(iso) {
  if (!iso) return 'N/A'
  return new Date(`${iso}T00:00:00`).toLocaleDateString('en-IN', {
    month: 'short',
    day: 'numeric'
  })
}

const monthlyEarnings = computed(() => {
  const monthly = Number(earnings.value?.this_month || 0)
  if (monthly > 99999) return `${(monthly / 1000).toFixed(0)}K`
  return monthly.toLocaleString('en-IN')
})

const payoutFrequencyLabel = computed(() => {
  const value = earnings.value?.payout_frequency
  if (!value) return 'Payout details available in Earnings'
  return `Payout: ${String(value).replace('-', ' ')}`
})

const upcomingJobs = computed(() => {
  return jobs.value
    .filter((j) => ['pending', 'accepted', 'in_progress'].includes(j.status))
    .slice(0, 4)
})

watch(
  statusStorageKey,
  (key) => {
    const raw = localStorage.getItem(key)
    if (raw === null) return
    isOnline.value = raw === '1'
  },
  { immediate: true }
)

watch(isOnline, (next) => {
  localStorage.setItem(statusStorageKey.value, next ? '1' : '0')
})

onMounted(async () => {
  if (bannerFireEl.value) {
    lottie.loadAnimation({ container: bannerFireEl.value, renderer: 'svg', loop: true, autoplay: true, path: '/animations/fire.json' })
  }
  if (chefLottieEl.value) {
    lottie.loadAnimation({ container: chefLottieEl.value, renderer: 'svg', loop: true, autoplay: true, path: '/animations/chef-dancing.json' })
  }
  try {
    const [earningsData, jobsData] = await Promise.all([cookApi.getEarnings(), cookApi.getJobs()])
    earnings.value = earningsData || {}
    jobs.value = jobsData.jobs || jobsData || []

    const pendingOrAccepted = jobs.value.filter(j => j.status === 'pending' || j.status === 'accepted').length
    metrics.value[0].value = pendingOrAccepted
    metrics.value[0].pct = Math.min(100, pendingOrAccepted * 20)

    metrics.value[1].value = earningsData?.total_bookings || 0
    metrics.value[1].pct = Math.min(100, Number(earningsData?.total_bookings || 0) * 4)

    const rating = Number(earningsData?.rating || 0)
    metrics.value[2].value = rating.toFixed(1)
    metrics.value[2].pct = Math.min(100, (rating / 5) * 100)

    const completedWithReviews = jobs.value.filter(j => j.status === 'completed' && j.review).length
    metrics.value[3].value = completedWithReviews
    metrics.value[3].pct = Math.min(100, completedWithReviews * 25)
  } catch (_) {}
})

const metrics = ref([
  { label: 'Pending', value: '—', pct: 0, color: '#F2734F' },
  { label: 'Completed', value: '—', pct: 0, color: '#2DB67D' },
  { label: 'Rating', value: '—', pct: 0, color: '#F59E0B' },
  { label: 'Reviews', value: '—', pct: 0, color: '#6366F1' }
])
</script>

<style scoped>
.ck { display: flex; flex-direction: column; gap: 20px; width: 100%; }

/* ═══ DARK BANNER ═══ */
.ck-banner {
  position: relative; overflow: hidden;
  border-radius: 20px;
  background: linear-gradient(135deg, #1A1A2E 0%, #16213E 50%, #0F3460 100%);
  padding: 28px 24px;
  color: #fff;
}
.ck-banner-lottie {
  position: absolute; bottom: -10px; right: -10px;
  width: 140px; height: 140px;
  opacity: 0.5;
  pointer-events: none; z-index: 0;
}

.ck-banner-content {
  position: relative; z-index: 1;
  display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
}
.ck-chef-ring {
  width: 56px; height: 56px; border-radius: 50%;
  background: linear-gradient(135deg, #F2734F, #FF9426);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.3rem; font-weight: 800;
  box-shadow: 0 0 24px rgba(242, 115, 79, 0.5);
  flex-shrink: 0;
}
.ck-banner-text { flex: 1; }
.ck-banner-text h2 { font-size: 1.15rem; font-weight: 800; }
.ck-banner-text p { font-size: 0.78rem; opacity: 0.6; margin-top: 2px; }

.ck-status-chip {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 18px; border-radius: 100px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.12);
  font-size: 0.75rem; font-weight: 600;
  cursor: pointer; transition: all 0.2s ease;
  user-select: none;
}
.ck-status-chip:hover { background: rgba(255,255,255,0.14); }
.ck-status-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: #666; transition: all 0.3s ease;
}
.ck-status-chip.online .ck-status-dot {
  background: #10B981;
  box-shadow: 0 0 10px rgba(16, 185, 129, 0.6);
}

/* ═══ EARNINGS ROW ═══ */
.ck-earnings-row {
  display: grid; grid-template-columns: auto 1fr; gap: 16px;
  align-items: start;
}

.ck-ring-card {
  padding: 24px 28px;
  border-radius: 20px;
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border-light);
  text-align: center;
}
.ck-ring-wrap { position: relative; width: 120px; height: 120px; margin: 0 auto 12px; }
.ck-ring-svg { width: 100%; height: 100%; }
.ck-ring-inner {
  position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center; gap: 2px;
}
.ck-ring-currency { font-size: 1rem; color: var(--color-text-light); font-weight: 500; }
.ck-ring-amount { font-size: 2rem; font-weight: 800; color: var(--color-text); }
.ck-ring-label { font-size: 0.78rem; font-weight: 600; color: var(--color-text); }
.ck-ring-target { font-size: 0.7rem; color: var(--color-text-light); margin-top: 2px; }

.ck-stats-col { display: flex; flex-direction: column; gap: 10px; }
.ck-stat-card {
  display: flex; align-items: center; gap: 14px;
  padding: 16px 18px;
  border-radius: 14px;
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border-light);
}
.ck-stat-bar {
  width: 4px; height: 32px; border-radius: 2px; flex-shrink: 0;
}
.ck-stat-val { font-size: 1.1rem; font-weight: 800; display: block; }
.ck-stat-lbl { font-size: 0.68rem; color: var(--color-text-light); display: block; }

/* ═══ TIMELINE ═══ */
.ck-section {
  border-radius: 20px;
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border-light);
  padding: 22px 24px;
}

.ck-job-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ck-job-item {
  border: 1px solid var(--color-border-light);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.ck-job-item p {
  margin-top: 3px;
  font-size: 0.76rem;
  color: var(--color-text-light);
}

.ck-job-status {
  font-size: 0.7rem;
  font-weight: 700;
  border-radius: 999px;
  padding: 4px 10px;
  white-space: nowrap;
}

.ck-job-status.pending { background: #FEF3C7; color: #D97706; }
.ck-job-status.accepted { background: #DBEAFE; color: #2563EB; }
.ck-job-status.in_progress { background: #E0E7FF; color: #4F46E5; }
.ck-section-head {
  display: flex; justify-content: space-between; align-items: center;
  margin-bottom: 18px;
}
.ck-section-head h3 { font-size: 0.95rem; font-weight: 700; }
.ck-link { font-size: 0.78rem; color: #F2734F; font-weight: 600; }

.ck-timeline-empty { position: relative; padding-left: 28px; }
.ck-timeline-line {
  position: absolute; left: 8px; top: 0; bottom: 0;
  width: 2px; background: linear-gradient(180deg, rgba(242,115,79,0.3), transparent);
}
.ck-timeline-node { position: relative; }
.ck-node-dot {
  position: absolute; left: -24px; top: 14px;
  width: 12px; height: 12px; border-radius: 50%;
  background: var(--color-surface-raised);
  border: 3px solid #F2734F;
}
.ck-node-content {
  display: flex; flex-direction: column; align-items: center;
  padding: 24px 16px; text-align: center; gap: 8px;
}
.ck-node-lottie { width: 100px; height: 100px; }
.ck-node-content p { font-size: 0.85rem; color: var(--color-text-light); }
.ck-set-avail {
  padding: 8px 20px; border-radius: 100px;
  border: 1.5px solid rgba(242,115,79,0.3);
  color: #F2734F; font-size: 0.78rem; font-weight: 600;
  transition: all 0.2s ease;
}
.ck-set-avail:hover { background: rgba(242,115,79,0.06); }

/* ═══ QUICK STRIP ═══ */
.ck-quick { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
.ck-quick-item {
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  padding: 18px 10px;
  border-radius: 14px;
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border-light);
  color: var(--color-text-secondary);
  font-size: 0.72rem; font-weight: 600;
  transition: all 0.25s ease; text-decoration: none;
}
.ck-quick-item:hover { transform: translateY(-3px); color: #F2734F; box-shadow: 0 6px 20px rgba(0,0,0,0.06); }

@media (max-width: 640px) {
  .ck-banner { padding: 22px 18px; }
  .ck-earnings-row { grid-template-columns: 1fr; }
  .ck-stats-col { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
  .ck-quick { grid-template-columns: repeat(2, 1fr); }
}
</style>
