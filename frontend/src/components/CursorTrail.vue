<template>
  <canvas ref="canvas" class="cursor-trail" aria-hidden="true"></canvas>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const canvas = ref(null)
let animFrame = null
let mouseX = -100
let mouseY = -100

const particles = []
const MAX = 50

class Spark {
  constructor(x, y) {
    this.x = x + (Math.random() - 0.5) * 8
    this.y = y + (Math.random() - 0.5) * 8
    this.vx = (Math.random() - 0.5) * 1.5
    this.vy = -(1 + Math.random() * 2.5)
    this.life = 1
    this.decay = 0.02 + Math.random() * 0.03
    this.size = 1.5 + Math.random() * 3
    const hues = [12, 22, 32, 42]
    this.hue = hues[Math.floor(Math.random() * hues.length)]
  }
  update() {
    this.x += this.vx
    this.y += this.vy
    this.vy += 0.04
    this.life -= this.decay
    this.size *= 0.98
  }
  draw(ctx) {
    if (this.life <= 0) return
    const a = this.life * 0.7
    ctx.beginPath()
    ctx.arc(this.x, this.y, Math.max(this.size * this.life, 0.4), 0, Math.PI * 2)
    ctx.fillStyle = `hsla(${this.hue}, 95%, 55%, ${a})`
    ctx.shadowBlur = 8
    ctx.shadowColor = `hsla(${this.hue}, 100%, 60%, ${a * 0.4})`
    ctx.fill()
    ctx.shadowBlur = 0
  }
}

onMounted(() => {
  const cvs = canvas.value
  if (!cvs) return
  const ctx = cvs.getContext('2d')
  let w, h

  function resize() {
    w = cvs.width = window.innerWidth
    h = cvs.height = window.innerHeight
  }
  resize()
  window.addEventListener('resize', resize)

  function onMove(e) {
    mouseX = e.clientX
    mouseY = e.clientY
  }
  function onTouch(e) {
    const t = e.touches[0]
    if (t) { mouseX = t.clientX; mouseY = t.clientY }
  }
  window.addEventListener('mousemove', onMove, { passive: true })
  window.addEventListener('touchstart', onTouch, { passive: true })
  window.addEventListener('touchmove', onTouch, { passive: true })

  let spawnCounter = 0
  function loop() {
    ctx.clearRect(0, 0, w, h)

    // Spawn new sparks at cursor
    spawnCounter++
    if (mouseX > 0 && spawnCounter % 2 === 0) {
      if (particles.length < MAX) {
        particles.push(new Spark(mouseX, mouseY))
      } else {
        const dead = particles.find(p => p.life <= 0)
        if (dead) {
          Object.assign(dead, new Spark(mouseX, mouseY))
        }
      }
    }

    for (const p of particles) {
      p.update()
      p.draw(ctx)
    }

    animFrame = requestAnimationFrame(loop)
  }
  loop()

  cvs._cleanup = () => {
    window.removeEventListener('resize', resize)
    window.removeEventListener('mousemove', onMove)
    window.removeEventListener('touchstart', onTouch)
    window.removeEventListener('touchmove', onTouch)
  }
})

onUnmounted(() => {
  if (animFrame) cancelAnimationFrame(animFrame)
  if (canvas.value?._cleanup) canvas.value._cleanup()
})
</script>

<style scoped>
.cursor-trail {
  position: fixed;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 99998;
}

/* Show on all devices including touch */
</style>
