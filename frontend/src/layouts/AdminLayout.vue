<template>
  <DashboardShell :nav-items="navItems" :page-title="pageTitle" portal="admin" portal-label="Administrator" portal-icon="shield" />
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import DashboardShell from '../components/DashboardShell.vue'

const route = useRoute()

const navItems = [
  { path: '/admin', icon: 'home', label: 'Dashboard' },
  { path: '/admin/managers', icon: 'users', label: 'Managers' },
  { path: '/admin/analytics', icon: 'bar-chart', label: 'Analytics' },
  { path: '/admin/policies', icon: 'clipboard', label: 'Policies' },
  { path: '/admin/disputes', icon: 'message-circle', label: 'Disputes' },
  { path: '/admin/profile', icon: 'user', label: 'Profile' }
]

const pageTitles = {
  AdminDashboard: 'Dashboard',
  ManageManagers: 'Managers',
  Analytics: 'Analytics',
  Policies: 'Policies',
  Disputes: 'Disputes',
  AdminProfile: 'Profile'
}

const pageTitle = computed(() => pageTitles[route.name] || 'Dashboard')
</script>
