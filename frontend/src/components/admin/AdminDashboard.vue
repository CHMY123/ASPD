<template>
  <div class="space-y-8">
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6">
      <div v-for="stat in statistics" :key="stat.label" class="bg-background-primary rounded-xl p-6 border border-border hover:border-brand-mint/50 transition-all hover:shadow-md">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-text-secondary">{{ stat.label }}</p>
            <p class="text-2xl font-bold text-text-primary mt-2">{{ stat.value }}</p>
          </div>
          <div class="w-12 h-12 rounded-lg flex items-center justify-center" :class="stat.bgClass">
            <svg class="w-6 h-6" :class="stat.iconClass" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path :d="stat.icon" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
            </svg>
          </div>
        </div>
      </div>
    </div>
    
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 bg-background-primary rounded-xl p-6 border border-border">
        <h3 class="text-lg font-semibold text-text-primary mb-4">最近注册用户</h3>
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead>
              <tr class="text-left text-sm text-text-secondary border-b border-border">
                <th class="pb-3 font-medium">用户名</th>
                <th class="pb-3 font-medium">邮箱</th>
                <th class="pb-3 font-medium">角色</th>
                <th class="pb-3 font-medium">注册时间</th>
                <th class="pb-3 font-medium">状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in recentUsers" :key="user.id" class="border-b border-border last:border-b-0">
                <td class="py-4">
                  <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full bg-brand-light flex items-center justify-center">
                      <svg class="w-4 h-4 text-brand-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                    <span class="text-sm text-text-primary">{{ user.username }}</span>
                  </div>
                </td>
                <td class="py-4 text-sm text-text-secondary">{{ user.email }}</td>
                <td class="py-4">
                  <span class="px-2 py-1 rounded-full text-xs font-medium" :class="getRoleClass(user.role)">
                    {{ getRoleLabel(user.role) }}
                  </span>
                </td>
                <td class="py-4 text-sm text-text-secondary">{{ formatTime(user.created_at) }}</td>
                <td class="py-4">
                  <span class="flex items-center gap-1">
                    <span class="w-2 h-2 rounded-full" :class="user.is_active ? 'bg-success' : 'bg-error'"></span>
                    <span class="text-sm" :class="user.is_active ? 'text-success' : 'text-error'">
                      {{ user.is_active ? '活跃' : '禁用' }}
                    </span>
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <div class="bg-background-primary rounded-xl p-6 border border-border">
        <h3 class="text-lg font-semibold text-text-primary mb-4">角色分布</h3>
        <div class="space-y-4">
          <div v-for="role in roleDistribution" :key="role.name" class="space-y-2">
            <div class="flex items-center justify-between text-sm">
              <span class="text-text-secondary">{{ role.label }}</span>
              <span class="font-medium text-text-primary">{{ role.count }}</span>
            </div>
            <div class="h-2 bg-background-secondary rounded-full overflow-hidden">
              <div class="h-full rounded-full transition-all duration-500" :class="role.bgClass" :style="{ width: role.percentage + '%' }"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="bg-background-primary rounded-xl p-6 border border-border">
        <h3 class="text-lg font-semibold text-text-primary mb-4">最近添加的课程</h3>
        <div class="space-y-4">
          <div v-for="course in recentCourses" :key="course.id" class="flex items-center gap-4 p-4 bg-background-secondary rounded-lg">
              <div class="w-12 h-12 rounded-lg bg-brand-light flex items-center justify-center">
                <svg class="w-6 h-6 text-brand-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-text-primary truncate">{{ course.course_name }}</p>
                <p class="text-xs text-text-secondary mt-1">{{ course.teacher_name }} · {{ course.credits }}学分</p>
              </div>
              <span class="text-xs text-text-light">{{ formatTime(course.created_at) }}</span>
            </div>
        </div>
      </div>
      
      <div class="bg-background-primary rounded-xl p-6 border border-border">
        <h3 class="text-lg font-semibold text-text-primary mb-4">最近添加的书籍</h3>
        <div class="space-y-4">
          <div v-for="book in recentBooks" :key="book.id" class="flex items-center gap-4 p-4 bg-background-secondary rounded-lg">
            <div class="w-12 h-12 rounded-lg bg-accent-coral/10 flex items-center justify-center">
              <svg class="w-6 h-6 text-accent-coral" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium text-text-primary truncate">{{ book.title }}</p>
              <p class="text-xs text-text-secondary mt-1">{{ book.author }} · {{ book.category }}</p>
            </div>
            <span class="text-xs text-text-light">{{ formatTime(book.created_at) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()

const statistics = ref({
  total_users: 0,
  total_students: 0,
  total_teachers: 0,
  total_courses: 0,
  total_books: 0,
  total_conversations: 0
})

const recentUsers = ref([])
const recentCourses = ref([])
const recentBooks = ref([])

const statItems = computed(() => [
  { label: '总用户数', value: statistics.value.total_users, icon: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z', bgClass: 'bg-brand-light', iconClass: 'text-brand-dark' },
  { label: '学生数', value: statistics.value.total_students, icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z', bgClass: 'bg-accent-coral/10', iconClass: 'text-accent-coral' },
  { label: '教师数', value: statistics.value.total_teachers, icon: 'M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z', bgClass: 'bg-blue-100', iconClass: 'text-blue-600' },
  { label: '课程数', value: statistics.value.total_courses, icon: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253', bgClass: 'bg-green-100', iconClass: 'text-green-600' },
  { label: '书籍数', value: statistics.value.total_books, icon: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253', bgClass: 'bg-purple-100', iconClass: 'text-purple-600' },
  { label: '会话数', value: statistics.value.total_conversations, icon: 'M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z', bgClass: 'bg-orange-100', iconClass: 'text-orange-600' }
])

const roleDistribution = computed(() => {
  const total = statistics.value.total_users || 1
  return [
    { name: 'student', label: '学生', count: statistics.value.total_students, percentage: (statistics.value.total_students / total) * 100, bgClass: 'bg-accent-coral' },
    { name: 'teacher', label: '教师', count: statistics.value.total_teachers, percentage: (statistics.value.total_teachers / total) * 100, bgClass: 'bg-blue-500' },
    { name: 'admin', label: '管理员', count: statistics.value.total_users - statistics.value.total_students - statistics.value.total_teachers, percentage: ((statistics.value.total_users - statistics.value.total_students - statistics.value.total_teachers) / total) * 100, bgClass: 'bg-brand-mint' }
  ]
})

const getRoleLabel = (role) => {
  const labels = { student: '学生', teacher: '教师', assistant: '助教', admin: '管理员' }
  return labels[role] || role
}

const getRoleClass = (role) => {
  const classes = {
    student: 'bg-accent-coral/10 text-accent-coral',
    teacher: 'bg-blue-100 text-blue-600',
    assistant: 'bg-orange-100 text-orange-600',
    admin: 'bg-brand-light text-brand-dark'
  }
  return classes[role] || 'bg-background-secondary text-text-secondary'
}

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`
  
  return `${date.getMonth() + 1}/${date.getDate()}`
}

const fetchData = async () => {
  try {
    const response = await fetch('http://localhost:8000/api/admin/statistics', {
      headers: { Authorization: `Bearer ${authStore.accessToken}` }
    })
    if (response.ok) {
      statistics.value = await response.json()
    }
    
    const usersResponse = await fetch('http://localhost:8000/api/admin/users?page=1&page_size=5', {
      headers: { Authorization: `Bearer ${authStore.accessToken}` }
    })
    if (usersResponse.ok) {
      recentUsers.value = await usersResponse.json()
    }
    
    const coursesResponse = await fetch('http://localhost:8000/api/admin/courses?page=1&page_size=5', {
      headers: { Authorization: `Bearer ${authStore.accessToken}` }
    })
    if (coursesResponse.ok) {
      const data = await coursesResponse.json()
      recentCourses.value = data.data || []
    }
    
    const booksResponse = await fetch('http://localhost:8000/api/admin/books?page=1&page_size=5', {
      headers: { Authorization: `Bearer ${authStore.accessToken}` }
    })
    if (booksResponse.ok) {
      const data = await booksResponse.json()
      recentBooks.value = data.data || []
    }
  } catch (error) {
    console.error('获取数据失败:', error)
  }
}

onMounted(fetchData)
</script>
