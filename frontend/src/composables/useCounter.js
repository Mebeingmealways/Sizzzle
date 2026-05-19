import { ref, onMounted, onUnmounted } from 'vue'

/**
 * Animated counter that counts up when triggered.
 * Returns `display` ref (formatted string) and a `start()` function.
 *
 * Usage:
 *   const { display, start } = useCounter(2500, { prefix: '', suffix: '+', duration: 2000 })
 *   // call start() when element enters viewport
 */
export function useCounter(target, opts = {}) {
  const { duration = 2000, prefix = '', suffix = '', decimals = 0 } = opts
  const display = ref(prefix + '0' + suffix)
  let frame = null

  function start() {
    const startTime = performance.now()
    function tick(now) {
      const elapsed = now - startTime
      const progress = Math.min(elapsed / duration, 1)
      // Ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3)
      const current = eased * target
      display.value = prefix + current.toFixed(decimals).replace(/\B(?=(\d{3})+(?!\d))/g, ',') + suffix
      if (progress < 1) {
        frame = requestAnimationFrame(tick)
      }
    }
    frame = requestAnimationFrame(tick)
  }

  onUnmounted(() => {
    if (frame) cancelAnimationFrame(frame)
  })

  return { display, start }
}
