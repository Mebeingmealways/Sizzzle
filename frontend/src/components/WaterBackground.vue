<template>
  <div class="water-bg" aria-hidden="true">
    <!-- Mesh gradient blobs -->
    <div class="mesh-layer">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>
      <div class="blob blob-4"></div>
    </div>
    <!-- Dot grid pattern -->
    <svg class="dot-grid" width="100%" height="100%">
      <defs>
        <pattern id="dots" x="0" y="0" width="32" height="32" patternUnits="userSpaceOnUse">
          <circle cx="1" cy="1" r="0.8" fill="currentColor" />
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#dots)" />
    </svg>
    <!-- Top accent line -->
    <div class="top-glow"></div>
  </div>
</template>

<style scoped>
.water-bg {
  position: fixed;
  inset: 0;
  z-index: -1;
  overflow: hidden;
  pointer-events: none;
  background: linear-gradient(
    168deg,
    #F6FBF9 0%,
    #FAFCFB 25%,
    #F0F7F4 50%,
    #FBF8F6 75%,
    #FAFCFB 100%
  );
}

.mesh-layer {
  position: absolute;
  inset: 0;
}

.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  will-change: transform;
}

.blob-1 {
  width: 600px;
  height: 600px;
  top: -15%;
  left: -5%;
  background: radial-gradient(circle, rgba(45, 182, 125, 0.12) 0%, transparent 70%);
  animation: drift1 28s ease-in-out infinite;
}

.blob-2 {
  width: 500px;
  height: 500px;
  top: 10%;
  right: -8%;
  background: radial-gradient(circle, rgba(242, 115, 79, 0.08) 0%, transparent 70%);
  animation: drift2 24s ease-in-out infinite;
}

.blob-3 {
  width: 450px;
  height: 450px;
  bottom: -10%;
  left: 25%;
  background: radial-gradient(circle, rgba(45, 182, 125, 0.07) 0%, transparent 70%);
  animation: drift3 32s ease-in-out infinite;
}

.blob-4 {
  width: 350px;
  height: 350px;
  bottom: 20%;
  right: 15%;
  background: radial-gradient(circle, rgba(242, 115, 79, 0.05) 0%, transparent 70%);
  animation: drift4 26s ease-in-out infinite;
}

.dot-grid {
  position: absolute;
  inset: 0;
  color: rgba(45, 182, 125, 0.07);
  z-index: 1;
}

.top-glow {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, rgba(45, 182, 125, 0.3), rgba(242, 115, 79, 0.2), transparent);
}

@keyframes drift1 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(60px, 40px) scale(1.05); }
  66% { transform: translate(-30px, 20px) scale(0.95); }
}

@keyframes drift2 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(-50px, 30px) scale(0.95); }
  66% { transform: translate(30px, -40px) scale(1.08); }
}

@keyframes drift3 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(40px, -30px) scale(1.1); }
  66% { transform: translate(-60px, 20px) scale(0.93); }
}

@keyframes drift4 {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(-40px, -50px) scale(1.06); }
  66% { transform: translate(50px, 30px) scale(0.97); }
}
</style>
