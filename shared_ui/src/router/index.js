import { createRouter, createWebHistory } from 'vue-router';

import home from '../views/Home.vue';
import tools_all from '../views/ToolsAll.vue';
import tools_potok from '../views/ToolsPotok.vue';
import tools_swarco from '../views/ToolsSwarco.vue';
import tools_peek from '../views/ToolsPeek.vue';
import tools_passport from '../views/ToolsPassport.vue';

const routes = [
  { path: '/', component: home },

  { path: '/tools_all/:toolName', component: tools_all, props: true }, 
  { path: '/tools_all', component: tools_all },

  { path: '/tools_potok/:toolName', component: tools_potok, props: true }, 
  { path: '/tools_potok', component: tools_potok },

  { path: '/tools_swarco/:toolName', component: tools_swarco, props: true }, 
  { path: '/tools_swarco', component: tools_swarco },

  { path: '/tools_peek/:toolName', component: tools_peek, props: true }, 
  { path: '/tools_peek', component: tools_peek },

  { path: '/tools_passport/:toolName', component: tools_passport, props: true }, 
  { path: '/tools_passport', component: tools_passport },
];
const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
