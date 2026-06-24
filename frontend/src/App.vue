<template>
  <div class="min-h-screen bg-background-main">
    <!-- 登录/注册模态框 -->
    <LoginModal 
      v-if="showLoginModal" 
      @close="showLoginModal = false"
      @switchToRegister="showLoginModal = false; showRegisterModal = true"
      @loginSuccess="handleLoginSuccess"
    />
    <RegisterModal 
      v-if="showRegisterModal" 
      @close="showRegisterModal = false"
      @switchToLogin="showRegisterModal = false; showLoginModal = true"
      @registerSuccess="handleRegisterSuccess"
    />

    <nav class="fixed top-0 left-0 right-0 z-50 bg-background-primary border-b border-border shadow-soft">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-xl bg-brand-mint flex items-center justify-center">
              <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <div>
              <h1 class="text-lg font-bold text-text-primary">课程管理系统</h1>
              <p class="text-xs text-text-light">华南师范大学</p>
            </div>
          </div>

          <div class="hidden md:flex items-center gap-1">
            <router-link v-for="item in navItems" :key="item.id" :to="{ name: item.id }" class="px-4 py-2 rounded-lg text-sm font-medium transition-colors" :class="$route.name === item.id ? 'bg-brand-mint text-white' : 'text-text-secondary hover:bg-background-dark hover:text-text-primary'">
              <svg class="w-4 h-4 inline-block mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path :d="item.icon" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
              </svg>
              {{ item.name }}
            </router-link>
          </div>

          <div class="flex items-center gap-4">
            <button class="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-background-secondary hover:bg-background-dark transition-colors">
              <svg class="w-4 h-4 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <span class="text-sm text-text-secondary">搜索</span>
            </button>
            <button class="relative p-2 rounded-lg hover:bg-background-dark transition-colors">
              <svg class="w-5 h-5 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
              <span class="absolute top-1 right-1 w-2 h-2 bg-accent-coral rounded-full"></span>
            </button>
            
            <template v-if="authStore.hasToken">
              <router-link :to="{ name: 'profile' }" class="flex items-center gap-3 pl-3 border-l border-border">
                <div class="w-8 h-8 rounded-full overflow-hidden">
                  <img v-if="authStore.user?.avatar" :src="authStore.user.avatar" alt="头像" class="w-full h-full object-cover" />
                  <div v-else class="w-full h-full bg-brand-light flex items-center justify-center">
                    <svg class="w-4 h-4 text-brand-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                </div>
                <span class="hidden sm:block text-sm font-medium text-text-primary">{{ authStore.user?.username || '加载中...' }}</span>
              </router-link>
            </template>
            <template v-else>
              <button @click="showLoginModal = true" class="px-4 py-2 bg-brand-mint text-white rounded-lg text-sm font-medium hover:bg-brand-dark transition-colors">
                登录
              </button>
            </template>
          </div>

          <button @click="mobileMenuOpen = !mobileMenuOpen" class="md:hidden p-2 rounded-lg hover:bg-background-dark transition-colors">
            <svg class="w-6 h-6 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </div>

      <div v-if="mobileMenuOpen" class="md:hidden bg-background-primary border-t border-border">
        <div class="px-4 py-3 space-y-1">
          <router-link v-for="item in navItems" :key="item.id" :to="{ name: item.id }" @click="mobileMenuOpen = false" class="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left text-sm font-medium transition-colors" :class="$route.name === item.id ? 'bg-brand-mint text-white' : 'text-text-secondary hover:bg-background-dark'">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path :d="item.icon" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
            </svg>
            {{ item.name }}
          </router-link>
        </div>
      </div>
    </nav>

    <main class="pt-20 pb-8">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </main>

    <footer class="bg-background-primary border-t border-border py-8">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <div class="flex items-center gap-3 mb-4">
              <div class="w-10 h-10 rounded-xl bg-brand-mint flex items-center justify-center">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <div>
                <h3 class="font-semibold text-text-primary">课程管理系统</h3>
                <p class="text-xs text-text-light">华南师范大学</p>
              </div>
            </div>
            <p class="text-sm text-text-secondary">为计算机专业学生提供课程管理、知识检索和智能问答服务。</p>
          </div>
          <div>
            <h4 class="font-semibold text-text-primary mb-4">快速链接</h4>
            <ul class="space-y-2">
              <li><a href="#" @click.prevent="navigateTo('courses')" class="text-sm text-text-secondary hover:text-brand-mint transition-colors">课程中心</a></li>
              <li><a href="#" @click.prevent="navigateTo('library')" class="text-sm text-text-secondary hover:text-brand-mint transition-colors">电子书库</a></li>
              <li><a href="#" @click.prevent="navigateTo('chat')" class="text-sm text-text-secondary hover:text-brand-mint transition-colors">智能问答</a></li>
              <li><a href="#" @click.prevent="navigateTo('profile')" class="text-sm text-text-secondary hover:text-brand-mint transition-colors">个人中心</a></li>
            </ul>
          </div>
          <div>
            <h4 class="font-semibold text-text-primary mb-4">帮助支持</h4>
            <ul class="space-y-2">
              <li><a href="#" class="text-sm text-text-secondary hover:text-brand-mint transition-colors">使用指南</a></li>
              <li><a href="#" class="text-sm text-text-secondary hover:text-brand-mint transition-colors">常见问题</a></li>
              <li><a href="#" class="text-sm text-text-secondary hover:text-brand-mint transition-colors">反馈建议</a></li>
              <li><a href="#" class="text-sm text-text-secondary hover:text-brand-mint transition-colors">联系我们</a></li>
            </ul>
          </div>
          <div>
            <h4 class="font-semibold text-text-primary mb-4">关于我们</h4>
            <ul class="space-y-2">
              <li><a href="#" class="text-sm text-text-secondary hover:text-brand-mint transition-colors">学校介绍</a></li>
              <li><a href="#" class="text-sm text-text-secondary hover:text-brand-mint transition-colors">学院简介</a></li>
              <li><a href="#" class="text-sm text-text-secondary hover:text-brand-mint transition-colors">师资力量</a></li>
              <li><a href="#" class="text-sm text-text-secondary hover:text-brand-mint transition-colors">招生信息</a></li>
            </ul>
          </div>
        </div>
        <div class="border-t border-border mt-8 pt-8 text-center">
          <p class="text-sm text-text-light">© 2024 华南师范大学计算机学院. All rights reserved.</p>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth';
import Dashboard from './components/Dashboard.vue';
import CourseList from './components/CourseList.vue';
import BookLibrary from './components/BookLibrary.vue';
import SmartChat from './components/SmartChat.vue';
import UserProfile from './components/UserProfile.vue';
import LoginModal from './components/LoginModal.vue';
import RegisterModal from './components/RegisterModal.vue';

const router = useRouter()
const authStore = useAuthStore();

const mobileMenuOpen = ref(false);
const showLoginModal = ref(false);
const showRegisterModal = ref(false);

const navItems = ref([
  { id: 'dashboard', name: '首页', icon: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
  { id: 'courses', name: '课程中心', icon: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253' },
  { id: 'library', name: '电子书库', icon: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253' },
  { id: 'chat', name: '智能问答', icon: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z' }
]);

const handleLoginSuccess = () => {
  showLoginModal.value = false;
};

const handleRegisterSuccess = () => {
  showRegisterModal.value = false;
  showLoginModal.value = true;
};

onMounted(async () => {
  if (authStore.hasToken && !authStore.user) {
    await authStore.fetchUser()
  }
});
</script>

<style>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
