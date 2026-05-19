<script setup>
import { ref } from 'vue'
import { RouterView } from 'vue-router'
import WaterBackground from './components/WaterBackground.vue'
import SplashScreen from './components/SplashScreen.vue'

const showSplash = ref(true)
</script>

<template>
  <SplashScreen v-if="showSplash" @complete="showSplash = false" />
  <template v-else>
    <WaterBackground />
    <router-view v-slot="{ Component, route }">
      <transition name="page" mode="out-in">
        <component :is="Component" :key="route.path" />
      </transition>
    </router-view>
  </template>
</template>

<style>
#app {
  position: relative;
  min-height: 100vh;
}
</style>
