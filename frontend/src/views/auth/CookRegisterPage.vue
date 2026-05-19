<template>
  <div class="auth-page page">
    <AppNavbar />
    <div class="container auth-container">
      <div class="auth-card card-glass animate-slide-up">
        <div class="auth-header">
          <SizzzleLogo size="lg" :show-text="false" />
          <h1 class="heading-md" style="margin-top:20px">Register as a Cook</h1>
          <p class="text-muted text-sm" style="margin-top:6px">
            Join our network of verified home cooks
          </p>
        </div>

        <!-- Step Indicator -->
        <div class="steps-indicator">
          <div v-for="s in 3" :key="s" class="step-dot" :class="{ active: step >= s, current: step === s }">
            {{ s }}
          </div>
        </div>

        <form @submit.prevent="nextStep" class="auth-form">
          <!-- Step 1: Basic Info -->
          <template v-if="step === 1">
            <h3 class="heading-sm">Basic Information</h3>
            <div class="input-group">
              <label>Full Name</label>
              <input v-model="form.name" type="text" class="input" placeholder="Your full name" required />
            </div>
            <div class="input-group">
              <label>Email</label>
              <input v-model="form.email" type="email" class="input" placeholder="you@example.com" required />
            </div>
            <div class="input-group">
              <label>Phone</label>
              <input v-model="form.phone" type="tel" class="input" placeholder="+91 98765 43210" required />
            </div>
            <div class="input-group">
              <label>Password</label>
              <input v-model="form.password" type="password" class="input" placeholder="Min 8 characters" required minlength="8" />
            </div>
            <div class="input-group">
              <label>Aadhar Number</label>
              <input v-model="form.aadhar" type="text" class="input" placeholder="XXXX XXXX XXXX" required />
            </div>
            <div class="input-group">
              <label>Address</label>
              <input v-model="form.address" type="text" class="input" placeholder="Full address" required />
            </div>
          </template>

          <!-- Step 2: Skill Verification -->
          <template v-if="step === 2">
            <h3 class="heading-sm">Skill Verification</h3>
            <div class="input-group">
              <label>Experience Type</label>
              <select v-model="form.experienceType" class="input" required>
                <option value="">Select type</option>
                <option value="restaurant">Restaurant Professional</option>
                <option value="freelancer">Freelance Cook</option>
                <option value="home">Home Cook</option>
              </select>
            </div>
            <div class="input-group">
              <label>Specialization</label>
              <input v-model="form.specialization" type="text" class="input" placeholder="e.g., North Indian, South Indian, Chinese" />
            </div>
            <div class="input-group">
              <label>Years of Experience</label>
              <input v-model="form.experience" type="number" class="input" placeholder="Years" min="0" />
            </div>
            <div class="upload-note card">
              <AppIcon name="info" :size="16" class="text-primary" />
              <p class="text-sm text-muted">
                After registration, you will need to upload a cooking video and photos of 3 signature dishes for verification.
              </p>
            </div>
          </template>

          <!-- Step 3: Payment -->
          <template v-if="step === 3">
            <h3 class="heading-sm">Payment Details</h3>
            <div class="input-group">
              <label>Bank Account Number</label>
              <input v-model="form.bankAccount" type="text" class="input" placeholder="Account number" required />
            </div>
            <div class="input-group">
              <label>IFSC Code</label>
              <input v-model="form.ifsc" type="text" class="input" placeholder="IFSC code" required />
            </div>
            <div class="input-group">
              <label>PAN Number</label>
              <input v-model="form.pan" type="text" class="input" placeholder="PAN number" required />
            </div>
            <div class="input-group">
              <label>UPI ID (optional)</label>
              <input v-model="form.upi" type="text" class="input" placeholder="yourname@upi" />
            </div>
            <div class="input-group">
              <label>Payout Frequency</label>
              <select v-model="form.payoutFrequency" class="input">
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
              </select>
            </div>
          </template>

          <div v-if="error" class="error-banner">
            <AppIcon name="alert-circle" :size="16" /> {{ error }}
          </div>

          <div class="form-actions">
            <button v-if="step > 1" type="button" class="btn btn-ghost" @click="step--">
              <AppIcon name="arrow-left" :size="16" /> Back
            </button>
            <button type="submit" class="btn btn-primary btn-lg" style="flex:1">
              {{ step === 3 ? 'Submit Application' : 'Continue' }}
              <AppIcon v-if="step < 3" name="arrow-right" :size="16" />
            </button>
          </div>
        </form>

        <p class="auth-footer text-sm">
          Want to book? <router-link to="/register">Register as customer</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { authApi } from '../../services/api'
import AppNavbar from '../../components/AppNavbar.vue'
import SizzzleLogo from '../../components/SizzzleLogo.vue'
import AppIcon from '../../components/AppIcon.vue'

const router = useRouter()
const auth = useAuthStore()

const step = ref(1)
const error = ref('')
const loading = ref(false)
const form = reactive({
  name: '', email: '', phone: '', password: '', aadhar: '', address: '',
  experienceType: '', specialization: '', experience: '',
  bankAccount: '', ifsc: '', pan: '', upi: '', payoutFrequency: 'weekly'
})

function isValidPhone(value) {
  const digits = String(value || '').replace(/\D/g, '')
  return digits.length >= 7 && digits.length <= 15
}

async function nextStep() {
  error.value = ''
  if (step.value === 1 && !isValidPhone(form.phone)) {
    error.value = 'Phone number must contain 7 to 15 digits'
    return
  }
  if (step.value < 3) {
    step.value++
    return
  }
  loading.value = true
  try {
    const res = await authApi.registerCook({
      name: form.name,
      email: form.email,
      phone: form.phone,
      password: form.password,
      address: form.address,
      aadhar_number: form.aadhar,
      experience_type: form.experienceType,
      specialization: form.specialization,
      years_experience: parseInt(form.experience) || 0,
      bank_account: form.bankAccount,
      ifsc_code: form.ifsc,
      pan_number: form.pan,
      upi_id: form.upi,
      payout_frequency: form.payoutFrequency
    })
    if (res.requires_verification) {
      router.push({ path: '/verify-email', query: { email: form.email } })
    } else {
      auth.setAuth(res.user, res.token)
      router.push('/cook')
    }
  } catch (e) {
    error.value = e.message || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-container {
  min-height: calc(100vh - 72px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
}

.auth-card {
  width: 100%;
  max-width: 480px;
  padding: 44px 40px;
  border-radius: var(--radius-xl);
}

.auth-header {
  text-align: center;
  margin-bottom: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.steps-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 32px;
  margin-bottom: 28px;
  position: relative;
}

.steps-indicator::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 25%;
  right: 25%;
  height: 2px;
  background: var(--color-border);
}

.step-dot {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.813rem;
  font-weight: 600;
  background: var(--color-bg-alt);
  color: var(--color-text-light);
  border: 2px solid var(--color-border);
  position: relative;
  z-index: 1;
  transition: all var(--transition-normal);
}

.step-dot.active {
  background: var(--color-primary);
  color: #fff;
  border-color: var(--color-primary);
}

.step-dot.current {
  box-shadow: 0 0 0 4px rgba(62, 180, 137, 0.2);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 8px;
}

.upload-note {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 14px 16px;
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  background: rgba(239, 68, 68, 0.08);
  color: var(--color-error);
  font-size: 0.875rem;
}

.auth-footer {
  text-align: center;
  margin-top: 24px;
  color: var(--color-text-secondary);
}

.auth-footer a { font-weight: 600; }

@media (max-width: 480px) {
  .auth-card { padding: 28px 16px; }
  .steps-indicator { gap: 16px; }
  .step-dot { width: 26px; height: 26px; font-size: 0.75rem; }
  .steps-indicator::before { top: 13px; }
  .form-actions { flex-wrap: wrap; }
  .form-actions .btn { width: 100%; }
}
</style>
