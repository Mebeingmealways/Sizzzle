<template>
  <div class="booking-page animate-fade-in">
    <!-- Steps -->
    <div class="booking-steps">
      <div v-for="(s, i) in stepLabels" :key="i" class="booking-step" :class="{ active: step > i, current: step === i + 1 }">
        <div class="step-circle">{{ i + 1 }}</div>
        <span class="step-text">{{ s }}</span>
      </div>
    </div>

    <!-- Step 1: Select Date & People -->
    <div v-if="step === 1" class="step-content card-glass">
      <h3 class="heading-sm">When and for how many?</h3>
      <div class="form-grid">
        <div class="input-group">
          <label>Date</label>
          <input v-model="form.date" type="date" class="input" :min="minDate" required />
        </div>
        <div class="input-group">
          <label>Time Slot</label>
          <select v-model="form.timeSlot" class="input" required>
            <option value="">Select time</option>
            <option value="breakfast">Breakfast (7:00 - 9:00)</option>
            <option value="lunch">Lunch (11:00 - 13:00)</option>
            <option value="dinner">Dinner (18:00 - 20:00)</option>
          </select>
        </div>
        <div class="input-group">
          <label>Number of People</label>
          <div class="counter">
            <button type="button" class="btn btn-icon counter-btn" @click="form.people = Math.max(1, form.people - 1)" aria-label="Decrease number of people">
              <AppIcon name="minus" :size="18" :stroke-width="2.5" />
            </button>
            <span class="counter-value">{{ form.people }}</span>
            <button type="button" class="btn btn-icon counter-btn" @click="form.people++" aria-label="Increase number of people">
              <AppIcon name="plus" :size="18" :stroke-width="2.5" />
            </button>
          </div>
        </div>
        <div class="input-group">
          <label>Service Tier</label>
          <div class="tier-select">
            <button type="button" class="tier-option" :class="{ selected: form.tier === 'standard' }" @click="form.tier = 'standard'">
              <strong>Standard</strong>
              <span class="text-xs text-muted">You provide groceries</span>
            </button>
            <button type="button" class="tier-option" :class="{ selected: form.tier === 'premium' }" @click="form.tier = 'premium'">
              <strong>Premium</strong>
              <span class="text-xs text-muted">Cook brings groceries</span>
            </button>
          </div>
        </div>
        <div class="input-group input-group-span">
          <label>Service Location</label>
          <div class="location-panel card">
            <div class="location-row">
              <div>
                <strong class="location-title">GPS-assisted address</strong>
                <p class="text-xs text-muted">
                  {{ locationSummary }}
                </p>
              </div>
              <div class="location-actions">
                <button type="button" class="btn btn-sm btn-outline" @click="captureCurrentLocation" :disabled="location.loading.value">
                  <AppIcon name="navigation" :size="14" />
                  {{ location.loading.value ? 'Locating...' : 'Use Current GPS' }}
                </button>
                <button
                  type="button"
                  class="btn btn-sm"
                  :class="location.watching.value ? 'btn-accent' : 'btn-ghost'"
                  @click="toggleLocationWatch"
                >
                  <AppIcon :name="location.watching.value ? 'x-circle' : 'activity'" :size="14" />
                  {{ location.watching.value ? 'Stop Live' : 'Live Track' }}
                </button>
              </div>
            </div>
            <div class="location-meta" v-if="location.position.value">
              <span>
                <AppIcon name="map-pin" :size="13" /> {{ Number(location.position.value.lat).toFixed(5) }}, {{ Number(location.position.value.lng).toFixed(5) }}
              </span>
              <span><AppIcon name="shield" :size="13" /> Accuracy {{ location.position.value.accuracy }}m</span>
              <span v-if="location.updatedAt.value"><AppIcon name="clock" :size="13" /> Updated {{ location.updatedAt.value.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }}</span>
            </div>
            <p v-if="location.error.value" class="location-error">{{ location.error.value }}</p>
            <div class="input-group" style="margin-top:12px">
              <label>Manual Address (fallback)</label>
              <input v-model="form.address" class="input" type="text" placeholder="Apartment, area, city" />
            </div>
          </div>
        </div>
      </div>
      <button class="btn btn-primary" style="margin-top:24px" @click="step = 2">
        Continue <AppIcon name="arrow-right" :size="16" />
      </button>
    </div>

    <!-- Step 2: Select Dishes -->
    <div v-if="step === 2" class="step-content card-glass">
      <h3 class="heading-sm">Choose your dishes</h3>
      <div class="dishes-search">
        <AppIcon name="search" :size="18" class="search-icon" />
        <input v-model="dishSearch" type="text" class="input search-input" placeholder="Search dishes..." />
      </div>
      <div class="dish-categories">
        <button v-for="cat in categories" :key="cat" class="cat-btn" :class="{ active: activeCat === cat }" @click="activeCat = cat">
          {{ cat }}
        </button>
      </div>
      <div class="dishes-grid">
        <div v-for="dish in filteredDishes" :key="dish.id" class="dish-card card"
          :class="{ selected: isDishSelected(dish) }" @click="toggleDish(dish)">
          <div class="dish-icon" :class="dish.veg ? 'dish-veg' : 'dish-non-veg'">
            <div class="veg-indicator"></div>
          </div>
          <div class="dish-info">
            <div class="dish-name">{{ dish.name }}</div>
            <div class="text-xs text-muted">{{ dish.category }} &middot; {{ dish.prep_time }}min</div>
          </div>
          <div class="dish-check" v-if="isDishSelected(dish)">
            <AppIcon name="check" :size="16" />
          </div>
        </div>
      </div>
      <div class="step-actions">
        <button class="btn btn-ghost" @click="step = 1">
          <AppIcon name="arrow-left" :size="16" /> Back
        </button>
        <button class="btn btn-primary" @click="goToStep(3)" :disabled="selectedDishes.length === 0">
          Continue <AppIcon name="arrow-right" :size="16" />
        </button>
      </div>
    </div>

    <!-- Step 3: Select Cook -->
    <div v-if="step === 3" class="step-content card-glass">
      <h3 class="heading-sm">Choose your cook</h3>
      <p class="text-sm text-muted" style="margin-bottom:20px">Recommended based on your location, preferences, and ratings</p>
      <p v-if="loadingCooks" class="text-muted text-sm">Loading recommended cooks...</p>
      <div class="cooks-list">
        <div v-for="cook in availableCooks" :key="cook.id" class="cook-select-card card"
          :class="{ selected: selectedCook?.id === cook.id }" @click="selectedCook = cook">
          <div class="cook-select-avatar">{{ cook.name?.charAt(0) }}</div>
          <div class="cook-select-info">
            <div class="cook-select-name">{{ cook.name }}</div>
            <div class="text-xs text-muted">{{ cook.specialty }}</div>
            <div class="cook-select-meta">
              <span class="badge badge-primary text-xs">Match: {{ Math.round(cook.matchScore) }}%</span>
              <span class="cook-rating">
                <AppIcon name="star" :size="12" style="color:#F59E0B" /> {{ cook.rating }}
              </span>
              <span class="text-xs text-muted">{{ cook.distance }}</span>
            </div>
          </div>
          <div class="cook-select-check" v-if="selectedCook?.id === cook.id">
            <AppIcon name="check-circle" :size="22" />
          </div>
        </div>
      </div>
      <div class="step-actions">
        <button class="btn btn-ghost" @click="step = 2">
          <AppIcon name="arrow-left" :size="16" /> Back
        </button>
        <button class="btn btn-primary" @click="goToStep(4)" :disabled="!selectedCook">
          Continue <AppIcon name="arrow-right" :size="16" />
        </button>
      </div>
    </div>

    <!-- Step 4: Review & Confirm -->
    <div v-if="step === 4" class="step-content card-glass">
      <h3 class="heading-sm">Review & Confirm</h3>
      <div class="review-section">
        <div class="review-row">
          <span class="text-muted">Date</span>
          <span class="review-value">{{ form.date }} ({{ form.timeSlot }})</span>
        </div>
        <div class="review-row">
          <span class="text-muted">People</span>
          <span class="review-value">{{ form.people }}</span>
        </div>
        <div class="review-row">
          <span class="text-muted">Service Address</span>
          <span class="review-value review-wrap">{{ form.address || locationSummary }}</span>
        </div>
        <div class="review-row">
          <span class="text-muted">Tier</span>
          <span class="review-value badge" :class="form.tier === 'premium' ? 'badge-accent' : 'badge-primary'">{{ form.tier }}</span>
        </div>
        <div class="review-row">
          <span class="text-muted">Dishes</span>
          <span class="review-value">{{ selectedDishes.map(d => d.name).join(', ') }}</span>
        </div>
        <div class="review-row">
          <span class="text-muted">Cook</span>
          <span class="review-value">{{ selectedCook?.name }}</span>
        </div>
        <div class="review-row review-total">
          <span>Estimated Total</span>
          <span class="review-price">Rs {{ estimatedTotal.toLocaleString() }}</span>
        </div>
      </div>

      <div v-if="form.tier === 'standard' && ingredientsList.length" class="ingredients-note card">
        <AppIcon name="info" :size="16" class="text-primary" />
        <div>
          <strong class="text-sm">Ingredients to arrange</strong>
          <p class="text-xs text-muted" style="margin-top:4px">
            {{ ingredientsList.map(i => `${i.name} (${i.quantity})`).join(', ') }}
          </p>
        </div>
      </div>

      <div class="extras-section">
        <label class="extra-option">
          <input type="checkbox" v-model="form.utensilCleaning" />
          <span>Add utensil cleaning service (+Rs 150)</span>
        </label>
      </div>

      <div class="step-actions">
        <button class="btn btn-ghost" @click="step = 3">
          <AppIcon name="arrow-left" :size="16" /> Back
        </button>
        <button class="btn btn-accent btn-lg" @click="confirmBooking">
          Confirm Booking
        </button>
      </div>
    </div>

    <!-- Step 5: Confirmation -->
    <div v-if="step === 5" class="step-content card-glass confirmation-card">
      <div class="confirm-icon">
        <AppIcon name="check-circle" :size="56" />
      </div>
      <h3 class="heading-md">Booking Confirmed</h3>
      <p class="text-muted">Your booking has been placed successfully. The cook will be notified.</p>
      <div class="confirm-details card" style="margin-top:24px; padding:20px">
        <div class="review-row"><span class="text-muted">Booking ID</span><span>#{{ bookingResult?.booking_code || 'N/A' }}</span></div>
        <div class="review-row"><span class="text-muted">Date</span><span>{{ form.date }}</span></div>
        <div class="review-row"><span class="text-muted">Cook</span><span>{{ selectedCook?.name }}</span></div>
        <div class="review-row"><span class="text-muted">OTP</span><span style="font-weight:700;color:var(--color-accent)">{{ bookingResult?.otp_code }}</span></div>
      </div>
      <div class="confirm-actions" style="margin-top:24px">
        <router-link to="/customer/bookings" class="btn btn-primary">View Bookings</router-link>
        <router-link to="/customer" class="btn btn-ghost">Back to Dashboard</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppIcon from '../../components/AppIcon.vue'
import { useLiveLocation } from '../../composables/useLiveLocation'
import { dishApi, cookApi, bookingApi } from '../../services/api'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const step = ref(1)
const stepLabels = ['Schedule', 'Dishes', 'Cook', 'Confirm']
const bookingResult = ref(null)

const tomorrow = new Date()
tomorrow.setDate(tomorrow.getDate() + 1)
const minDate = tomorrow.toISOString().split('T')[0]

const form = ref({
  date: '', timeSlot: '', people: 4, tier: 'standard', utensilCleaning: false, address: auth.user?.address || ''
})

const location = useLiveLocation()

const locationSummary = computed(() => {
  if (!location.position.value) {
    return 'No GPS lock yet. Use current location to improve cook matching and ETA precision.'
  }
  return `GPS locked (${Number(location.position.value.lat).toFixed(5)}, ${Number(location.position.value.lng).toFixed(5)})`
})

const dishSearch = ref('')
const activeCat = ref('All')
const selectedDishes = ref([])
const selectedCook = ref(null)

const categories = ref(['All'])
const dishes = ref([])
const availableCooks = ref([])
const ingredientsList = ref([])
const loadingDishes = ref(true)
const loadingCooks = ref(false)

onMounted(async () => {
  try {
    const data = await dishApi.list()
    dishes.value = data.map(d => ({
      id: d.id,
      name: d.name,
      category: d.cuisine || d.category,
      veg: d.veg_nonveg === 'veg',
      prep_time: d.prep_time_minutes,
      description: d.description
    }))
    const cats = [...new Set(data.map(d => d.cuisine || d.category))]
    categories.value = ['All', ...cats]
  } catch (e) {
    console.error('Failed to load dishes', e)
  } finally {
    loadingDishes.value = false
  }
})

const filteredDishes = computed(() => {
  return dishes.value.filter(d => {
    const matchCat = activeCat.value === 'All' || d.category === activeCat.value
    const matchSearch = d.name.toLowerCase().includes(dishSearch.value.toLowerCase())
    return matchCat && matchSearch
  })
})

function toggleDish(dish) {
  const idx = selectedDishes.value.findIndex(d => d.id === dish.id)
  if (idx >= 0) selectedDishes.value.splice(idx, 1)
  else selectedDishes.value.push(dish)
}

function isDishSelected(dish) {
  return selectedDishes.value.some(d => d.id === dish.id)
}

async function loadCooks() {
  loadingCooks.value = true
  try {
    const params = {
      latitude: location.position.value?.lat || auth.user?.latitude,
      longitude: location.position.value?.lng || auth.user?.longitude
    }
    if (form.value.date) {
      params.date = form.value.date
    }
    const data = await cookApi.recommend(params)
    availableCooks.value = data.map(c => ({
      id: c.id,
      name: c.name,
      specialty: c.specialization,
      rating: c.rating,
      distance: c.distance_km ? `${c.distance_km} km` : 'N/A',
      matchScore: c.match_score,
      phone: c.phone
    }))
  } catch (e) {
    console.error('Failed to load cooks', e)
  } finally {
    loadingCooks.value = false
  }
}

async function loadIngredients() {
  if (selectedDishes.value.length === 0) return
  try {
    const ids = selectedDishes.value.map(d => d.id)
    ingredientsList.value = await dishApi.getIngredients(ids)
  } catch (e) {
    console.error('Failed to load ingredients', e)
  }
}

function goToStep(s) {
  if (s === 3) loadCooks()
  if (s === 4) loadIngredients()
  step.value = s
}

const estimatedTotal = computed(() => {
  const base = selectedDishes.value.length * 150
  const peopleFactor = form.value.people
  const tierMultiplier = form.value.tier === 'premium' ? 1.3 : 1
  const extra = form.value.utensilCleaning ? 150 : 0
  return Math.round(base * peopleFactor * tierMultiplier / 2 + extra)
})

async function confirmBooking() {
  if (!selectedCook.value) return
  try {
    const data = {
      cook_id: selectedCook.value.id,
      date: form.value.date,
      time_slot: form.value.timeSlot,
      num_people: form.value.people,
      tier: form.value.tier,
      total_amount: estimatedTotal.value,
      dish_ids: selectedDishes.value.map(d => d.id),
      address: form.value.address || locationSummary.value,
      latitude: location.position.value?.lat,
      longitude: location.position.value?.lng,
      notes: form.value.utensilCleaning ? 'Utensil cleaning requested' : ''
    }
    const result = await bookingApi.create(data)
    bookingResult.value = result
    step.value = 5
  } catch (e) {
    alert(e.message || 'Booking failed')
  }
}

function captureCurrentLocation() {
  location.fetchCurrentPosition()
}

function toggleLocationWatch() {
  if (location.watching.value) {
    location.stopWatching()
  } else {
    location.startWatching()
  }
}
</script>

<style scoped>
.booking-page {
  width: 100%;
}

.booking-steps {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 28px;
}

.booking-step {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  position: relative;
}

.booking-step:not(:last-child)::after {
  content: '';
  flex: 1;
  height: 2px;
  background: var(--color-border);
  margin-left: 8px;
}

.booking-step.active::after {
  background: var(--color-primary);
}

.step-circle {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  background: var(--color-bg-alt);
  color: var(--color-text-light);
  border: 2px solid var(--color-border);
  flex-shrink: 0;
}

.booking-step.active .step-circle,
.booking-step.current .step-circle {
  background: var(--color-primary);
  color: #fff;
  border-color: var(--color-primary);
}

.booking-step.current .step-circle {
  box-shadow: 0 0 0 4px rgba(62, 180, 137, 0.2);
}

.step-text {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--color-text-light);
  white-space: nowrap;
}

.booking-step.active .step-text,
.booking-step.current .step-text {
  color: var(--color-text);
}

.step-content {
  padding: 32px;
  border-radius: var(--radius-lg);
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-top: 20px;
}

.input-group-span {
  grid-column: 1 / -1;
}

.counter {
  display: flex;
  align-items: center;
  gap: 16px;
}

.counter-btn {
  width: 36px;
  height: 36px;
  border: 1.5px solid var(--color-primary);
  border-radius: var(--radius-md);
  background: #fff;
  color: var(--color-primary-dark);
  box-shadow: 0 4px 12px rgba(45, 182, 125, 0.14);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast), background var(--transition-fast);
}

.counter-btn:hover {
  background: var(--color-primary-ghost);
  transform: translateY(-1px);
  box-shadow: 0 7px 14px rgba(45, 182, 125, 0.2);
}

.counter-value {
  font-size: 1.25rem;
  font-weight: 700;
  min-width: 24px;
  text-align: center;
}

.tier-select {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.tier-option {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 14px;
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  text-align: left;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.tier-option.selected {
  border-color: var(--color-primary);
  background: rgba(62, 180, 137, 0.04);
}

.location-panel {
  padding: 14px;
  border-radius: var(--radius-md);
  background: linear-gradient(180deg, rgba(45, 182, 125, 0.06), rgba(255, 255, 255, 0.88));
  border: 1px solid var(--color-border-accent);
}

.location-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.location-title {
  font-size: 0.875rem;
  color: var(--color-text);
}

.location-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.location-meta {
  margin-top: 10px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  color: var(--color-text-secondary);
  font-size: 0.75rem;
}

.location-meta span {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.location-error {
  margin-top: 8px;
  color: var(--color-error);
  font-size: 0.75rem;
  font-weight: 500;
}

/* Dishes */
.dishes-search {
  position: relative;
  margin-top: 16px;
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--color-text-light);
}

.search-input {
  padding-left: 42px;
}

.dish-categories {
  display: flex;
  gap: 8px;
  margin-top: 16px;
  flex-wrap: wrap;
}

.cat-btn {
  padding: 6px 16px;
  border-radius: var(--radius-full);
  font-size: 0.813rem;
  font-weight: 500;
  background: var(--color-bg-alt);
  color: var(--color-text-secondary);
  border: 1px solid transparent;
  transition: all var(--transition-fast);
  cursor: pointer;
}

.cat-btn.active {
  background: var(--color-primary);
  color: #fff;
}

.dishes-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 16px;
  max-height: 360px;
  overflow-y: auto;
}

.dish-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.dish-card.selected {
  border-color: var(--color-primary);
  background: rgba(62, 180, 137, 0.04);
}

.dish-icon {
  width: 12px;
  height: 12px;
  flex-shrink: 0;
}

.veg-indicator {
  width: 10px;
  height: 10px;
  border-radius: 2px;
  border: 1.5px solid;
}

.dish-veg .veg-indicator {
  border-color: #16a34a;
  background: #16a34a;
}

.dish-non-veg .veg-indicator {
  border-color: #dc2626;
  background: #dc2626;
}

.dish-info { flex: 1; }

.dish-name {
  font-weight: 500;
  font-size: 0.875rem;
}

.dish-check {
  color: var(--color-primary);
}

/* Cook selection */
.cooks-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.cook-select-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px 20px;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.cook-select-card.selected {
  border-color: var(--color-primary);
  background: rgba(62, 180, 137, 0.04);
}

.cook-select-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  flex-shrink: 0;
}

.cook-select-info { flex: 1; }

.cook-select-name {
  font-weight: 600;
}

.cook-select-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 6px;
}

.cook-rating {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 0.813rem;
}

.cook-select-check {
  color: var(--color-primary);
}

/* Review */
.review-section {
  margin-top: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.review-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid var(--color-border-light);
  font-size: 0.938rem;
}

.review-row:last-child { border-bottom: none; }

.review-total {
  font-weight: 600;
  padding-top: 14px;
  margin-top: 4px;
  border-top: 2px solid var(--color-border);
}

.review-wrap {
  max-width: 62%;
  text-align: right;
}

.review-price {
  font-size: 1.25rem;
  color: var(--color-primary-dark);
  font-weight: 700;
}

.ingredients-note {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 16px;
  margin-top: 20px;
}

.extras-section {
  margin-top: 20px;
}

.extra-option {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-size: 0.938rem;
}

.extra-option input {
  width: 18px;
  height: 18px;
  accent-color: var(--color-primary);
}

/* Confirmation */
.confirmation-card {
  text-align: center;
}

.confirm-icon {
  color: var(--color-primary);
  margin-bottom: 16px;
}

.confirm-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.step-actions {
  display: flex;
  justify-content: space-between;
  margin-top: 24px;
}

@media (max-width: 640px) {
  .form-grid { grid-template-columns: 1fr; }
  .dishes-grid { grid-template-columns: 1fr; }
  .step-content { padding: 20px; }
  .step-text { display: none; }
  .review-wrap { max-width: 55%; }
}
</style>
