import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// 导入共享CSS样式
import './styles/common.css'
import './styles/dashboard.css'

const app = createApp(App)

app.use(router)

app.mount('#app')
