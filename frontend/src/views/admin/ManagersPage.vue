<template>
  <div class="managers-page animate-fade-in">
    <div class="page-header">
      <h2 class="heading-md">Managers</h2>
      <p class="text-sm text-muted">Manage regional managers and their assignments</p>
    </div>

    <div class="actions-bar" style="margin-top:16px">
      <div class="search-input-wrap">
        <AppIcon name="search" :size="16" />
        <input class="input" v-model="search" placeholder="Search managers..." />
      </div>
      <button class="btn btn-primary btn-sm" @click="showAdd = !showAdd">
        <AppIcon name="plus" :size="14" /> Add Manager
      </button>
    </div>

    <!-- Add Manager Form -->
    <div v-if="showAdd" class="card-glass add-form" style="margin-top:16px">
      <h3 class="heading-sm">New Manager</h3>
      <div class="form-grid" style="margin-top:12px">
        <input class="input" v-model="newMgr.name" placeholder="Full Name" />
        <input class="input" v-model="newMgr.email" placeholder="Email" type="email" />
        <input class="input" v-model="newMgr.phone" placeholder="Phone" />
        <input class="input" v-model="newMgr.region" placeholder="Region" />
      </div>
      <div style="margin-top:12px;display:flex;gap:8px;justify-content:flex-end">
        <button class="btn btn-outline btn-sm" @click="showAdd = false">Cancel</button>
            <button class="btn btn-primary btn-sm" @click="createManager">Create</button>
      </div>
    </div>

    <div class="table-wrap card-glass" style="margin-top:20px">
      <table class="data-table">
        <thead>
          <tr><th>Manager</th><th>Region</th><th>Cooks Managed</th><th>Verifications</th><th>Performance</th><th>Status</th></tr>
        </thead>
        <tbody>
          <tr v-for="m in filteredManagers" :key="m.id">
            <td>
              <div class="mgr-cell">
                <div class="mgr-avatar">{{ m.initials }}</div>
                <div>
                  <div class="fw-600 text-sm">{{ m.name }}</div>
                  <div class="text-xs text-muted">{{ m.email }}</div>
                </div>
              </div>
            </td>
            <td class="text-sm">{{ m.region }}</td>
            <td class="text-sm fw-600">{{ m.cooksManaged }}</td>
            <td class="text-sm">{{ m.verifications }}</td>
            <td>
              <div class="perf-bar-wrap">
                <div class="perf-bar" :style="{ width: m.performance + '%' }"></div>
              </div>
              <span class="text-xs fw-600">{{ m.performance }}%</span>
            </td>
            <td><span class="badge" :class="'status-' + m.status">{{ m.status }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import AppIcon from '@/components/AppIcon.vue'
import { adminApi } from '@/services/api.js'

const search = ref('')
const showAdd = ref(false)
const newMgr = reactive({ name: '', email: '', phone: '', region: '' })
const managers = ref([])
const loading = ref(true)

async function loadManagers() {
  loading.value = true
  try {
    const data = await adminApi.getManagers()
    managers.value = (data || []).map(m => ({
      id: m.id,
      name: m.name || 'Manager',
      initials: (m.name || 'M').split(' ').map(w => w[0]).join('').slice(0,2),
      email: m.email || '',
      region: m.region || m.address || '',
      cooksManaged: m.cooks_managed || 0,
      verifications: m.verifications || 0,
      performance: m.performance || 0,
      status: m.is_active !== false ? 'Active' : 'Inactive'
    }))
  } catch (e) {
    console.error('Failed to load managers', e)
  } finally {
    loading.value = false
  }
}

onMounted(loadManagers)

const filteredManagers = computed(() => {
  const q = search.value.toLowerCase()
  if (!q) return managers.value
  return managers.value.filter(m => m.name.toLowerCase().includes(q) || m.region.toLowerCase().includes(q))
})

async function createManager() {
  try {
    await adminApi.createManager({ name: newMgr.name, email: newMgr.email, phone: newMgr.phone, password: 'manager123' })
    showAdd.value = false
    newMgr.name = ''; newMgr.email = ''; newMgr.phone = ''; newMgr.region = ''
    await loadManagers()
  } catch (e) {
    alert(e.message || 'Failed to create manager')
  }
}
</script>

<style scoped>
.managers-page { width: 100%; }

.actions-bar { display: flex; justify-content: space-between; gap: 12px; align-items: center; flex-wrap: wrap; }
.search-input-wrap { display: flex; align-items: center; gap: 10px; padding: 0 14px; background: var(--color-bg); border: 1px solid var(--color-border); border-radius: var(--radius-md); flex: 1; max-width: 340px; }
.search-input-wrap .input { border: none; padding-left: 0; }

.add-form { padding: 24px; border-radius: var(--radius-lg); }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }

.table-wrap { padding: 0; border-radius: var(--radius-lg); overflow: hidden; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th { text-align: left; font-size: 0.75rem; font-weight: 600; color: var(--color-text-light); text-transform: uppercase; letter-spacing: 0.05em; padding: 14px 16px; background: var(--color-bg-alt); border-bottom: 1px solid var(--color-border); }
.data-table td { padding: 14px 16px; border-bottom: 1px solid var(--color-border-light); vertical-align: middle; }
.data-table tr:hover td { background: rgba(62, 180, 137, 0.04); }

.mgr-cell { display: flex; align-items: center; gap: 10px; }
.mgr-avatar { width: 36px; height: 36px; border-radius: 50%; background: var(--color-primary-light); color: var(--color-primary-dark); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.688rem; flex-shrink: 0; }

.perf-bar-wrap { width: 80px; height: 6px; background: var(--color-bg-alt); border-radius: var(--radius-full); overflow: hidden; display: inline-block; vertical-align: middle; margin-right: 8px; }
.perf-bar { height: 100%; background: var(--color-primary); border-radius: var(--radius-full); }

.status-Active { background: #D1FAE5; color: #059669; }
.status-Inactive { background: #FEE2E2; color: #DC2626; }
[class*="status-"] { padding: 3px 10px; border-radius: var(--radius-full); font-size: 0.688rem; font-weight: 600; }

.btn-sm { padding: 6px 16px; font-size: 0.813rem; display: inline-flex; align-items: center; gap: 6px; }
</style>
