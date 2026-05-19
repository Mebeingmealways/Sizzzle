<template>
  <div class="portal-layout" :class="['portal-' + portal, { 'sidebar-collapsed': sidebarCollapsed }]">
    <!-- Desktop Sidebar -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed && !mobileOpen, 'mobile-open': mobileOpen }">
      <div class="sidebar-header">
        <router-link to="/" class="sidebar-brand">
          <SizzzleLogo :size="sidebarCollapsed ? 'sm' : 'md'" :show-text="!sidebarCollapsed" />
        </router-link>
        <button class="btn-collapse" @click="sidebarCollapsed = !sidebarCollapsed" v-if="!isMobile">
          <AppIcon :name="sidebarCollapsed ? 'chevron-right' : 'chevron-left'" :size="16" />
        </button>
      </div>

      <!-- Portal identity badge -->
      <div class="portal-badge" v-if="!sidebarCollapsed || mobileOpen">
        <div class="portal-badge-icon">
          <AppIcon :name="portalIcon" :size="18" />
        </div>
        <div class="portal-badge-text">
          <span class="portal-badge-role">{{ portalLabel }}</span>
          <span class="portal-badge-name">{{ auth.user?.name || 'User' }}</span>
        </div>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="sidebar-link"
          :class="{ active: isActive(item.path) }"
          @click="mobileOpen = false"
        >
          <AppIcon :name="item.icon" :size="20" />
          <span v-if="!sidebarCollapsed || mobileOpen" class="sidebar-link-text">{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <button class="sidebar-logout" @click="logout">
          <AppIcon name="log-out" :size="18" />
          <span v-if="!sidebarCollapsed || mobileOpen">Sign out</span>
        </button>
      </div>
    </aside>

    <!-- Mobile overlay -->
    <div v-if="mobileOpen" class="sidebar-overlay" @click="mobileOpen = false"></div>

    <!-- Main Area -->
    <div class="portal-main">
      <!-- Top Bar -->
      <header class="topbar" @click="closeDropdowns">
        <button v-if="isMobile" class="btn-menu" @click="mobileOpen = !mobileOpen">
          <AppIcon name="menu" :size="20" />
        </button>
        <div class="topbar-title">
          <h2 class="heading-sm">{{ pageTitle }}</h2>
        </div>
        <div class="topbar-actions">
          <div class="topbar-notif-wrap" @click.stop="showNotif = !showNotif">
            <button class="btn-notif" title="Notifications">
              <AppIcon name="bell" :size="20" />
            </button>
            <div v-if="showNotif" class="topbar-dd glass">
              <div class="topbar-dd-head">Notifications</div>
              <div class="topbar-dd-empty">
                <AppIcon name="bell" :size="24" />
                <p>No notifications yet</p>
              </div>
            </div>
          </div>
          <div class="topbar-profile-wrap" @click.stop="showProfileMenu = !showProfileMenu">
            <div class="topbar-avatar">{{ auth.user?.name?.charAt(0)?.toUpperCase() || 'U' }}</div>
            <div v-if="showProfileMenu" class="topbar-dd glass">
              <router-link :to="'/' + portal + '/profile'" class="topbar-dd-item" @click="showProfileMenu = false">
                <AppIcon name="user" :size="16" /> Profile
              </router-link>
              <hr class="topbar-dd-hr" />
              <button class="topbar-dd-item topbar-dd-signout" @click="logout">
                <AppIcon name="log-out" :size="16" /> Sign out
              </button>
            </div>
          </div>
        </div>
      </header>

      <!-- Content -->
      <main class="portal-content">
        <router-view />
      </main>
    </div>

    <!-- Bottom Navigation (mobile) -->
    <nav class="bottom-nav" v-if="isMobile">
      <router-link
        v-for="item in navItems"
        :key="item.path"
        :to="item.path"
        class="bottom-nav-item"
        :class="{ active: isActive(item.path) }"
      >
        <div class="bottom-nav-icon-wrap">
          <AppIcon :name="item.icon" :size="22" />
        </div>
        <span class="bottom-nav-label">{{ item.label }}</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import SizzzleLogo from '../components/SizzzleLogo.vue'
import AppIcon from '../components/AppIcon.vue'

const props = defineProps({
  navItems: { type: Array, required: true },
  pageTitle: { type: String, default: 'Dashboard' },
  portal: { type: String, default: 'customer' },
  portalLabel: { type: String, default: 'Customer' },
  portalIcon: { type: String, default: 'user' }
})

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const sidebarCollapsed = ref(false)
const mobileOpen = ref(false)
const isMobile = ref(false)
const showNotif = ref(false)
const showProfileMenu = ref(false)

function closeDropdowns() {
  showNotif.value = false
  showProfileMenu.value = false
}

function isActive(path) {
  if (route.path === path) return true
  if (path === `/${props.portal}`) return false
  return route.path.startsWith(`${path}/`)
}

function logout() {
  auth.logout()
  router.push('/')
}

function handleResize() {
  isMobile.value = window.innerWidth < 1024
  if (isMobile.value) sidebarCollapsed.value = true
}

function handleClickOutside() {
  closeDropdowns()
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  document.addEventListener('click', handleClickOutside)
  handleResize()
})
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
/* ═══ PORTAL THEME SYSTEM ═══ */
.portal-layout {
  display: flex;
  min-height: 100vh;
  --portal-hue: 160;
  --portal-color: hsl(var(--portal-hue), 65%, 45%);
  --portal-color-light: hsl(var(--portal-hue), 65%, 95%);
  --portal-color-ghost: hsla(var(--portal-hue), 65%, 45%, 0.08);
  --portal-gradient: linear-gradient(135deg, hsl(var(--portal-hue), 65%, 45%), hsl(calc(var(--portal-hue) + 30), 60%, 50%));
}

/* Customer = Warm green */
.portal-customer {
  --portal-hue: 155;
}
/* Cook = Fiery orange */
.portal-cook {
  --portal-hue: 18;
}
/* Admin = Deep indigo */
.portal-admin {
  --portal-hue: 240;
}
/* Manager = Teal */
.portal-manager {
  --portal-hue: 190;
}

/* ═══ SIDEBAR ═══ */
.sidebar {
  width: 260px;
  height: 100vh;
  position: fixed;
  top: 0; left: 0; z-index: 100;
  display: flex;
  flex-direction: column;
  background: var(--color-surface-raised);
  border-right: 1px solid var(--color-border-light);
  transition: all 0.35s cubic-bezier(0.22, 1, 0.36, 1);
  backdrop-filter: blur(24px) saturate(1.3);
}
.sidebar.collapsed { width: 72px; }

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 16px;
  border-bottom: 1px solid var(--color-border-light);
}
.sidebar-brand { color: inherit; display: flex; align-items: center; }
.btn-collapse {
  width: 28px; height: 28px; padding: 0;
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-sm);
  background: var(--color-bg-alt);
  color: var(--color-text-light);
  cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s ease;
}
.btn-collapse:hover { background: var(--portal-color-ghost); color: var(--portal-color); }

/* Portal badge */
.portal-badge {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 16px 16px 8px;
  padding: 12px 14px;
  border-radius: var(--radius-md);
  background: var(--portal-color-ghost);
  border: 1px solid var(--portal-color-light);
}
.portal-badge-icon {
  width: 36px; height: 36px;
  border-radius: var(--radius-md);
  background: var(--portal-gradient);
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.portal-badge-role {
  display: block;
  font-size: 0.65rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--portal-color);
}
.portal-badge-name {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text);
  margin-top: 1px;
}

.sidebar-nav {
  flex: 1;
  padding: 16px 12px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow-y: auto;
}
.sidebar-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 11px 14px;
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.2s ease;
  white-space: nowrap;
  position: relative;
}
.sidebar-link:hover {
  color: var(--portal-color);
  background: var(--portal-color-ghost);
}
.sidebar-link.active {
  color: var(--portal-color);
  background: var(--portal-color-ghost);
  font-weight: 600;
}
.sidebar-link.active::before {
  content: '';
  position: absolute;
  left: 0; top: 6px; bottom: 6px;
  width: 3px; border-radius: 0 3px 3px 0;
  background: var(--portal-color);
}
.sidebar.collapsed .sidebar-link {
  justify-content: center;
  padding: 11px;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--color-border-light);
}
.sidebar-logout {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px;
  border-radius: var(--radius-md);
  border: none;
  background: transparent;
  color: var(--color-text-secondary);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}
.sidebar-logout:hover {
  color: var(--color-error);
  background: rgba(239, 68, 68, 0.06);
}

/* ═══ OVERLAY ═══ */
.sidebar-overlay {
  position: fixed; inset: 0;
  background: rgba(15, 28, 21, 0.2);
  backdrop-filter: blur(4px);
  z-index: 99;
}

/* ═══ MAIN AREA ═══ */
.portal-main {
  margin-left: 260px;
  flex: 1;
  min-height: 100vh;
  transition: margin-left 0.35s cubic-bezier(0.22, 1, 0.36, 1);
}
.sidebar-collapsed .portal-main {
  margin-left: 72px;
}

.topbar {
  position: sticky;
  top: 0; z-index: 50;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
  padding: 0 28px;
  border-bottom: 1px solid var(--color-border-light);
  background: var(--color-surface-raised);
  backdrop-filter: blur(24px) saturate(1.3);
}
.topbar-title { flex: 1; }
.topbar-actions { display: flex; align-items: center; gap: 8px; }

.btn-menu, .btn-notif {
  width: 40px; height: 40px;
  display: flex; align-items: center; justify-content: center;
  border: none; background: transparent;
  color: var(--color-text-secondary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-menu:hover, .btn-notif:hover {
  background: var(--portal-color-ghost);
  color: var(--portal-color);
}

/* ═══ TOPBAR PROFILE & NOTIFICATIONS ═══ */
.topbar-notif-wrap, .topbar-profile-wrap {
  position: relative;
}
.topbar-avatar {
  width: 34px; height: 34px;
  border-radius: 50%;
  background: var(--portal-gradient);
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 0.78rem;
  cursor: pointer;
  transition: transform 0.2s ease;
}
.topbar-avatar:hover { transform: scale(1.08); }
.topbar-dd {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 220px;
  border-radius: var(--radius-lg);
  padding: 6px;
  z-index: 200;
  animation: scaleIn 0.15s ease-out;
}
@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.95) translateY(-4px); }
  to { opacity: 1; transform: scale(1) translateY(0); }
}
.topbar-dd-head {
  padding: 10px 14px;
  font-size: 0.85rem;
  font-weight: 700;
  border-bottom: 1px solid var(--color-border-light);
}
.topbar-dd-empty {
  display: flex; flex-direction: column; align-items: center; gap: 4px;
  padding: 24px 16px;
  color: var(--color-text-light);
  text-align: center;
}
.topbar-dd-empty p { font-size: 0.82rem; font-weight: 500; margin: 0; }
.topbar-dd-item {
  display: flex; align-items: center; gap: 10px;
  width: 100%; padding: 10px 14px;
  font-size: 0.85rem; font-weight: 500;
  color: var(--color-text);
  background: none; border: none; border-radius: var(--radius-sm);
  cursor: pointer; text-decoration: none;
  transition: background 0.15s ease;
}
.topbar-dd-item:hover { background: var(--color-bg-alt); }
.topbar-dd-signout { color: var(--color-error); }
.topbar-dd-signout:hover { background: rgba(239,68,68,0.06); }
.topbar-dd-hr {
  border: none;
  border-top: 1px solid var(--color-border-light);
  margin: 4px 0;
}

.portal-content {
  padding: 28px;
  min-height: calc(100vh - 64px);
}

/* ═══ BOTTOM NAVIGATION (mobile) ═══ */
.bottom-nav {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  z-index: 100;
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  padding: 6px 8px calc(6px + env(safe-area-inset-bottom));
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(20px) saturate(1.4);
  border-top: 1px solid rgba(0,0,0,0.06);
  box-shadow: 0 -4px 24px rgba(0,0,0,0.04);
}
.bottom-nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  padding: 4px 6px 6px;
  border-radius: 12px;
  color: var(--color-text-light);
  font-size: 0.6rem;
  font-weight: 600;
  transition: all 0.25s cubic-bezier(0.22, 1, 0.36, 1);
  min-width: 56px;
  text-decoration: none;
  position: relative;
}
.bottom-nav-icon-wrap {
  width: 38px; height: 38px;
  border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.25s cubic-bezier(0.22, 1, 0.36, 1);
}
.bottom-nav-item.active .bottom-nav-icon-wrap {
  background: var(--portal-color-ghost);
  color: var(--portal-color);
  transform: translateY(-3px) scale(1.05);
  box-shadow: 0 4px 16px var(--portal-color-ghost);
}
.bottom-nav-item.active {
  color: var(--portal-color);
}
.bottom-nav-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 72px;
  letter-spacing: 0.02em;
  font-size: 0.62rem;
}

/* ═══ RESPONSIVE ═══ */
@media (max-width: 1280px) {
  .sidebar:not(.collapsed) { width: 220px; }
  .portal-main { margin-left: 220px; }
  .sidebar-collapsed .portal-main { margin-left: 72px; }
}

@media (max-width: 1024px) {
  .sidebar { transform: translateX(-100%); }
  .sidebar.mobile-open { transform: translateX(0); width: 260px; }
  .portal-main { margin-left: 0; }
  .sidebar-collapsed .portal-main { margin-left: 0; }
  .portal-content { padding: 20px 16px 100px; }
  .topbar { padding: 0 16px; }
  .bottom-nav-label { display: block; max-width: 64px; }
}

@media (max-width: 480px) {
  .portal-content { padding: 16px 12px 100px; }
  .topbar { height: 56px; padding: 0 12px; }
  .sidebar.mobile-open { width: 240px; }
  .bottom-nav-item { font-size: 0.58rem; min-width: 44px; }
  .bottom-nav-label { max-width: 52px; font-size: 0.55rem; }
}
</style>
