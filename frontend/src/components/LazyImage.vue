<template>
  <div class="lazy-img-wrap" :style="wrapStyle" ref="wrapEl">
    <img
      v-if="loaded"
      :src="src"
      :alt="alt"
      :class="imgClass"
      class="lazy-img lazy-img--real"
      :style="imgStyle"
      @load="onImgLoad"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  src: { type: String, required: true },
  blur: { type: String, default: '' },
  alt: { type: String, default: '' },
  width: { type: Number, default: 0 },
  height: { type: Number, default: 0 },
  imgClass: { type: String, default: '' },
  imgStyle: { type: [String, Object], default: '' },
  eager: { type: Boolean, default: false }
})

const wrapEl = ref(null)
const loaded = ref(false)
const revealed = ref(false)
let observer = null

const wrapStyle = computed(() => {
  const bg = props.blur ? `background-image:url(${props.blur});background-size:cover;background-position:center;` : ''
  return bg
})

function onImgLoad() {
  revealed.value = true
}

onMounted(() => {
  if (props.eager) {
    loaded.value = true
    return
  }
  observer = new IntersectionObserver(
    ([entry]) => {
      if (entry.isIntersecting) {
        loaded.value = true
        observer.disconnect()
      }
    },
    { rootMargin: '200px' }
  )
  if (wrapEl.value) observer.observe(wrapEl.value)
})

onUnmounted(() => { observer?.disconnect() })
</script>

<style scoped>
.lazy-img-wrap {
  overflow: hidden;
  position: relative;
}
.lazy-img--real {
  transition: opacity 0.4s ease;
}
</style>
