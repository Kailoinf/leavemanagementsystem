import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomePage.vue')
    },
    {
      path: '/students',
      name: 'students',
      component: () => import('../views/StudentsList.vue')
    },
    {
      path: '/leaves',
      name: 'leaves',
      component: () => import('../views/LeavesList.vue')
    },
    {
      path: '/reviewers',
      name: 'reviewers',
      component: () => import('../views/ReviewersList.vue')
    }
  ],
})

export default router
