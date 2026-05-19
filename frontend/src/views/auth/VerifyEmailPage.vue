<template>
  <div class="auth-page page">
    <AppNavbar />
    <div class="container auth-container">
      <div class="auth-card card-glass animate-slide-up">
        <div class="auth-header">
          <SizzzleLogo size="lg" :show-text="false" />
          <h1 class="heading-md" style="margin-top:20px">Verify your email</h1>
          <p class="text-muted text-sm" style="margin-top:6px">
            We sent a 6-digit code to <strong>{{ email }}</strong>
          </p>
        </div>

        <form @submit.prevent="handleVerify" class="auth-form">
          <div class="otp-inputs">
            <input
              v-for="(_, i) in 6"
              :key="i"
              :ref="el => { if (el) otpRefs[i] = el }"
              v-model="otp[i]"
              type="text"
              inputmode="numeric"
              maxlength="1"
              class="otp-box"
              @input="onOtpInput(i)"
              @keydown.backspace="onBackspace(i, $event)"
              @paste.prevent="onPaste"
            />
          </div>

          <div v-if="error" class="error-banner">
            <AppIcon name="alert-circle" :size="16" /> {{ error }}
          </div>

          <div v-if="success" class="success-banner">
            <AppIcon name="check-circle" :size="16" /> {{ success }}
          </div>

          <button type="submit" class="btn btn-primary btn-lg full-width" :disabled="loading || otpString.length < 6">
            {{ loading ? 'Verifying...' : 'Verify Email' }}
          </button>
        </form>

        <p class="auth-footer text-sm">
          Didn't receive the code?
          <button class="btn-link" :disabled="resendCooldown > 0" @click="handleResend">
            {{ resendCooldown > 0 ? `Resend in ${resendCooldown}s` : 'Resend OTP' }}
          </button>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { authApi } from '../../services/api'
import AppNavbar from '../../components/AppNavbar.vue'
import SizzzleLogo from '../../components/SizzzleLogo.vue'
import AppIcon from '../../components/AppIcon.vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const email = ref(route.query.email || '')
const otp = reactive(['', '', '', '', '', ''])
const otpRefs = reactive([])
const loading = ref(false)
const error = ref('')
const success = ref('')
const resendCooldown = ref(0)
let cooldownTimer = null

const otpString = computed(() => otp.join(''))

const rolePaths = { customer: '/customer', cook: '/cook', manager: '/manager', admin: '/admin' }

function onOtpInput(i) {
  otp[i] = otp[i].replace(/\D/g, '')
  if (otp[i] && i < 5) {
    otpRefs[i + 1]?.focus()
  }
}

function onBackspace(i, e) {
  if (!otp[i] && i > 0) {
    otpRefs[i - 1]?.focus()
  }
}

function onPaste(e) {
  const pasted = (e.clipboardData.getData('text') || '').replace(/\D/g, '').slice(0, 6)
  for (let i = 0; i < 6; i++) {
    otp[i] = pasted[i] || ''
  }
  const focusIdx = Math.min(pasted.length, 5)
  otpRefs[focusIdx]?.focus()
}

function startCooldown() {
  resendCooldown.value = 30
  cooldownTimer = setInterval(() => {
    resendCooldown.value--
    if (resendCooldown.value <= 0) clearInterval(cooldownTimer)
  }, 1000)
}

async function handleVerify() {
  error.value = ''
  success.value = ''
  loading.value = true
  try {
    const res = await authApi.verifyEmail({ email: email.value, otp: otpString.value })
    auth.setAuth(res.user, res.token)
    router.push(rolePaths[res.user.role] || '/customer')
  } catch (e) {
    error.value = e.message || 'Verification failed'
  } finally {
    loading.value = false
  }
}

async function handleResend() {
  error.value = ''
  success.value = ''
  try {
    const res = await authApi.resendOtp({ email: email.value })
    success.value = res.message || 'OTP resent!'
    startCooldown()
  } catch (e) {
    error.value = e.message || 'Failed to resend OTP'
  }
}

onMounted(() => {
  if (!email.value) {
    router.replace('/register')
    return
  }
  otpRefs[0]?.focus()
  startCooldown()
})

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
  max-width: 440px;
  padding: 48px 42px;
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
  background: linear-gradient(90deg, var(--color-accent), var(--color-primary));
}

.auth-header {
  text-align: center;
  margin-bottom: 36px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.otp-inputs {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.otp-box {
  width: 48px;
  height: 56px;
  text-align: center;
  font-size: 1.5rem;
  font-weight: 700;
  border-radius: var(--radius-md);
  border: 2px solid var(--color-border-light);
  background: var(--color-surface);
  color: var(--color-text);
  transition: border-color 0.2s;
}

.otp-box:focus {
  outline: none;
  border-color: var(--color-accent);
  box-shadow: 0 0 0 3px rgba(242, 115, 79, 0.15);
}

.full-width { width: 100%; }

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
  background: rgba(45, 182, 125, 0.06);
  border: 1px solid rgba(45, 182, 125, 0.12);
  color: var(--color-primary);
  font-size: 0.85rem;
  font-weight: 500;
}

.auth-footer {
  text-align: center;
  margin-top: 28px;
  color: var(--color-text-secondary);
}

.btn-link {
  background: none;
  border: none;
  color: var(--color-accent);
  font-weight: 700;
  cursor: pointer;
  font-size: inherit;
  padding: 0;
}

.btn-link:disabled {
  color: var(--color-text-light);
  cursor: not-allowed;
}

@media (max-width: 480px) {
  .auth-card {
    padding: 36px 24px;
  }
  .otp-box {
    width: 42px;
    height: 48px;
    font-size: 1.25rem;
  }
}
</style>
