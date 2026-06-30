<template>
  <div class="dashboard">
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-2xl font-semibold text-text-primary">学习概览</h2>
        <p class="text-sm text-text-secondary mt-1">欢迎回来，{{ userName }}！今天也要加油学习哦</p>
      </div>
      <div class="flex items-center gap-3">
        <span class="text-sm text-text-secondary">{{ currentDate }}</span>
      </div>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-gradient-to-br from-brand-mint to-brand-dark rounded-xl p-5 text-white">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-white/80 text-sm">今日学习</p>
            <p class="text-2xl font-semibold mt-1">45分钟</p>
          </div>
          <div class="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
      </div>
      <div class="bg-background-primary border border-border rounded-xl p-5 shadow-soft">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-text-secondary text-sm">本周课程</p>
            <p class="text-2xl font-semibold text-text-primary mt-1">8节</p>
          </div>
          <div class="w-12 h-12 rounded-full bg-accent-lavender/30 flex items-center justify-center">
            <svg class="w-6 h-6 text-accent-lavender" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        </div>
      </div>
      <div class="bg-background-primary border border-border rounded-xl p-5 shadow-soft">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-text-secondary text-sm">获得学分</p>
            <p class="text-2xl font-semibold text-text-primary mt-1">78</p>
          </div>
          <div class="w-12 h-12 rounded-full bg-accent-coral/30 flex items-center justify-center">
            <svg class="w-6 h-6 text-accent-coral" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
            </svg>
          </div>
        </div>
      </div>
      <div class="bg-background-primary border border-border rounded-xl p-5 shadow-soft">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-text-secondary text-sm">学习成就</p>
            <p class="text-2xl font-semibold text-text-primary mt-1">4/6</p>
          </div>
          <div class="w-12 h-12 rounded-full bg-accent-orange/30 flex items-center justify-center">
            <svg class="w-6 h-6 text-accent-orange" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2">
        <div class="bg-background-primary border border-border rounded-xl p-6 shadow-soft">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-text-primary">学习进度</h3>
            <button class="text-sm text-brand-mint hover:text-brand-dark transition-colors">查看全部</button>
          </div>
          <div class="space-y-4">
            <div v-for="course in recentCourses" :key="course.id" class="flex items-center gap-4 p-3 rounded-lg hover:bg-background-secondary transition-colors cursor-pointer">
              <div class="w-16 h-16 rounded-xl bg-gradient-to-br from-brand-light to-brand-mint/30 flex items-center justify-center">
                <svg class="w-8 h-8 text-brand-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <div class="flex-1">
                <div class="flex items-center justify-between mb-2">
                  <h4 class="font-medium text-text-primary">{{ course.name }}</h4>
                  <span class="text-sm" :class="course.progress === 100 ? 'text-brand-mint' : 'text-text-secondary'">{{ course.progress }}%</span>
                </div>
                <div class="w-full bg-background-secondary rounded-full h-2">
                  <div class="h-2 rounded-full transition-all duration-500" :class="course.progress === 100 ? 'bg-brand-mint' : 'bg-brand-light'" :style="{ width: course.progress + '%' }"></div>
                </div>
                <p class="text-xs text-text-light mt-2">{{ course.teacher }} · {{ course.hours }}学时</p>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-background-primary border border-border rounded-xl p-6 shadow-soft mt-6">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-text-primary">最近学习</h3>
          </div>
          <div class="space-y-3">
            <div v-for="record in recentRecords" :key="record.id" class="flex items-center gap-4 p-3 rounded-lg hover:bg-background-secondary transition-colors">
              <div class="w-10 h-10 rounded-lg flex items-center justify-center" :class="record.type === 'course' ? 'bg-brand-light' : 'bg-accent-lavender/30'">
                <svg v-if="record.type === 'course'" class="w-5 h-5 text-brand-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <svg v-else class="w-5 h-5 text-accent-lavender" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <div class="flex-1">
                <p class="text-sm font-medium text-text-primary">{{ record.title }}</p>
                <p class="text-xs text-text-light">{{ record.description }} · {{ record.time }}</p>
              </div>
              <span class="text-xs text-text-light">{{ record.duration }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="space-y-6">
        <div class="bg-background-primary border border-border rounded-xl p-6 shadow-soft">
          <h3 class="text-lg font-semibold text-text-primary mb-4">快捷入口</h3>
          <div class="grid grid-cols-2 gap-3">
            <button
              v-for="action in quickActions"
              :key="action.id"
              type="button"
              @click="handleQuickAction(action)"
              class="flex flex-col items-center p-4 rounded-xl hover:bg-background-secondary transition-colors cursor-pointer active:scale-95"
            >
              <div class="w-12 h-12 rounded-full flex items-center justify-center mb-2" :class="action.bgColor">
                <svg class="w-6 h-6" :class="action.iconColor" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path :d="action.icon" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
                </svg>
              </div>
              <span class="text-xs font-medium text-text-primary">{{ action.name }}</span>
            </button>
          </div>
        </div>

        <div class="bg-background-primary border border-border rounded-xl p-6 shadow-soft">
          <h3 class="text-lg font-semibold text-text-primary mb-4">推荐问题</h3>
          <div class="space-y-2">
            <button
              v-for="question in recommendedQuestions"
              :key="question"
              type="button"
              @click="askRecommendedQuestion(question)"
              class="w-full text-left px-3 py-2 rounded-lg hover:bg-background-secondary transition-colors text-sm text-text-secondary cursor-pointer"
            >
              <svg class="w-4 h-4 inline-block mr-2 text-brand-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ question }}
            </button>
          </div>
        </div>

        <div class="bg-gradient-to-br from-accent-lavender to-accent-lavender/50 rounded-xl p-6 text-white">
          <h3 class="text-lg font-semibold mb-2">学习提醒</h3>
          <p class="text-sm text-white/80 mb-4">您有2门课程即将到期，请及时完成学习</p>
          <div class="space-y-2">
            <div class="flex items-center justify-between bg-white/10 rounded-lg px-3 py-2">
              <span class="text-sm">数据结构</span>
              <span class="text-xs bg-white/20 px-2 py-1 rounded-full">3天</span>
            </div>
            <div class="flex items-center justify-between bg-white/10 rounded-lg px-3 py-2">
              <span class="text-sm">操作系统</span>
              <span class="text-xs bg-white/20 px-2 py-1 rounded-full">7天</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import { useSmartChatStore } from '../stores/smartChat';

const router = useRouter();
const authStore = useAuthStore();
const smartChatStore = useSmartChatStore();

const userName = computed(() => {
  return authStore.user?.real_name || authStore.user?.username || '同学';
});

const currentDate = computed(() => {
  const now = new Date();
  return now.getFullYear() + '年' + (now.getMonth() + 1) + '月' + now.getDate() + '日';
});

const recentCourses = ref([
  { id: '1', name: '数据结构', teacher: '李老师', hours: 64, progress: 85 },
  { id: '2', name: '操作系统', teacher: '王老师', hours: 64, progress: 60 },
  { id: '3', name: '计算机网络', teacher: '张老师', hours: 48, progress: 100 }
]);

const recentRecords = ref([
  { id: '1', type: 'course', title: '数据结构', description: '学习了第7章 图算法', time: '今天', duration: '45分钟' },
  { id: '2', type: 'chat', title: '智能问答', description: '提问: TCP三次握手', time: '今天', duration: '10分钟' },
  { id: '3', type: 'course', title: '操作系统', description: '学习了第4章 进程管理', time: '昨天', duration: '60分钟' }
]);

const quickActions = ref([
  { id: 'courses', name: '课程中心', route: 'courses', icon: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253', bgColor: 'bg-brand-light', iconColor: 'text-brand-dark' },
  { id: 'library', name: '电子书库', route: 'library', icon: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253', bgColor: 'bg-accent-lavender/30', iconColor: 'text-accent-lavender' },
  { id: 'chat', name: '智能问答', route: 'chat', icon: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z', bgColor: 'bg-accent-coral/30', iconColor: 'text-accent-coral' },
  { id: 'learning', name: '学习报告', route: 'learning', icon: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z', bgColor: 'bg-accent-sky/30', iconColor: 'text-accent-sky' }
]);

const handleQuickAction = (action) => {
  router.push({ name: action.route });
};

const askRecommendedQuestion = (question) => {
  smartChatStore.setPendingQuestion(question);
  router.push({ name: 'chat' });
};

const recommendedQuestions = ref([
  '什么是时间复杂度和空间复杂度？',
  '操作系统中的进程和线程有什么区别？',
  'TCP三次握手的过程是怎样的？'
]);
</script>
