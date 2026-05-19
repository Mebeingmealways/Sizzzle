<template>
  <header class="navbar glass" :class="{ scrolled, 'navbar-compact': deepScrolled }">
    <!-- Reading progress bar -->
    <div class="nav-progress" :style="{ transform: `scaleX(${scrollProgress})` }"></div>

    <div class="container navbar-inner">
      <router-link to="/" class="navbar-brand">
        <SizzzleLogo size="sm" :show-text="true" />
      </router-link>

      <!-- Desktop Nav -->
      <nav class="navbar-links" v-if="!isMobile">
        <template v-if="!isLoggedIn">
          <router-link to="/how-it-works" class="nav-link">How it works</router-link>
          <router-link to="/how-it-works#features" class="nav-link">Features</router-link>
          <div class="nav-lang-btn" @click.stop="toggleLang">
            <AppIcon name="globe" :size="16" />
          </div>
          <router-link to="/login" class="btn btn-ghost btn-sm">Sign in</router-link>
          <router-link to="/register" class="btn btn-primary btn-sm">Get started</router-link>
        </template>
        <template v-else>
          <router-link :to="dashboardPath" class="nav-link">Dashboard</router-link>
          <div class="nav-notif-wrap" @click.stop="toggleNotifications">
            <button class="btn btn-ghost btn-icon" title="Notifications">
              <AppIcon name="bell" :size="20" />
              <span v-if="unreadCount > 0" class="notif-badge">{{ unreadCount > 99 ? '99+' : unreadCount }}</span>
            </button>
            <div v-if="showNotif" class="notif-dropdown glass">
              <div class="notif-header">
                <span class="notif-title">Notifications</span>
                <button v-if="unreadCount > 0" class="notif-mark-all" @click.stop="markAllRead">Mark all read</button>
              </div>
              <div v-if="notifications.length === 0" class="notif-empty">
                <AppIcon name="bell" :size="28" />
                <p>No notifications yet</p>
                <span class="text-sm text-muted">We'll notify you when something arrives</span>
              </div>
              <div v-else class="notif-list">
                <button
                  v-for="item in notifications"
                  :key="item.id"
                  class="notif-item"
                  :class="{ unread: !item.is_read }"
                  @click.stop="handleRead(item.id)"
                >
                  <div class="notif-item-title">{{ item.title }}</div>
                  <div class="notif-item-msg">{{ item.message }}</div>
                  <div class="notif-item-time">{{ formatTime(item.created_at) }}</div>
                </button>
              </div>
            </div>
          </div>
          <div class="nav-lang-btn" @click.stop="toggleLang">
            <AppIcon name="globe" :size="16" />
          </div>
          <div class="nav-avatar" @click.stop="showProfileMenu = !showProfileMenu">
            <div class="avatar-circle">{{ userInitial }}</div>
            <div v-if="showProfileMenu" class="profile-dropdown glass" @click.stop>
              <router-link :to="dashboardPath" class="dropdown-item" @click="showProfileMenu = false">
                <AppIcon name="grid" :size="16" /> Dashboard
              </router-link>
              <router-link :to="profilePath" class="dropdown-item" @click="showProfileMenu = false">
                <AppIcon name="user" :size="16" /> Profile
              </router-link>
              <hr />
              <button class="dropdown-item" @click="logout">
                <AppIcon name="log-out" :size="16" /> Sign out
              </button>
            </div>
          </div>
        </template>
      </nav>

      <!-- Mobile right side -->
      <div v-if="isMobile" class="mobile-right">
        <div class="nav-lang-btn" @click.stop="toggleLang">
          <AppIcon name="globe" :size="16" />
        </div>
        <div v-if="isLoggedIn" class="nav-avatar mobile-avatar" @click="goToDashboard">
          <div class="avatar-circle avatar-circle-sm">{{ userInitial }}</div>
        </div>
        <button class="btn btn-ghost btn-icon mobile-toggle" @click="mobileOpen = !mobileOpen">
          <AppIcon :name="mobileOpen ? 'x' : 'menu'" :size="22" />
        </button>
      </div>
    </div>

    <!-- Mobile menu -->
    <transition name="slide-down">
      <div v-if="mobileOpen && isMobile" class="mobile-menu glass">
        <template v-if="!isLoggedIn">
          <router-link to="/how-it-works" class="mobile-link" @click="mobileOpen = false">How it works</router-link>
          <router-link to="/how-it-works#features" class="mobile-link" @click="mobileOpen = false">Features</router-link>
          <router-link to="/login" class="mobile-link" @click="mobileOpen = false">Sign in</router-link>
          <router-link to="/register" class="btn btn-primary" style="margin-top:8px" @click="mobileOpen = false">Get started</router-link>
        </template>
        <template v-else>
          <router-link :to="dashboardPath" class="mobile-link" @click="mobileOpen = false">Dashboard</router-link>
          <router-link :to="profilePath" class="mobile-link" @click="mobileOpen = false">Profile</router-link>
          <button class="mobile-link" @click="logout">Sign out</button>
        </template>
      </div>
    </transition>
  </header>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import SizzzleLogo from './SizzzleLogo.vue'
import AppIcon from './AppIcon.vue'
import { useNotifications } from '../composables/useNotifications'

const router = useRouter()
const auth = useAuthStore()

const scrolled = ref(false)
const deepScrolled = ref(false)
const scrollProgress = ref(0)
const mobileOpen = ref(false)
const showProfileMenu = ref(false)
const showNotif = ref(false)
const langOpen = ref(false)
const isMobile = ref(false)

const isLoggedIn = computed(() => auth.isLoggedIn)
const userInitial = computed(() => auth.user?.name?.charAt(0)?.toUpperCase() || 'U')
const {
  items: notifications,
  unreadCount,
  refreshNotifications,
  markRead,
  markAllRead,
  startPolling,
  stopPolling,
} = useNotifications()

const dashboardPath = computed(() => {
  const role = auth.user?.role
  if (role === 'cook') return '/cook'
  if (role === 'manager') return '/manager'
  if (role === 'admin') return '/admin'
  return '/customer'
})

const profilePath = computed(() => `${dashboardPath.value}/profile`)
const settingsPath = computed(() => `${dashboardPath.value}/profile`)

function logout() {
  auth.logout()
  showProfileMenu.value = false
  mobileOpen.value = false
  router.push('/')
}

function goToDashboard() {
  router.push(dashboardPath.value)
}

function toggleNotifications() {
  showNotif.value = !showNotif.value
  if (showNotif.value) refreshNotifications(8)
}

function handleRead(notificationId) {
  markRead(notificationId)
}

function formatTime(value) {
  if (!value) return 'just now'
  try {
    return new Date(value).toLocaleString()
  } catch {
    return 'just now'
  }
}

function handleScroll() {
  scrolled.value = window.scrollY > 10
  deepScrolled.value = window.scrollY > 300
  const docH = document.documentElement.scrollHeight - window.innerHeight
  scrollProgress.value = docH > 0 ? Math.min(window.scrollY / docH, 1) : 0
}

function handleResize() {
  isMobile.value = window.innerWidth < 768
  if (!isMobile.value) mobileOpen.value = false
}

function handleClickOutside(e) {
  const target = e.target

  if (!target.closest('.nav-avatar') && !target.closest('.profile-dropdown')) {
    showProfileMenu.value = false
  }

  if (!target.closest('.nav-notif-wrap') && !target.closest('.notif-dropdown')) {
    showNotif.value = false
  }

  const wrap = document.getElementById('lang-toggle-wrap')
  const clickedLangControl = target.closest('.nav-lang-btn') || target.closest('#lang-toggle-wrap')
  if (wrap && wrap.classList.contains('open') && !clickedLangControl) {
    wrap.classList.remove('open')
    langOpen.value = false
  }
}

function toggleLang() {
  const wrap = document.getElementById('lang-toggle-wrap')
  if (wrap) {
    langOpen.value = !langOpen.value
    wrap.classList.toggle('open')
    if (langOpen.value && typeof window.initGoogleTranslate === 'function') {
      window.initGoogleTranslate()
    }
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true })
  window.addEventListener('resize', handleResize)
  document.addEventListener('click', handleClickOutside)
  handleResize()
  handleScroll()
})

watch(
  isLoggedIn,
  (loggedIn) => {
    if (loggedIn) {
      refreshNotifications(8)
      startPolling(12000)
    } else {
      stopPolling()
      showNotif.value = false
    }
  },
  { immediate: true }
)

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  window.removeEventListener('resize', handleResize)
  document.removeEventListener('click', handleClickOutside)
  stopPolling()
})
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  transition: all 0.35s var(--ease-out-expo);
  border-bottom: 1px solid transparent;
}

/* Reading progress bar */
.nav-progress {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--color-primary), var(--color-accent));
  transform-origin: left;
  transform: scaleX(0);
  transition: none;
  z-index: 2;
}

.navbar.scrolled {
  border-bottom-color: var(--color-border-light);
  box-shadow: 0 1px 16px rgba(15, 28, 21, 0.04), 0 0 1px rgba(15, 28, 21, 0.06);
}

/* Compact mode after scrolling deeper */
.navbar-compact .navbar-inner {
  height: 56px;
}

.navbar-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 72px;
}

.navbar-brand {
  display: flex;
  align-items: center;
  color: inherit;
}

.navbar-links {
  display: flex;
  align-items: center;
  gap: 6px;
}

.nav-link {
  padding: 8px 16px;
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  border-radius: var(--radius-md);
  transition: all 0.2s var(--ease-out-expo);
  position: relative;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: 4px;
  left: 50%;
  width: 0;
  height: 1.5px;
  background: var(--color-primary);
  border-radius: 1px;
  transition: all 0.3s var(--ease-out-expo);
  transform: translateX(-50%);
}

.nav-link:hover::after,
.nav-link.router-link-active::after {
  width: calc(100% - 32px);
}

.nav-link:hover,
.nav-link.router-link-active {
  color: var(--color-primary-dark);
}

.nav-avatar {
  position: relative;
  margin-left: 8px;
  cursor: pointer;
}

.avatar-circle {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(160deg, var(--color-primary), var(--color-primary-dark));
  color: var(--color-text-inverse);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.8rem;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(45, 182, 125, 0.25);
}

.avatar-circle:hover {
  transform: scale(1.06);
  box-shadow: 0 4px 12px rgba(45, 182, 125, 0.35);
}

.profile-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 200px;
  padding: 8px;
  border-radius: var(--radius-lg);
  animation: scaleIn 0.15s ease-out;
}

.profile-dropdown hr {
  border: none;
  border-top: 1px solid var(--color-border-light);
  margin: 4px 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 14px;
  font-size: 0.875rem;
  color: var(--color-text);
  background: none;
  border-radius: var(--radius-sm);
  transition: background var(--transition-fast);
}

.dropdown-item:hover {
  background: var(--color-bg-alt);
}

/* Mobile */
.mobile-toggle {
  display: flex;
}

.mobile-right {
  display: flex;
  align-items: center;
  gap: 4px;
}

.nav-lang-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  cursor: pointer;
  color: var(--color-text-secondary);
  transition: all 0.2s ease;
}
.nav-lang-btn:hover {
  background: var(--color-bg-alt);
  color: var(--color-primary);
}

.mobile-menu {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 16px 24px 24px;
  border-top: 1px solid var(--color-border-light);
}

.mobile-link {
  display: block;
  padding: 12px 16px;
  font-size: 0.938rem;
  font-weight: 500;
  color: var(--color-text);
  border-radius: var(--radius-md);
  background: none;
  text-align: left;
  width: 100%;
  transition: background var(--transition-fast);
}

.mobile-link:hover {
  background: var(--color-bg-alt);
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.25s ease;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* ═══ MOBILE AVATAR ═══ */
.mobile-avatar .avatar-circle-sm {
  width: 30px;
  height: 30px;
  font-size: 0.7rem;
}

/* ═══ NOTIFICATION DROPDOWN ═══ */
.nav-notif-wrap {
  position: relative;
}
.notif-badge {
  position: absolute;
  top: 5px;
  right: 5px;
  min-width: 18px;
  height: 18px;
  border-radius: 999px;
  background: var(--color-error);
  color: #fff;
  font-size: 0.64rem;
  font-weight: 700;
  line-height: 18px;
  text-align: center;
  padding: 0 5px;
}
.notif-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 280px;
  border-radius: var(--radius-lg);
  animation: scaleIn 0.15s ease-out;
  overflow: hidden;
}
.notif-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid var(--color-border-light);
}
.notif-title {
  font-size: 0.9rem;
  font-weight: 700;
}
.notif-mark-all {
  border: none;
  background: transparent;
  color: var(--color-primary);
  font-size: 0.76rem;
  font-weight: 600;
  cursor: pointer;
}
.notif-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 28px 20px;
  color: var(--color-text-light);
  text-align: center;
}
.notif-empty p {
  font-size: 0.85rem;
  font-weight: 600;
  margin: 0;
  color: var(--color-text-secondary);
}
.notif-list {
  max-height: 320px;
  overflow: auto;
}
.notif-item {
  width: 100%;
  border: none;
  background: transparent;
  text-align: left;
  padding: 12px 14px;
  border-bottom: 1px solid var(--color-border-light);
  cursor: pointer;
}
.notif-item:hover {
  background: var(--color-bg-alt);
}
.notif-item.unread {
  background: rgba(45, 182, 125, 0.07);
}
.notif-item-title {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--color-text);
}
.notif-item-msg {
  margin-top: 3px;
  font-size: 0.76rem;
  color: var(--color-text-secondary);
  line-height: 1.3;
}
.notif-item-time {
  margin-top: 5px;
  font-size: 0.68rem;
  color: var(--color-text-light);
}
</style>
