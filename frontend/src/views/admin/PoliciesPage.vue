<template>
  <div class="policies-page animate-fade-in">
    <div class="page-header">
      <h2 class="heading-md">Policies</h2>
      <p class="text-sm text-muted">Configure platform-wide policies and rates</p>
    </div>

    <!-- Cancellation Policy -->
    <div class="card-glass section" style="margin-top:20px">
      <h3 class="heading-sm">Cancellation Policy</h3>
      <div class="policy-grid" style="margin-top:16px">
        <div class="form-group">
          <label>Free Cancellation Window</label>
          <div class="input-group">
            <input class="input" type="number" v-model.number="cancellation.freeWindow" min="1" max="24" />
            <span class="input-suffix">hours before booking</span>
          </div>
        </div>
        <div class="form-group">
          <label>Late Cancellation Fee</label>
          <div class="input-group">
            <input class="input" type="number" v-model.number="cancellation.lateFee" min="0" max="100" />
            <span class="input-suffix">% of booking value</span>
          </div>
        </div>
        <div class="form-group">
          <label>No-Show Fee</label>
          <div class="input-group">
            <input class="input" type="number" v-model.number="cancellation.noShowFee" min="0" max="100" />
            <span class="input-suffix">% of booking value</span>
          </div>
        </div>
        <div class="form-group">
          <label>Cook Cancellation Penalty</label>
          <div class="input-group">
            <input class="input" type="number" v-model.number="cancellation.cookPenalty" min="0" />
            <span class="input-suffix">INR flat fee</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Commission Rates -->
    <div class="card-glass section" style="margin-top:20px">
      <h3 class="heading-sm">Commission Rates</h3>
      <div class="commission-table" style="margin-top:16px">
        <div class="commission-row header">
          <span>Tier</span><span>Platform Fee</span><span>Cook Share</span><span>GST</span>
        </div>
        <div class="commission-row" v-for="tier in commission" :key="tier.name">
          <span class="fw-600">{{ tier.name }}</span>
          <span>
            <input class="input compact" type="number" v-model.number="tier.platformFee" min="0" max="50" />%
          </span>
          <span class="fw-600" style="color:var(--color-primary)">{{ 100 - tier.platformFee - tier.gst }}%</span>
          <span>
            <input class="input compact" type="number" v-model.number="tier.gst" min="0" max="28" />%
          </span>
        </div>
      </div>
    </div>

    <!-- Payout Settings -->
    <div class="card-glass section" style="margin-top:20px">
      <h3 class="heading-sm">Payout Settings</h3>
      <div class="policy-grid" style="margin-top:16px">
        <div class="form-group">
          <label>Default Payout Cycle</label>
          <select class="input" v-model="payout.cycle">
            <option>Weekly</option><option>Bi-Weekly</option><option>Monthly</option>
          </select>
        </div>
        <div class="form-group">
          <label>Payout Day</label>
          <select class="input" v-model="payout.day">
            <option>Monday</option><option>Tuesday</option><option>Wednesday</option>
            <option>Thursday</option><option>Friday</option>
          </select>
        </div>
        <div class="form-group">
          <label>Minimum Payout</label>
          <div class="input-group">
            <input class="input" type="number" v-model.number="payout.minimum" min="100" />
            <span class="input-suffix">INR</span>
          </div>
        </div>
        <div class="form-group">
          <label>Hold Period</label>
          <div class="input-group">
            <input class="input" type="number" v-model.number="payout.holdDays" min="0" max="14" />
            <span class="input-suffix">days after job</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Service Limits -->
    <div class="card-glass section" style="margin-top:20px">
      <h3 class="heading-sm">Service Limits</h3>
      <div class="policy-grid" style="margin-top:16px">
        <div class="form-group">
          <label>Max People per Booking</label>
          <input class="input" type="number" v-model.number="limits.maxPeople" />
        </div>
        <div class="form-group">
          <label>Max Dishes per Booking</label>
          <input class="input" type="number" v-model.number="limits.maxDishes" />
        </div>
        <div class="form-group">
          <label>Min Advance Booking</label>
          <div class="input-group">
            <input class="input" type="number" v-model.number="limits.minAdvance" />
            <span class="input-suffix">hours</span>
          </div>
        </div>
        <div class="form-group">
          <label>Max Advance Booking</label>
          <div class="input-group">
            <input class="input" type="number" v-model.number="limits.maxAdvance" />
            <span class="input-suffix">days</span>
          </div>
        </div>
      </div>
    </div>

    <button class="btn btn-primary" style="margin-top:16px" @click="savePolicies" :disabled="saving">{{ saving ? 'Saving...' : 'Save All Policies' }}</button>
  </div>
</template>

<script setup>
import { reactive, onMounted, ref } from 'vue'
import { adminApi } from '@/services/api.js'

const cancellation = reactive({ freeWindow: 4, lateFee: 25, noShowFee: 50, cookPenalty: 500 })
const commission = reactive([
  { name: 'Standard', platformFee: 15, gst: 5 },
  { name: 'Premium', platformFee: 12, gst: 5 }
])
const payout = reactive({ cycle: 'Weekly', day: 'Wednesday', minimum: 500, holdDays: 3 })
const limits = reactive({ maxPeople: 20, maxDishes: 10, minAdvance: 6, maxAdvance: 30 })
const saving = ref(false)

onMounted(async () => {
  try {
    const policies = await adminApi.getPolicies()
    if (Array.isArray(policies)) {
      for (const p of policies) {
        if (p.key === 'cancellation_free_window') cancellation.freeWindow = parseInt(p.value) || 4
        if (p.key === 'late_fee_pct') cancellation.lateFee = parseInt(p.value) || 25
        if (p.key === 'platform_fee_pct') commission[0].platformFee = parseInt(p.value) || 15
        if (p.key === 'max_people') limits.maxPeople = parseInt(p.value) || 20
        if (p.key === 'min_advance_hours') limits.minAdvance = parseInt(p.value) || 6
      }
    }
  } catch (e) { /* use defaults */ }
})

async function savePolicies() {
  saving.value = true
  try {
    await adminApi.updatePolicies([
      { key: 'cancellation_free_window', value: String(cancellation.freeWindow) },
      { key: 'late_fee_pct', value: String(cancellation.lateFee) },
      { key: 'no_show_fee_pct', value: String(cancellation.noShowFee) },
      { key: 'platform_fee_pct', value: String(commission[0].platformFee) },
      { key: 'max_people', value: String(limits.maxPeople) },
      { key: 'min_advance_hours', value: String(limits.minAdvance) }
    ])
    alert('Policies saved!')
  } catch (e) { alert(e.message || 'Failed to save') }
  finally { saving.value = false }
}
</script>

<style scoped>
.policies-page { width: 100%; }

.section { padding: 28px; border-radius: var(--radius-lg); }

.policy-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
@media (max-width: 600px) { .policy-grid { grid-template-columns: 1fr; } }

.form-group label { display: block; font-size: 0.75rem; font-weight: 600; color: var(--color-text-light); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 0.04em; }

.input-group { display: flex; align-items: center; gap: 8px; }
.input-suffix { font-size: 0.75rem; color: var(--color-text-light); white-space: nowrap; }

.commission-table { display: flex; flex-direction: column; gap: 0; }
.commission-row { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 12px; padding: 12px 0; border-bottom: 1px solid var(--color-border-light); align-items: center; font-size: 0.875rem; }
.commission-row.header { font-size: 0.75rem; font-weight: 600; color: var(--color-text-light); text-transform: uppercase; letter-spacing: 0.04em; }

.input.compact { width: 64px; padding: 6px 8px; display: inline-block; text-align: center; }
</style>
