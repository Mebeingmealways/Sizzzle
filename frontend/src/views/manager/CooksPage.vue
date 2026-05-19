<template>
  <div class="cooks-page animate-fade-in">
    <div class="page-header">
      <h2 class="heading-md">Cooks</h2>
      <p class="text-sm text-muted">Monitor cook performance in your region</p>
    </div>

    <div class="search-bar" style="margin-top:16px">
      <div class="search-input-wrap">
        <AppIcon name="search" :size="16" />
        <input class="input" v-model="search" placeholder="Search cooks by name or specialization..." />
      </div>
    </div>

    <div class="table-wrap card-glass" style="margin-top:20px">
      <table class="data-table">
        <thead>
          <tr>
            <th>Cook</th>
            <th>Specialization</th>
            <th>Jobs</th>
            <th>Rating</th>
            <th>Earnings</th>
            <th>Status</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="cook in filteredCooks" :key="cook.id">
            <td>
              <div class="cook-cell">
                <div class="cook-avatar">{{ cook.initials }}</div>
                <div>
                  <div class="fw-600 text-sm">{{ cook.name }}</div>
                  <div class="text-xs text-muted">{{ cook.city }}</div>
                </div>
              </div>
            </td>
            <td class="text-sm">{{ cook.specialization }}</td>
            <td class="text-sm fw-600">{{ cook.jobs }}</td>
            <td>
              <div class="rating-cell">
                <AppIcon name="star" :size="13" color="#F59E0B" />
                <span class="text-sm fw-600">{{ cook.rating }}</span>
              </div>
            </td>
            <td class="text-sm fw-600" style="color:var(--color-primary-dark)">{{ cook.earnings }}</td>
            <td><span class="badge" :class="'status-' + cook.status">{{ cook.status }}</span></td>
            <td>
              <button
                class="btn btn-sm"
                :class="cook.status === 'Active' ? 'btn-outline' : 'btn-primary'"
                @click="toggleCook(cook)"
              >
                {{ cook.status === 'Active' ? 'Disable' : 'Enable' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import AppIcon from '@/components/AppIcon.vue'
import { managerApi } from '@/services/api.js'

const search = ref('')
const cooks = ref([])
const loading = ref(true)

async function loadCooks() {
  loading.value = true
  try {
    const data = await managerApi.getCookMetrics()
    cooks.value = (data || []).map(c => ({
      id: c.id,
      name: c.name || 'Cook',
      initials: (c.name || 'C').split(' ').map(w => w[0]).join('').slice(0,2),
      city: c.city || '',
      specialization: c.specialization || '',
      jobs: c.total_jobs || 0,
      rating: Number(c.rating || 0).toFixed(1),
      earnings: `Rs ${((c.total_earnings || 0) / 1000).toFixed(0)}K`,
      status: c.verification_status === 'approved' ? 'Active' : c.verification_status === 'pending' ? 'Under Review' : 'Inactive'
    }))
  } catch (e) {
    console.error('Failed to load cooks', e)
  } finally {
    loading.value = false
  }
}

onMounted(loadCooks)

const filteredCooks = computed(() => {
  const q = search.value.toLowerCase()
  if (!q) return cooks.value
  return cooks.value.filter(c => c.name.toLowerCase().includes(q) || c.specialization.toLowerCase().includes(q))
})

async function toggleCook(cook) {
  const enable = cook.status !== 'Active'
  try {
    await managerApi.setCookStatus(cook.id, { enabled: enable })
    await loadCooks()
  } catch (e) {
    alert(e.message || 'Failed to update cook status')
  }
}
</script>

<style scoped>
.cooks-page { width: 100%; }

.search-input-wrap { display: flex; align-items: center; gap: 10px; padding: 0 14px; background: var(--color-bg); border: 1px solid var(--color-border); border-radius: var(--radius-md); }
.search-input-wrap .input { border: none; padding-left: 0; }

.table-wrap { padding: 0; border-radius: var(--radius-lg); overflow: hidden; }

.data-table { width: 100%; border-collapse: collapse; }
.data-table th { text-align: left; font-size: 0.75rem; font-weight: 600; color: var(--color-text-light); text-transform: uppercase; letter-spacing: 0.05em; padding: 14px 16px; background: var(--color-bg-alt); border-bottom: 1px solid var(--color-border); }
.data-table td { padding: 14px 16px; border-bottom: 1px solid var(--color-border-light); }
.data-table tr:hover td { background: rgba(62, 180, 137, 0.04); }

.cook-cell { display: flex; align-items: center; gap: 10px; }
.cook-avatar { width: 36px; height: 36px; border-radius: 50%; background: var(--color-primary-light); color: var(--color-primary-dark); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.688rem; flex-shrink: 0; }

.rating-cell { display: flex; align-items: center; gap: 4px; }

.status-Active { background: #D1FAE5; color: #059669; }
.status-Inactive { background: #FEE2E2; color: #DC2626; }
.status-Under\ Review { background: #FEF3C7; color: #D97706; }
[class*="status-"] { padding: 3px 10px; border-radius: var(--radius-full); font-size: 0.688rem; font-weight: 600; }
</style>
