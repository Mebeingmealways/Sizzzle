<template>
  <div class="bookings-page animate-fade-in">
    <div class="page-header flex-between">
      <div>
        <h2 class="heading-md">My Bookings</h2>
        <p class="text-sm text-muted">Track all your past and upcoming bookings</p>
      </div>
      <router-link to="/customer/book" class="btn btn-primary btn-sm">
        <AppIcon name="plus" :size="16" /> New Booking
      </router-link>
    </div>

    <!-- Filters -->
    <div class="filters-bar">
      <button v-for="f in filters" :key="f" class="filter-btn" :class="{ active: activeFilter === f }" @click="activeFilter = f">
        {{ f }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center" style="padding:40px"><p class="text-muted">Loading bookings...</p></div>

    <!-- Empty -->
    <div v-else-if="filteredBookings.length === 0" class="text-center" style="padding:40px">
      <p class="text-muted">No bookings found</p>
      <router-link to="/customer/book" class="btn btn-primary" style="margin-top:12px">Book a Cook</router-link>
    </div>

    <!-- Bookings List -->
    <div v-else class="bookings-list">
      <div v-for="booking in filteredBookings" :key="booking.id" class="booking-item card">
        <div class="booking-item-header">
          <div class="booking-item-cook">
            <div class="cook-avatar-sm">{{ (booking.cook_name || 'C').charAt(0) }}</div>
            <div>
              <div class="booking-item-cook-name">{{ booking.cook_name || 'Cook' }}</div>
              <div class="text-xs text-muted">{{ booking.tier || 'standard' }}</div>
            </div>
          </div>
          <span class="badge" :class="statusClass(booking.status, booking)">{{ displayStatus(booking.status, booking) }}</span>
        </div>
        <div class="booking-item-details">
          <div class="detail">
            <AppIcon name="calendar" :size="14" class="text-muted" />
            <span class="text-sm">{{ formatDate(booking.date) }}</span>
          </div>
          <div class="detail">
            <AppIcon name="clock" :size="14" class="text-muted" />
            <span class="text-sm">{{ booking.time_slot || 'N/A' }}</span>
          </div>
          <div class="detail">
            <AppIcon name="users" :size="14" class="text-muted" />
            <span class="text-sm">{{ booking.num_people }} people</span>
          </div>
        </div>
        <div class="booking-item-dishes text-sm text-muted">{{ dishNames(booking) }}</div>
        <div class="booking-item-footer">
          <span class="booking-price">Rs {{ booking.total_amount?.toLocaleString('en-IN') || '0' }}</span>
          <div class="booking-item-actions">
            <button v-if="displayStatus(booking.status, booking) === 'Upcoming'" class="btn btn-ghost btn-sm" style="color:var(--color-error)" @click="cancelBooking(booking)">Cancel</button>
            <router-link :to="`/customer/booking/${booking.id}`" class="btn btn-outline btn-sm">Details</router-link>
            <router-link v-if="['pending','accepted','in_progress'].includes(booking.status)" :to="`/customer/booking/${booking.id}`" class="btn btn-primary btn-sm">
              <AppIcon name="activity" :size="14" /> Live Track
            </router-link>
            <button v-if="booking.status === 'completed' && !booking.review" class="btn btn-outline btn-sm" @click="openRating(booking)">Rate</button>
            <router-link v-if="booking.status === 'completed'" to="/customer/book" class="btn btn-ghost btn-sm">Rebook</router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- Rating Modal -->
    <div v-if="ratingBooking" class="modal-overlay" @click.self="ratingBooking = null">
      <div class="card" style="max-width:400px;width:100%;padding:24px">
        <h3 class="heading-sm" style="margin-bottom:16px">Rate {{ ratingBooking.cook_name }}</h3>
        <div style="display:flex;gap:8px;margin-bottom:12px">
          <button v-for="s in 5" :key="s" class="btn btn-ghost btn-sm" :style="{ color: s <= ratingValue ? 'var(--color-warning)' : 'var(--color-text-muted)' }" @click="ratingValue = s">
            ★
          </button>
        </div>
        <textarea v-model="ratingComment" placeholder="Leave a comment (optional)" class="input" rows="3" style="width:100%;margin-bottom:12px"></textarea>
        <div style="display:flex;gap:8px;justify-content:flex-end">
          <button class="btn btn-ghost btn-sm" @click="ratingBooking = null">Cancel</button>
          <button class="btn btn-primary btn-sm" @click="submitRating">Submit</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppIcon from '../../components/AppIcon.vue'
import { bookingApi } from '../../services/api.js'

const activeFilter = ref('All')
const filters = ['All', 'Upcoming', 'Completed', 'Cancelled', 'Inactive']
const bookings = ref([])
const loading = ref(true)
const ratingBooking = ref(null)
const ratingValue = ref(5)
const ratingComment = ref('')

const statusMap = {
  pending: 'Upcoming', accepted: 'Upcoming', in_progress: 'In Progress',
  completed: 'Completed', cancelled: 'Cancelled'
}

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
  return statusMap[status] || status
}

function isPastDate(isoDate) {
  if (!isoDate) return false
  const d = new Date(`${isoDate}T00:00:00`)
  const today = new Date()
  today.setHours(0, 0, 0, 0)
  return d < today
}

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric' })
}

async function loadBookings() {
  loading.value = true
  try {
    const data = await bookingApi.list()
    bookings.value = data
  } catch (e) {
    console.error('Failed to load bookings', e)
  } finally {
    loading.value = false
  }
}

onMounted(loadBookings)

const filteredBookings = computed(() => {
  if (activeFilter.value === 'All') return bookings.value
  return bookings.value.filter((b) => {
    const matchesStatus = displayStatus(b.status, b) === activeFilter.value
    if (!matchesStatus) return false

    if (activeFilter.value === 'Upcoming') {
      // Hide stale upcoming records whose date is already in the past.
      return !isPastDate(b.date)
    }

    return true
  })
})

function statusClass(status, booking) {
  const display = displayStatus(status, booking)
  return {
    Completed: 'badge-success',
    Upcoming: 'badge-primary',
    Cancelled: 'badge-error',
    Inactive: 'badge-warning',
    'In Progress': 'badge-warning'
  }[display] || 'badge-primary'
}

async function cancelBooking(booking) {
  if (!confirm('Are you sure you want to cancel this booking?')) return
  try {
    await bookingApi.cancel(booking.id)
    await loadBookings()
  } catch (e) {
    alert(e.message || 'Failed to cancel booking')
  }
}

function openRating(booking) {
  ratingBooking.value = booking
  ratingValue.value = 5
  ratingComment.value = ''
}

async function submitRating() {
  if (!ratingBooking.value) return
  try {
    await bookingApi.rate(ratingBooking.value.id, { rating: ratingValue.value, comment: ratingComment.value })
    ratingBooking.value = null
    await loadBookings()
  } catch (e) {
    alert(e.message || 'Failed to submit rating')
  }
}

function dishNames(booking) {
  return (booking.dishes || []).map(d => d.name).join(', ')
}
</script>

<style scoped>
.bookings-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  flex-wrap: wrap;
  gap: 16px;
}

.filters-bar {
  display: flex;
  gap: 8px;
}

.filter-btn {
  padding: 8px 18px;
  border-radius: var(--radius-full);
  font-size: 0.813rem;
  font-weight: 500;
  background: var(--color-surface);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.filter-btn.active {
  background: var(--color-primary);
  color: #fff;
  border-color: var(--color-primary);
}

.bookings-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.booking-item {
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.booking-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.booking-item-cook {
  display: flex;
  align-items: center;
  gap: 12px;
}

.cook-avatar-sm {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.813rem;
}

.booking-item-cook-name {
  font-weight: 600;
}

.booking-item-details {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.detail {
  display: flex;
  align-items: center;
  gap: 6px;
}

.booking-item-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 12px;
  border-top: 1px solid var(--color-border-light);
}

.booking-price {
  font-weight: 700;
  font-size: 1.063rem;
  color: var(--color-primary-dark);
}

.booking-item-actions {
  display: flex;
  gap: 8px;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
</style>
