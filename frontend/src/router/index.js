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
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
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
  
  next()
})

export default router
