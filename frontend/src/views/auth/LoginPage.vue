<template>
  <div class="auth-page page">
    <AppNavbar />
    <div class="container auth-container">
      <div class="auth-card card-glass animate-slide-up">
        <div class="auth-header">
          <SizzzleLogo size="lg" :show-text="false" />
          <h1 class="heading-md" style="margin-top:20px">Welcome back</h1>
          <p class="text-muted text-sm" style="margin-top:6px">
            Sign in to your Sizzzle account
          </p>
        </div>

        <form @submit.prevent="handleLogin" class="auth-form">
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
          <div class="input-group">
            <label for="password">Password</label>
            <input
              id="password"
              v-model="form.password"
              type="password"
              class="input"
              placeholder="Enter your password"
              required
              autocomplete="current-password"
            />
            <div class="auth-links text-sm">
              <router-link to="/forgot-password">Forgot password?</router-link>
            </div>
          </div>

          <div v-if="error" class="error-banner">
            <AppIcon name="alert-circle" :size="16" />
            {{ error }}
          </div>

          <button type="submit" class="btn btn-primary btn-lg full-width" :disabled="loading">
            {{ loading ? 'Signing in...' : 'Sign in' }}
          </button>
        </form>

        <p class="auth-footer text-sm">
          Don't have an account?
          <router-link to="/register">Create one</router-link>
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

const form = reactive({ email: '', password: '' })
const loading = ref(false)
const error = ref('')

const rolePaths = { customer: '/customer', cook: '/cook', manager: '/manager', admin: '/admin' }

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    const res = await authApi.login({ email: form.email, password: form.password })
    auth.setAuth(res.user, res.token)
    router.push(rolePaths[res.user.role] || '/customer')
  } catch (e) {
    error.value = e.message || 'Login failed'
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

/* Decorative elements */
.auth-container::before {
  content: '';
  position: absolute;
  top: 10%;
  right: 8%;
  width: 250px;
  height: 250px;
  border-radius: 50%;
  border: 1.5px solid rgba(45, 182, 125, 0.06);
  pointer-events: none;
}

.auth-container::after {
  content: '';
  position: absolute;
  bottom: 15%;
  left: 5%;
  width: 180px;
  height: 180px;
  border-radius: 50%;
  border: 1.5px solid rgba(242, 115, 79, 0.05);
  pointer-events: none;
}

.auth-card {
  width: 100%;
  max-width: 440px;
  padding: 48px 42px;
  border-radius: var(--radius-xl);
  position: relative;
}

/* Accent bar at top of card */
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

.full-width {
  width: 100%;
}

.auth-links {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}

.auth-links a {
  font-weight: 700;
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

.auth-footer {
  text-align: center;
  margin-top: 28px;
  color: var(--color-text-secondary);
}

.auth-footer a {
  font-weight: 700;
}

@media (max-width: 480px) {
  .auth-card {
    padding: 36px 24px;
  }
  .auth-card::after {
    left: 24px;
    right: 24px;
  }
  .auth-container::before,
  .auth-container::after {
    display: none;
  }
}
</style>
