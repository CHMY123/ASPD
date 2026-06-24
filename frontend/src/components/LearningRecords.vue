<template>
  <div class="learning-records">
    <div class="mb-6 flex items-center justify-between">
      <div>
        <h2 class="text-2xl font-semibold text-text-primary">学习记录</h2>
        <p class="text-text-secondary text-sm mt-1">追踪您的学习时长和活动</p>
      </div>
      <div class="flex items-center gap-3">
        <select
          v-model="selectedPeriod"
          class="px-4 py-2.5 border border-border rounded-lg focus:outline-none focus:border-brand-mint focus:ring-2 focus:ring-brand-mint/20 transition-all text-sm bg-white"
        >
          <option value="week">本周</option>
          <option value="month">本月</option>
          <option value="year">本年</option>
          <option value="all">全部</option>
        </select>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-white rounded-xl border border-border p-5">
        <div class="flex items-center justify-between mb-3">
          <div class="w-10 h-10 rounded-lg bg-brand-mint/10 flex items-center justify-center text-xl">📚</div>
          <span class="text-xs text-text-light">总学习时间</span>
        </div>
        <div class="text-2xl font-bold text-text-primary">{{ stats.totalHours }}小时</div>
        <p class="text-xs text-text-light mt-1">{{ stats.totalDays }}天</p>
      </div>

      <div class="bg-white rounded-xl border border-border p-5">
        <div class="flex items-center justify-between mb-3">
          <div class="w-10 h-10 rounded-lg bg-accent-orange/10 flex items-center justify-center text-xl">💬</div>
          <span class="text-xs text-text-light">提问次数</span>
        </div>
        <div class="text-2xl font-bold text-text-primary">{{ stats.questions }}</div>
        <p class="text-xs text-success mt-1">+{{ stats.questionGrowth }}% 较上周</p>
      </div>

      <div class="bg-white rounded-xl border border-border p-5">
        <div class="flex items-center justify-between mb-3">
          <div class="w-10 h-10 rounded-lg bg-accent-lavender/10 flex items-center justify-center text-xl">📖</div>
          <span class="text-xs text-text-light">阅读书籍</span>
        </div>
        <div class="text-2xl font-bold text-text-primary">{{ stats.books }}</div>
        <p class="text-xs text-text-light mt-1">本</p>
      </div>

      <div class="bg-white rounded-xl border border-border p-5">
        <div class="flex items-center justify-between mb-3">
          <div class="w-10 h-10 rounded-lg bg-success/10 flex items-center justify-center text-xl">✅</div>
          <span class="text-xs text-text-light">完成任务</span>
        </div>
        <div class="text-2xl font-bold text-text-primary">{{ stats.completedTasks }}</div>
        <p class="text-xs text-success mt-1">完成率 {{ stats.completionRate }}%</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 bg-white rounded-xl border border-border p-6">
        <h3 class="text-lg font-semibold text-text-primary mb-4">学习时间分布</h3>
        <div class="h-48 flex items-end justify-between gap-2">
          <div 
            v-for="(day, index) in weeklyData" 
            :key="index"
            class="flex-1 flex flex-col items-center gap-2"
          >
            <div 
              class="w-full bg-brand-mint/20 rounded-t-lg transition-all hover:bg-brand-mint/40 cursor-pointer relative group"
              :style="{ height: day.height + '%' }"
            >
              <div class="absolute -top-8 left-1/2 -translate-x-1/2 px-2 py-1 bg-text-primary text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                {{ day.hours }}小时
              </div>
            </div>
            <span class="text-xs text-text-light">{{ day.label }}</span>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-xl border border-border p-6">
        <h3 class="text-lg font-semibold text-text-primary mb-4">学习成就</h3>
        <div class="space-y-3">
          <div 
            v-for="achievement in achievements" 
            :key="achievement.id"
            :class="[
              'flex items-center gap-3 p-3 rounded-xl',
              achievement.unlocked ? 'bg-background-secondary' : 'bg-gray-100 opacity-50'
            ]"
          >
            <div :class="[
              'w-10 h-10 rounded-lg flex items-center justify-center text-xl',
              achievement.unlocked ? achievement.bgClass : 'bg-gray-200'
            ]">
              {{ achievement.icon }}
            </div>
            <div class="flex-1">
              <p class="font-medium text-text-primary">{{ achievement.title }}</p>
              <p class="text-xs text-text-light">{{ achievement.description }}</p>
            </div>
            <svg 
              v-if="achievement.unlocked" 
              class="w-5 h-5 text-success" 
              fill="currentColor" 
              viewBox="0 0 20 20"
            >
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            <span v-else class="text-xs text-text-light">未解锁</span>
          </div>
        </div>
      </div>
    </div>

    <div class="mt-6 bg-white rounded-xl border border-border p-6">
      <h3 class="text-lg font-semibold text-text-primary mb-4">最近活动</h3>
      <div class="space-y-3">
        <div 
          v-for="(activity, index) in recentActivities" 
          :key="index"
          class="flex items-center gap-4 p-4 bg-background-secondary rounded-xl hover:bg-background-dark transition-colors"
        >
          <div :class="[
            'w-10 h-10 rounded-lg flex items-center justify-center text-xl flex-shrink-0',
            activity.type === 'course' ? 'bg-brand-mint/10' :
            activity.type === 'book' ? 'bg-accent-lavender/10' :
            'bg-accent-orange/10'
          ]">
            {{ activity.icon }}
          </div>
          <div class="flex-1">
            <p class="font-medium text-text-primary">{{ activity.title }}</p>
            <p class="text-sm text-text-light">{{ activity.description }}</p>
          </div>
          <span class="text-sm text-text-light">{{ activity.time }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";

const selectedPeriod = ref("week");

const stats = ref({
  totalHours: 128,
  totalDays: 45,
  questions: 156,
  questionGrowth: 12,
  books: 23,
  completedTasks: 48,
  completionRate: 85
});

const weeklyData = ref([
  { label: "周一", hours: 2.5, height: 50 },
  { label: "周二", hours: 4, height: 80 },
  { label: "周三", hours: 1.5, height: 30 },
  { label: "周四", hours: 3, height: 60 },
  { label: "周五", hours: 5, height: 100 },
  { label: "周六", hours: 3.5, height: 70 },
  { label: "周日", hours: 2, height: 40 }
]);

const achievements = ref([
  { id: "1", icon: "🎉", title: "初学者", description: "完成第一次学习", unlocked: true, bgClass: "bg-accent-orange/10" },
  { id: "2", icon: "📚", title: "知识渊博", description: "阅读10本书籍", unlocked: true, bgClass: "bg-accent-lavender/10" },
  { id: "3", icon: "💬", title: "提问达人", description: "提问50次以上", unlocked: true, bgClass: "bg-accent-sky/10" },
  { id: "4", icon: "🔥", title: "连续学习", description: "连续学习7天", unlocked: false, bgClass: "bg-accent-coral/10" },
  { id: "5", icon: "🌟", title: "学习之星", description: "累计学习100小时", unlocked: true, bgClass: "bg-brand-mint/10" }
]);

const recentActivities = ref([
  { id: "1", type: "course", icon: "📚", title: "数据结构学习", description: "学习图论算法章节", time: "2小时前" },
  { id: "2", type: "chat", icon: "💬", title: "智能问答", description: "询问二叉搜索树算法", time: "3小时前" },
  { id: "3", type: "book", icon: "📖", title: "阅读", description: "《算法导论》第3章", time: "昨天" },
  { id: "4", type: "course", icon: "📚", title: "完成操作系统作业", description: "进程调度作业", time: "昨天" },
  { id: "5", type: "chat", icon: "💬", title: "智能问答", description: "询问TCP三次握手", time: "2天前" }
]);
</script>
