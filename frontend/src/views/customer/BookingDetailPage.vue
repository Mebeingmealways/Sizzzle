<template>
  <div class="bd-page animate-fade-in">
    <div v-if="loading" class="text-center" style="padding:40px"><p class="text-muted">Loading booking...</p></div>
    <template v-else-if="booking">
    <header class="bd-header">
      <div>
        <h2 class="heading-md">Booking Details</h2>
        <p class="text-muted" style="margin-top:8px">{{ booking.booking_code }}</p>
      </div>
      <div class="bd-header-actions">
        <button class="btn btn-sm btn-outline" @click="setMyLocation" :disabled="tracker.loading.value">
          <AppIcon name="navigation" :size="14" />
          {{ tracker.loading.value ? 'Updating GPS...' : 'Use My Live GPS' }}
        </button>
        <button class="btn btn-sm" :class="trackingActive ? 'btn-accent' : 'btn-primary'" @click="toggleTracking">
          <AppIcon :name="trackingActive ? 'x-circle' : 'activity'" :size="14" />
          {{ trackingActive ? 'Stop Tracking' : 'Start Live Tracking' }}
        </button>
      </div>
    </header>

    <section class="card-glass bd-overview">
      <div class="detail-grid">
        <div class="detail-item">
          <span class="text-sm text-muted">Status</span>
          <span class="badge" :class="statusBadgeClass">{{ displayStatus }}</span>
        </div>
        <div class="detail-item">
          <span class="text-sm text-muted">Date</span>
          <span>{{ formatDate(booking.date) }}</span>
        </div>
        <div class="detail-item">
          <span class="text-sm text-muted">Time</span>
          <span>{{ booking.time_slot || 'N/A' }}</span>
        </div>
        <div class="detail-item">
          <span class="text-sm text-muted">Cook</span>
          <span>{{ booking.cook_name || 'Assigned Cook' }}</span>
        </div>
        <div class="detail-item">
          <span class="text-sm text-muted">People</span>
          <span>{{ booking.num_people }}</span>
        </div>
        <div class="detail-item">
          <span class="text-sm text-muted">Tier</span>
          <span class="badge badge-accent">{{ booking.tier }}</span>
        </div>
        <div class="detail-item">
          <span class="text-sm text-muted">Amount</span>
          <span style="font-weight:700;color:var(--color-primary-dark)">Rs {{ booking.total_amount?.toLocaleString('en-IN') }}</span>
        </div>
      </div>
      <div style="margin-top:24px">
        <h4 class="heading-sm">Dishes</h4>
        <p class="text-sm text-muted" style="margin-top:8px">{{ (booking.dishes || []).map(d => d.name).join(', ') }}</p>
      </div>
    </section>

    <section class="card bd-live-track">
      <div class="bd-live-top">
        <div>
          <p class="text-xs live-kicker">LIVE SERVICE TRACKING</p>
          <h4 class="heading-sm">{{ displayStatus }}</h4>
          <p class="text-sm text-muted" style="margin-top:6px">
            {{ destinationLabel }}
          </p>
        </div>
        <button class="btn btn-sm btn-outline" @click="tracker.openMaps(cookPosition, bookingLocation)">
          <AppIcon name="map-pin" :size="14" /> Open Route
        </button>
      </div>

      <div class="bd-live-metrics">
        <div class="metric-pill">
          <AppIcon name="navigation" :size="14" />
          <div>
            <small>Cook Distance</small>
            <strong>{{ distanceLabel }}</strong>
          </div>
        </div>
        <div class="metric-pill">
          <AppIcon name="clock" :size="14" />
          <div>
            <small>ETA</small>
            <strong>{{ etaLabel }}</strong>
          </div>
        </div>
        <div class="metric-pill">
          <AppIcon name="shield" :size="14" />
          <div>
            <small>Location Confidence</small>
            <strong>{{ locationAccuracy }}</strong>
          </div>
        </div>
      </div>

      <div class="bd-map-preview">
        <div class="route-line"></div>
        <div class="point start">
          <span>Cook</span>
        </div>
        <div class="point destination">
          <span>You</span>
        </div>
        <div class="point moving" :style="{ left: movingDot + '%' }"></div>
      </div>

      <ul class="timeline">
        <li v-for="item in timeline" :key="item.label" :class="{ done: item.done }">
          <span class="dot"></span>
          <div>
            <strong>{{ item.label }}</strong>
            <p class="text-xs text-muted">{{ item.time }}</p>
          </div>
        </li>
      </ul>

      <p v-if="tracker.error.value" class="track-error">{{ tracker.error.value }}</p>
    </section>

    <section class="card-glass" style="padding:22px">
      <h4 class="heading-sm">Arrival Verification Code</h4>
      <p class="text-sm text-muted" style="margin-top:6px">Share this when the cook arrives at your location.</p>
      <div class="otp-display" style="margin-top:12px">
        <span v-for="digit in otpDigits" :key="digit" class="otp-digit">{{ digit }}</span>
      </div>
    </section>

    <section class="card-glass" style="padding:22px">
      <h4 class="heading-sm">Need Help? Raise a Complaint</h4>
      <p class="text-sm text-muted" style="margin-top:6px">If there was an issue with this booking, submit a complaint for manager review.</p>
      <div style="display:grid;gap:10px;margin-top:12px;max-width:560px">
        <input v-model="complaintForm.subject" class="input" type="text" placeholder="Complaint subject" />
        <textarea v-model="complaintForm.description" class="input" rows="3" placeholder="Describe the issue"></textarea>
        <select v-model="complaintForm.priority" class="input">
          <option value="Low">Low</option>
          <option value="Medium">Medium</option>
          <option value="High">High</option>
          <option value="Critical">Critical</option>
        </select>
      </div>
      <div style="margin-top:12px">
        <button class="btn btn-outline btn-sm" @click="submitComplaint">Submit Complaint</button>
      </div>
    </section>

    <div class="action-bar">
      <button v-if="booking.status === 'pending' || booking.status === 'accepted'" class="btn btn-ghost" style="color:var(--color-error)" @click="cancelBooking">Cancel Booking</button>
      <router-link to="/customer/bookings" class="btn btn-primary">Back to Bookings</router-link>
    </div>
    </template>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import AppIcon from '../../components/AppIcon.vue'
import { useLiveLocation } from '../../composables/useLiveLocation'
import { bookingApi, managerApi } from '../../services/api.js'

const props = defineProps({ id: String })

const booking = ref(null)
const loading = ref(true)

const bookingLocation = ref({ lat: 19.076, lng: 72.8777, label: 'Booking location' })
const cookPosition = ref({ lat: 19.076, lng: 72.8777 })
const trackingActive = ref(false)
let trackingTimer = null
const complaintForm = ref({
  subject: '',
  description: '',
  priority: 'Medium'
})

const tracker = useLiveLocation(bookingLocation)

async function loadBooking() {
  loading.value = true
  try {
    const data = await bookingApi.get(props.id)
    booking.value = data
    if (data.latitude && data.longitude) {
      bookingLocation.value = { lat: data.latitude, lng: data.longitude, label: data.address || 'Booking location' }
    }
  } catch (e) {
    console.error('Failed to load booking', e)
  } finally {
    loading.value = false
  }
}

onMounted(loadBooking)

// Cook location polling
async function pollCookLocation() {
  try {
    const loc = await bookingApi.getCookLocation(props.id)
    if (loc.latitude !== null && loc.longitude !== null) {
      cookPosition.value = { lat: loc.latitude, lng: loc.longitude }
    }
  } catch (e) { /* silent */ }
}

function toggleTracking() {
  if (trackingActive.value) {
    stopTracking()
  } else {
    startTracking()
  }
}

function startTracking() {
  trackingActive.value = true
  pollCookLocation()
  trackingTimer = window.setInterval(pollCookLocation, 5000)
}

function stopTracking() {
  trackingActive.value = false
  if (trackingTimer) { window.clearInterval(trackingTimer); trackingTimer = null }
}

onBeforeUnmount(stopTracking)

function setMyLocation() { tracker.fetchCurrentPosition() }

watch(() => tracker.position.value, (pos) => {
  if (!pos) return
  bookingLocation.value = { lat: pos.lat, lng: pos.lng, label: 'Your live GPS location' }
})

// Computed
const distanceKm = computed(() => tracker.getDistanceKm(cookPosition.value, bookingLocation.value))
const distanceLabel = computed(() => tracker.formatDistance(distanceKm.value))
const etaLabel = computed(() => tracker.estimateEta(distanceKm.value, 24))

const displayStatus = computed(() => {
  if (!booking.value) return 'Loading...'
  const map = { pending: 'Pending', accepted: 'Cook En Route', in_progress: 'Cooking In Progress', completed: 'Completed', cancelled: 'Cancelled' }
  return map[booking.value.status] || booking.value.status
})

const statusBadgeClass = computed(() => {
  if (!booking.value) return 'badge-primary'
  const map = { pending: 'badge-primary', accepted: 'badge-primary', in_progress: 'badge-warning', completed: 'badge-success', cancelled: 'badge-error' }
  return map[booking.value.status] || 'badge-primary'
})

const locationAccuracy = computed(() => {
  if (!tracker.position.value) return 'Standard'
  if (tracker.position.value.accuracy <= 15) return 'High'
  if (tracker.position.value.accuracy <= 40) return 'Medium'
  return 'Low'
})

const destinationLabel = computed(() => {
  if (tracker.position.value) return 'Using your live GPS destination for precise ETA and routing.'
  return `Default destination: ${bookingLocation.value.label}`
})

const movingDot = computed(() => {
  if (distanceKm.value <= 0.05) return 89
  if (distanceKm.value >= 10) return 11
  return 11 + (1 - distanceKm.value / 10) * 78
})

const otpDigits = computed(() => {
  if (!booking.value?.otp_code) return ['—','—','—','—']
  return booking.value.otp_code.split('')
})

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric' })
}

const timeline = computed(() => {
  const b = booking.value
  if (!b) return []
  return [
    { label: 'Booking created', time: b.created_at ? new Date(b.created_at).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) : '', done: true },
    { label: 'Cook accepted', time: b.status !== 'pending' ? 'Done' : 'Pending', done: b.status !== 'pending' },
    { label: 'Service started', time: b.service_started_at ? new Date(b.service_started_at).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) : (trackingActive.value ? etaLabel.value : 'Pending'), done: !!b.service_started_at },
    { label: 'Service completed', time: b.service_ended_at ? new Date(b.service_ended_at).toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' }) : 'Pending', done: !!b.service_ended_at }
  ]
})

async function cancelBooking() {
  if (!confirm('Are you sure you want to cancel this booking?')) return
  try {
    await bookingApi.cancel(props.id)
    await loadBooking()
  } catch (e) {
    alert(e.message || 'Failed to cancel')
  }
}

async function submitComplaint() {
  if (!booking.value?.id) return
  if (!complaintForm.value.subject.trim()) {
    alert('Please enter a complaint subject')
    return
  }

  try {
    await managerApi.createComplaint({
      booking_id: booking.value.id,
      subject: complaintForm.value.subject.trim(),
      description: complaintForm.value.description.trim(),
      priority: complaintForm.value.priority
    })
    complaintForm.value = { subject: '', description: '', priority: 'Medium' }
    alert('Complaint submitted successfully')
  } catch (e) {
    alert(e.message || 'Failed to submit complaint')
  }
}
</script>

<style scoped>
.bd-page {
  display: grid;
  gap: 18px;
}

.bd-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.bd-header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.bd-overview {
  padding: 26px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 18px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.bd-live-track {
  padding: 22px;
  border: 1px solid var(--color-border-accent);
  background: linear-gradient(175deg, rgba(45, 182, 125, 0.05), rgba(255, 255, 255, 0.95));
}

.bd-live-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  flex-wrap: wrap;
}

.live-kicker {
  color: var(--color-primary-dark);
  font-weight: 700;
  letter-spacing: 0.1em;
}

.bd-live-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  margin-top: 14px;
}

.metric-pill {
  display: flex;
  gap: 8px;
  align-items: center;
  background: var(--color-surface);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  padding: 10px;
}

.metric-pill small {
  display: block;
  color: var(--color-text-light);
  font-size: 0.68rem;
}

.metric-pill strong {
  font-size: 0.88rem;
}

.bd-map-preview {
  position: relative;
  margin-top: 14px;
  border-radius: var(--radius-md);
  min-height: 116px;
  border: 1px dashed var(--color-border);
  background: radial-gradient(circle at 20% 30%, rgba(242, 115, 79, 0.12), transparent 48%), radial-gradient(circle at 80% 80%, rgba(45, 182, 125, 0.13), transparent 48%), #f8fcfa;
  overflow: hidden;
}

.route-line {
  position: absolute;
  left: 11%;
  right: 11%;
  top: 50%;
  height: 4px;
  border-radius: var(--radius-full);
  background: linear-gradient(90deg, rgba(45, 182, 125, 0.2), rgba(242, 115, 79, 0.25));
}

.point {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 13px;
  height: 13px;
  border-radius: 50%;
}

.point.start {
  left: 11%;
  background: var(--color-primary-dark);
}

.point.destination {
  left: 89%;
  background: var(--color-accent);
}

.point span {
  position: absolute;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 0.68rem;
  font-weight: 700;
  color: var(--color-text-secondary);
}

.point.moving {
  top: 50%;
  width: 16px;
  height: 16px;
  background: #ffffff;
  border: 3px solid var(--color-primary-dark);
  box-shadow: 0 0 0 6px rgba(45, 182, 125, 0.18);
  transition: left 3.4s linear;
}

.timeline {
  margin-top: 16px;
  list-style: none;
  display: grid;
  gap: 10px;
}

.timeline li {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  opacity: 0.58;
}

.timeline li.done {
  opacity: 1;
}

.timeline .dot {
  width: 10px;
  height: 10px;
  margin-top: 6px;
  border-radius: 50%;
  background: var(--color-border);
}

.timeline li.done .dot {
  background: var(--color-primary);
}

.track-error {
  margin-top: 10px;
  color: var(--color-error);
  font-size: 0.78rem;
  font-weight: 500;
}

.otp-display {
  display: flex;
  gap: 8px;
}

.otp-digit {
  width: 48px;
  height: 56px;
  border-radius: var(--radius-md);
  background: var(--color-bg-alt);
  border: 1.5px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-primary-dark);
}

.action-bar {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  padding-top: 8px;
}

@media (max-width: 760px) {
  .bd-overview,
  .bd-live-track {
    padding: 18px;
  }

  .bd-live-metrics {
    grid-template-columns: 1fr;
  }
}
</style>
