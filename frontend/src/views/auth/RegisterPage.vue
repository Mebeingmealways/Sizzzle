<template>
  <div class="auth-page page">
    <AppNavbar />
    <div class="container auth-container">
      <div class="auth-card card-glass animate-slide-up">
        <div class="auth-header">
          <SizzzleLogo size="lg" :show-text="false" />
          <h1 class="heading-md" style="margin-top:20px">Create your account</h1>
          <p class="text-muted text-sm" style="margin-top:6px">
            Start booking home cooks today
          </p>
        </div>

        <form @submit.prevent="handleRegister" class="auth-form">
          <div class="input-group">
            <label for="name">Full Name</label>
            <input id="name" v-model="form.name" type="text" class="input" placeholder="Your full name" required />
          </div>
          <div class="input-group">
            <label for="email">Email</label>
            <input id="email" v-model="form.email" type="email" class="input" placeholder="you@example.com" required autocomplete="email" />
          </div>
          <div class="input-group">
            <label for="phone">Phone Number</label>
            <input id="phone" v-model="form.phone" type="tel" class="input" placeholder="+91 98765 43210" required />
          </div>
          <div class="input-group">
            <label for="password">Password</label>
            <input id="password" v-model="form.password" type="password" class="input" placeholder="Min 8 characters" required minlength="8" autocomplete="new-password" />
          </div>
          <div class="input-group">
            <label for="address">Address</label>
            <input id="address" v-model="form.address" type="text" class="input" placeholder="Your address" />
          </div>

          <div v-if="error" class="error-banner">
            <AppIcon name="alert-circle" :size="16" /> {{ error }}
          </div>

          <button type="submit" class="btn btn-primary btn-lg full-width" :disabled="loading">
            {{ loading ? 'Creating account...' : 'Create Account' }}
          </button>
        </form>

        <p class="auth-footer text-sm">
          Already have an account? <router-link to="/login">Sign in</router-link>
        </p>
        <p class="auth-footer text-sm" style="margin-top:8px">
          Want to cook? <router-link to="/register/cook">Register as a Cook</router-link>
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

const form = reactive({ name: '', email: '', phone: '', password: '', address: '' })
const loading = ref(false)
const error = ref('')

function isValidPhone(value) {
  const digits = String(value || '').replace(/\D/g, '')
  return digits.length >= 7 && digits.length <= 15
}

async function handleRegister() {
  error.value = ''
  if (!isValidPhone(form.phone)) {
    error.value = 'Phone number must contain 7 to 15 digits'
    return
  }
  loading.value = true
  try {
    const res = await authApi.register({
      name: form.name,
      email: form.email,
      phone: form.phone,
      password: form.password,
      address: form.address,
      role: 'customer'
    })
    if (res.requires_verification) {
      router.push({ path: '/verify-email', query: { email: form.email } })
    } else {
      auth.setAuth(res.user, res.token)
      router.push('/customer')
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
  position: relative;
}

.auth-container::before {
  content: '';
  position: absolute;
  top: 8%;
  left: 6%;
  width: 220px;
  height: 220px;
  border-radius: 50%;
  border: 1.5px solid rgba(45, 182, 125, 0.06);
  pointer-events: none;
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
  gap: 18px;
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

.auth-footer {
  text-align: center;
  margin-top: 28px;
  color: var(--color-text-secondary);
}

.auth-footer a { font-weight: 700; }

@media (max-width: 480px) {
  .auth-card {
    padding: 36px 24px;
  }
  .auth-card::after {
    left: 24px;
    right: 24px;
  }
}
</style>
