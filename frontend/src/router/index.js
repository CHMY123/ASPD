import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  {
    path: '/',
    name: 'home',
    redirect: '/dashboard'
  },
  {
    path: '/dashboard',
    name: 'dashboard',
    component: () => import('../components/Dashboard.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/courses',
    name: 'courses',
    component: () => import('../components/CourseList.vue'),
    meta: { title: '课程中心' }
  },
  {
    path: '/library',
    name: 'library',
    component: () => import('../components/BookLibrary.vue'),
    meta: { title: '电子书库' }
  },
  {
    path: '/chat',
    name: 'chat',
    component: () => import('../components/SmartChat.vue'),
    meta: { title: '智能问答' }
  },
  {
    path: '/agents',
    name: 'agents',
    component: () => import('../components/AgentWorkflow.vue'),
    meta: { title: '多Agent系统', requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'profile',
    component: () => import('../components/UserProfile.vue'),
    meta: { title: '个人中心', requiresAuth: true }
  },
  {
    path: '/learning',
    name: 'learning',
    component: () => import('../components/LearningRecords.vue'),
    meta: { title: '学习报告' }
  },
  {
    path: '/admin',
    name: 'admin',
    redirect: '/admin/dashboard',
    meta: { requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/dashboard',
    name: 'adminDashboard',
    component: () => import('../components/admin/AdminDashboard.vue'),
    meta: { title: '管理后台', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/users',
    name: 'adminUsers',
    component: () => import('../components/admin/AdminUsers.vue'),
    meta: { title: '用户管理', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/courses',
    name: 'adminCourses',
    component: () => import('../components/admin/AdminCourses.vue'),
    meta: { title: '课程管理', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/admin/books',
    name: 'adminBooks',
    component: () => import('../components/admin/AdminBooks.vue'),
    meta: { title: '书籍管理', requiresAuth: true, requiresAdmin: true }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

router.beforeEach(async (to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 课程管理系统` : '课程管理系统'
  
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth) {
    if (!authStore.hasToken) {
      next({ name: 'dashboard' })
      return
    }
    
    if (!authStore.user) {
      const userData = await authStore.fetchUser()
      
      if (!userData) {
        next({ name: 'dashboard' })
        return
      }
    }
  }
  
  if (to.meta.requiresAdmin) {
    if (!authStore.user || authStore.user.role !== 'admin') {
      next({ name: 'dashboard' })
      return
    }
  }
  
  next()
})

export default router
