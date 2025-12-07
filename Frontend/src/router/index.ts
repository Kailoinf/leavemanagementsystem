import { createRouter, createWebHistory } from 'vue-router'
import { isAuthenticated } from '../utils/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/admin/create',
      name: 'admin-create',
      component: () => import('../views/AdminCreateView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomePage.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/students',
      name: 'students',
      component: () => import('../views/StudentsList.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/leaves',
      name: 'leaves',
      component: () => import('../views/LeavesList.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/reviewers',
      name: 'reviewers',
      component: () => import('../views/ReviewersList.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/teachers',
      name: 'teachers',
      component: () => import('../views/TeachersList.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/courses',
      name: 'courses',
      component: () => import('../views/CoursesList.vue'),
      meta: { requiresAuth: true }
    }
  ],
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  // 如果路由不需要认证，直接通过
  if (to.meta.requiresAuth === false) {
    // 如果已登录，访问登录页时重定向到首页
    const authenticated = await isAuthenticated()
    if (to.name === 'login' && authenticated) {
      next('/')
      return
    }
    next()
    return
  }

  // 检查是否需要认证的路由
  const requiresAuth = to.meta.requiresAuth !== false

  if (requiresAuth) {
    const authenticated = await isAuthenticated()

    if (!authenticated) {
      // 未登录，重定向到登录页
      next('/login')
      return
    }
  }

  next()
})

export default router
