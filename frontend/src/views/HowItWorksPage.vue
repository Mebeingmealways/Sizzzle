<template>
  <div class="info-page page">
    <AppNavbar />

    <section class="hero-section">
      <div class="container">
        <div class="hero-card card-glass animate-slide-up">
          <span class="section-tag">Sizzzle Guide</span>
          <h1 class="heading-lg">How It Works</h1>
          <p class="text-lg text-muted hero-sub">
            Sizzzle connects customers with verified home cooks, with manager oversight and admin controls to keep quality high.
          </p>
          <div class="hero-actions">
            <router-link to="/register" class="btn btn-primary btn-lg">Get Started</router-link>
            <router-link to="/register/cook" class="btn btn-outline btn-lg">Become a Cook</router-link>
          </div>
        </div>
      </div>
    </section>

    <section id="how-it-works" class="section flow-section">
      <div class="container">
        <div class="section-header">
          <span class="section-tag">Step by Step</span>
          <h2 class="heading-lg">Platform Flow</h2>
          <p class="text-muted section-subtitle">From registration to completed booking in a transparent workflow.</p>
        </div>

        <div class="flow-grid">
          <article v-for="(item, idx) in flow" :key="item.title" class="flow-card card-glass">
            <div class="flow-index">{{ String(idx + 1).padStart(2, '0') }}</div>
            <div class="flow-icon">
              <AppIcon :name="item.icon" :size="20" />
            </div>
            <h3 class="heading-sm">{{ item.title }}</h3>
            <p class="text-muted">{{ item.desc }}</p>
          </article>
        </div>
      </div>
    </section>

    <section id="features" class="section features-section">
      <div class="container">
        <div class="section-header">
          <span class="section-tag">Features</span>
          <h2 class="heading-lg">What You Get</h2>
          <p class="text-muted section-subtitle">Core capabilities for customers, cooks, managers, and admins.</p>
        </div>

        <div class="features-grid">
          <article v-for="feature in features" :key="feature.title" class="feature-card card-glass">
            <div class="feature-head">
              <span class="feature-pill">{{ feature.role }}</span>
              <AppIcon :name="feature.icon" :size="18" />
            </div>
            <h3 class="heading-sm">{{ feature.title }}</h3>
            <ul>
              <li v-for="point in feature.points" :key="point">{{ point }}</li>
            </ul>
          </article>
        </div>
      </div>
    </section>

    <section class="section cta-section">
      <div class="container">
        <div class="cta-card card-glass">
          <h2 class="heading-md">Ready to use Sizzzle?</h2>
          <p class="text-muted">Create an account and start booking or serving today.</p>
          <div class="hero-actions">
            <router-link to="/register" class="btn btn-primary">Create Account</router-link>
            <router-link to="/login" class="btn btn-outline">Sign In</router-link>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import AppNavbar from '../components/AppNavbar.vue'
import AppIcon from '../components/AppIcon.vue'

const flow = [
  {
    icon: 'user-plus',
    title: 'Create and Verify Account',
    desc: 'User registers, receives OTP by email, verifies account, and signs in securely.'
  },
  {
    icon: 'search',
    title: 'Discover and Select',
    desc: 'Customer explores cooks and dishes, then picks service type and schedule.'
  },
  {
    icon: 'calendar',
    title: 'Book and Confirm',
    desc: 'Booking is created with status tracking, role-based visibility, and OTP checkpoints.'
  },
  {
    icon: 'utensils',
    title: 'Service Delivery',
    desc: 'Cook delivers the home-cooking session, and customer can track status updates.'
  },
  {
    icon: 'shield',
    title: 'Operations Oversight',
    desc: 'Managers handle verifications and complaints while admins monitor policies and analytics.'
  }
]

const features = [
  {
    role: 'Customer',
    icon: 'home',
    title: 'Customer Experience',
    points: [
      'Smart cook discovery and role-safe dashboard access',
      'Booking lifecycle tracking and OTP-based verification',
      'Profile, preferences, and review support'
    ]
  },
  {
    role: 'Cook',
    icon: 'chef-hat',
    title: 'Cook Operations',
    points: [
      'Cook onboarding with profile and payout information',
      'Availability updates, job management, and earnings insights',
      'Location updates for active bookings'
    ]
  },
  {
    role: 'Manager',
    icon: 'briefcase',
    title: 'Manager Controls',
    points: [
      'Verification queue and complaint resolution tools',
      'Cook performance and metrics monitoring',
      'Region-level operational visibility'
    ]
  },
  {
    role: 'Admin',
    icon: 'settings',
    title: 'Admin Governance',
    points: [
      'Platform analytics, policy management, and disputes handling',
      'Manager account creation and role governance',
      'Global performance and growth tracking'
    ]
  }
]
</script>

<style scoped>
.info-page {
  background: linear-gradient(180deg, #f7faf8 0%, #f0f7f4 45%, #f9f6f2 100%);
  min-height: 100vh;
}

.hero-section {
  padding: 108px 0 24px;
}

.hero-card {
  padding: 36px;
  border-radius: var(--radius-xl);
}

.hero-sub {
  margin-top: 10px;
  max-width: 760px;
}

.hero-actions {
  margin-top: 20px;
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.section {
  padding: 38px 0;
}

.section-header {
  text-align: center;
  max-width: 760px;
  margin: 0 auto 24px;
}

.section-subtitle {
  margin-top: 8px;
}

.flow-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 14px;
}

.flow-card {
  padding: 18px;
  border-radius: var(--radius-lg);
}

.flow-index {
  font-weight: 800;
  color: var(--color-primary);
  font-size: 0.86rem;
  letter-spacing: 0.06em;
}

.flow-icon {
  margin: 10px 0;
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  color: #fff;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.feature-card {
  padding: 20px;
  border-radius: var(--radius-lg);
}

.feature-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
  color: var(--color-primary-dark);
}

.feature-pill {
  font-size: 0.76rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--color-primary);
}

.feature-card ul {
  margin: 10px 0 0;
  padding-left: 18px;
}

.feature-card li {
  margin-bottom: 6px;
  color: var(--color-text-secondary);
}

.cta-card {
  padding: 24px;
  border-radius: var(--radius-xl);
  text-align: center;
}

@media (max-width: 1024px) {
  .flow-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 768px) {
  .hero-card {
    padding: 24px;
  }

  .flow-grid,
  .features-grid {
    grid-template-columns: 1fr;
  }
}
</style>
