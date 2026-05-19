<template>
  <DashboardShell :nav-items="navItems" :page-title="pageTitle" portal="customer" portal-label="Customer" portal-icon="user" />
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import DashboardShell from '../components/DashboardShell.vue'

const route = useRoute()

const navItems = [
  { path: '/customer', icon: 'home', label: 'Dashboard' },
  { path: '/customer/book', icon: 'calendar', label: 'Book a Cook' },
  { path: '/customer/bookings', icon: 'list', label: 'My Bookings' },
  { path: '/customer/preferences', icon: 'sliders', label: 'Taste Profile' },
  { path: '/customer/profile', icon: 'user', label: 'Profile' }
]

const pageTitles = {
  CustomerDashboard: 'Dashboard',
  BookCook: 'Book a Cook',
  MyBookings: 'My Bookings',
  BookingDetail: 'Booking Details',
  TasteProfile: 'Taste Profile',
  CustomerProfile: 'Profile'
}

const pageTitle = computed(() => pageTitles[route.name] || 'Dashboard')
</script>
