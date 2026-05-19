<template>
  <DashboardShell :nav-items="navItems" :page-title="pageTitle" portal="cook" portal-label="Cook" portal-icon="utensils" />
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import DashboardShell from '../components/DashboardShell.vue'

const route = useRoute()

const navItems = [
  { path: '/cook', icon: 'home', label: 'Dashboard' },
  { path: '/cook/jobs', icon: 'list', label: 'Jobs' },
  { path: '/cook/earnings', icon: 'dollar-sign', label: 'Earnings' },
  { path: '/cook/availability', icon: 'calendar', label: 'Availability' },
  { path: '/cook/profile', icon: 'user', label: 'Profile' }
]

const pageTitles = {
  CookDashboard: 'Dashboard',
  CookJobs: 'Jobs',
  CookEarnings: 'Earnings',
  CookAvailability: 'Availability',
  CookProfile: 'Profile'
}

const pageTitle = computed(() => pageTitles[route.name] || 'Dashboard')
</script>
