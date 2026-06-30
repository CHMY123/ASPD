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
            <img src="/scnu_logo.png" alt="华南师范大学" class="w-10 h-10 rounded-lg" />
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
            <!-- 搜索按钮 -->
            <div class="relative" ref="searchContainer">
              <button @click="toggleSearch" class="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-background-secondary hover:bg-background-dark transition-all duration-300 hover:scale-105 hover:shadow-md active:scale-95">
                <svg class="w-4 h-4 text-text-secondary transition-transform duration-300" :class="showSearchPanel ? 'rotate-90' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <span class="text-sm text-text-secondary">搜索</span>
              </button>
              
              <!-- 搜索下拉框 -->
              <transition name="search-panel">
                <div v-if="showSearchPanel" class="absolute right-0 top-full mt-2 w-80 bg-background-primary rounded-xl shadow-2xl border border-border z-50 overflow-hidden backdrop-blur-sm">
                  <div class="p-3">
                    <div class="flex items-center gap-2 px-3 py-2.5 rounded-lg border border-border bg-background-secondary transition-all duration-200 focus-within:border-brand-mint focus-within:ring-0">
                      <svg class="w-4 h-4 text-brand-mint flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                      <input v-model="searchKeyword" @keyup.enter="performSearch" type="text" placeholder="搜索课程、电子书..." class="bg-transparent text-sm text-text-primary placeholder-text-light outline-none w-full" />
                      <button v-if="searchKeyword" @click="searchKeyword = ''" class="text-text-light hover:text-error transition-colors duration-200 hover:rotate-90 transform">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                  </div>
                  <div class="max-h-80 overflow-y-auto scrollbar-thin scrollbar-thumb-brand-mint scrollbar-track-background-secondary">
                    <!-- 搜索结果 -->
                    <div v-if="searchResults.length > 0">
                      <div class="px-3 py-2 text-xs font-medium text-brand-mint bg-brand-light/30 flex items-center gap-2">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        搜索结果
                      </div>
                      <div v-for="(item, index) in searchResults" :key="item.id" @click="goToResult(item)" class="px-4 py-3 hover:bg-brand-light/20 cursor-pointer border-b border-border last:border-b-0 transition-all duration-200 hover:translate-x-1 hover:shadow-sm group" :style="{ animationDelay: `${index * 50}ms` }">
                        <div class="flex items-center gap-3">
                          <div class="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 transition-all duration-200 group-hover:scale-110 group-hover:rotate-3" :class="item.type === 'course' ? 'bg-brand-light' : 'bg-accent-coral/10'">
                            <svg v-if="item.type === 'course'" class="w-4 h-4 text-brand-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                            </svg>
                            <svg v-else class="w-4 h-4 text-accent-coral" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                            </svg>
                          </div>
                          <div class="flex-1 min-w-0">
                            <div class="text-sm font-medium text-text-primary truncate transition-colors duration-200 group-hover:text-brand-mint">{{ item.title }}</div>
                            <div class="text-xs text-text-secondary transition-colors duration-200 group-hover:text-text-primary">{{ item.subtitle }}</div>
                          </div>
                          <svg class="w-4 h-4 text-text-light opacity-0 group-hover:opacity-100 transition-all duration-200 transform group-hover:translate-x-0 -translate-x-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                          </svg>
                        </div>
                      </div>
                    </div>
                    <div v-else-if="searchKeyword" class="px-4 py-8 text-center">
                      <svg class="w-12 h-12 mx-auto mb-2 text-text-light animate-bounce" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <div class="text-sm text-text-secondary">未找到相关结果</div>
                      <div class="text-xs text-text-light mt-1">试试其他关键词</div>
                    </div>
                    <div v-else class="px-4 py-8 text-center">
                      <svg class="w-12 h-12 mx-auto mb-2 text-brand-mint animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                      </svg>
                      <div class="text-sm text-text-secondary">输入关键词开始搜索</div>
                      <div class="text-xs text-text-light mt-1">支持课程、电子书搜索</div>
                    </div>
                  </div>
                </div>
              </transition>
            </div>
            
            <!-- 通知按钮 -->
            <div class="relative" ref="notificationContainer">
              <button @click="toggleNotification" class="relative p-2 rounded-lg hover:bg-background-dark transition-colors">
                <svg class="w-5 h-5 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
                <span v-if="unreadCount > 0" class="absolute top-1 right-1 w-2 h-2 bg-accent-coral rounded-full"></span>
              </button>
              
              <!-- 通知下拉菜单 -->
              <div v-if="showNotificationPanel" class="absolute right-0 top-full mt-2 w-80 bg-background-primary rounded-xl shadow-xl border border-border z-50 overflow-hidden">
                <div class="px-4 py-3 border-b border-border flex items-center justify-between">
                  <h3 class="text-sm font-semibold text-text-primary">通知</h3>
                  <button v-if="unreadCount > 0" @click="markAllRead" class="text-xs text-brand-mint hover:text-brand-dark transition-colors">全部已读</button>
                </div>
                <div class="max-h-80 overflow-y-auto">
                  <div v-if="notifications.length > 0">
                    <div v-for="(notification, index) in notifications" :key="index" @click="handleNotificationClick(notification)" class="px-4 py-3 hover:bg-background-secondary cursor-pointer border-b border-border last:border-b-0 transition-colors" :class="!notification.read ? 'bg-brand-light/30' : ''">
                      <div class="flex items-start gap-3">
                        <div class="w-2 h-2 rounded-full mt-1.5 flex-shrink-0" :class="!notification.read ? 'bg-accent-coral' : 'bg-transparent'"></div>
                        <div class="flex-1 min-w-0">
                          <div class="text-sm text-text-primary">{{ notification.title }}</div>
                          <div class="text-xs text-text-secondary mt-1">{{ notification.time }}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div v-else class="px-4 py-8 text-center text-sm text-text-secondary">
                    暂无通知
                  </div>
                </div>
              </div>
            </div>

            <template v-if="authStore.hasToken">
              <router-link v-if="authStore.user?.role === 'admin'" :to="{ name: 'adminDashboard' }" class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-accent-coral/10 text-accent-coral text-sm font-medium hover:bg-accent-coral/20 transition-colors">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                </svg>
                管理后台
              </router-link>
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
              <img src="/scnu_logo.png" alt="华南师范大学" class="w-10 h-10 rounded-lg" />
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
import { ref, onMounted, onUnmounted, computed } from 'vue';
import { useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth';
import { useCourseStore } from './stores/course';
import { useBookStore } from './stores/book';
import Dashboard from './components/Dashboard.vue';
import CourseList from './components/CourseList.vue';
import BookLibrary from './components/BookLibrary.vue';
import SmartChat from './components/SmartChat.vue';
import UserProfile from './components/UserProfile.vue';
import LoginModal from './components/LoginModal.vue';
import RegisterModal from './components/RegisterModal.vue';

const router = useRouter()
const authStore = useAuthStore();
const courseStore = useCourseStore();
const bookStore = useBookStore();

const mobileMenuOpen = ref(false);
const showLoginModal = ref(false);
const showRegisterModal = ref(false);

// 搜索相关
const showSearchPanel = ref(false);
const searchKeyword = ref('');
const searchResults = ref([]);
const searchContainer = ref(null);

// 通知相关
const showNotificationPanel = ref(false);
const notificationContainer = ref(null);
const notifications = ref([
  { title: '欢迎使用课程管理系统', time: '刚刚', read: false },
  { title: '您有新的课程推荐', time: '10分钟前', read: false },
  { title: '系统维护通知：今晚22:00-24:00', time: '1小时前', read: true },
  { title: '电子书《数据结构》已更新', time: '2小时前', read: true }
]);

const unreadCount = computed(() => notifications.value.filter(n => !n.read).length);

// 点击外部关闭搜索和通知面板
const handleClickOutside = (event) => {
  if (searchContainer.value && !searchContainer.value.contains(event.target)) {
    showSearchPanel.value = false;
  }
  if (notificationContainer.value && !notificationContainer.value.contains(event.target)) {
    showNotificationPanel.value = false;
  }
};

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

// 搜索功能
const toggleSearch = () => {
  showSearchPanel.value = !showSearchPanel.value;
  showNotificationPanel.value = false;
  if (showSearchPanel.value) {
    searchKeyword.value = '';
    searchResults.value = [];
  }
};

const performSearch = async () => {
  if (!searchKeyword.value.trim()) {
    searchResults.value = [];
    return;
  }
  
  const keyword = searchKeyword.value.toLowerCase();
  const results = [];
  
  // 搜索课程
  if (courseStore.allCourses.length === 0) {
    await courseStore.fetchCourses();
  }
  courseStore.allCourses.forEach(course => {
    if (course.name?.toLowerCase().includes(keyword) || 
        course.description?.toLowerCase().includes(keyword) ||
        course.instructor?.toLowerCase().includes(keyword)) {
      results.push({
        id: course.id,
        type: 'course',
        title: course.name,
        subtitle: `${course.instructor || '未知教师'} · ${course.credits || 0}学分`,
        route: 'courses'
      });
    }
  });
  
  // 搜索电子书
  if (bookStore.books.length === 0) {
    await bookStore.fetchBooks();
  }
  bookStore.books.forEach(book => {
    if (book.title?.toLowerCase().includes(keyword) || 
        book.author?.toLowerCase().includes(keyword) ||
        book.category?.toLowerCase().includes(keyword)) {
      results.push({
        id: book.id,
        type: 'book',
        title: book.title,
        subtitle: `${book.author || '未知作者'} · ${book.category || '未分类'}`,
        route: 'library'
      });
    }
  });
  
  searchResults.value = results.slice(0, 8); // 最多显示8条
};

const goToResult = (item) => {
  showSearchPanel.value = false;
  searchKeyword.value = '';
  router.push({ name: item.route });
};

// 通知功能
const toggleNotification = () => {
  showNotificationPanel.value = !showNotificationPanel.value;
  showSearchPanel.value = false;
};

const markAllRead = () => {
  notifications.value.forEach(n => n.read = true);
};

const handleNotificationClick = (notification) => {
  notification.read = true;
  showNotificationPanel.value = false;
};

onMounted(async () => {
  if (authStore.hasToken && !authStore.user) {
    await authStore.fetchUser()
  }
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
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

/* 搜索面板动画 */
.search-panel-enter-active {
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
}

.search-panel-leave-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.search-panel-enter-from {
  opacity: 0;
  transform: translateY(-10px) scale(0.95);
}

.search-panel-leave-to {
  opacity: 0;
  transform: translateY(10px) scale(0.95);
}

/* 自定义滚动条 */
.scrollbar-thin::-webkit-scrollbar {
  width: 4px;
}

.scrollbar-thin::-webkit-scrollbar-track {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 2px;
}

.scrollbar-thin::-webkit-scrollbar-thumb {
  background: #10B981;
  border-radius: 2px;
}

.scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background: #059669;
}
</style>
