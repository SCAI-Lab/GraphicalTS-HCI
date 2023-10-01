import { createApp } from 'vue';






import Vuesax from 'vuesax3';
import 'vuesax3/dist/vuesax.css'; //Vuesax styles
import 'material-icons/iconfont/material-icons.css';





import App from './App.vue';



const app = createApp(App)


app.use(Vuesax, {
    theme:{
      colors:{
        primary:'#5b3cc4',
        success:'rgb(23, 201, 100)',
        danger:'rgb(242, 19, 93)',
        warning:'rgb(255, 130, 0)',
        dark:'rgb(36, 33, 69)',
      }
    }
  })


app.mount('#app')

