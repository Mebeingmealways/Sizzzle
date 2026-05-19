<template>
  <div class="not-found animate-fade-in">
    <div class="not-found-content">
      <div class="error-code">404</div>
      <h1 class="heading-lg">Page not found</h1>
      <p class="text-md text-muted" style="margin-top:8px;max-width:400px;text-align:center">
        The page you&rsquo;re looking for doesn&rsquo;t exist or may have been moved.
      </p>
      <div style="margin-top:28px;display:flex;gap:12px">
        <router-link to="/" class="btn btn-primary">Go Home</router-link>
        <button class="btn btn-outline" @click="$router.back()">Go Back</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.not-found {
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.not-found-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.error-code {
  font-size: 8rem;
  font-weight: 800;
  line-height: 1;
  background: linear-gradient(135deg, var(--color-primary), var(--color-accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

@media (max-width: 480px) {
  .error-code { font-size: 4.5rem; }
  .not-found-content > div { flex-wrap: wrap; justify-content: center; }
}
</style>
