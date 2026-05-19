<template>
  <div class="availability-page animate-fade-in">
    <div class="page-header">
      <h2 class="heading-md">Availability</h2>
      <p class="text-sm text-muted">Set your weekly schedule and block dates</p>
    </div>

    <!-- Weekly Schedule -->
    <div class="card-glass section" style="margin-top:20px">
      <h3 class="heading-sm">Weekly Schedule</h3>
      <div class="schedule-grid" style="margin-top:16px">
        <div class="day-row" v-for="day in schedule" :key="day.name">
          <label class="day-toggle">
            <input type="checkbox" v-model="day.active" />
            <span class="day-name">{{ day.name }}</span>
          </label>
          <div class="time-slots" v-if="day.active">
            <div class="slot" v-for="slot in ['Morning', 'Afternoon', 'Evening']" :key="slot">
              <button class="slot-btn" :class="{ active: day.slots.includes(slot) }" @click="toggleSlot(day, slot)">
                {{ slot }}
              </button>
            </div>
          </div>
          <span v-else class="text-xs text-muted">Unavailable</span>
        </div>
      </div>
    </div>

    <!-- Blocked Dates -->
    <div class="card-glass section" style="margin-top:20px">
      <h3 class="heading-sm">Blocked Dates</h3>
      <p class="text-xs text-muted" style="margin-top:4px">You won&rsquo;t receive bookings on these dates</p>
      <div class="blocked-list" style="margin-top:16px">
        <div class="blocked-item" v-for="(date, i) in blockedDates" :key="i">
          <span>{{ date }}</span>
          <button class="remove-btn" @click="removeBlockDate(i)">
            <AppIcon name="x" :size="14" />
          </button>
        </div>
        <div class="add-block">
          <input type="date" v-model="newBlockDate" class="input" style="max-width:200px" />
          <button class="btn btn-sm btn-outline" @click="addBlockDate">Block Date</button>
        </div>
      </div>
    </div>

    <!-- Travel Radius -->
    <div class="card-glass section" style="margin-top:20px">
      <h3 class="heading-sm">Travel Radius</h3>
      <div style="margin-top:16px">
        <input type="range" v-model.number="travelRadius" min="2" max="25" class="range-input" />
        <div class="flex" style="justify-content:space-between;margin-top:6px">
          <span class="text-xs text-muted">2 km</span>
          <span class="text-sm fw-600" style="color:var(--color-primary)">{{ travelRadius }} km</span>
          <span class="text-xs text-muted">25 km</span>
        </div>
      </div>
    </div>

    <button class="btn btn-primary" style="margin-top:16px" @click="saveAvailability" :disabled="saving">{{ saving ? 'Saving...' : 'Save Availability' }}</button>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import AppIcon from '@/components/AppIcon.vue'
import { cookApi, profileApi } from '@/services/api.js'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const DAY_NAMES = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

function createDefaultSchedule() {
  return DAY_NAMES.map((name, index) => ({
    name,
    day: index,
    active: index < 6,
    slots: index < 6 ? ['Morning', 'Afternoon'] : []
  }))
}

const schedule = reactive(createDefaultSchedule())

const blockedDates = reactive([])
const newBlockDate = ref('')
const travelRadius = ref(10)
const saving = ref(false)
const cookProfileId = ref(null)

onMounted(async () => {
  await loadAvailability()
})

function getBlockedDatesKey() {
  return `sizzzle_blocked_dates_${auth.user?.id || 'me'}`
}

function replaceSchedule(nextSchedule) {
  schedule.splice(0, schedule.length, ...nextSchedule)
}

function resetScheduleFromAvailability(availabilityRows = []) {
  const map = new Map()

  for (const row of availabilityRows) {
    if (!map.has(row.day)) map.set(row.day, [])
    if (row.available !== false) map.get(row.day).push(row.slot)
  }

  const next = DAY_NAMES.map((name, day) => {
    const slots = map.get(day) || []
    return {
      name,
      day,
      active: slots.length > 0,
      slots
    }
  })

  replaceSchedule(next)
}

function loadBlockedDates() {
  blockedDates.splice(0, blockedDates.length)
  const raw = localStorage.getItem(getBlockedDatesKey())
  if (!raw) return
  try {
    const parsed = JSON.parse(raw)
    if (Array.isArray(parsed)) {
      blockedDates.push(...parsed)
    }
  } catch {
    // Ignore malformed persisted dates.
  }
}

function persistBlockedDates() {
  localStorage.setItem(getBlockedDatesKey(), JSON.stringify([...blockedDates]))
}

async function loadAvailability() {
  try {
    const profile = await profileApi.get()
    const cookProfile = profile.cook_profile || null
    cookProfileId.value = cookProfile?.id || null

    if (cookProfile?.travel_radius_km != null) {
      travelRadius.value = Number(cookProfile.travel_radius_km)
    }

    if (cookProfileId.value) {
      const cook = await cookApi.get(cookProfileId.value)
      resetScheduleFromAvailability(cook.availability || [])
      if (cook.travel_radius_km != null) {
        travelRadius.value = Number(cook.travel_radius_km)
      }
    }
  } catch (e) {
    console.error('Failed to load availability', e)
    replaceSchedule(createDefaultSchedule())
  } finally {
    loadBlockedDates()
  }
}

function toggleSlot(day, slot) {
  const idx = day.slots.indexOf(slot)
  if (idx >= 0) day.slots.splice(idx, 1)
  else day.slots.push(slot)
}

function addBlockDate() {
  if (newBlockDate.value && !blockedDates.includes(newBlockDate.value)) {
    blockedDates.push(newBlockDate.value)
    persistBlockedDates()
    newBlockDate.value = ''
  }
}

function removeBlockDate(index) {
  blockedDates.splice(index, 1)
  persistBlockedDates()
}

async function saveAvailability() {
  saving.value = true
  try {
    const slots = []
    for (const day of schedule) {
      if (!day.active) continue
      for (const slot of day.slots) {
        slots.push({ day: day.day, slot, available: true })
      }
    }

    await cookApi.updateAvailability({
      slots,
      travel_radius_km: travelRadius.value
    })

    persistBlockedDates()
    await loadAvailability()
    alert('Availability saved!')
  } catch (e) {
    alert(e.message || 'Failed to save')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.availability-page {
  width: 100%;
}

.section {
  padding: 24px;
  border-radius: var(--radius-lg);
}

.schedule-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.day-row {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px 0;
  border-bottom: 1px solid var(--color-border-light);
}

.day-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 130px;
  cursor: pointer;
}

.day-toggle input {
  width: 16px;
  height: 16px;
  accent-color: var(--color-primary);
}

.day-name {
  font-size: 0.875rem;
  font-weight: 500;
}

.time-slots {
  display: flex;
  gap: 8px;
}

.slot-btn {
  padding: 6px 14px;
  border-radius: var(--radius-full);
  font-size: 0.75rem;
  font-weight: 500;
  background: var(--color-bg-alt);
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.slot-btn.active {
  background: var(--color-primary);
  color: #fff;
  border-color: var(--color-primary);
}

.blocked-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.blocked-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: var(--color-bg-alt);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
}

.remove-btn {
  background: none;
  border: none;
  color: var(--color-error);
  cursor: pointer;
  padding: 4px;
}

.add-block {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-top: 8px;
}

.range-input {
  width: 100%;
  accent-color: var(--color-primary);
}

.btn-sm {
  padding: 6px 16px;
  font-size: 0.813rem;
}
</style>
