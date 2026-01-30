import Vue from 'vue'
import App from './App.vue'

import router from './router';



import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import * as echarts from 'echarts';
Vue.prototype.$echarts = echarts

// 导入全局样式
import './assets/css/global.css'

// 导入按钮效果
import { initializeButtonEffects } from './utils/buttonEffects'

// 导入动画效果
import { initializeDialogAnimations } from './utils/dialogAnimation'

// 导入统计分析交互效果
import { initializeChartInteractions } from './utils/chartInteractions'

Vue.config.productionTip = false
Vue.use(ElementUI);

new Vue({
  router,

  render: h => h(App),
}).$mount('#app')

// 初始化全局按钮效果
initializeButtonEffects()

// 初始化全局弹窗动画
initializeDialogAnimations()

// 初始化统计分析图表交互
initializeChartInteractions()
