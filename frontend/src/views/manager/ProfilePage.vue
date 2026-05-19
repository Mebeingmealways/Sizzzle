<template>
  <div class="mgr-profile animate-fade-in">
    <div class="profile-hero">
      <div class="profile-hero-bg mgr-bg"></div>
      <div class="profile-hero-content">
        <div class="profile-avatar-lg mgr-avatar">
          <span>{{ auth.user?.name?.charAt(0) || 'M' }}</span>
        </div>
        <div class="profile-hero-info">
          <h2 class="heading-md">{{ auth.user?.name || 'Manager' }}</h2>
          <p class="text-sm text-muted">{{ auth.user?.email || '' }}</p>
          <span class="role-badge mgr-badge">Regional Manager</span>
        </div>
      </div>
    </div>

    <div class="profile-tabs">
      <button class="profile-tab" :class="{ active: tab === 'info' }" @click="tab = 'info'">
        <AppIcon name="user" :size="16" /> Account Info
      </button>
      <button class="profile-tab" :class="{ active: tab === 'security' }" @click="tab = 'security'">
        <AppIcon name="lock" :size="16" /> Security
      </button>
    </div>

    <div class="profile-section" v-if="tab === 'info'">
      <h3 class="heading-sm">Account Information</h3>
      <div class="form-grid">
        <div class="input-group">
          <label>Full Name</label>
          <input v-model="form.name" type="text" class="input" />
        </div>
        <div class="input-group">
          <label>Email</label>
          <input v-model="form.email" type="email" class="input" />
        </div>
        <div class="input-group">
          <label>Phone</label>
          <input v-model="form.phone" type="tel" class="input" />
        </div>
        <div class="input-group">
          <label>Region</label>
          <input v-model="form.region" class="input" />
        </div>
      </div>
      <div class="form-actions">
        <button class="btn btn-primary" @click="saveProfile">Save Changes</button>
      </div>
    </div>

    <div class="profile-section" v-if="tab === 'security'">
      <h3 class="heading-sm">Change Password</h3>
      <div class="form-stack">
        <div class="input-group">
          <label>Current Password</label>
          <input v-model="passwords.current" type="password" class="input" placeholder="Current password" />
        </div>
        <div class="input-group">
          <label>New Password</label>
          <input v-model="passwords.newPass" type="password" class="input" placeholder="New password" />
        </div>
        <div class="input-group">
          <label>Confirm Password</label>
          <input v-model="passwords.confirm" type="password" class="input" placeholder="Confirm password" />
        </div>
      </div>
      <div class="form-actions">
        <button class="btn btn-primary" @click="changePassword">Update Password</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { profileApi, authApi } from '@/services/api.js'
import AppIcon from '@/components/AppIcon.vue'

const auth = useAuthStore()
const tab = ref('info')

const form = reactive({ name: '', email: '', phone: '', region: '' })
const passwords = reactive({ current: '', newPass: '', confirm: '' })

onMounted(async () => {
  try {
    const data = await profileApi.get()
    form.name = data.name || ''
    form.email = data.email || ''
    form.phone = data.phone || ''
    form.region = data.address || ''
  } catch (e) {
    form.name = auth.user?.name || ''
    form.email = auth.user?.email || ''
    form.region = auth.user?.address || ''
  }
})

async function saveProfile() {
  try {
    await profileApi.update({ name: form.name, email: form.email, phone: form.phone, address: form.region })
    auth.updateUser({ name: form.name, email: form.email, phone: form.phone, address: form.region })
    alert('Profile saved!')
  } catch (e) { alert(e.message || 'Failed to save') }
}

async function changePassword() {
  if (passwords.newPass !== passwords.confirm) { alert('Passwords do not match'); return }
  try {
    await authApi.changePassword({ current_password: passwords.current, new_password: passwords.newPass })
    passwords.current = ''; passwords.newPass = ''; passwords.confirm = ''
    alert('Password changed!')
  } catch (e) { alert(e.message || 'Failed') }
}
</script>

<style scoped>
.mgr-profile {
  display: flex; flex-direction: column;
  gap: 24px; width: 100%;
}
.profile-hero {
  position: relative; border-radius: var(--radius-lg);
  overflow: hidden; background: var(--color-surface-raised);
  border: 1px solid var(--color-border-light);
}
.mgr-bg { height: 100px; background: linear-gradient(135deg, #0891B2, #0E7490); }
.profile-hero-content {
  display: flex; align-items: flex-end; gap: 20px;
  padding: 0 28px 24px; margin-top: -36px; position: relative;
}
.mgr-avatar {
  width: 72px; height: 72px; border-radius: 50%;
  background: linear-gradient(135deg, #0891B2, #22D3EE);
  color: #fff; display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 1.6rem;
  border: 4px solid var(--color-surface-raised);
  box-shadow: 0 4px 16px rgba(8, 145, 178, 0.25);
  flex-shrink: 0;
}
.profile-hero-info { padding-top: 8px; }
.mgr-badge {
  display: inline-block; margin-top: 6px;
  padding: 3px 12px; border-radius: var(--radius-full);
  background: rgba(8, 145, 178, 0.08); color: #0891B2;
  font-size: 0.7rem; font-weight: 600; text-transform: uppercase;
}
.profile-tabs {
  display: flex; gap: 4px; padding: 4px;
  border-radius: var(--radius-md); background: var(--color-bg-alt);
  border: 1px solid var(--color-border-light);
}
.profile-tab {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 8px;
  padding: 10px 16px; border: none; background: transparent;
  border-radius: var(--radius-sm); font-size: 0.8rem; font-weight: 600;
  color: var(--color-text-secondary); cursor: pointer; transition: all 0.2s ease;
}
.profile-tab.active {
  background: var(--color-surface-raised); color: #0891B2;
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.profile-section {
  padding: 28px; border-radius: var(--radius-lg);
  background: var(--color-surface-raised); border: 1px solid var(--color-border-light);
}
.profile-section h3 { margin-bottom: 20px; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
.form-stack { display: flex; flex-direction: column; gap: 18px; max-width: 400px; }
.form-actions { margin-top: 24px; }

@media (max-width: 640px) {
  .form-grid { grid-template-columns: 1fr; }
  .profile-hero-content { flex-direction: column; align-items: center; text-align: center; padding: 0 20px 20px; }
  .profile-section { padding: 20px 16px; }
}
</style>
