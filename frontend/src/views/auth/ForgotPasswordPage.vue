<template>
  <div class="auth-page page">
    <AppNavbar />
    <div class="container auth-container">
      <div class="auth-card card-glass animate-slide-up">
        <div class="auth-header">
          <SizzzleLogo size="lg" :show-text="false" />
          <h1 class="heading-md" style="margin-top:20px">Reset your password</h1>
          <p class="text-muted text-sm" style="margin-top:6px">
            {{ step === 1 ? 'Get a reset code on your email' : 'Enter OTP and your new password' }}
          </p>
        </div>

        <form v-if="step === 1" @submit.prevent="handleSendOtp" class="auth-form">
          <div class="input-group">
            <label for="email">Email</label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              class="input"
              placeholder="you@example.com"
              required
              autocomplete="email"
            />
          </div>

          <div v-if="error" class="error-banner">
            <AppIcon name="alert-circle" :size="16" />
            {{ error }}
          </div>

          <div v-if="success" class="success-banner">
            <AppIcon name="check-circle" :size="16" />
            {{ success }}
          </div>

          <button type="submit" class="btn btn-primary btn-lg full-width" :disabled="loading">
            {{ loading ? 'Sending OTP...' : 'Send Reset OTP' }}
          </button>
        </form>

        <form v-else @submit.prevent="handleResetPassword" class="auth-form">
          <div class="input-group">
            <label for="otp">OTP</label>
            <input
              id="otp"
              v-model="form.otp"
              type="text"
              inputmode="numeric"
              maxlength="6"
              class="input"
              placeholder="Enter 6-digit OTP"
              required
            />
          </div>

          <div class="input-group">
            <label for="newPassword">New Password</label>
            <input
              id="newPassword"
              v-model="form.newPassword"
              type="password"
              class="input"
              placeholder="Minimum 8 characters"
              required
              minlength="8"
              autocomplete="new-password"
            />
          </div>

          <div class="input-group">
            <label for="confirmPassword">Confirm New Password</label>
            <input
              id="confirmPassword"
              v-model="form.confirmPassword"
              type="password"
              class="input"
              placeholder="Re-enter new password"
              required
              minlength="8"
              autocomplete="new-password"
            />
          </div>

          <div v-if="error" class="error-banner">
            <AppIcon name="alert-circle" :size="16" />
            {{ error }}
          </div>

          <div v-if="success" class="success-banner">
            <AppIcon name="check-circle" :size="16" />
            {{ success }}
          </div>

          <button type="submit" class="btn btn-primary btn-lg full-width" :disabled="loading">
            {{ loading ? 'Resetting password...' : 'Reset Password' }}
          </button>

          <button
            type="button"
            class="btn btn-outline full-width"
            :disabled="resendCooldown > 0 || loading"
            @click="handleResend"
          >
            {{ resendCooldown > 0 ? `Resend OTP in ${resendCooldown}s` : 'Resend OTP' }}
          </button>
        </form>

        <p class="auth-footer text-sm">
          Remember your password?
          <router-link to="/login">Back to Sign in</router-link>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '../../services/api'
import AppNavbar from '../../components/AppNavbar.vue'
import SizzzleLogo from '../../components/SizzzleLogo.vue'
import AppIcon from '../../components/AppIcon.vue'

const router = useRouter()

const step = ref(1)
const loading = ref(false)
const error = ref('')
const success = ref('')
const resendCooldown = ref(0)
let cooldownTimer = null

const form = reactive({
  email: '',
  otp: '',
  newPassword: '',
  confirmPassword: ''
})

function startCooldown() {
  resendCooldown.value = 30
  if (cooldownTimer) clearInterval(cooldownTimer)
  cooldownTimer = setInterval(() => {
    resendCooldown.value -= 1
    if (resendCooldown.value <= 0) {
      clearInterval(cooldownTimer)
      cooldownTimer = null
    }
  }, 1000)
}

async function handleSendOtp() {
  error.value = ''
  success.value = ''
  loading.value = true
  try {
    const res = await authApi.forgotPassword({ email: form.email })
    success.value = res.message || 'If your email is registered, reset OTP has been sent.'
    step.value = 2
    startCooldown()
  } catch (e) {
    error.value = e.message || 'Failed to send reset OTP'
  } finally {
    loading.value = false
  }
}

async function handleResend() {
  if (!form.email) {
    error.value = 'Please enter your email first'
    return
  }
  await handleSendOtp()
}

async function handleResetPassword() {
  error.value = ''
  success.value = ''

  if ((form.otp || '').trim().length !== 6) {
    error.value = 'Please enter a valid 6-digit OTP'
    return
  }

  if (form.newPassword.length < 8) {
    error.value = 'Password must be at least 8 characters'
    return
  }

  if (form.newPassword !== form.confirmPassword) {
    error.value = 'Passwords do not match'
    return
  }

  loading.value = true
  try {
    const res = await authApi.resetPassword({
      email: form.email,
      otp: form.otp.trim(),
      new_password: form.newPassword
    })
    success.value = res.message || 'Password reset successful'
    setTimeout(() => router.push('/login'), 1100)
  } catch (e) {
    error.value = e.message || 'Failed to reset password'
  } finally {
    loading.value = false
  }
}

onUnmounted(() => {
  if (cooldownTimer) clearInterval(cooldownTimer)
})
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
  max-width: 460px;
  padding: 46px 40px;
  border-radius: var(--radius-xl);
  position: relative;
}

.auth-card::after {
  content: '';
  position: absolute;
  top: 0;
  left: 40px;
  right: 40px;
  height: 3px;
  border-radius: 0 0 3px 3px;
  background: linear-gradient(90deg, var(--color-primary), var(--color-accent));
}

.auth-header {
  text-align: center;
  margin-bottom: 30px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.full-width {
  width: 100%;
}

.error-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  background: rgba(239, 68, 68, 0.06);
  border: 1px solid rgba(239, 68, 68, 0.12);
  color: var(--color-error);
  font-size: 0.85rem;
  font-weight: 500;
}

.success-banner {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  background: rgba(45, 182, 125, 0.08);
  border: 1px solid rgba(45, 182, 125, 0.2);
  color: var(--color-primary);
  font-size: 0.85rem;
  font-weight: 600;
}

.auth-footer {
  text-align: center;
  margin-top: 24px;
  color: var(--color-text-secondary);
}

.auth-footer a {
  font-weight: 700;
}

@media (max-width: 480px) {
  .auth-card {
    padding: 34px 22px;
  }

  .auth-card::after {
    left: 22px;
    right: 22px;
  }
}
</style>
