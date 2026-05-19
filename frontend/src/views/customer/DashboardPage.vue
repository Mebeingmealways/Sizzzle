<template>
  <div class="cd animate-fade-in">
    <!-- ═══ HERO: curved gradient card ═══ -->
    <div class="cd-hero">
      <div class="cd-hero-curve"></div>
      <div class="cd-hero-inner">
        <div class="cd-avatar-wrap">
          <div class="cd-avatar">{{ auth.user?.name?.charAt(0) || 'U' }}</div>
          <div class="cd-avatar-pulse"></div>
        </div>
        <div class="cd-hero-text">
          <span class="cd-hello">{{ greeting }} 👋</span>
          <h2 class="cd-name">{{ auth.user?.name?.split(' ')[0] || 'there' }}</h2>
          <p class="cd-prompt">What are you craving today?</p>
        </div>
        <router-link to="/customer/book" class="cd-hero-cta">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        </router-link>
      </div>
    </div>

    <!-- ═══ ROUND ACTION CIRCLES (app-style) ═══ -->
    <div class="cd-actions">
      <router-link to="/customer/book" class="cd-act">
        <div class="cd-act-icon" style="background: linear-gradient(135deg, #2DB67D, #1A8F5F)">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#fff" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
        </div>
        <span>Book</span>
      </router-link>
      <router-link to="/customer/bookings" class="cd-act">
        <div class="cd-act-icon" style="background: linear-gradient(135deg, #F2734F, #D4552E)">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#fff" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
        </div>
        <span>Orders</span>
      </router-link>
      <router-link to="/customer/preferences" class="cd-act">
        <div class="cd-act-icon" style="background: linear-gradient(135deg, #E85D3A, #C7412A)">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#fff" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
        </div>
        <span>Taste</span>
      </router-link>
      <router-link to="/customer/profile" class="cd-act">
        <div class="cd-act-icon" style="background: linear-gradient(135deg, #6366F1, #4F46E5)">
          <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="#fff" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        </div>
        <span>Profile</span>
      </router-link>
    </div>

    <!-- ═══ CTA BANNER (full width) ═══ -->
    <div class="cd-cta-banner">
      <div class="cd-cta-text">
        <h3>Ready to eat homemade?</h3>
        <p>Book a verified home cook in 3 simple steps</p>
      </div>
      <router-link to="/customer/book" class="cd-cta-btn">Book Now →</router-link>
    </div>

    <!-- ═══ RECENT BOOKINGS ═══ -->
    <div class="cd-card">
      <div class="cd-card-head">
        <h3>Recent Bookings</h3>
        <router-link to="/customer/bookings" class="cd-see-all">View all →</router-link>
      </div>
      <div v-if="bookings.length === 0 && !loading" class="cd-empty-state">
        <div class="cd-empty-lottie" ref="emptyLottieEl"></div>
        <p class="cd-empty-text">No bookings yet</p>
        <p class="cd-empty-sub">Book your first cook and discover amazing homemade food</p>
        <router-link to="/customer/book" class="cd-empty-btn">Get Started</router-link>
      </div>
      <div v-else style="padding:16px 24px 24px">
        <div v-for="b in bookings.slice(0,3)" :key="b.id" style="display:flex;justify-content:space-between;align-items:center;padding:12px 0;border-bottom:1px solid var(--color-border-light)">
          <div>
            <div class="fw-600 text-sm">{{ b.cook_name || 'Cook' }}</div>
            <div class="text-xs text-muted">{{ (b.dishes || []).map(d => d.name).join(', ') }}</div>
          </div>
          <span class="text-sm fw-600" style="color:var(--color-primary)">{{ displayStatus(b.status, b) }}</span>
        </div>
      </div>
    </div>

    <!-- ═══ STATS ROW ═══ -->
    <div class="cd-stats">
      <div class="cd-stat" v-for="s in stats" :key="s.label">
        <div class="cd-stat-num">{{ s.value }}</div>
        <div class="cd-stat-label">{{ s.label }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import lottie from 'lottie-web'
import { useAuthStore } from '../../stores/auth'
import { bookingApi } from '../../services/api.js'

const auth = useAuthStore()
const emptyLottieEl = ref(null)
const bookings = ref([])
const loading = ref(true)

const slotEndTimes = {
  breakfast: '09:00',
  lunch: '13:00',
  dinner: '20:00'
}

function parseBookingEndDate(booking) {
  if (!booking?.date) return null
  const date = new Date(booking.date)
  const endTime = slotEndTimes[booking.time_slot]
  if (endTime) {
    const [hours, minutes] = endTime.split(':').map(Number)
    date.setHours(hours, minutes, 0, 0)
    return date
  }
  date.setHours(23, 59, 59, 999)
  return date
}

function isBookingInactive(booking) {
  if (!booking || ['completed', 'cancelled'].includes(booking.status)) return false
  const endDate = parseBookingEndDate(booking)
  if (!endDate) return false
  return new Date() > endDate
}

function displayStatus(status, booking) {
  if (isBookingInactive(booking)) return 'Inactive'
  const statusMap = {
    pending: 'Upcoming',
    accepted: 'Upcoming',
    in_progress: 'In Progress',
    completed: 'Completed',
    cancelled: 'Cancelled'
  }
  return statusMap[status] || status
}

onMounted(async () => {
  if (emptyLottieEl.value) {
    lottie.loadAnimation({ container: emptyLottieEl.value, renderer: 'svg', loop: true, autoplay: true, path: '/animations/foodie.json' })
  }
  try {
    bookings.value = await bookingApi.list()
  } catch (e) { /* empty */ }
  loading.value = false
})

const greeting = computed(() => {
  const h = new Date().getHours()
  if (h < 12) return 'Good morning'
  if (h < 17) return 'Good afternoon'
  return 'Good evening'
})

const stats = computed(() => {
  const total = bookings.value.length
  const upcoming = bookings.value.filter(b => displayStatus(b.status, b) === 'Upcoming').length
  const completed = bookings.value.filter(b => b.status === 'completed').length
  return [
    { label: 'Bookings', value: total },
    { label: 'Upcoming', value: upcoming },
    { label: 'Completed', value: completed },
    { label: 'Avg Rating', value: '—' }
  ]
})
</script>

<style scoped>
.cd { display: flex; flex-direction: column; gap: 20px; width: 100%; }

/* ═══ HERO ═══ */
.cd-hero {
  position: relative;
  border-radius: 24px;
  overflow: hidden;
  background: linear-gradient(140deg, #2DB67D 0%, #1A8F5F 50%, #157A50 100%);
  padding: 32px 28px;
  color: #fff;
}
.cd-hero-curve {
  position: absolute; bottom: -40px; left: -10%; right: -10%;
  height: 80px;
  background: var(--color-bg);
  border-radius: 50% 50% 0 0;
}
.cd-hero-inner {
  position: relative; z-index: 1;
  display: flex; align-items: center; gap: 18px;
}
.cd-avatar-wrap { position: relative; flex-shrink: 0; }
.cd-avatar {
  width: 60px; height: 60px; border-radius: 50%;
  background: rgba(255,255,255,0.2);
  backdrop-filter: blur(10px);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.4rem; font-weight: 700;
  border: 2px solid rgba(255,255,255,0.3);
}
.cd-avatar-pulse {
  position: absolute; inset: -4px; border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.2);
  animation: cd-pulse 2s ease-in-out infinite;
}
@keyframes cd-pulse { 0%,100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.1); opacity: 0.4; } }

.cd-hero-text { flex: 1; }
.cd-hello { font-size: 0.8rem; opacity: 0.85; font-weight: 500; }
.cd-name { font-size: 1.5rem; font-weight: 800; margin: 2px 0; }
.cd-prompt { font-size: 0.8rem; opacity: 0.75; }

.cd-hero-cta {
  width: 48px; height: 48px; border-radius: 50%;
  background: rgba(255,255,255,0.2); backdrop-filter: blur(10px);
  display: flex; align-items: center; justify-content: center;
  border: 2px solid rgba(255,255,255,0.3);
  transition: all 0.2s ease; flex-shrink: 0;
}
.cd-hero-cta:hover { background: rgba(255,255,255,0.35); transform: scale(1.08); }

/* ═══ ACTION CIRCLES ═══ */
.cd-actions {
  display: flex; justify-content: center; gap: 24px;
  margin: -8px 0 4px;
}
.cd-act {
  display: flex; flex-direction: column; align-items: center; gap: 8px;
  text-decoration: none;
}
.cd-act-icon {
  width: 58px; height: 58px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  box-shadow: 0 6px 20px rgba(0,0,0,0.12);
  transition: all 0.25s ease;
}
.cd-act:hover .cd-act-icon { transform: translateY(-4px) scale(1.06); box-shadow: 0 10px 28px rgba(0,0,0,0.18); }
.cd-act span { font-size: 0.72rem; font-weight: 600; color: var(--color-text-secondary); }

/* ═══ CTA BANNER ═══ */
.cd-cta-banner {
  display: flex; align-items: center; justify-content: space-between;
  padding: 20px 24px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(45, 182, 125, 0.08), rgba(26, 143, 95, 0.04));
  border: 1px solid rgba(45, 182, 125, 0.15);
  gap: 16px; flex-wrap: wrap;
}
.cd-cta-text h3 { font-size: 0.95rem; font-weight: 700; color: var(--color-text); }
.cd-cta-text p { font-size: 0.78rem; color: var(--color-text-light); margin-top: 2px; }
.cd-cta-btn {
  padding: 10px 24px; border-radius: 100px;
  background: linear-gradient(135deg, #2DB67D, #1A8F5F);
  color: #fff; font-size: 0.82rem; font-weight: 700;
  white-space: nowrap; transition: all 0.2s ease;
  box-shadow: 0 4px 16px rgba(45, 182, 125, 0.25);
}
.cd-cta-btn:hover { transform: translateY(-2px); box-shadow: 0 6px 24px rgba(45, 182, 125, 0.35); }

/* ═══ CARD ═══ */
.cd-card {
  border-radius: 20px;
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border-light);
  overflow: hidden;
}
.cd-card-head {
  display: flex; justify-content: space-between; align-items: center;
  padding: 20px 24px 0;
}
.cd-card-head h3 { font-size: 0.95rem; font-weight: 700; }
.cd-see-all { font-size: 0.78rem; color: #2DB67D; font-weight: 600; }

/* ═══ EMPTY STATE ═══ */
.cd-empty-state {
  display: flex; flex-direction: column; align-items: center;
  padding: 40px 24px 36px; text-align: center;
}
.cd-empty-lottie { width: 160px; height: 160px; margin-bottom: 8px; }
.cd-empty-text { font-size: 1rem; font-weight: 700; color: var(--color-text); }
.cd-empty-sub { font-size: 0.8rem; color: var(--color-text-light); margin: 6px 0 18px; max-width: 300px; }
.cd-empty-btn {
  padding: 10px 28px; border-radius: 100px;
  background: var(--color-primary); color: #fff;
  font-size: 0.82rem; font-weight: 700;
  transition: all 0.2s ease;
}
.cd-empty-btn:hover { transform: translateY(-2px); }

/* ═══ STATS ═══ */
.cd-stats {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;
}
.cd-stat {
  text-align: center;
  padding: 16px 8px;
  border-radius: 16px;
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border-light);
}
.cd-stat-num { font-size: 1.3rem; font-weight: 800; color: #2DB67D; }
.cd-stat-label { font-size: 0.65rem; color: var(--color-text-light); margin-top: 2px; }

@media (max-width: 640px) {
  .cd-hero { padding: 24px 20px; }
  .cd-hero-inner { flex-wrap: wrap; }
  .cd-actions { gap: 16px; }
  .cd-act-icon { width: 50px; height: 50px; }
  .cd-stats { grid-template-columns: repeat(2, 1fr); }
  .cd-name { font-size: 1.2rem; }
}
</style>
