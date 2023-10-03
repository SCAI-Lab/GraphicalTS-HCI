import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'

import 'element-plus/dist/index.css'


import App from './App.vue'

const app = createApp(App)

app.use(ElementPlus)
app.component(ArrowDown.name, ArrowDown)
app.mount('#app')