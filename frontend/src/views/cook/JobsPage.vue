<template>
  <div class="jobs-page animate-fade-in">
    <div class="page-header">
      <h2 class="heading-md">Jobs</h2>
      <p class="text-sm text-muted">Manage incoming and scheduled bookings</p>
    </div>

    <div v-if="loading" class="text-center" style="padding:30px"><p class="text-muted">Loading jobs...</p></div>

    <div class="active-service card-glass" v-else-if="activeService">
      <div class="active-head">
        <div>
          <p class="text-xs active-kicker">ACTIVE SERVICE</p>
          <h3 class="heading-sm">{{ activeService.customer_name || 'Customer' }} • {{ activeService.time_slot || '' }}</h3>
          <p class="text-sm text-muted">{{ activeService.address || 'N/A' }}</p>
        </div>
        <span class="badge" :class="'badge-' + activeService._status">{{ activeService._status }}</span>
      </div>

      <div class="active-metrics">
        <div class="metric-card">
          <AppIcon name="map-pin" :size="14" />
          <div>
            <small>Distance to customer</small>
            <strong>{{ location.distanceLabel.value }}</strong>
          </div>
        </div>
        <div class="metric-card">
          <AppIcon name="clock" :size="14" />
          <div>
            <small>Estimated arrival</small>
            <strong>{{ location.etaLabel.value }}</strong>
          </div>
        </div>
        <div class="metric-card">
          <AppIcon name="shield" :size="14" />
          <div>
            <small>GPS status</small>
            <strong>{{ gpsStatus }}</strong>
          </div>
        </div>
      </div>

      <div class="active-actions">
        <button class="btn btn-sm" :class="location.watching.value ? 'btn-accent' : 'btn-primary'" @click="toggleSharing">
          <AppIcon :name="location.watching.value ? 'x-circle' : 'activity'" :size="14" />
          {{ location.watching.value ? 'Stop Sharing' : 'Share Live Location' }}
        </button>
        <button class="btn btn-sm btn-outline" @click="location.fetchCurrentPosition" :disabled="location.loading.value">
          <AppIcon name="navigation" :size="14" />
          {{ location.loading.value ? 'Locating...' : 'Update GPS' }}
        </button>
      </div>
      <p class="gps-error" v-if="location.error.value">{{ location.error.value }}</p>
    </div>

    <div class="filter-tabs" style="margin-top:16px">
      <button v-for="tab in tabs" :key="tab" class="tab-btn" :class="{ active: activeTab === tab }" @click="activeTab = tab">
        {{ tab }}
      </button>
    </div>

    <div class="jobs-list" style="margin-top:20px">
      <div class="job-card card-glass" v-for="job in filteredJobs" :key="job.id">
        <div class="job-header">
          <div>
            <div class="fw-600">{{ job.customer_name || 'Customer' }}</div>
            <div class="text-xs text-muted">{{ job.address || '' }}</div>
          </div>
          <span class="badge" :class="'badge-' + job._status">{{ job._status }}</span>
        </div>
        <div class="job-details">
          <span class="detail"><AppIcon name="calendar" :size="14" /> {{ formatDate(job.date) }}</span>
          <span class="detail"><AppIcon name="clock" :size="14" /> {{ job.time_slot || '' }}</span>
          <span class="detail"><AppIcon name="users" :size="14" /> {{ job.num_people }} people</span>
          <span class="detail"><AppIcon name="utensils" :size="14" /> {{ (job.dishes || []).length }} dishes</span>
        </div>
        <div class="job-footer">
          <span class="job-amount">Rs {{ job.cook_earnings?.toLocaleString('en-IN') || job.total_amount?.toLocaleString('en-IN') || '0' }}</span>
          <div class="job-actions" v-if="job.status === 'pending'">
            <button class="btn btn-sm btn-outline" @click="updateJobStatus(job, 'Declined')">Decline</button>
            <button class="btn btn-sm btn-primary" @click="updateJobStatus(job, 'Accepted')">Accept</button>
          </div>
          <div class="job-actions" v-else-if="job.status === 'accepted'">
            <button class="btn btn-sm btn-primary" @click="updateJobStatus(job, 'In Progress')">Start Service</button>
          </div>
          <div class="job-actions" v-else-if="job.status === 'in_progress'">
            <button class="btn btn-sm btn-accent" @click="updateJobStatus(job, 'Completed')">Mark Complete</button>
          </div>
          <div class="job-actions" v-else-if="job.status === 'completed'">
            <button class="btn btn-sm btn-ghost" @click="openSummary(job)">View Summary</button>
          </div>
          <button
            v-if="job.status !== 'cancelled'"
            class="btn btn-sm btn-outline"
            @click="raiseComplaint(job)"
          >
            Raise Complaint
          </button>
        </div>
      </div>
    </div>

    <div v-if="summaryJob" class="summary-modal" @click.self="summaryJob = null">
      <div class="summary-card card-glass">
        <h3 class="heading-sm">Booking Summary</h3>
        <p class="text-sm text-muted" style="margin-top:4px">{{ summaryJob.customer_name || 'Customer' }} • {{ formatDate(summaryJob.date) }}</p>
        <div class="summary-grid" style="margin-top:14px">
          <div><strong>Status:</strong> {{ displayStatus(summaryJob.status) }}</div>
          <div><strong>Time:</strong> {{ summaryJob.time_slot || 'N/A' }}</div>
          <div><strong>People:</strong> {{ summaryJob.num_people || 0 }}</div>
          <div><strong>Earnings:</strong> Rs {{ summaryJob.cook_earnings?.toLocaleString('en-IN') || summaryJob.total_amount?.toLocaleString('en-IN') || 0 }}</div>
          <div class="summary-span"><strong>Address:</strong> {{ summaryJob.address || 'N/A' }}</div>
          <div class="summary-span"><strong>Dishes:</strong> {{ (summaryJob.dishes || []).map(d => d.name).join(', ') || 'N/A' }}</div>
        </div>
        <div style="display:flex;justify-content:flex-end;margin-top:16px">
          <button class="btn btn-sm btn-primary" @click="summaryJob = null">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import AppIcon from '@/components/AppIcon.vue'
import { useLiveLocation } from '@/composables/useLiveLocation'
import { cookApi, bookingApi, managerApi } from '@/services/api.js'

const activeTab = ref('All')
const tabs = ['All', 'Pending', 'Accepted', 'In Progress', 'Completed']
const jobs = ref([])
const loading = ref(true)
let locationInterval = null
const summaryJob = ref(null)

const statusMap = {
  pending: 'Pending', accepted: 'Accepted', in_progress: 'In Progress',
  completed: 'Completed', cancelled: 'Cancelled'
}
function displayStatus(s) { return statusMap[s] || s }

function formatDate(iso) {
  if (!iso) return ''
  return new Date(iso).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' })
}

async function loadJobs() {
  loading.value = true
  try {
    const data = await cookApi.getJobs()
    jobs.value = (data.jobs || data || []).map(j => ({
      ...j,
      _status: displayStatus(j.status)
    }))
  } catch (e) {
    console.error('Failed to load jobs', e)
  } finally {
    loading.value = false
  }
}

onMounted(loadJobs)

const activeServiceId = ref(null)

watch(jobs, (list) => {
  const inProgress = list.find(j => j.status === 'in_progress')
  if (inProgress) {
    activeServiceId.value = inProgress.id
    return
  }

  // Only show Active Service card for in-progress jobs.
  if (activeServiceId.value && !list.find(j => j.id === activeServiceId.value && j.status === 'in_progress')) {
    activeServiceId.value = null
  }
}, { immediate: true })

const activeService = computed(() => {
  const match = jobs.value.find(j => j.id === activeServiceId.value && j.status === 'in_progress')
  return match || null
})

const activeInProgressJob = computed(() => jobs.value.find(j => j.status === 'in_progress') || null)

const destination = computed(() => {
  if (!activeService.value) return null
  return {
    lat: activeService.value.latitude ?? 19.076,
    lng: activeService.value.longitude ?? 72.877,
  }
})

const location = useLiveLocation(destination)

const gpsStatus = computed(() => {
  if (location.watching.value) return 'Live sharing on'
  if (location.position.value) return 'GPS ready'
  if (location.permission.value === 'denied') return 'Permission denied'
  return 'Not started'
})

const filteredJobs = computed(() => {
  if (activeTab.value === 'All') return jobs.value
  return jobs.value.filter(j => j._status === activeTab.value)
})

async function updateJobStatus(job, targetStatus) {
  const backendStatus = { 'Accepted': 'accepted', 'Declined': 'cancelled', 'In Progress': 'in_progress', 'Completed': 'completed' }[targetStatus]
  if (!backendStatus) return

  try {
    if (targetStatus === 'In Progress') {
      if (activeInProgressJob.value && activeInProgressJob.value.id !== job.id) {
        alert('Finish the current in-progress booking before starting another service.')
        return
      }

      const otp = window.prompt('Enter customer OTP to start service:')
      if (!otp) return
      await bookingApi.verifyOtp(job.id, otp.trim())
    } else if (targetStatus === 'Completed') {
      await bookingApi.endService(job.id)
    } else {
      await bookingApi.updateStatus(job.id, backendStatus)
    }
    await loadJobs()
    if (targetStatus === 'Accepted' || targetStatus === 'In Progress') {
      activeServiceId.value = job.id
    }
    if (targetStatus === 'Completed' && activeServiceId.value === job.id) {
      location.stopWatching()
      stopLocationSharing()
    }
  } catch (e) {
    alert(e.message || 'Failed to update job status')
  }
}

function toggleSharing() {
  if (location.watching.value) {
    location.stopWatching()
    stopLocationSharing()
  } else {
    if (location.permission.value === 'denied') {
      alert('Location permission is blocked. Please allow location access in browser settings.')
      return
    }
    location.startWatching()
    if (location.watching.value) {
      startLocationSharing()
    }
  }
}

function startLocationSharing() {
  if (locationInterval) return
  sendLocation()
  locationInterval = window.setInterval(sendLocation, 3000)
}

function stopLocationSharing() {
  if (locationInterval) { window.clearInterval(locationInterval); locationInterval = null }
}

async function sendLocation() {
  const pos = location.position.value
  if (!pos) return
  try {
    await cookApi.updateLocation({
      latitude: pos.lat,
      longitude: pos.lng,
      accuracy_m: pos.accuracy,
      source_timestamp: pos.timestamp,
    })
  } catch (e) { /* silent */ }
}

watch(() => activeServiceId.value, () => {
  if (location.watching.value) { location.stopWatching(); stopLocationSharing() }
})

function openSummary(job) {
  summaryJob.value = job
}

async function raiseComplaint(job) {
  const subject = window.prompt('Complaint subject:')
  if (!subject) return
  const description = window.prompt('Describe the issue (optional):') || ''

  try {
    await managerApi.createComplaint({
      booking_id: job.id,
      subject,
      description,
      priority: 'Medium'
    })
    alert('Complaint submitted successfully.')
  } catch (e) {
    alert(e.message || 'Failed to submit complaint')
  }
}

onBeforeUnmount(() => { stopLocationSharing() })
</script>

<style scoped>
.jobs-page {
  width: 100%;
}

.active-service {
  margin-top: 14px;
  padding: 18px;
  border-radius: var(--radius-lg);
}

.active-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  flex-wrap: wrap;
}

.active-kicker {
  font-weight: 700;
  letter-spacing: 0.09em;
  color: var(--color-primary-dark);
}

.active-metrics {
  margin-top: 12px;
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  padding: 10px;
  background: rgba(255, 255, 255, 0.9);
}

.metric-card small {
  display: block;
  font-size: 0.68rem;
  color: var(--color-text-light);
}

.metric-card strong {
  font-size: 0.84rem;
}

.active-actions {
  display: flex;
  gap: 8px;
  margin-top: 14px;
  flex-wrap: wrap;
}

.gps-error {
  margin-top: 8px;
  color: var(--color-error);
  font-size: 0.75rem;
  font-weight: 500;
}

.filter-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tab-btn {
  padding: 8px 18px;
  border-radius: var(--radius-full);
  font-size: 0.813rem;
  font-weight: 500;
  background: var(--color-bg-alt);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.tab-btn.active {
  background: var(--color-primary);
  color: #fff;
  border-color: var(--color-primary);
}

.jobs-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.job-card {
  padding: 20px;
  border-radius: var(--radius-lg);
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.badge-Pending { background: #FEF3C7; color: #D97706; }
.badge-Accepted { background: #DBEAFE; color: #2563EB; }
.badge-Completed { background: #D1FAE5; color: #059669; }
.badge-Declined { background: #FEE2E2; color: #DC2626; }
[class*="badge-"] {
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: 0.688rem;
  font-weight: 600;
}
.badge-In\ Progress { background: #E0E7FF; color: #4F46E5; }

.job-details {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid var(--color-border);
}

.detail {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.813rem;
  color: var(--color-text-secondary);
}

.job-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid var(--color-border);
}

.job-amount {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--color-primary-dark);
}

.job-actions {
  display: flex;
  gap: 8px;
}

.btn-sm {
  padding: 6px 16px;
  font-size: 0.813rem;
}

.btn-accent {
  background: var(--color-accent);
  color: #fff;
}

.summary-modal {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.summary-card {
  width: min(560px, 92vw);
  padding: 22px;
  border-radius: var(--radius-lg);
}

.summary-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.summary-span {
  grid-column: 1 / -1;
}

@media (max-width: 640px) {
  .active-metrics {
    grid-template-columns: 1fr;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>
