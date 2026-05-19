import { onMounted, onUnmounted } from 'vue'

/**
 * Scroll-reveal system using IntersectionObserver.
 * Adds `.revealed` class when elements with `[data-reveal]` enter the viewport.
 *
 * Usage in templates:
 *   <div data-reveal>…</div>
 *   <div data-reveal="slide-left">…</div>
 *   <div data-reveal="scale">…</div>
 *
 * The attribute value maps to CSS classes: .reveal-slide-left, .reveal-scale, etc.
 * Stagger children with data-reveal-stagger on the parent.
 */
export function useScrollReveal() {
  let observer = null

  onMounted(() => {
    observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            entry.target.classList.add('revealed')
            observer.unobserve(entry.target)
          }
        }
      },
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
    )

    // Observe all [data-reveal] elements
    document.querySelectorAll('[data-reveal]').forEach((el) => {
      observer.observe(el)
    })

    // For staggered containers, set --stagger-i on each child
    document.querySelectorAll('[data-reveal-stagger]').forEach((container) => {
      const children = container.querySelectorAll('[data-reveal]')
      children.forEach((child, i) => {
        child.style.setProperty('--stagger-i', i)
      })
    })
  })

  onUnmounted(() => {
    if (observer) observer.disconnect()
  })
}
