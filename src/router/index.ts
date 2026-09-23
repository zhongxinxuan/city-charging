import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
    },
    {
      path: '/overview',
      name: 'overview',
      component: () => import('../views/DataOverviewView.vue'),
    },
  ],
})

export default router
