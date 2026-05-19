<template>
  <DashboardShell :nav-items="navItems" :page-title="pageTitle" portal="manager" portal-label="Manager" portal-icon="clipboard" />
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import DashboardShell from '../components/DashboardShell.vue'

const route = useRoute()

const navItems = [
  { path: '/manager', icon: 'home', label: 'Dashboard' },
  { path: '/manager/verification', icon: 'shield', label: 'Verification' },
  { path: '/manager/cooks', icon: 'users', label: 'Cooks' },
  { path: '/manager/complaints', icon: 'message-circle', label: 'Complaints' },
  { path: '/manager/profile', icon: 'user', label: 'Profile' }
]

const pageTitles = {
  ManagerDashboard: 'Dashboard',
  CookVerification: 'Cook Verification',
  ManageCooks: 'Manage Cooks',
  Complaints: 'Complaints',
  ManagerProfile: 'Profile'
}

const pageTitle = computed(() => pageTitles[route.name] || 'Dashboard')
</script>
