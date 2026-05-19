import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import { vTilt } from './directives/vTilt'
import { vMagnetic } from './directives/vMagnetic'
import './assets/main.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)
app.directive('tilt', vTilt)
app.directive('magnetic', vMagnetic)
app.mount('#app')
