<template>
  <div class="ad animate-fade-in">
    <!-- ═══ STATUS BAR (terminal/console style) ═══ -->
    <div class="ad-status-bar">
      <div class="ad-status-left">
        <div class="ad-terminal-dot green"></div>
        <span class="ad-mono">SYSTEM ONLINE</span>
        <div class="ad-separator"></div>
        <span class="ad-mono dim">ADMIN CONSOLE v1.0</span>
      </div>
      <div class="ad-status-right">
        <span class="ad-mono dim">{{ currentTime }}</span>
        <div class="ad-live-dot"></div>
        <span class="ad-mono" style="color: #10B981">LIVE</span>
      </div>
    </div>

    <!-- ═══ COMPACT DATA BLOCKS ═══ -->
    <div class="ad-data-blocks">
      <div v-for="s in stats" :key="s.label" class="ad-block">
        <div class="ad-block-header">
          <span class="ad-block-label">{{ s.label }}</span>
          <div class="ad-block-indicator" :style="{ background: s.color }"></div>
        </div>
        <div class="ad-block-value">{{ s.value }}</div>
        <div class="ad-block-bar">
          <div class="ad-block-bar-fill" :style="{ width: s.pct + '%', background: s.color }"></div>
        </div>
      </div>
    </div>

    <!-- ═══ TWO-PANEL GRID ═══ -->
    <div class="ad-panels">
      <!-- Activity Feed -->
      <div class="ad-panel">
        <div class="ad-panel-head">
          <div class="ad-panel-indicator indigo"></div>
          <h3>Activity Feed</h3>
        </div>
        <div class="ad-feed-empty">
          <div class="ad-feed-lottie" ref="adminLottieEl"></div>
          <p class="ad-feed-msg">No activity to display</p>
        </div>
      </div>

      <!-- Platform Health -->
      <div class="ad-panel">
        <div class="ad-panel-head">
          <div class="ad-panel-indicator green"></div>
          <h3>Platform Health</h3>
        </div>
        <div class="ad-health-list">
          <div class="ad-health-item" v-for="h in health" :key="h.label">
            <div class="ad-health-top">
              <span>{{ h.label }}</span>
              <span class="ad-mono" :style="{ color: h.color }">{{ h.value }}%</span>
            </div>
            <div class="ad-health-track">
              <div class="ad-health-fill" :style="{ width: h.value + '%', background: h.color }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ═══ COMMAND GRID (action tiles) ═══ -->
    <div class="ad-commands">
      <router-link to="/admin/managers" class="ad-cmd">
        <div class="ad-cmd-icon indigo">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        </div>
        <div class="ad-cmd-text">
          <span class="ad-cmd-name">Managers</span>
          <span class="ad-cmd-desc">Manage regional team</span>
        </div>
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" class="ad-cmd-arrow"><polyline points="9 18 15 12 9 6"/></svg>
      </router-link>
      <router-link to="/admin/analytics" class="ad-cmd">
        <div class="ad-cmd-icon green">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
        </div>
        <div class="ad-cmd-text">
          <span class="ad-cmd-name">Analytics</span>
          <span class="ad-cmd-desc">Revenue & metrics</span>
        </div>
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" class="ad-cmd-arrow"><polyline points="9 18 15 12 9 6"/></svg>
      </router-link>
      <router-link to="/admin/disputes" class="ad-cmd">
        <div class="ad-cmd-icon red">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
        </div>
        <div class="ad-cmd-text">
          <span class="ad-cmd-name">Disputes</span>
          <span class="ad-cmd-desc">Escalated issues</span>
        </div>
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" class="ad-cmd-arrow"><polyline points="9 18 15 12 9 6"/></svg>
      </router-link>
      <router-link to="/admin/policies" class="ad-cmd">
        <div class="ad-cmd-icon amber">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="#fff" stroke-width="2"><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><rect x="8" y="2" width="8" height="4" rx="1"/></svg>
        </div>
        <div class="ad-cmd-text">
          <span class="ad-cmd-name">Policies</span>
          <span class="ad-cmd-desc">Platform rules</span>
        </div>
        <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" class="ad-cmd-arrow"><polyline points="9 18 15 12 9 6"/></svg>
      </router-link>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import lottie from 'lottie-web'
import { adminApi } from '@/services/api.js'

const currentTime = ref('')
let timer = null
const adminLottieEl = ref(null)

function updateTime() {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('en-US', { hour12: false })
}

onMounted(async () => {
  updateTime(); timer = setInterval(updateTime, 1000)
  if (adminLottieEl.value) {
    lottie.loadAnimation({ container: adminLottieEl.value, renderer: 'svg', loop: true, autoplay: true, path: '/animations/businessman.json' })
  }
  try {
    const data = await adminApi.getStats()
    stats.value = [
      { label: 'TOTAL USERS', value: data.total_users || 0, color: '#6366F1', pct: 100 },
      { label: 'ACTIVE COOKS', value: data.total_cooks || 0, color: '#F2734F', pct: Math.round((data.total_cooks || 0) / Math.max(data.total_users || 1, 1) * 100) },
      { label: 'BOOKINGS', value: data.total_bookings || 0, color: '#2DB67D', pct: 0 },
      { label: 'DISPUTES', value: data.total_complaints || 0, color: '#EF4444', pct: 0 }
    ]
    health.value[0].value = data.total_bookings > 0 ? Math.round(((data.completed_bookings || 0) / data.total_bookings) * 100) : 0
  } catch (e) { /* use defaults */ }
})
onUnmounted(() => clearInterval(timer))

const stats = ref([
  { label: 'TOTAL USERS', value: '—', color: '#6366F1', pct: 0 },
  { label: 'ACTIVE COOKS', value: '—', color: '#F2734F', pct: 0 },
  { label: 'BOOKINGS', value: '—', color: '#2DB67D', pct: 0 },
  { label: 'DISPUTES', value: '—', color: '#EF4444', pct: 0 }
])

const health = ref([
  { label: 'Booking Success', value: 0, color: '#6366F1' },
  { label: 'Cook Retention', value: 0, color: '#2DB67D' },
  { label: 'User Satisfaction', value: 0, color: '#F59E0B' },
  { label: 'Platform Uptime', value: 100, color: '#10B981' }
])
</script>

<style scoped>
.ad { display: flex; flex-direction: column; gap: 16px; width: 100%; }
.ad-mono { font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace; font-size: 0.72rem; letter-spacing: 0.05em; }
.ad-mono.dim { opacity: 0.5; }

/* ═══ STATUS BAR ═══ */
.ad-status-bar {
  display: flex; justify-content: space-between; align-items: center;
  padding: 12px 20px;
  border-radius: 12px;
  background: linear-gradient(135deg, #1E1B4B, #312E81);
  color: #fff;
}
.ad-status-left, .ad-status-right { display: flex; align-items: center; gap: 10px; }
.ad-terminal-dot { width: 8px; height: 8px; border-radius: 50%; }
.ad-terminal-dot.green { background: #10B981; box-shadow: 0 0 8px rgba(16, 185, 129, 0.6); }
.ad-separator { width: 1px; height: 14px; background: rgba(255,255,255,0.15); }
.ad-live-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: #EF4444; animation: ad-blink 1.5s ease-in-out infinite;
}
@keyframes ad-blink { 0%,100% { opacity: 1; } 50% { opacity: 0.3; } }

/* ═══ DATA BLOCKS ═══ */
.ad-data-blocks { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.ad-block {
  padding: 18px 16px;
  border-radius: 14px;
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border-light);
}
.ad-block-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.ad-block-label { font-size: 0.6rem; font-weight: 700; letter-spacing: 0.1em; color: var(--color-text-light); text-transform: uppercase; }
.ad-block-indicator { width: 6px; height: 6px; border-radius: 50%; }
.ad-block-value { font-size: 1.5rem; font-weight: 800; color: var(--color-text); margin-bottom: 10px; }
.ad-block-bar { height: 3px; background: var(--color-bg-alt); border-radius: 2px; overflow: hidden; }
.ad-block-bar-fill { height: 100%; border-radius: 2px; transition: width 1s ease; }

/* ═══ PANELS ═══ */
.ad-panels { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.ad-panel {
  padding: 22px;
  border-radius: 16px;
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border-light);
}
.ad-panel-head {
  display: flex; align-items: center; gap: 10px; margin-bottom: 18px;
}
.ad-panel-head h3 { font-size: 0.9rem; font-weight: 700; }
.ad-panel-indicator { width: 8px; height: 8px; border-radius: 2px; }
.ad-panel-indicator.indigo { background: #6366F1; }
.ad-panel-indicator.green { background: #10B981; }

/* Feed empty */
.ad-feed-empty { text-align: center; }
.ad-feed-lottie { width: 140px; height: 140px; margin: 0 auto 12px; }
.ad-feed-msg { font-size: 0.78rem; color: var(--color-text-light); }

/* Health */
.ad-health-list { display: flex; flex-direction: column; gap: 14px; }
.ad-health-item {}
.ad-health-top { display: flex; justify-content: space-between; margin-bottom: 6px; font-size: 0.78rem; color: var(--color-text-secondary); }
.ad-health-track { height: 6px; background: var(--color-bg-alt); border-radius: 3px; overflow: hidden; }
.ad-health-fill { height: 100%; border-radius: 3px; transition: width 1s ease; }

/* ═══ COMMAND GRID ═══ */
.ad-commands { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.ad-cmd {
  display: flex; align-items: center; gap: 14px;
  padding: 18px 20px;
  border-radius: 14px;
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border-light);
  text-decoration: none; color: var(--color-text);
  transition: all 0.25s ease;
}
.ad-cmd:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.06); }
.ad-cmd-icon {
  width: 42px; height: 42px; border-radius: 10px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.ad-cmd-icon.indigo { background: linear-gradient(135deg, #6366F1, #4F46E5); }
.ad-cmd-icon.green { background: linear-gradient(135deg, #10B981, #059669); }
.ad-cmd-icon.red { background: linear-gradient(135deg, #EF4444, #DC2626); }
.ad-cmd-icon.amber { background: linear-gradient(135deg, #F59E0B, #D97706); }
.ad-cmd-text { flex: 1; }
.ad-cmd-name { display: block; font-size: 0.88rem; font-weight: 700; }
.ad-cmd-desc { display: block; font-size: 0.7rem; color: var(--color-text-light); margin-top: 1px; }
.ad-cmd-arrow { color: var(--color-text-light); flex-shrink: 0; }

@media (max-width: 768px) {
  .ad-data-blocks { grid-template-columns: repeat(2, 1fr); }
  .ad-panels { grid-template-columns: 1fr; }
  .ad-commands { grid-template-columns: 1fr; }
}
@media (max-width: 480px) {
  .ad-status-bar { flex-direction: column; gap: 8px; align-items: flex-start; padding: 14px 16px; }
  .ad-data-blocks { grid-template-columns: 1fr 1fr; gap: 8px; }
  .ad-block { padding: 14px 12px; }
}
</style>
