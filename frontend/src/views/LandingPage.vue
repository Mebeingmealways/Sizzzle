<template>
  <div class="landing" ref="landingEl">
    <AppNavbar />

    <!-- ═══════════════ HERO ═══════════════ -->
    <section class="hero" ref="heroEl">
      <div class="hero-fire hero-fire-1"></div>
      <div class="hero-fire hero-fire-2"></div>
      <div class="hero-fire hero-fire-3"></div>
      <div class="hero-kanji" aria-hidden="true">炎</div>

      <div class="orbit-ring" aria-hidden="true">
        <div class="orbit-dot orbit-dot-1"></div>
        <div class="orbit-dot orbit-dot-2"></div>
        <div class="orbit-dot orbit-dot-3"></div>
      </div>

      <div class="container hero-center">
        <div class="hero-content" :style="heroParallax">
          <div class="hero-badge glass">
            <span class="badge-dot"></span>
            Now serving in your city
          </div>

          <h1 class="hero-title text-3d">
            <span class="hero-title-line">Home Cooks.</span>
            <span class="hero-title-fire text-3d-fire">Real Taste.</span>
          </h1>

          <p class="hero-subtitle text-lg">
            Book verified home cooks who come to your kitchen and prepare
            authentic, home-style meals. Fresh ingredients, real flavors,
            zero hassle.
          </p>

          <div class="hero-actions">
            <router-link v-magnetic to="/register" class="btn btn-hero-primary btn-lg">
              <span>Book a Cook</span>
              <AppIcon name="arrow-right" :size="18" />
            </router-link>
            <router-link v-magnetic to="/register/cook" class="btn btn-hero-outline btn-lg">
              Join as Cook
            </router-link>
          </div>

          <div class="hero-showcase card-glass" data-reveal="scale">
            <div class="showcase-visual">
              <LazyImage
                :src="opt('dan-gold-4-jhdo54byg-unsplash.jpg').webp"
                :blur="opt('dan-gold-4-jhdo54byg-unsplash.jpg').blur"
                alt="Warm kitchen mood"
                img-class="showcase-image"
              />
              <div class="showcase-overlay">
                <p class="showcase-tag">Taste the comfort of home</p>
                <p class="showcase-copy">Fresh home-style cooking by trusted local chefs.</p>
              </div>
            </div>

            <div class="showcase-panel">
              <div class="showcase-brand-pill">
                <SizzzleLogo size="sm" :show-text="false" />
              </div>
              <h3 class="showcase-title">Welcome back</h3>
              <p class="showcase-sub">Plan your next meal in under 60 seconds.</p>

              <div class="showcase-roles">
                <span class="role-pill active"><AppIcon name="user" :size="13" /> Customer</span>
                <span class="role-pill"><AppIcon name="utensils" :size="13" /> Cook</span>
                <span class="role-pill"><AppIcon name="shield" :size="13" /> Manager</span>
                <span class="role-pill"><AppIcon name="settings" :size="13" /> Admin</span>
              </div>

              <router-link to="/login" class="btn btn-hero-primary showcase-cta">
                Continue to Login
                <AppIcon name="arrow-right" :size="16" />
              </router-link>
              <router-link to="/register" class="showcase-secondary">New here? Create your account</router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- Lottie Fire + Prepare Food Animation -->
      <div class="hero-lottie-fire" ref="heroFireEl" aria-hidden="true"></div>
      <div class="hero-lottie-pan" ref="heroPanEl" aria-hidden="true"></div>

      <!-- Hero food image accents -->
      <LazyImage
        :src="opt('dan-gold-4-jhdo54byg-unsplash.jpg').webp"
        :blur="opt('dan-gold-4-jhdo54byg-unsplash.jpg').blur"
        alt="Food" class="hero-food-img hero-food-1" :eager="true"
        img-class="hero-food-inner"
      />
      <LazyImage
        :src="opt('joseph-gonzalez-zcugjyqewe8-unsplash.jpg').webp"
        :blur="opt('joseph-gonzalez-zcugjyqewe8-unsplash.jpg').blur"
        alt="Food" class="hero-food-img hero-food-2" :eager="true"
        img-class="hero-food-inner"
      />

      <div class="scroll-hint" aria-hidden="true">
        <div class="scroll-mouse"><div class="scroll-dot"></div></div>
      </div>
    </section>

    <!-- ═══════════════ FOOD GALLERY — scroll-driven reveal ═══════════════ -->
    <section class="kitchen-curtain" ref="curtainSection">
      <div class="curtain-sticky">
        <!-- Food grid that scales away on scroll -->
        <div class="food-gallery" :style="{
          transform: `scale(${1 + curtainProgress * 0.15})`,
          opacity: Math.max(0, 1 - curtainProgress * 1.6),
          filter: `blur(${curtainProgress * 8}px)`
        }">
          <div v-for="(item, i) in curtainFoods" :key="i"
               class="food-gallery-item" :class="'gallery-item-' + (i + 1)">
            <img :src="item.img" :alt="item.name" class="food-gallery-img" loading="lazy" />
            <div class="food-gallery-overlay">
              <span class="food-gallery-name">{{ item.name }}</span>
            </div>
          </div>
        </div>

        <!-- Content that emerges from behind -->
        <div class="curtain-content" :style="{ opacity: curtainContentOpacity }">
          <div class="curtain-lottie" ref="curtainLottieEl"></div>
          <span class="section-tag">From Your Kitchen</span>
          <h2 class="heading-lg text-3d">Fresh From the Kitchen</h2>
          <p class="text-lg text-muted" style="max-width: 560px; margin: 16px auto 0;">
            Authentic meals prepared by verified home cooks, right in your own kitchen.
          </p>
        </div>
      </div>
    </section>

    <!-- ═══════════════ MARQUEE ═══════════════ -->
    <section class="marquee-section">
      <div class="marquee-track">
        <div class="marquee-inner">
          <span v-for="(city, i) in [...cities, ...cities]" :key="i" class="marquee-item">
            <span class="marquee-dot"></span>
            {{ city }}
          </span>
        </div>
      </div>
    </section>

    <!-- ═══════════════ HOW IT WORKS ═══════════════ -->
    <section id="how-it-works" class="section">
      <div class="container">
        <div class="section-header" data-reveal>
          <span class="section-tag">Simple Process</span>
          <h2 class="heading-lg text-3d">How Sizzzle Works</h2>
          <p class="text-lg text-muted section-subtitle">
            From booking to a perfectly cooked meal in three simple steps
          </p>
        </div>
        <div class="steps-grid" data-reveal-stagger>
          <div v-for="(step, i) in steps" :key="i"
               v-tilt="{ max: 14, perspective: 600, layers: true }"
               class="step-card card-3d" data-reveal="scale">
            <div class="step-number" data-depth="3">{{ String(i + 1).padStart(2, '0') }}</div>
            <div class="step-icon-wrap glow-ring" data-depth="2">
              <AppIcon :name="step.icon" :size="28" />
            </div>
            <h3 class="heading-sm" data-depth="1">{{ step.title }}</h3>
            <p class="text-muted" data-depth="1">{{ step.desc }}</p>
            <div v-if="i < steps.length - 1" class="step-connector"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════ CUISINES — SVG CARDS (no emojis) ═══════════════ -->
    <section class="section cuisine-section">
      <div class="container">
        <div class="section-header" data-reveal>
          <span class="section-tag">Explore Cuisines</span>
          <h2 class="heading-lg text-3d">A World of Flavors</h2>
          <p class="text-lg text-muted section-subtitle">
            From regional specialties to global favorites — all home-cooked
          </p>
        </div>
        <div class="cuisine-grid" data-reveal-stagger>
          <div v-for="(cuisine, i) in cuisines" :key="i"
               v-tilt="{ max: 12, perspective: 600, layers: true }"
               class="cuisine-card card-3d" data-reveal>
            <div class="cuisine-img-wrap" data-depth="3">
              <LazyImage
                :src="cuisine.webp" :blur="cuisine.blur"
                :alt="cuisine.name" img-class="cuisine-img"
              />
            </div>
            <div class="cuisine-name" data-depth="1">{{ cuisine.name }}</div>
            <div class="cuisine-glow" :style="{ background: cuisine.glow }"></div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════ FEATURES — 3D BENTO ═══════════════ -->
    <section id="features" class="section features-section">
      <div class="container">
        <div class="section-header" data-reveal>
          <span class="section-tag">Why Sizzzle</span>
          <h2 class="heading-lg text-3d">Built for Real Convenience</h2>
          <p class="text-lg text-muted section-subtitle">
            Every feature designed to make home-cooked meals effortless
          </p>
        </div>
        <div class="bento-grid" data-reveal-stagger>
          <div v-for="(feat, i) in features" :key="i"
               v-tilt="{ max: 12, perspective: 600, layers: true }"
               class="bento-card card-3d" :class="'bento-' + (i + 1)" data-reveal>
            <div class="feature-icon" :class="feat.color" data-depth="2">
              <AppIcon :name="feat.icon" :size="22" />
            </div>
            <h3 class="heading-sm" data-depth="1">{{ feat.title }}</h3>
            <p class="text-muted text-sm" data-depth="1">{{ feat.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════ SERVICE TIERS ═══════════════ -->
    <section class="section">
      <div class="container">
        <div class="section-header" data-reveal>
          <span class="section-tag">Flexible Plans</span>
          <h2 class="heading-lg text-3d">Choose Your Service</h2>
          <p class="text-lg text-muted section-subtitle">Two tiers to match your preference</p>
        </div>
        <div class="tiers-grid" data-reveal-stagger>
          <div v-tilt="{ max: 10, perspective: 600, layers: true }"
               class="tier-card card-3d" data-reveal="slide-left">
            <div class="tier-badge badge badge-primary" data-depth="2">Standard</div>
            <h3 class="heading-md" data-depth="1" style="margin-top:16px">You Provide Groceries</h3>
            <p class="text-muted" data-depth="1" style="margin-top:8px">
              Arrange the ingredients beforehand. The cook arrives and prepares your meal fresh in your kitchen.
            </p>
            <ul class="tier-features" data-depth="1">
              <li><AppIcon name="check" :size="16" class="text-primary" /> Ingredient list sent in advance</li>
              <li><AppIcon name="check" :size="16" class="text-primary" /> Lower service cost</li>
              <li><AppIcon name="check" :size="16" class="text-primary" /> Full control over ingredients</li>
              <li><AppIcon name="check" :size="16" class="text-primary" /> Kitchen checklist verified</li>
            </ul>
          </div>
          <div v-tilt="{ max: 10, perspective: 600, layers: true }"
               class="tier-card tier-card-premium card-3d" data-reveal="slide-right">
            <div class="tier-glow"></div>
            <div class="tier-badge badge badge-accent" data-depth="2">Premium</div>
            <h3 class="heading-md" data-depth="1" style="margin-top:16px">Cook Brings Groceries</h3>
            <p class="text-muted" data-depth="1" style="margin-top:8px">
              Sit back completely. The cook purchases and brings all ingredients before the cooking session.
            </p>
            <ul class="tier-features" data-depth="1">
              <li><AppIcon name="check" :size="16" class="text-accent" /> Zero effort from you</li>
              <li><AppIcon name="check" :size="16" class="text-accent" /> Fresh market ingredients</li>
              <li><AppIcon name="check" :size="16" class="text-accent" /> Cook selects best available</li>
              <li><AppIcon name="check" :size="16" class="text-accent" /> Premium quality guarantee</li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════ CTA ═══════════════ -->
    <section class="section cta-section">
      <div class="container">
        <div class="cta-card card-3d" data-reveal="scale">
          <div class="cta-flame cta-flame-1"></div>
          <div class="cta-flame cta-flame-2"></div>
          <div class="cta-content">
            <h2 class="heading-lg text-3d">Ready to taste the difference?</h2>
            <p class="text-lg text-muted" style="max-width:500px; margin-top:12px">
              Join families enjoying authentic home-cooked meals prepared by verified local cooks.
            </p>
            <div class="cta-actions">
              <router-link v-magnetic to="/register" class="btn btn-primary btn-lg">
                Get Started Free
                <AppIcon name="arrow-right" :size="18" />
              </router-link>
              <router-link v-magnetic to="/register/cook" class="btn btn-outline btn-lg">
                Become a Cook
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════ STATS COUNTER STRIP ═══════════════ -->
    <section class="stats-strip section" data-reveal>
      <div class="container">
        <div class="stats-grid">
          <div class="stat-block" v-for="s in platformStats" :key="s.label">
            <div class="stat-number">{{ s.value }}</div>
            <div class="stat-label">{{ s.label }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════ APP DOWNLOAD TEASE ═══════════════ -->
    <section class="section app-tease-section">
      <div class="container">
        <div class="app-tease" data-reveal>
          <div class="app-tease-content">
            <span class="section-tag">Coming Soon</span>
            <h2 class="heading-lg">Get the Sizzzle App</h2>
            <p class="text-lg text-muted" style="max-width: 400px; margin-top: 8px;">
              Book cooks, track orders in real-time, and manage your kitchen preferences — all from your phone.
            </p>
            <div class="app-badges">
              <div class="app-badge glass">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M17.05 20.28c-.98.95-2.05.8-3.08.35-1.09-.46-2.09-.48-3.24 0-1.44.62-2.2.44-3.06-.35C2.79 15.25 3.51 7.59 9.05 7.31c1.35.07 2.29.74 3.08.8 1.18-.24 2.31-.93 3.57-.84 1.51.12 2.65.72 3.4 1.8-3.12 1.87-2.38 5.98.48 7.13-.57 1.5-1.31 2.99-2.54 4.09zM12.03 7.25c-.15-2.23 1.66-4.07 3.74-4.25.29 2.58-2.34 4.5-3.74 4.25z"/></svg>
                <div>
                  <span class="app-badge-sub">Coming on</span>
                  <span class="app-badge-store">App Store</span>
                </div>
              </div>
              <div class="app-badge glass">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M3.609 1.814L13.792 12 3.61 22.186a.996.996 0 0 1-.61-.92V2.734a1 1 0 0 1 .609-.92zm10.89 10.893l2.302 2.302-10.937 6.333 8.635-8.635zm3.199-3.199l2.38 1.379a1 1 0 0 1 0 1.726l-2.38 1.379-2.537-2.537 2.537-2.537zM5.864 2.658L16.8 8.99l-2.302 2.302-8.634-8.634z"/></svg>
                <div>
                  <span class="app-badge-sub">Coming on</span>
                  <span class="app-badge-store">Google Play</span>
                </div>
              </div>
            </div>
          </div>
          <div class="app-tease-visual">
            <div class="app-phone-mockup">
              <div class="phone-screen">
                <div class="phone-splash-screen">
                  <img src="/iconlogo.png" alt="Sizzzle logo" class="phone-splash-logo" />
                  <div class="phone-splash-brand">SIZZLE</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ═══════════════ FOOTER ═══════════════ -->
    <footer class="footer">
      <div class="container">
        <div class="footer-grid">
          <div class="footer-brand">
            <SizzzleLogo size="md" :show-text="true" :show-tagline="true" />
            <p class="text-sm text-muted" style="margin-top:16px; max-width:280px">
              Connecting households with skilled home cooks for authentic, freshly prepared meals.
            </p>
          </div>
          <div class="footer-links-group">
            <h4 class="footer-heading">Platform</h4>
            <a href="#how-it-works">How it works</a>
            <a href="#features">Features</a>
            <router-link to="/register">Book a cook</router-link>
            <router-link to="/register/cook">Join as cook</router-link>
          </div>
          <div class="footer-links-group">
            <h4 class="footer-heading">Company</h4>
            <a href="#">About us</a>
            <a href="#">Blog</a>
            <a href="#">Careers</a>
            <a href="#">Contact</a>
          </div>
          <div class="footer-links-group">
            <h4 class="footer-heading">Legal</h4>
            <router-link to="/terms">Terms of Service</router-link>
            <router-link to="/privacy">Privacy Policy</router-link>
            <router-link to="/cancellation-policy">Cancellation Policy</router-link>
            <router-link to="/refund-policy">Refund Policy</router-link>
          </div>
        </div>
        <div class="footer-bottom">
          <p class="text-sm text-muted">&copy; 2026 Sizzzle. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import lottie from 'lottie-web'
import AppNavbar from '../components/AppNavbar.vue'
import SizzzleLogo from '../components/SizzzleLogo.vue'
import AppIcon from '../components/AppIcon.vue'
import LazyImage from '../components/LazyImage.vue'
import { useScrollReveal } from '../composables/useScrollReveal'
import imgManifest from '../assets/image-manifest.json'

/* helper to resolve optimized image + blur from manifest */
function opt(originalFilename) {
  const entry = imgManifest[originalFilename]
  if (!entry) return { webp: `/images/food/${originalFilename}`, blur: '' }
  return entry
}

useScrollReveal()

const landingEl = ref(null)
const heroEl = ref(null)
const curtainSection = ref(null)
const curtainProgress = ref(0)
const heroFireEl = ref(null)
const heroPanEl = ref(null)
const curtainLottieEl = ref(null)
const scrollY = ref(0)

/* smooth hero parallax tied to scroll */
const heroParallax = computed(() => {
  const y = scrollY.value
  const t = Math.min(y / 600, 1)
  return {
    transform: `translateY(${y * 0.15}px)`,
    opacity: 1 - t * 0.6
  }
})

const curtainContentOpacity = computed(() => {
  return Math.min(1, Math.max(0, (curtainProgress.value - 0.5) * 2))
})

function onScroll() {
  const y = window.scrollY
  scrollY.value = y

  // Parallax on kanji
  const kanji = document.querySelector('.hero-kanji')
  if (kanji) kanji.style.transform = `translate(-50%, ${-55 + y * 0.06}%)`

  // Kitchen curtain progress
  if (curtainSection.value) {
    const rect = curtainSection.value.getBoundingClientRect()
    const vh = window.innerHeight
    if (rect.top < vh && rect.bottom > 0) {
      const total = rect.height - vh
      const scrolled = vh - rect.top
      curtainProgress.value = Math.min(1, Math.max(0, scrolled / total))
    }
  }
}

onMounted(() => {
  window.addEventListener('scroll', onScroll, { passive: true })
  onScroll()

  if (heroFireEl.value) {
    lottie.loadAnimation({ container: heroFireEl.value, renderer: 'svg', loop: true, autoplay: true, path: '/animations/fire.json' })
  }
  if (heroPanEl.value) {
    lottie.loadAnimation({ container: heroPanEl.value, renderer: 'svg', loop: true, autoplay: true, path: '/animations/prepare-food.json' })
  }
  if (curtainLottieEl.value) {
    lottie.loadAnimation({ container: curtainLottieEl.value, renderer: 'svg', loop: true, autoplay: true, path: '/animations/cooking.json' })
  }
})
onUnmounted(() => { window.removeEventListener('scroll', onScroll) })

const cities = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Pune', 'Kolkata', 'Ahmedabad']

const curtainFoods = [
  { name: 'Curry', img: opt('pexels-idinarisk-3008740.jpg').webp },
  { name: 'Dosa', img: opt('joseph-gonzalez-fdlzbwip0am-unsplash.jpg').webp },
  { name: 'Noodles', img: opt('eiliv-aceron-zuidlsz3xlg-unsplash.jpg').webp },
  { name: 'Pasta', img: opt('odiseo-castrejon-1spu0kt-ejg-unsplash.jpg').webp },
  { name: 'Biryani', img: opt('chad-montano-eeqbbemh9-c-unsplash.jpg').webp },
  { name: 'Fish Fry', img: opt('anh-nguyen-kca-c3f-3fe-unsplash.jpg').webp },
  { name: 'Chaat', img: opt('pexels-clickerhappy-9210.jpg').webp },
  { name: 'Salad', img: opt('anna-pelzer-igfigp5onv0-unsplash.jpg').webp },
  { name: 'Dessert', img: opt('pexels-framed-by-rania-2454533.jpg').webp },
  { name: 'Thali', img: opt('joseph-gonzalez-zcugjyqewe8-unsplash.jpg').webp },
  { name: 'Tandoori', img: opt('pexels-saveurssecretes-7625056.jpg').webp },
  { name: 'Kebab', img: opt('pexels-saveurssecretes-5410418.jpg').webp },
  { name: 'Masala', img: opt('pexels-shiva-kumar-146021-4595313.jpg').webp },
  { name: 'Platter', img: opt('pexels-saveurssecretes-14831540.jpg').webp },
  { name: 'Stir Fry', img: opt('fast-ink-Oyslr_PiPg0-unsplash.jpg').webp },
  { name: 'Bowl', img: opt('dan-gold-4-jhdo54byg-unsplash.jpg').webp },
]

const steps = [
  { icon: 'calendar', title: 'Schedule Your Booking', desc: 'Choose a date, select dishes, and specify the number of people. Book at least one day in advance.' },
  { icon: 'navigation', title: 'Cook Gets Matched', desc: 'Our smart algorithm matches you with the nearest, highest-rated cook based on your preferences.' },
  { icon: 'utensils', title: 'Enjoy Your Meal', desc: 'The cook arrives, verifies via OTP, and prepares your meal fresh in your kitchen. Rate after service.' }
]

const features = [
  { icon: 'shield', title: 'Verified Cooks', desc: 'Three-step verification: ID check, skill test, and background clearance before any cook goes live.', color: 'icon-green' },
  { icon: 'star', title: 'Smart Matching', desc: 'Normalized match score based on distance, ratings, verification status, and your taste profile.', color: 'icon-orange' },
  { icon: 'sliders', title: 'Taste Profiles', desc: 'Set your allergies, spice tolerance, and dietary preferences. Every cook knows your palate.', color: 'icon-green' },
  { icon: 'lock', title: 'OTP Check-in', desc: 'Secure arrival confirmation ensures the right cook reaches you at the scheduled time.', color: 'icon-orange' },
  { icon: 'credit-card', title: 'Transparent Pricing', desc: 'Clear breakdown of service costs, GST, and any extras. No hidden charges or surprises.', color: 'icon-green' },
  { icon: 'clock', title: 'Fair Cancellation', desc: 'Flexible cancellation windows with transparent charge tiers. Cancel free up to 12 hours before.', color: 'icon-orange' }
]

// SVG icons for cuisines instead of emojis
const cuisines = [
  { name: 'North Indian', glow: 'rgba(255,150,38,0.15)', ...opt('pexels-idinarisk-3008740.jpg') },
  { name: 'South Indian', glow: 'rgba(242,115,79,0.12)', ...opt('joseph-gonzalez-fdlzbwip0am-unsplash.jpg') },
  { name: 'Chinese', glow: 'rgba(255,206,51,0.14)', ...opt('eiliv-aceron-zuidlsz3xlg-unsplash.jpg') },
  { name: 'Italian', glow: 'rgba(45,182,125,0.12)', ...opt('odiseo-castrejon-1spu0kt-ejg-unsplash.jpg') },
  { name: 'Mughlai', glow: 'rgba(242,115,79,0.15)', ...opt('chad-montano-eeqbbemh9-c-unsplash.jpg') },
  { name: 'Bengali', glow: 'rgba(255,150,38,0.12)', ...opt('anh-nguyen-kca-c3f-3fe-unsplash.jpg') },
  { name: 'Street Food', glow: 'rgba(255,206,51,0.15)', ...opt('pexels-clickerhappy-9210.jpg') },
  { name: 'Healthy', glow: 'rgba(45,182,125,0.14)', ...opt('anna-pelzer-igfigp5onv0-unsplash.jpg') },
  { name: 'Desserts', glow: 'rgba(242,115,79,0.1)', ...opt('pexels-framed-by-rania-2454533.jpg') },
  { name: 'Gujarati', glow: 'rgba(255,150,38,0.13)', ...opt('joseph-gonzalez-zcugjyqewe8-unsplash.jpg') }
]

const platformStats = [
  { value: '8+', label: 'Cities Launching' },
  { value: '500+', label: 'Cooks Onboarding' },
  { value: '20+', label: 'Cuisines Available' },
  { value: '24/7', label: 'Support Ready' }
]
</script>

<style scoped>
/* ═══ SMOOTH SCROLL ═══ */
.landing { scroll-behavior: smooth; }

/* ═══════════════ HERO ═══════════════ */
.hero {
  padding: 140px 0 80px;
  position: relative; overflow: hidden;
  text-align: center;
  background: linear-gradient(180deg, #FFFAF6 0%, #FFF5ED 60%, var(--color-bg) 100%);
  will-change: transform;
}
.hero-kanji {
  position: absolute; top: 50%; left: 50%;
  transform: translate(-50%, -55%);
  font-family: 'Yuji Boku', serif;
  font-size: clamp(16rem, 30vw, 28rem);
  color: rgba(242, 115, 79, 0.04);
  pointer-events: none; user-select: none;
  line-height: 1; z-index: 0; will-change: transform;
}
.orbit-ring {
  position: absolute; top: 50%; left: 50%;
  width: 500px; height: 500px;
  transform: translate(-50%, -55%);
  pointer-events: none; z-index: 0;
}
.orbit-dot {
  position: absolute; width: 8px; height: 8px;
  border-radius: 50%; top: 50%; left: 50%;
}
.orbit-dot-1 {
  background: var(--color-accent);
  box-shadow: 0 0 16px rgba(242,115,79,0.5);
  animation: orbitSpin 12s linear infinite;
  --orbit-r: 220px;
}
.orbit-dot-2 {
  background: var(--color-primary);
  box-shadow: 0 0 16px rgba(45,182,125,0.5);
  animation: orbitSpin 18s linear infinite reverse;
  --orbit-r: 180px; width: 6px; height: 6px;
}
.orbit-dot-3 {
  background: #FFCE33;
  box-shadow: 0 0 12px rgba(255,206,51,0.5);
  animation: orbitSpin 15s linear infinite;
  --orbit-r: 260px; width: 5px; height: 5px;
}
@keyframes orbitSpin {
  0%   { transform: rotate(0deg) translateX(var(--orbit-r)) rotate(0deg); }
  100% { transform: rotate(360deg) translateX(var(--orbit-r)) rotate(-360deg); }
}
.hero-fire {
  position: absolute; border-radius: 50%;
  pointer-events: none; filter: blur(90px); z-index: 0;
}
.hero-fire-1 {
  width: 400px; height: 400px; top: 10%; left: 5%;
  background: radial-gradient(circle, rgba(255,150,38,0.18), transparent 70%);
  animation: firePulse 5s ease-in-out infinite;
}
.hero-fire-2 {
  width: 350px; height: 350px; bottom: -5%; right: 8%;
  background: radial-gradient(circle, rgba(242,115,79,0.15), transparent 70%);
  animation: firePulse 3.8s ease-in-out infinite 1.2s;
}
.hero-fire-3 {
  width: 260px; height: 260px; top: 35%; right: 25%;
  background: radial-gradient(circle, rgba(255,206,51,0.12), transparent 70%);
  animation: firePulse 6s ease-in-out infinite 0.6s;
}
@keyframes firePulse {
  0%, 100% { opacity: 0.5; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.2); }
}

.hero-center {
  position: relative; z-index: 1;
  display: flex; flex-direction: column; align-items: center;
}
.hero-content {
  max-width: 700px;
  animation: heroEntry 1s cubic-bezier(0.16, 1, 0.3, 1) both;
  will-change: transform, opacity;
}
@keyframes heroEntry {
  from { opacity: 0; transform: translateY(40px) scale(0.97); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
.hero-badge {
  display: inline-flex; align-items: center; gap: 10px;
  padding: 8px 20px; border-radius: var(--radius-full);
  font-size: 0.8rem; font-weight: 600;
  color: var(--color-primary-dark); letter-spacing: 0.02em;
  margin-bottom: 28px;
}
.badge-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--color-primary);
  animation: pulse 2.5s ease-in-out infinite;
  box-shadow: 0 0 8px rgba(45, 182, 125, 0.4);
}
.hero-title {
  font-family: 'Sekaiwo', var(--font-brand);
  font-size: clamp(2.8rem, 7vw, 5.5rem);
  font-weight: 400; line-height: 1.1;
  letter-spacing: -0.02em; color: var(--color-text);
}
.hero-title-line { display: block; }
.hero-title-fire { display: block; color: var(--color-accent); }
.hero-subtitle {
  margin-top: 24px; max-width: 520px;
  line-height: 1.8; margin-inline: auto;
  color: var(--color-text-secondary);
}
.hero-actions {
  display: flex; gap: 16px; margin-top: 40px;
  justify-content: center; flex-wrap: wrap;
}

.hero-showcase {
  margin-top: 34px;
  display: grid;
  grid-template-columns: 1.15fr 1fr;
  border-radius: 28px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.7);
  box-shadow: 0 24px 58px rgba(29, 28, 25, 0.12);
}

.showcase-visual {
  position: relative;
  min-height: 340px;
  overflow: hidden;
}

.showcase-visual :deep(.lazy-img-wrap),
.showcase-visual :deep(.showcase-image) {
  width: 100%;
  height: 100%;
}

.showcase-visual :deep(.showcase-image) {
  object-fit: cover;
  filter: saturate(1.05) contrast(1.02);
}

.showcase-overlay {
  position: absolute;
  inset: auto 0 0;
  padding: 30px;
  text-align: left;
  color: #fff;
  background: linear-gradient(180deg, rgba(15, 20, 26, 0) 0%, rgba(15, 20, 26, 0.72) 100%);
}

.showcase-tag {
  font-size: clamp(1.55rem, 2.4vw, 2.2rem);
  font-weight: 800;
  line-height: 1.08;
  letter-spacing: -0.02em;
}

.showcase-copy {
  margin-top: 10px;
  font-size: 0.9rem;
  opacity: 0.92;
}

.showcase-panel {
  background: #fff;
  padding: 28px;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
}

.showcase-brand-pill {
  width: 48px;
  height: 48px;
  border-radius: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(242, 115, 79, 0.16), rgba(242, 115, 79, 0.05));
  border: 1px solid rgba(242, 115, 79, 0.28);
}

.showcase-title {
  margin-top: 16px;
  font-size: clamp(1.65rem, 2.1vw, 2rem);
  line-height: 1.12;
  font-weight: 800;
}

.showcase-sub {
  margin-top: 8px;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}

.showcase-roles {
  margin-top: 18px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.role-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 12px;
  border-radius: var(--radius-full);
  border: 1px solid var(--color-border);
  background: #fff;
  font-size: 0.73rem;
  font-weight: 700;
  color: var(--color-text-secondary);
}

.role-pill.active {
  border-color: rgba(242, 115, 79, 0.36);
  color: var(--color-accent-dark);
  background: rgba(242, 115, 79, 0.09);
}

.showcase-cta {
  margin-top: 22px;
  width: 100%;
  justify-content: center;
}

.showcase-secondary {
  margin-top: 12px;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--color-text-secondary);
}

.showcase-secondary:hover {
  color: var(--color-accent-dark);
}
.btn-hero-primary {
  display: inline-flex; align-items: center; gap: 10px;
  padding: 14px 36px; font-weight: 700; font-size: 1rem;
  border-radius: var(--radius-full); color: #fff;
  background: linear-gradient(135deg, #F2734F 0%, #FF9426 100%);
  border: none; cursor: pointer; position: relative; overflow: hidden;
  box-shadow: 0 4px 24px rgba(242, 115, 79, 0.35), 0 12px 40px rgba(242, 115, 79, 0.15);
  transition: all 0.3s ease;
}
.btn-hero-primary:hover {
  box-shadow: 0 8px 32px rgba(242, 115, 79, 0.45), 0 0 60px rgba(255, 148, 38, 0.2);
  transform: translateY(-3px);
}
.btn-hero-primary::after {
  content: ''; position: absolute; inset: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.25), transparent);
  transform: translateX(-100%); transition: transform 0.5s ease;
}
.btn-hero-primary:hover::after { transform: translateX(100%); }
.btn-hero-outline {
  display: inline-flex; align-items: center; gap: 10px;
  padding: 14px 36px; font-weight: 700; font-size: 1rem;
  border-radius: var(--radius-full); color: #F2734F;
  background: transparent; border: 2px solid rgba(242, 115, 79, 0.3);
  cursor: pointer; transition: all 0.3s ease;
}
.btn-hero-outline:hover {
  background: rgba(242, 115, 79, 0.06); border-color: #F2734F;
  transform: translateY(-2px);
}

/* Scroll indicator */
.scroll-hint {
  position: absolute; bottom: 28px; left: 50%;
  transform: translateX(-50%); animation: fadeIn 1s 1.5s both;
}
.scroll-mouse {
  width: 24px; height: 38px;
  border: 2px solid rgba(242, 115, 79, 0.3);
  border-radius: 12px; position: relative;
}
.scroll-dot {
  width: 4px; height: 4px; background: #F2734F;
  border-radius: 50%; position: absolute;
  top: 8px; left: 50%; transform: translateX(-50%);
  animation: scrollBounce 2s ease-in-out infinite;
}
@keyframes scrollBounce { 0%,100% { top:8px; opacity:1 } 50% { top:22px; opacity:.3 } }

/* ═══ LOTTIE HERO ELEMENTS ═══ */
.hero-lottie-fire {
  position: absolute; bottom: 20px; right: 6%;
  width: 180px; height: 180px;
  z-index: 1; pointer-events: none;
  filter: drop-shadow(0 0 20px rgba(255, 100, 30, 0.3));
}
.hero-lottie-pan {
  position: absolute; bottom: 10px; right: 2%;
  width: 220px; height: 160px;
  z-index: 2; pointer-events: none;
  filter: drop-shadow(0 4px 16px rgba(0,0,0,0.15));
}
.hero-food-img {
  position: absolute; z-index: 0;
  border-radius: 50%;
  overflow: hidden;
  pointer-events: none;
  box-shadow: 0 8px 32px rgba(0,0,0,0.1);
  border: 3px solid rgba(255,255,255,0.6);
}
.hero-food-img :deep(.lazy-img--real) {
  width: 100%; height: 100%;
  object-fit: cover;
}
.hero-food-1 {
  width: 90px; height: 90px;
  bottom: 25%; left: 6%;
  animation: floatImg 5s ease-in-out infinite;
}
.hero-food-2 {
  width: 70px; height: 70px;
  top: 18%; right: 5%;
  animation: floatImg 4s ease-in-out infinite 1.5s;
}
@keyframes floatImg {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-10px) rotate(3deg); }
}

@media (max-width: 768px) {
  .hero-lottie-fire { width: 120px; height: 120px; right: 2%; bottom: 10px; }
  .hero-lottie-pan { width: 160px; height: 120px; right: 0; bottom: 5px; }
  .hero-food-1 { width: 60px; height: 60px; }
  .hero-food-2 { width: 50px; height: 50px; }
}
@media (max-width: 480px) {
  .hero-lottie-fire, .hero-lottie-pan { display: none; }
  .hero-food-1, .hero-food-2 { display: none; }
}

/* ═══ CURTAIN LOTTIE ═══ */
.curtain-lottie {
  width: 200px; height: 120px;
  margin: 0 auto 16px;
}

/* ═══════════════ KITCHEN CURTAIN ═══════════════ */
.kitchen-curtain {
  height: 200vh;
  position: relative;
}
.curtain-sticky {
  position: sticky;
  top: 0;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: var(--color-bg);
}

/* ═══ FOOD GALLERY GRID ═══ */
.food-gallery {
  position: absolute;
  inset: 0;
  z-index: 2;
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-auto-rows: 1fr;
  gap: 4px;
  padding: 4px;
  will-change: transform, opacity, filter;
  transition: none;
}
.food-gallery-item {
  position: relative;
  overflow: hidden;
  border-radius: 6px;
}
/* Create visual variety with spanning */
.gallery-item-1 { grid-row: span 2; }
.gallery-item-5 { grid-column: span 2; }
.gallery-item-9 { grid-row: span 2; }
.gallery-item-13 { grid-column: span 2; }
.food-gallery-img {
  width: 100%; height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.4s ease;
}
.food-gallery-item:hover .food-gallery-img {
  transform: scale(1.08);
}
.food-gallery-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 50%, rgba(0,0,0,0.55) 100%);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding: 8px;
  opacity: 0;
  transition: opacity 0.3s ease;
}
.food-gallery-item:hover .food-gallery-overlay {
  opacity: 1;
}
.food-gallery-name {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #fff;
  text-shadow: 0 1px 4px rgba(0,0,0,0.3);
}

.curtain-content {
  position: relative;
  z-index: 1;
  text-align: center;
  padding: 0 24px;
  transition: opacity 0.1s linear;
}

/* ═══ MARQUEE ═══ */
.marquee-section {
  padding: 20px 0; overflow: hidden;
  border-top: 1px solid var(--color-border-light);
  border-bottom: 1px solid var(--color-border-light);
  background: var(--color-bg-alt);
}
.marquee-track {
  overflow: hidden;
  mask-image: linear-gradient(90deg, transparent, black 10%, black 90%, transparent);
  -webkit-mask-image: linear-gradient(90deg, transparent, black 10%, black 90%, transparent);
}
.marquee-inner {
  display: flex; gap: 48px; white-space: nowrap;
  animation: marquee 25s linear infinite; width: max-content;
}
.marquee-item {
  display: inline-flex; align-items: center; gap: 10px;
  font-size: 0.85rem; font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase; letter-spacing: 0.08em;
}
.marquee-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--color-accent); opacity: 0.5;
}
@keyframes marquee { 0% { transform: translateX(0) } 100% { transform: translateX(-50%) } }

/* ═══ SECTION LAYOUT ═══ */
.section {
  padding: 100px 0;
}
.section-tag {
  display: inline-block; font-size: 0.7rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.15em;
  color: var(--color-accent); margin-bottom: 12px;
  position: relative; padding-left: 20px;
}
.section-tag::before {
  content: ''; position: absolute; left: 0; top: 50%;
  transform: translateY(-50%); width: 12px; height: 2px;
  background: var(--color-accent); border-radius: 1px;
}
.section-header {
  text-align: center; max-width: 580px; margin: 0 auto 64px;
}
.section-subtitle { margin-top: 14px; }

/* ═══ STEPS ═══ */
.steps-grid {
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 24px; perspective: 1200px;
}
.step-card {
  padding: 40px 32px; text-align: center;
  position: relative; overflow: visible;
}
.step-connector {
  position: absolute; top: 50%; right: -14px;
  width: 28px; height: 2px;
  background: linear-gradient(90deg, var(--color-primary-light), transparent);
  z-index: 1;
}
.step-number {
  font-size: 0.7rem; font-weight: 800;
  color: var(--color-accent);
  letter-spacing: 0.15em; text-transform: uppercase;
}
.step-icon-wrap {
  width: 64px; height: 64px;
  border-radius: var(--radius-lg);
  background: linear-gradient(160deg, var(--color-primary-ghost), rgba(45, 182, 125, 0.18));
  color: var(--color-primary);
  display: flex; align-items: center; justify-content: center;
  margin: 18px auto 22px;
  border: 1px solid rgba(45, 182, 125, 0.12);
}
.step-card h3 { margin-bottom: 10px; }

/* ═══ CUISINES GRID ═══ */
.cuisine-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 20px;
  perspective: 800px;
}
.cuisine-card {
  padding: 20px 16px;
  text-align: center;
  position: relative; overflow: hidden;
}
.cuisine-img-wrap {
  width: 80px; height: 80px;
  margin: 0 auto 12px;
  border-radius: 50%;
  overflow: hidden;
  box-shadow: 0 4px 16px rgba(0,0,0,0.1);
  border: 2px solid rgba(255,255,255,0.7);
}
.cuisine-img-wrap :deep(.lazy-img-wrap) {
  width: 100%; height: 100%;
}
.cuisine-img-wrap :deep(.cuisine-img) {
  width: 100%; height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}
.cuisine-card:hover :deep(.cuisine-img) {
  transform: scale(1.15);
}
.cuisine-name {
  font-weight: 700; font-size: 0.9rem;
  color: var(--color-text);
}
.cuisine-glow {
  position: absolute; bottom: -20px; left: 50%;
  transform: translateX(-50%);
  width: 100px; height: 100px;
  border-radius: 50%; filter: blur(40px);
  pointer-events: none; z-index: -1;
}

/* ═══ BENTO FEATURES ═══ */
.features-section {
  background: var(--color-bg-alt); position: relative;
}
.features-section::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--color-border), transparent);
}
.bento-grid {
  display: grid; grid-template-columns: repeat(3, 1fr);
  grid-template-rows: auto auto; gap: 24px;
  perspective: 1200px;
}
.bento-1 { grid-column: span 2; }
.bento-card {
  padding: 36px 30px; position: relative; overflow: hidden;
}
.bento-card::after {
  content: ''; position: absolute; top: 0; left: 24px; right: 24px;
  height: 3px; border-radius: 0 0 3px 3px;
  background: linear-gradient(90deg, var(--color-primary), transparent);
  opacity: 0; transition: opacity 0.3s ease;
}
.bento-card:nth-child(even)::after {
  background: linear-gradient(90deg, var(--color-accent), transparent);
}
.bento-card:hover::after { opacity: 1; }
.feature-icon {
  width: 52px; height: 52px;
  border-radius: var(--radius-md);
  display: flex; align-items: center; justify-content: center;
  margin-bottom: 20px;
}
.icon-green {
  background: var(--color-primary-ghost); color: var(--color-primary);
  border: 1px solid rgba(45, 182, 125, 0.12);
}
.icon-orange {
  background: var(--color-accent-ghost); color: var(--color-accent);
  border: 1px solid rgba(242, 115, 79, 0.12);
}
.bento-card h3 { margin-bottom: 10px; }

/* ═══ TIERS ═══ */
.tiers-grid {
  display: grid; grid-template-columns: repeat(2, 1fr);
  gap: 24px; max-width: 850px; margin: 0 auto;
  perspective: 1200px;
}
.tier-card { padding: 36px; position: relative; overflow: hidden; }
.tier-card-premium {
  border: 1.5px solid rgba(242, 115, 79, 0.2);
  background: linear-gradient(170deg, var(--color-surface-raised) 0%, rgba(242, 115, 79, 0.03) 100%);
}
.tier-glow {
  position: absolute; top: -60px; right: -60px;
  width: 200px; height: 200px; border-radius: 50%;
  background: radial-gradient(circle, rgba(242, 115, 79, 0.12), transparent 70%);
  filter: blur(40px); animation: firePulse 4s ease-in-out infinite;
  pointer-events: none;
}
.tier-features {
  list-style: none; margin-top: 28px;
  display: flex; flex-direction: column; gap: 14px;
}
.tier-features li {
  display: flex; align-items: center; gap: 12px;
  font-size: 0.875rem; font-weight: 500;
}

/* ═══ CTA ═══ */
.cta-section { padding-bottom: 100px; }
.cta-card {
  padding: 72px; text-align: center;
  display: flex; justify-content: center;
  position: relative; overflow: hidden;
  background: linear-gradient(170deg, var(--color-surface-raised) 0%, rgba(45, 182, 125, 0.04) 100%);
}
.cta-flame {
  position: absolute; border-radius: 50%;
  filter: blur(80px); pointer-events: none;
  animation: firePulse 5s ease-in-out infinite;
}
.cta-flame-1 {
  width: 260px; height: 260px; bottom: -80px; left: -40px;
  background: radial-gradient(circle, rgba(242, 115, 79, 0.12), transparent 70%);
}
.cta-flame-2 {
  width: 200px; height: 200px; top: -60px; right: -20px;
  background: radial-gradient(circle, rgba(255, 206, 51, 0.1), transparent 70%);
  animation-delay: 1.5s;
}
.cta-content {
  display: flex; flex-direction: column; align-items: center;
  position: relative; z-index: 1;
}
.cta-actions {
  display: flex; gap: 16px; margin-top: 36px;
  flex-wrap: wrap; justify-content: center;
}

/* ═══ STATS STRIP ═══ */
.stats-strip {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
  padding: 56px 0;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  text-align: center;
}
.stat-number {
  font-size: 2.4rem;
  font-weight: 800;
  color: #fff;
  line-height: 1;
  letter-spacing: -0.02em;
}
.stat-label {
  font-size: 0.82rem;
  font-weight: 500;
  color: rgba(255,255,255,0.55);
  margin-top: 6px;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

/* ═══ APP TEASE ═══ */
.app-tease {
  display: flex;
  align-items: center;
  gap: 60px;
}
.app-tease-content {
  flex: 1;
}
.app-tease-visual {
  flex: 0 0 260px;
  display: flex;
  justify-content: center;
}
.app-phone-mockup {
  width: 220px;
  height: 440px;
  border-radius: 32px;
  background: #1a1a2e;
  padding: 12px;
  box-shadow: 0 24px 64px rgba(0,0,0,0.18), 0 0 0 1px rgba(255,255,255,0.06);
  position: relative;
  overflow: hidden;
}
.app-phone-mockup::before {
  content: '';
  position: absolute;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  width: 80px;
  height: 22px;
  background: #0f0f1a;
  border-radius: 12px;
  z-index: 2;
}
.phone-screen {
  width: 100%;
  height: 100%;
  border-radius: 22px;
  overflow: hidden;
}

.phone-splash-screen {
  width: 100%;
  height: 100%;
  background: linear-gradient(160deg, #fff8ef 0%, #fff4e8 52%, #fffdf8 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 18px;
  padding: 22px;
}

.phone-splash-logo {
  width: 88px;
  height: 88px;
  object-fit: contain;
  filter: drop-shadow(0 8px 18px rgba(15, 28, 21, 0.14));
}

.phone-splash-brand {
  font-family: var(--font-brand);
  font-size: 2.2rem;
  letter-spacing: 0.06em;
  color: #12131a;
  line-height: 1;
}
.app-badges {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}
.app-badge {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 18px;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.2s ease;
}
.app-badge:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}
.app-badge-sub {
  display: block;
  font-size: 0.62rem;
  opacity: 0.5;
  letter-spacing: 0.03em;
}
.app-badge-store {
  display: block;
  font-size: 0.88rem;
  font-weight: 700;
}

/* ═══ FOOTER ═══ */
.footer {
  padding: 72px 0 36px;
  border-top: 1px solid var(--color-border-light);
  background: var(--color-bg-alt); position: relative;
}
.footer::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--color-primary-ghost), transparent);
}
.footer-grid {
  display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 52px;
}
.footer-heading {
  font-size: 0.7rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: 0.1em;
  color: var(--color-text); margin-bottom: 18px;
}
.footer-links-group { display: flex; flex-direction: column; gap: 11px; }
.footer-links-group a {
  font-size: 0.875rem; color: var(--color-text-secondary);
  transition: all var(--transition-fast); font-weight: 450;
}
.footer-links-group a:hover { color: var(--color-primary); transform: translateX(3px); }
.footer-bottom {
  margin-top: 52px; padding-top: 24px;
  border-top: 1px solid var(--color-border-light);
}

/* ═══════════════ RESPONSIVE ═══════════════ */
@media (max-width: 1024px) {
  .hero-fire { display: none; }
  .hero-kanji { font-size: 14rem; }
  .orbit-ring { display: none; }
  .bento-1 { grid-column: span 1; }
  .cuisine-grid { grid-template-columns: repeat(3, 1fr); }
  .food-gallery { grid-template-columns: repeat(3, 1fr); }
  .section { padding: 72px 0; }
}

@media (max-width: 768px) {
  .hero { padding: 110px 0 60px; }
  .hero-title { font-size: clamp(2.2rem, 8vw, 3.2rem); }
  .hero-kanji { display: none; }
  .scroll-hint { display: none; }
  .steps-grid, .bento-grid { grid-template-columns: 1fr; }
  .step-connector { display: none; }
  .tiers-grid { grid-template-columns: 1fr; }
  .footer-grid { grid-template-columns: 1fr 1fr; gap: 28px; }
  .cta-card { padding: 48px 28px; }
  .hero-badge { font-size: 0.75rem; padding: 6px 14px; margin-bottom: 20px; }
  .hero-subtitle { font-size: 0.95rem; line-height: 1.7; }
  .hero-actions { margin-top: 28px; }
  .hero-showcase {
    grid-template-columns: 1fr;
    margin-top: 26px;
  }
  .showcase-visual { min-height: 240px; }
  .showcase-panel { padding: 22px; }
  .section-header { margin-bottom: 36px; }
  .step-card { padding: 28px 22px; }
  .bento-card { padding: 28px 22px; }
  .tier-card { padding: 28px; }
  .cuisine-grid { grid-template-columns: repeat(3, 1fr); gap: 14px; }
  .cuisine-card { padding: 24px 16px; }
  .kitchen-curtain { height: 170vh; }
  .food-gallery { grid-template-columns: repeat(3, 1fr); gap: 3px; }
  .gallery-item-1, .gallery-item-9 { grid-row: span 1; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); gap: 16px; }
  .stat-number { font-size: 1.8rem; }
  .app-tease { flex-direction: column; gap: 32px; text-align: center; }
  .app-tease-content { align-items: center; display: flex; flex-direction: column; }
  .app-badges { justify-content: center; }
  .app-tease-visual { flex: 0; }
  .app-phone-mockup { width: 180px; height: 360px; }
  .section { padding: 56px 0; }
  .testimonial-card { width: 300px; }
}

@media (max-width: 480px) {
  .hero { padding: 96px 0 40px; }
  .hero-actions { flex-direction: column; gap: 12px; }
  .hero-actions .btn-hero-primary,
  .hero-actions .btn-hero-outline { width: 100%; justify-content: center; }
  .footer-grid { grid-template-columns: 1fr; gap: 24px; }
  .cta-card { padding: 36px 20px; }
  .cta-actions { flex-direction: column; width: 100%; }
  .cta-actions .btn { width: 100%; justify-content: center; }
  .marquee-item { font-size: 0.75rem; }
  .testimonial-card { width: 260px; padding: 20px; }
  .cuisine-grid { grid-template-columns: repeat(2, 1fr); }
  .cuisine-img-wrap { width: 64px; height: 64px; }
  .btn-hero-primary, .btn-hero-outline { padding: 12px 28px; font-size: 0.9rem; }
  .showcase-tag { font-size: 1.35rem; }
  .showcase-copy { font-size: 0.8rem; }
  .kitchen-curtain { height: 150vh; }
  .food-gallery { grid-template-columns: repeat(3, 1fr); gap: 2px; padding: 2px; }
  .gallery-item-5, .gallery-item-13 { grid-column: span 1; }
  .food-gallery-name { font-size: 0.6rem; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); gap: 12px; }
  .stat-number { font-size: 1.5rem; }
  .stats-strip { padding: 36px 0; }
  .app-badges { flex-direction: column; }
  .section { padding: 44px 0; }
  .step-card { padding: 24px 18px; }
  .tier-card { padding: 24px 18px; }
  .bento-card { padding: 24px 18px; }
  .section-header { margin-bottom: 28px; }
}
</style>
