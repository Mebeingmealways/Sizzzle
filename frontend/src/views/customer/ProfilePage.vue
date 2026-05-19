<template>
  <div class="profile-page animate-fade-in">
    <!-- Profile Hero Card -->
    <div class="profile-hero">
      <div class="profile-hero-bg"></div>
      <div class="profile-hero-content">
        <div class="profile-avatar-lg">
          <span>{{ auth.user?.name?.charAt(0) || 'U' }}</span>
        </div>
        <div class="profile-hero-info">
          <h2 class="heading-md">{{ auth.user?.name || 'User' }}</h2>
          <p class="text-sm text-muted">{{ auth.user?.email || '' }}</p>
          <span class="profile-role-badge">Customer</span>
        </div>
      </div>
    </div>

    <!-- Tab navigation -->
    <div class="profile-tabs">
      <button class="profile-tab" :class="{ active: activeTab === 'personal' }" @click="activeTab = 'personal'">
        <AppIcon name="user" :size="16" /> Personal Info
      </button>
      <button class="profile-tab" :class="{ active: activeTab === 'security' }" @click="activeTab = 'security'">
        <AppIcon name="lock" :size="16" /> Security
      </button>
      <button class="profile-tab" :class="{ active: activeTab === 'preferences' }" @click="activeTab = 'preferences'">
        <AppIcon name="sliders" :size="16" /> Preferences
      </button>
    </div>

    <!-- Personal Info -->
    <div class="profile-section" v-if="activeTab === 'personal'">
      <h3 class="heading-sm">Personal Information</h3>
      <div class="form-grid">
        <div class="input-group">
          <label>Full Name</label>
          <input v-model="profile.name" type="text" class="input" />
        </div>
        <div class="input-group">
          <label>Email</label>
          <input v-model="profile.email" type="email" class="input" />
        </div>
        <div class="input-group">
          <label>Phone</label>
          <input v-model="profile.phone" type="tel" class="input" />
        </div>
        <div class="input-group">
          <label>Address</label>
          <input v-model="profile.address" type="text" class="input" />
        </div>
      </div>
      <div class="form-actions">
        <button class="btn btn-primary" @click="saveProfile">Save Changes</button>
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

      <div class="security-info">
        <h4 class="heading-sm" style="margin-top: 32px;">Account Security</h4>
        <div class="security-items">
          <div class="security-item">
            <div class="security-icon secure">
              <AppIcon name="check-circle" :size="18" />
            </div>
            <div>
              <div class="fw-600 text-sm">Email Verified</div>
              <div class="text-xs text-muted">Your email address has been verified</div>
            </div>
          </div>
          <div class="security-item">
            <div class="security-icon">
              <AppIcon name="shield" :size="18" />
            </div>
            <div>
              <div class="fw-600 text-sm">Two-Factor Authentication</div>
              <div class="text-xs text-muted">Add an extra layer of security</div>
            </div>
            <button class="btn btn-outline btn-sm">Enable</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Preferences -->
    <div class="profile-section" v-if="activeTab === 'preferences'">
      <h3 class="heading-sm">Notification Preferences</h3>
      <div class="pref-list">
        <label class="pref-item">
          <div>
            <div class="fw-600 text-sm">Booking Confirmations</div>
            <div class="text-xs text-muted">Get notified when a booking is confirmed</div>
          </div>
          <input type="checkbox" v-model="preferences.booking_confirmations" class="toggle" />
        </label>
        <label class="pref-item">
          <div>
            <div class="fw-600 text-sm">Cook Arrival Alerts</div>
            <div class="text-xs text-muted">Notification when cook is on the way</div>
          </div>
          <input type="checkbox" v-model="preferences.cook_arrival_alerts" class="toggle" />
        </label>
        <label class="pref-item">
          <div>
            <div class="fw-600 text-sm">Promotional Offers</div>
            <div class="text-xs text-muted">Receive offers and discounts</div>
          </div>
          <input type="checkbox" v-model="preferences.promotional_offers" class="toggle" />
        </label>
      </div>
      <div class="form-actions">
        <button class="btn btn-primary" :disabled="savingPreferences" @click="savePreferences">
          {{ savingPreferences ? 'Saving...' : 'Save Preferences' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { profileApi, authApi } from '../../services/api.js'
import AppIcon from '../../components/AppIcon.vue'

const auth = useAuthStore()
const activeTab = ref('personal')

const profile = reactive({
  name: '',
  email: '',
  phone: '',
  address: ''
})

const preferences = reactive({
  booking_confirmations: true,
  cook_arrival_alerts: true,
  promotional_offers: false
})

const savingPreferences = ref(false)

const passwords = reactive({ current: '', newPass: '', confirm: '' })

onMounted(async () => {
  let data = null
  try {
    data = await profileApi.get()
    profile.name = data.name || ''
    profile.email = data.email || ''
    profile.phone = data.phone || ''
    profile.address = data.address || ''
    if (data.notification_preferences) {
      preferences.booking_confirmations = data.notification_preferences.booking_confirmations ?? true
      preferences.cook_arrival_alerts = data.notification_preferences.cook_arrival_alerts ?? true
      preferences.promotional_offers = data.notification_preferences.promotional_offers ?? false
    }
  } catch (e) {
    profile.name = auth.user?.name || ''
    profile.email = auth.user?.email || ''
  }

  const prefRaw = localStorage.getItem(`sizzzle_customer_prefs_${auth.user?.id || 'me'}`)
  if (prefRaw) {
    try {
      const parsed = JSON.parse(prefRaw)
      preferences.booking_confirmations = parsed.booking_confirmations ?? parsed.bookingConfirmations ?? preferences.booking_confirmations
      preferences.cook_arrival_alerts = parsed.cook_arrival_alerts ?? parsed.cookArrivalAlerts ?? preferences.cook_arrival_alerts
      preferences.promotional_offers = parsed.promotional_offers ?? parsed.promotionalOffers ?? preferences.promotional_offers
    } catch {
      // Ignore invalid local storage payloads.
    }
  }
})

async function saveProfile() {
  try {
    await profileApi.update({ name: profile.name, email: profile.email, phone: profile.phone, address: profile.address })
    auth.user = { ...auth.user, name: profile.name, email: profile.email }
    alert('Profile updated!')
  } catch (e) {
    alert(e.message || 'Failed to update profile')
  }
}

async function changePassword() {
  if (passwords.newPass !== passwords.confirm) { alert('Passwords do not match'); return }
  try {
    await authApi.changePassword({ current_password: passwords.current, new_password: passwords.newPass })
    passwords.current = ''; passwords.newPass = ''; passwords.confirm = ''
    alert('Password changed!')
  } catch (e) {
    alert(e.message || 'Failed to change password')
  }
}

async function savePreferences() {
  savingPreferences.value = true
  localStorage.setItem(
    `sizzzle_customer_prefs_${auth.user?.id || 'me'}`,
    JSON.stringify({ ...preferences })
  )
  try {
    await profileApi.update({ notification_preferences: { ...preferences } })
    alert('Preferences saved!')
  } catch (e) {
    alert(e.message || 'Preferences saved locally, but server sync failed')
  } finally {
    savingPreferences.value = false
  }
}
</script>

<style scoped>
.profile-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
  width: 100%;
}

/* Hero */
.profile-hero {
  position: relative;
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--color-surface-raised);
  border: 1px solid var(--color-border-light);
}
.profile-hero-bg {
  height: 100px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
}
.profile-hero-content {
  display: flex;
  align-items: flex-end;
  gap: 20px;
  padding: 0 28px 24px;
  margin-top: -36px;
  position: relative;
}
.profile-avatar-lg {
  width: 72px; height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 1.6rem;
  border: 4px solid var(--color-surface-raised);
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
  flex-shrink: 0;
}
.profile-hero-info { padding-top: 8px; }
.profile-role-badge {
  display: inline-block;
  margin-top: 6px;
  padding: 3px 12px;
  border-radius: var(--radius-full);
  background: var(--color-primary-ghost);
  color: var(--color-primary-dark);
  font-size: 0.7rem; font-weight: 600;
  text-transform: uppercase;
}

/* Tabs */
.profile-tabs {
  display: flex;
  gap: 4px;
  padding: 4px;
  border-radius: var(--radius-md);
  background: var(--color-bg-alt);
  border: 1px solid var(--color-border-light);
}
.profile-tab {
  flex: 1;
  display: flex; align-items: center; justify-content: center;
  gap: 8px;
  padding: 10px 16px;
  border: none; background: transparent;
  border-radius: var(--radius-sm);
  font-size: 0.8rem; font-weight: 600;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}
.profile-tab.active {
  background: var(--color-surface-raised);
  color: var(--color-primary-dark);
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
  display: flex;
  flex-direction: column;
  gap: 18px;
  max-width: 400px;
}
.form-actions { margin-top: 24px; }

/* Security */
.security-items {
  display: flex; flex-direction: column;
  gap: 14px; margin-top: 16px;
}
.security-item {
  display: flex; align-items: center; gap: 14px;
  padding: 16px;
  border-radius: var(--radius-md);
  background: var(--color-bg-alt);
}
.security-icon {
  width: 36px; height: 36px;
  border-radius: 50%;
  background: var(--color-bg-alt);
  border: 1px solid var(--color-border-light);
  display: flex; align-items: center; justify-content: center;
  color: var(--color-text-light);
  flex-shrink: 0;
}
.security-icon.secure { background: rgba(45, 182, 125, 0.1); color: var(--color-primary); border-color: rgba(45, 182, 125, 0.2); }

/* Preferences */
.pref-list {
  display: flex; flex-direction: column;
  gap: 0;
}
.pref-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 0;
  border-bottom: 1px solid var(--color-border-light);
  cursor: pointer;
}
.pref-item:last-child { border-bottom: none; }
.toggle {
  width: 40px; height: 22px;
  appearance: none;
  background: var(--color-border);
  border-radius: 11px;
  position: relative;
  cursor: pointer;
  transition: background 0.2s ease;
}
.toggle::before {
  content: '';
  position: absolute;
  top: 2px; left: 2px;
  width: 18px; height: 18px;
  border-radius: 50%;
  background: #fff;
  transition: transform 0.2s ease;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.toggle:checked { background: var(--color-primary); }
.toggle:checked::before { transform: translateX(18px); }

@media (max-width: 640px) {
  .form-grid { grid-template-columns: 1fr; }
  .profile-hero-content { flex-direction: column; align-items: center; text-align: center; padding: 0 20px 20px; }
  .profile-tabs { flex-wrap: wrap; }
  .profile-tab { font-size: 0.72rem; padding: 8px 10px; }
  .profile-section { padding: 20px 16px; }
}
</style>
