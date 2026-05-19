<template>
  <div class="taste-page animate-fade-in">
    <div class="page-header">
      <h2 class="heading-md">Taste Profile</h2>
      <p class="text-sm text-muted">Help cooks prepare meals tailored to your preferences</p>
    </div>

    <!-- Dietary Preferences -->
    <div class="section-card card-glass">
      <h3 class="heading-sm">Dietary Preferences</h3>
      <div class="chip-grid" style="margin-top:16px">
        <button v-for="pref in dietaryOptions" :key="pref" class="chip"
          :class="{ active: taste.dietary.includes(pref) }" @click="toggleArray(taste.dietary, pref)">
          {{ pref }}
        </button>
      </div>
    </div>

    <!-- Allergies -->
    <div class="section-card card-glass">
      <h3 class="heading-sm">Food Allergies</h3>
      <div class="chip-grid" style="margin-top:16px">
        <button v-for="allergy in allergyOptions" :key="allergy" class="chip chip-warn"
          :class="{ active: taste.allergies.includes(allergy) }" @click="toggleArray(taste.allergies, allergy)">
          {{ allergy }}
        </button>
      </div>
    </div>

    <!-- Spice Level -->
    <div class="section-card card-glass">
      <h3 class="heading-sm">Spice Tolerance</h3>
      <div class="spice-slider" style="margin-top:20px">
        <input type="range" v-model.number="taste.spiceLevel" min="1" max="5" class="range-input" />
        <div class="spice-labels">
          <span :class="{ active: taste.spiceLevel === 1 }">Mild</span>
          <span :class="{ active: taste.spiceLevel === 2 }">Light</span>
          <span :class="{ active: taste.spiceLevel === 3 }">Medium</span>
          <span :class="{ active: taste.spiceLevel === 4 }">Hot</span>
          <span :class="{ active: taste.spiceLevel === 5 }">Extra Hot</span>
        </div>
      </div>
    </div>

    <!-- Kitchen Equipment -->
    <div class="section-card card-glass">
      <h3 class="heading-sm">Kitchen Equipment Available</h3>
      <p class="text-xs text-muted" style="margin-top:4px">Checked before booking to ensure the cook can prepare your dishes</p>
      <div class="equipment-grid" style="margin-top:16px">
        <label v-for="eq in equipmentOptions" :key="eq" class="equipment-item">
          <input type="checkbox" :checked="taste.equipment.includes(eq)" @change="toggleArray(taste.equipment, eq)" />
          <span>{{ eq }}</span>
        </label>
      </div>
    </div>

    <button class="btn btn-primary" style="margin-top:12px" @click="savePreferences" :disabled="saving">{{ saving ? 'Saving...' : 'Save Preferences' }}</button>
  </div>
</template>

<script setup>
import { reactive, onMounted, ref } from 'vue'
import { profileApi } from '@/services/api.js'

const taste = reactive({
  dietary: [],
  allergies: [],
  spiceLevel: 3,
  equipment: []
})

const saving = ref(false)

const dietaryOptions = ['Vegetarian', 'Vegan', 'Eggetarian', 'Non-Vegetarian', 'Keto', 'Gluten-Free', 'Jain', 'Low-Carb']
const allergyOptions = ['Peanuts', 'Tree Nuts', 'Dairy', 'Gluten', 'Soy', 'Shellfish', 'Eggs', 'Sesame']
const equipmentOptions = ['Gas Stove', 'Induction', 'Microwave', 'Oven', 'Blender', 'Mixer Grinder', 'Pressure Cooker', 'Air Fryer', 'Tandoor', 'Kadhai/Wok']

onMounted(async () => {
  try {
    const data = await profileApi.getTasteProfile()
    if (data) {
      taste.dietary = data.dietary_preferences || []
      taste.allergies = data.allergies || []
      taste.spiceLevel = data.spice_level || 3
      taste.equipment = data.kitchen_equipment || []
    }
  } catch (e) { /* first time – empty */ }
})

function toggleArray(arr, item) {
  const idx = arr.indexOf(item)
  if (idx >= 0) arr.splice(idx, 1)
  else arr.push(item)
}

async function savePreferences() {
  saving.value = true
  try {
    await profileApi.updateTasteProfile({
      dietary_preferences: taste.dietary,
      allergies: taste.allergies,
      spice_level: taste.spiceLevel,
      kitchen_equipment: taste.equipment
    })
    alert('Preferences saved!')
  } catch (e) {
    alert(e.message || 'Failed to save')
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.taste-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
}

.section-card {
  padding: 28px;
  border-radius: var(--radius-lg);
}

.chip-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
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

.chip.active {
  background: var(--color-primary);
  color: #fff;
  border-color: var(--color-primary);
}

.chip-warn.active {
  background: var(--color-error);
  border-color: var(--color-error);
}

.range-input {
  width: 100%;
  accent-color: var(--color-primary);
  height: 6px;
}

.spice-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 0.75rem;
  color: var(--color-text-light);
}

.spice-labels span.active {
  color: var(--color-primary-dark);
  font-weight: 600;
}

.equipment-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 10px;
}

.equipment-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
  cursor: pointer;
}

.equipment-item input {
  width: 16px;
  height: 16px;
  accent-color: var(--color-primary);
}
</style>
