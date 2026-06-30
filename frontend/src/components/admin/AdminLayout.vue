<template>
  <div class="min-h-screen bg-background-main flex">
    <aside class="w-64 bg-background-primary border-r border-border flex flex-col fixed h-screen left-0 top-0 z-40">
      <div class="p-6 border-b border-border">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-brand-mint flex items-center justify-center">
            <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </div>
          <div>
            <h2 class="font-bold text-text-primary">管理后台</h2>
            <p class="text-xs text-text-light">课程管理系统</p>
          </div>
        </div>
      </div>
      
      <nav class="flex-1 p-4 space-y-1">
        <router-link 
          v-for="item in menuItems" 
          :key="item.path"
          :to="item.path"
          class="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all"
          :class="$route.name === item.name ? 'bg-brand-mint text-white' : 'text-text-secondary hover:bg-background-dark hover:text-text-primary'"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path :d="item.icon" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
          </svg>
          {{ item.label }}
        </router-link>
      </nav>
      
      <div class="p-4 border-t border-border">
        <router-link to="/dashboard" class="flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium text-text-secondary hover:bg-background-dark hover:text-text-primary transition-all">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          返回首页
        </router-link>
      </div>
    </aside>
    
    <main class="flex-1 ml-64 p-8">
      <div class="max-w-7xl mx-auto">
        <div class="flex items-center justify-between mb-8">
          <div>
            <h1 class="text-2xl font-bold text-text-primary">{{ pageTitle }}</h1>
            <p class="text-text-secondary mt-1">{{ pageDescription }}</p>
          </div>
          <div class="flex items-center gap-3">
            <span class="px-3 py-1.5 bg-brand-light/30 text-brand-dark text-xs font-medium rounded-full">
              {{ authStore.user?.real_name || '管理员' }}
            </span>
          </div>
        </div>
        
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const route = useRoute()
const authStore = useAuthStore()

const menuItems = [
  { name: 'adminDashboard', path: '/admin/dashboard', label: '系统概览', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
  { name: 'adminUsers', path: '/admin/users', label: '用户管理', icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z' },
  { name: 'adminCourses', path: '/admin/courses', label: '课程管理', icon: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253' },
  { name: 'adminBooks', path: '/admin/books', label: '书籍管理', icon: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253' }
]

const pageTitle = computed(() => {
  const titles = {
    adminDashboard: '系统概览',
    adminUsers: '用户管理',
    adminCourses: '课程管理',
    adminBooks: '书籍管理'
  }
  return titles[route.name] || '管理后台'
})

const pageDescription = computed(() => {
  const descriptions = {
    adminDashboard: '查看系统整体运行数据',
    adminUsers: '管理系统用户账户',
    adminCourses: '管理课程信息',
    adminBooks: '管理电子书库'
  }
  return descriptions[route.name] || ''
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style>
