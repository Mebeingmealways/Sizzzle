<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import lottie from 'lottie-web'

const emit = defineEmits(['complete'])
const phase = ref(0)
const showTitle = ref(false)
const showTagline = ref(false)
const splashFireEl = ref(null)
const timeouts = []

onMounted(() => {
  if (splashFireEl.value) {
    lottie.loadAnimation({ container: splashFireEl.value, renderer: 'svg', loop: true, autoplay: true, path: '/animations/fire.json' })
  }
  timeouts.push(setTimeout(() => phase.value = 1, 50))
  timeouts.push(setTimeout(() => showTitle.value = true, 400))
  timeouts.push(setTimeout(() => phase.value = 2, 700))
  timeouts.push(setTimeout(() => { phase.value = 3; showTagline.value = true }, 1100))
  timeouts.push(setTimeout(() => {
    phase.value = 4
    setTimeout(() => emit('complete'), 500)
  }, 2600))
})

onUnmounted(() => timeouts.forEach(id => clearTimeout(id)))
</script>

<template>
  <div class="splash" :class="'phase-' + phase">
    <div class="bg-glow bg-1"></div>
    <div class="bg-glow bg-2"></div>
    <div class="bg-glow bg-3"></div>

    <div class="splash-core">
      <div class="logo-stage">
        <div class="splash-fire-lottie" ref="splashFireEl"></div>
        <div class="shine-ring"></div>
        <div class="shine-rays"></div>
        <img src="/iconlogo.png" alt="Sizzzle" class="logo-img" />
      </div>

      <div class="brand-title" :class="{ visible: showTitle }">
        <span v-for="(ch, i) in 'SIZZZLE'.split('')" :key="i"
              class="brand-letter" :style="{ '--d': i }">{{ ch }}</span>
      </div>

      <p class="brand-sub" :class="{ visible: showTagline }">Book a Home Cook</p>
    </div>
  </div>
</template>

<style scoped>
@font-face {
  font-family: 'Sekaiwo';
  src: url('/fonts/Sekaiwo-Regular.otf') format('opentype'),
       url('/fonts/Sekaiwo-Regular.ttf') format('truetype');
  font-weight: 400; font-style: normal; font-display: block;
}

.splash {
  position: fixed; inset: 0; z-index: 99999;
  display: flex; align-items: center; justify-content: center;
  background: #FFFAF6;
  perspective: 1200px;
  overflow: hidden;
  transition: opacity 0.5s ease, filter 0.5s ease;
}

.bg-glow {
  position: absolute; border-radius: 50%;
  pointer-events: none; filter: blur(100px); opacity: 0;
  transition: opacity 1s ease;
}
.bg-1 { width: 420px; height: 420px; top: 25%; left: 25%; background: rgba(255, 150, 38, 0.18); }
.bg-2 { width: 300px; height: 300px; bottom: 15%; right: 12%; background: rgba(242, 115, 79, 0.12); }
.bg-3 { width: 260px; height: 260px; top: 8%; right: 25%; background: rgba(255, 206, 51, 0.1); }
.phase-1 .bg-glow, .phase-2 .bg-glow, .phase-3 .bg-glow { opacity: 1; }

.splash-core {
  position: relative; z-index: 2;
  display: flex; flex-direction: column; align-items: center;
  transform-style: preserve-3d;
}

/* ── LOGO: emerge from deep behind ── */
.logo-stage {
  position: relative;
  margin-bottom: 16px;
  transform: translateZ(-600px) scale(0.15);
  opacity: 0;
  filter: blur(24px);
  transition: transform 0.9s cubic-bezier(0.16, 1, 0.3, 1),
              opacity 0.5s ease,
              filter 0.8s ease;
}

.logo-img {
  width: 100px; height: 100px;
  object-fit: contain; border-radius: 24px;
  position: relative; z-index: 2;
  filter: drop-shadow(0 0 0 transparent);
  transition: filter 0.6s ease;
}

.splash-fire-lottie {
  position: absolute;
  inset: -60px;
  z-index: 0;
  opacity: 0;
  transition: opacity 0.6s ease;
  pointer-events: none;
}
.phase-3 .splash-fire-lottie { opacity: 0.6; }

.shine-ring {
  position: absolute; inset: -40px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255, 180, 50, 0.5), rgba(255, 150, 38, 0.15) 40%, transparent 70%);
  opacity: 0;
  transform: scale(0.3);
  transition: opacity 0.5s ease, transform 0.9s cubic-bezier(0.16, 1, 0.3, 1);
}

.shine-rays {
  position: absolute; inset: -80px;
  opacity: 0;
  background: conic-gradient(
    from 0deg,
    transparent 0deg, rgba(255, 200, 50, 0.18) 8deg, transparent 16deg,
    transparent 36deg, rgba(255, 180, 30, 0.12) 44deg, transparent 52deg,
    transparent 72deg, rgba(255, 200, 50, 0.18) 80deg, transparent 88deg,
    transparent 108deg, rgba(255, 180, 30, 0.12) 116deg, transparent 124deg,
    transparent 144deg, rgba(255, 200, 50, 0.18) 152deg, transparent 160deg,
    transparent 180deg, rgba(255, 180, 30, 0.12) 188deg, transparent 196deg,
    transparent 216deg, rgba(255, 200, 50, 0.18) 224deg, transparent 232deg,
    transparent 252deg, rgba(255, 180, 30, 0.12) 260deg, transparent 268deg,
    transparent 288deg, rgba(255, 200, 50, 0.18) 296deg, transparent 304deg,
    transparent 324deg, rgba(255, 180, 30, 0.12) 332deg, transparent 340deg
  );
  border-radius: 50%;
  transition: opacity 0.6s ease, transform 1s ease;
  transform: scale(0.2) rotate(0deg);
}

/* Phase 1: emerge from depth */
.phase-1 .logo-stage,
.phase-2 .logo-stage {
  transform: translateZ(0) scale(1);
  opacity: 1;
  filter: blur(0);
}

/* Phase 2: overshoot settle */
.phase-2 .logo-stage {
  transform: translateZ(30px) scale(1.04);
  transition: transform 0.35s cubic-bezier(0.34, 1.56, 0.64, 1);
}

/* Phase 3: SHINE burst */
.phase-3 .logo-stage {
  transform: translateZ(0) scale(1);
}
.phase-3 .logo-img {
  filter: drop-shadow(0 0 28px rgba(255, 160, 40, 0.8))
          drop-shadow(0 0 70px rgba(242, 115, 79, 0.45))
          drop-shadow(0 0 120px rgba(255, 206, 51, 0.25));
}
.phase-3 .shine-ring {
  opacity: 1;
  transform: scale(1.8);
}
.phase-3 .shine-rays {
  opacity: 1;
  transform: scale(2.2) rotate(30deg);
  animation: ray-rotate 5s linear infinite;
}
@keyframes ray-rotate { to { transform: scale(2.2) rotate(390deg); } }

/* Phase 4: exit */
.phase-4 { opacity: 0; filter: blur(10px); pointer-events: none; }

/* ── TITLE ── */
.brand-title { display: flex; gap: 0.02em; user-select: none; }

.brand-letter {
  font-family: 'Sekaiwo', serif;
  font-size: clamp(2.8rem, 10vw, 5.5rem);
  color: #1a1a1a;
  display: inline-block;
  opacity: 0;
  transform: translateY(28px) scale(0.8);
  filter: blur(5px);
}
.brand-title.visible .brand-letter {
  animation: pop 0.4s cubic-bezier(0.22, 1, 0.36, 1) forwards;
  animation-delay: calc(var(--d) * 0.055s);
}
@keyframes pop {
  0%   { opacity: 0; transform: translateY(28px) scale(0.8); filter: blur(5px); }
  60%  { opacity: 1; transform: translateY(-3px) scale(1.06); filter: blur(0); text-shadow: 0 0 28px rgba(242,115,79,0.55); }
  100% { opacity: 1; transform: translateY(0) scale(1); filter: blur(0); text-shadow: 0 2px 14px rgba(242,115,79,0.12); }
}

/* ── TAGLINE ── */
.brand-sub {
  font-size: clamp(0.65rem, 2.2vw, 0.9rem);
  font-weight: 500; letter-spacing: 0.3em; text-transform: uppercase;
  color: rgba(30, 30, 30, 0.3);
  margin-top: 8px;
  opacity: 0; transform: translateY(10px);
  transition: opacity 0.4s ease, transform 0.4s ease;
}
.brand-sub.visible { opacity: 1; transform: translateY(0); }

@media (max-width: 480px) {
  .logo-img { width: 76px; height: 76px; }
  .brand-letter { font-size: clamp(2rem, 12vw, 3.2rem); }
  .brand-sub { font-size: 0.6rem; letter-spacing: 0.2em; }
}
</style>
