<template>
  <div class="cook-profile animate-fade-in">
    <!-- Chef Profile Hero -->
    <div class="chef-hero">
      <div class="chef-hero-bg"></div>
      <div class="chef-hero-content">
        <div class="chef-hero-avatar-ring">
          <div class="chef-hero-avatar">{{ auth.user?.name?.charAt(0) || 'C' }}</div>
        </div>
        <div class="chef-hero-info">
          <h2 class="heading-md">{{ form.name }}</h2>
          <p class="text-sm text-muted">{{ form.specialization }} Cook</p>
          <div class="chef-hero-meta">
            <span class="chef-role-badge">Cook</span>
            <div class="chef-rating-badge">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="#F59E0B"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
              <span>--</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="profile-tabs">
      <button class="profile-tab" :class="{ active: activeTab === 'personal' }" @click="activeTab = 'personal'">
        <AppIcon name="user" :size="16" /> Personal
      </button>
      <button class="profile-tab" :class="{ active: activeTab === 'professional' }" @click="activeTab = 'professional'">
        <AppIcon name="utensils" :size="16" /> Professional
      </button>
      <button class="profile-tab" :class="{ active: activeTab === 'payout' }" @click="activeTab = 'payout'">
        <AppIcon name="credit-card" :size="16" /> Payout
      </button>
      <button class="profile-tab" :class="{ active: activeTab === 'security' }" @click="activeTab = 'security'">
        <AppIcon name="lock" :size="16" /> Security
      </button>
    </div>

    <!-- Personal Details -->
    <div class="profile-section" v-if="activeTab === 'personal'">
      <h3 class="heading-sm">Personal Details</h3>
      <div class="form-grid">
        <div class="input-group">
          <label>Full Name</label>
          <input class="input" v-model="form.name" />
        </div>
        <div class="input-group">
          <label>Email</label>
          <input class="input" type="email" v-model="form.email" />
        </div>
        <div class="input-group">
          <label>Phone</label>
          <input class="input" v-model="form.phone" />
        </div>
        <div class="input-group">
          <label>Address</label>
          <input class="input" v-model="form.address" />
        </div>
      </div>
      <div class="form-actions">
        <button class="btn btn-primary" @click="saveProfile">Save Changes</button>
      </div>
    </div>

    <!-- Professional Details -->
    <div class="profile-section" v-if="activeTab === 'professional'">
      <h3 class="heading-sm">Professional Details</h3>
      <div class="form-grid">
        <div class="input-group">
          <label>Specialization</label>
          <select class="input" v-model="form.specialization">
            <option>North Indian</option><option>South Indian</option><option>Chinese</option>
            <option>Continental</option><option>Bengali</option><option>Mughlai</option>
          </select>
        </div>
        <div class="input-group">
          <label>Experience Level</label>
          <select class="input" v-model="form.experience">
            <option>Home Cook</option><option>Professional Chef</option><option>Catering Expert</option>
          </select>
        </div>
        <div class="input-group">
          <label>Years of Experience</label>
          <input class="input" type="number" v-model="form.years" />
        </div>
        <div class="input-group">
          <label>Aadhar Number</label>
          <input class="input" v-model="form.aadhar" disabled />
        </div>
      </div>
      <div class="form-actions">
        <button class="btn btn-primary" @click="saveProfessional">Save Changes</button>
      </div>
    </div>

    <!-- Payout Info -->
    <div class="profile-section" v-if="activeTab === 'payout'">
      <h3 class="heading-sm">Payout Information</h3>
      <div class="form-grid">
        <div class="input-group">
          <label>Bank Account</label>
          <input class="input" v-model="form.bankAccount" />
        </div>
        <div class="input-group">
          <label>IFSC Code</label>
          <input class="input" v-model="form.ifsc" />
        </div>
        <div class="input-group">
          <label>UPI ID</label>
          <input class="input" v-model="form.upi" />
        </div>
        <div class="input-group">
          <label>PAN Number</label>
          <input class="input" v-model="form.pan" />
        </div>
      </div>
      <div class="form-actions">
        <button class="btn btn-primary" @click="savePayout">Save Changes</button>
      </div>
    </div>

    <!-- Security -->
    <div class="profile-section" v-if="activeTab === 'security'">
      <h3 class="heading-sm">Change Password</h3>
      <div class="form-stack">
        <div class="input-group">
          <label>Current Password</label>
          <input v-model="passwords.current" type="password" class="input" placeholder="Enter current password" />
        </div>
        <div class="input-group">
          <label>New Password</label>
          <input v-model="passwords.newPass" type="password" class="input" placeholder="Enter new password" />
        </div>
        <div class="input-group">
          <label>Confirm New Password</label>
          <input v-model="passwords.confirm" type="password" class="input" placeholder="Confirm new password" />
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
const activeTab = ref('personal')

const form = reactive({
  name: '', email: '', phone: '', address: '',
  specialization: '', experience: '', years: 0,
  aadhar: '', bankAccount: '', ifsc: '', upi: '', pan: ''
})

const passwords = reactive({ current: '', newPass: '', confirm: '' })

onMounted(async () => {
  try {
    const data = await profileApi.get()
    form.name = data.name || ''; form.email = data.email || ''; form.phone = data.phone || ''; form.address = data.address || ''
    if (data.cook_profile) {
      form.specialization = data.cook_profile.specialization || ''
      form.experience = data.cook_profile.experience_type || ''
      form.years = data.cook_profile.years_experience || 0
      form.aadhar = data.cook_profile.aadhar_number || ''
      form.bankAccount = data.cook_profile.bank_account || ''
      form.ifsc = data.cook_profile.ifsc_code || ''
      form.upi = data.cook_profile.upi_id || ''
      form.pan = data.cook_profile.pan_number || ''
    }
  } catch (e) {
    form.name = auth.user?.name || ''; form.email = auth.user?.email || ''
  }
})

async function saveProfile() {
  try {
    await profileApi.update({ name: form.name, email: form.email, phone: form.phone, address: form.address })
    auth.updateUser({ name: form.name, email: form.email, phone: form.phone, address: form.address })
    alert('Profile saved!')
  } catch (e) { alert(e.message || 'Failed') }
}

async function saveProfessional() {
  try {
    await profileApi.update({
      specialization: form.specialization,
      experience_type: form.experience,
      years_experience: Number(form.years || 0)
    })
    alert('Professional details saved!')
  } catch (e) {
    alert(e.message || 'Failed to save professional details')
  }
}

async function savePayout() {
  try {
    await profileApi.update({
      bank_account: form.bankAccount,
      ifsc_code: form.ifsc,
      upi_id: form.upi,
      pan_number: form.pan
    })
    alert('Payout details saved!')
  } catch (e) {
    alert(e.message || 'Failed to save payout details')
  }
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
.cook-profile {
  display: flex;
  flex-direction: column;
  gap: 24px;
  width: 100%;
}

/* Chef Hero */
.chef-hero {
  position: relative;
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border-light);
}
.chef-hero-bg {
  height: 100px;
  background: linear-gradient(135deg, var(--color-accent), #FF9426);
}
.chef-hero-content {
  display: flex; align-items: flex-end; gap: 20px;
  padding: 0 28px 24px;
  margin-top: -36px; position: relative;
}
.chef-hero-avatar-ring {
  width: 76px; height: 76px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-accent), #FF9426);
  padding: 3px; flex-shrink: 0;
  border: 4px solid var(--color-surface-raised);
  box-shadow: 0 4px 16px rgba(242, 115, 79, 0.25);
}
.chef-hero-avatar {
  width: 100%; height: 100%;
  border-radius: 50%;
  background: var(--color-bg);
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 1.3rem;
  color: var(--color-accent);
}
.chef-hero-info { padding-top: 8px; }
.chef-hero-meta { display: flex; align-items: center; gap: 10px; margin-top: 6px; }
.chef-role-badge {
  padding: 3px 12px;
  border-radius: var(--radius-full);
  background: rgba(242, 115, 79, 0.08);
  color: var(--color-accent);
  font-size: 0.7rem; font-weight: 600; text-transform: uppercase;
}
.chef-rating-badge {
  display: flex; align-items: center; gap: 4px;
  font-size: 0.8rem; font-weight: 600;
}

/* Tabs */
.profile-tabs {
  display: flex; gap: 4px;
  padding: 4px;
  border-radius: var(--radius-md);
  background: var(--color-bg-alt);
  border: 1px solid var(--color-border-light);
}
.profile-tab {
  flex: 1;
  display: flex; align-items: center; justify-content: center; gap: 6px;
  padding: 10px 14px;
  border: none; background: transparent;
  border-radius: var(--radius-sm);
  font-size: 0.78rem; font-weight: 600;
  color: var(--color-text-secondary);
  cursor: pointer; transition: all 0.2s ease;
}
.profile-tab.active {
  background: var(--color-surface-raised);
  color: var(--color-accent);
  box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.profile-tab:hover:not(.active) { color: var(--color-text); }

/* Section */
.profile-section {
  padding: 28px;
  border-radius: var(--radius-lg);
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border-light);
}
.profile-section h3 { margin-bottom: 20px; }

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}
.form-stack {
  display: flex; flex-direction: column;
  gap: 18px; max-width: 400px;
}
.form-actions { margin-top: 24px; }

@media (max-width: 640px) {
  .form-grid { grid-template-columns: 1fr; }
  .chef-hero-content { flex-direction: column; align-items: center; text-align: center; padding: 0 20px 20px; }
  .profile-tabs { flex-wrap: wrap; }
  .profile-tab { font-size: 0.7rem; padding: 8px 8px; }
  .profile-section { padding: 20px 16px; }
  .chef-hero-meta { justify-content: center; }
}
</style>
