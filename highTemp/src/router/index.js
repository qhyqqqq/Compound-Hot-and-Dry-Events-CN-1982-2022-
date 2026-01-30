import Vue from 'vue';
import Router from 'vue-router';
import UserLogin from '../components/UserLogin.vue';
import HomePage from '../components/HomePage.vue'

import SpeiShow from '../components/SpeiShow'
import SpiShow from '../components/SpiShow'
import HwmidShow from '../components/HwmidShow.vue'
import HighShow from '../components/HighShow.vue'
import DataManage from '../components/DataManage.vue'
Vue.use(Router);
const router = new Router({
    mode: 'history',
    routes: [


        {
            path: '/login',
            name: 'login',
            component: UserLogin,

        },
        {
            path: '/',

            component: HomePage,
            meta: { requiresAuth: true }, // 添加这一行
            children: [
                {
                    path: '',
                    redirect: 'spi',
                },
                {
                    path: 'spi',
                    name: 'spi',
                    component: SpiShow
                },
                {
                    path: 'spei',
                    name: 'spei',
                    component: SpeiShow
                },
                {
                    path: 'hwmid',
                    name: 'hwmid',
                    component: HwmidShow

                },
                {
                    path: 'high',
                    name: 'high',
                    component: HighShow

                },
                {
                    path: 'data',
                    name: 'data',
                    component: DataManage

                }
         

            ]
        }
    ]
});

router.beforeEach((to, from, next) => {
    const isAuthenticated = isLoggedIn(); // 检查登录状态
    if (to.matched.some(record => record.meta.requiresAuth) && !isAuthenticated) {
        // 如果需要认证但用户未登录，则重定向到登录页

        next('/login');
    } else if (to.path === '/login' && isAuthenticated) {
        // 如果用户已登录但尝试访问登录页，则重定向到主页
        next('/');
    } else {
        // 其他情况正常导航
        next();
    }
});
function isLoggedIn() {

    return localStorage.getItem('isLoggedIn') === 'true'; // 确保返回布尔值
}
export default router;
