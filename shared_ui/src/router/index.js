import { createRouter, createWebHistory } from 'vue-router';

import home from '../views/Home.vue';
import tools_all from '../views/ToolsAll.vue';
import tools_potok from '../views/ToolsPotok.vue';
import tools_swarco from '../views/ToolsSwarco.vue';
import tools_peek from '../views/ToolsPeek.vue';

const routes = [
  { path: '/', component: () => null }, // Заглушка для корневого пути
  { path: '/home', component: home, name: 'home' },

  { path: '/tools_all/:toolName', component: tools_all, props: true, name: 'tools_all' }, 
  { path: '/tools_all', component: tools_all, name: 'tools_all_default' },

  { path: '/tools_potok/:toolName', component: tools_potok, props: true, name: 'tools_potok' }, 
  { path: '/tools_potok', component: tools_potok, name: 'tools_potok_default' },

  { path: '/tools_swarco/:toolName', component: tools_swarco, props: true, name: 'tools_swarco' }, 
  { path: '/tools_swarco', component: tools_swarco, name: 'tools_swarco_default' },

  { path: '/tools_peek/:toolName', component: tools_peek, props: true, name: 'tools_peek' }, 
  { path: '/tools_peek', component: tools_peek, name: 'tools_peek_default' },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  if (to.path === '/') {
    const lastRoute = JSON.parse(localStorage.getItem('lastRoute'));
    console.log('Последний сохраненный маршрут:', lastRoute);

    if (lastRoute) {
      // Перенаправляем на последний сохраненный маршрут
      next({ path: lastRoute.path, query: lastRoute.query, params: lastRoute.params });
    } else {
      // Если сохраненного маршрута нет, перенаправляем на /home
      next('/home');
    }
  } else {
    next();
  }
});

router.afterEach((to) => {
  if (!to.path.startsWith('/login') && !to.path.startsWith('/error')) {
    const lastRoute = {
      path: to.path,
      query: to.query,
      params: to.params,
    };
    localStorage.setItem('lastRoute', JSON.stringify(lastRoute));
    console.log('Сохранено в localStorage:', JSON.stringify(lastRoute));
  }
});

export default router;