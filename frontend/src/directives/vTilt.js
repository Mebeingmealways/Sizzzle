/**
 * v-tilt — Real 3D perspective card with layered depth separation.
 *
 * On hover, the card tilts and inner elements lift off the surface at
 * different z-depths, creating genuine parallax depth.
 *
 * Usage:
 *   <div v-tilt>…</div>
 *   <div v-tilt="{ max: 15, perspective: 600, layers: true }">…</div>
 *
 * When `layers: true`, child elements with [data-depth="1|2|3"] get
 * progressively lifted off the card surface on hover.
 */
export const vTilt = {
  mounted(el, binding) {
    const opts = {
      max: 12,
      perspective: 700,
      scale: 1.02,
      speed: 400,
      layers: true,
      glare: true,
      ...binding.value
    }

    el.style.transition = `transform ${opts.speed}ms cubic-bezier(0.03,0.98,0.52,0.99)`
    el.style.transformStyle = 'preserve-3d'
    el.style.willChange = 'transform'

    // Set up depth layers
    if (opts.layers) {
      const depthEls = el.querySelectorAll('[data-depth]')
      depthEls.forEach(child => {
        child.style.transition = `transform ${opts.speed}ms cubic-bezier(0.03,0.98,0.52,0.99)`
        child.style.willChange = 'transform'
      })
    }

    // Glare overlay
    let glareEl = null
    if (opts.glare) {
      glareEl = document.createElement('div')
      Object.assign(glareEl.style, {
        position: 'absolute',
        inset: '0',
        borderRadius: 'inherit',
        pointerEvents: 'none',
        opacity: '0',
        transition: `opacity ${opts.speed}ms ease`,
        zIndex: '10',
        background: 'linear-gradient(135deg, rgba(255,255,255,0.18), transparent 60%)'
      })
      if (!el.style.position || el.style.position === 'static') {
        el.style.position = 'relative'
      }
      el.style.overflow = 'hidden'
      el.appendChild(glareEl)
    }

    function onMove(e) {
      const rect = el.getBoundingClientRect()
      const x = (e.clientX - rect.left) / rect.width   // 0-1
      const y = (e.clientY - rect.top) / rect.height    // 0-1
      const rotY = (x - 0.5) * opts.max * 2
      const rotX = -(y - 0.5) * opts.max * 2

      el.style.transform = `perspective(${opts.perspective}px) rotateX(${rotX}deg) rotateY(${rotY}deg) scale3d(${opts.scale},${opts.scale},${opts.scale})`

      // Lift layers at different depths
      if (opts.layers) {
        el.querySelectorAll('[data-depth]').forEach(child => {
          const depth = parseInt(child.dataset.depth) || 1
          const liftZ = depth * 18
          const shiftX = (x - 0.5) * depth * -8
          const shiftY = (y - 0.5) * depth * -8
          child.style.transform = `translate3d(${shiftX}px, ${shiftY}px, ${liftZ}px)`
        })
      }

      // Dynamic glare
      if (glareEl) {
        const angle = Math.atan2(y - 0.5, x - 0.5) * (180 / Math.PI) + 90
        glareEl.style.background = `linear-gradient(${angle}deg, rgba(255,255,255,0.2), transparent 55%)`
        glareEl.style.opacity = '1'
      }
    }

    function onLeave() {
      el.style.transform = `perspective(${opts.perspective}px) rotateX(0) rotateY(0) scale3d(1,1,1)`
      if (opts.layers) {
        el.querySelectorAll('[data-depth]').forEach(child => {
          child.style.transform = 'translate3d(0,0,0)'
        })
      }
      if (glareEl) glareEl.style.opacity = '0'
    }

    el.addEventListener('mousemove', onMove)
    el.addEventListener('mouseleave', onLeave)
    el._tiltCleanup = () => {
      el.removeEventListener('mousemove', onMove)
      el.removeEventListener('mouseleave', onLeave)
    }
  },
  unmounted(el) {
    if (el._tiltCleanup) el._tiltCleanup()
  }
}
