/**
 * v-magnetic directive — buttons subtly gravitate toward cursor on hover.
 *
 * Usage: <button v-magnetic>Book</button>
 *        <button v-magnetic="{ strength: 0.35 }">Book</button>
 */
export const vMagnetic = {
  mounted(el, binding) {
    const strength = binding.value?.strength ?? 0.3
    el.style.transition = 'transform 0.3s cubic-bezier(0.03,0.98,0.52,0.99)'

    function onMove(e) {
      const rect = el.getBoundingClientRect()
      const cx = rect.left + rect.width / 2
      const cy = rect.top + rect.height / 2
      const dx = (e.clientX - cx) * strength
      const dy = (e.clientY - cy) * strength
      el.style.transform = `translate(${dx}px, ${dy}px)`
    }

    function onLeave() {
      el.style.transform = 'translate(0, 0)'
    }

    el.addEventListener('mousemove', onMove)
    el.addEventListener('mouseleave', onLeave)
    el._magneticCleanup = () => {
      el.removeEventListener('mousemove', onMove)
      el.removeEventListener('mouseleave', onLeave)
    }
  },
  unmounted(el) {
    if (el._magneticCleanup) el._magneticCleanup()
  }
}
