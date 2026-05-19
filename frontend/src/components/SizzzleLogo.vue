<template>
  <div class="logo-wrapper" :class="[size]">
    <div class="logo-glass">
      <div class="logo-inner">
        <img :width="iconSize" :height="iconSize" src="/iconlogo.png" alt="Sizzzle" class="logo-icon-img" />
      </div>
    </div>
    <span v-if="showText" class="logo-text">
      <span class="logo-name">Sizzzle</span>
      <span v-if="showTagline" class="logo-tagline">Home Cooks. Real Taste.</span>
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  size: { type: String, default: 'md' },
  showText: { type: Boolean, default: true },
  showTagline: { type: Boolean, default: false }
})

const iconSize = computed(() => {
  const sizes = { sm: 28, md: 36, lg: 56, xl: 80 }
  return sizes[props.size] || 36
})
</script>

<style scoped>
.logo-wrapper {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  user-select: none;
}

.logo-glass {
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(160deg, rgba(255, 255, 255, 0.7), rgba(255, 255, 255, 0.4));
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow:
    0 4px 16px rgba(45, 182, 125, 0.12),
    inset 0 1px 0 rgba(255, 255, 255, 0.7);
  transition: all 0.35s var(--ease-out-expo, cubic-bezier(0.16, 1, 0.3, 1));
}

.logo-wrapper:hover .logo-glass {
  box-shadow:
    0 6px 24px rgba(45, 182, 125, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  transform: translateY(-2px) scale(1.02);
}

.logo-wrapper.sm .logo-glass {
  width: 40px;
  height: 40px;
  border-radius: 10px;
}

.logo-wrapper.md .logo-glass {
  width: 48px;
  height: 48px;
  border-radius: 12px;
}

.logo-wrapper.lg .logo-glass {
  width: 72px;
  height: 72px;
  border-radius: 18px;
}

.logo-wrapper.xl .logo-glass {
  width: 100px;
  height: 100px;
  border-radius: 24px;
}

.logo-inner {
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-icon-img {
  object-fit: contain;
  border-radius: 4px;
}

.logo-text {
  display: flex;
  flex-direction: column;
}

.logo-name {
  font-family: 'Sekaiwo', 'Yuji Boku', serif;
  font-weight: 400;
  color: #0F1C15;
  line-height: 1;
  letter-spacing: 0.03em;
}

.logo-wrapper.sm .logo-name {
  font-size: 1.125rem;
}

.logo-wrapper.md .logo-name {
  font-size: 1.375rem;
}

.logo-wrapper.lg .logo-name {
  font-size: 2rem;
}

.logo-wrapper.xl .logo-name {
  font-size: 2.75rem;
}

.logo-tagline {
  font-family: 'Inter', sans-serif;
  font-size: 0.65rem;
  color: #536B5C;
  font-weight: 500;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin-top: 4px;
}

.logo-wrapper.lg .logo-tagline,
.logo-wrapper.xl .logo-tagline {
  font-size: 0.875rem;
  margin-top: 4px;
}
</style>
