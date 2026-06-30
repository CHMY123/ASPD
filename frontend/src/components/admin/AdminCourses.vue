<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div class="relative">
        <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-light" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
        <input 
          v-model="searchKeyword" 
          @input="handleSearch"
          type="text" 
          placeholder="搜索课程名称、教师..." 
          class="pl-10 pr-4 py-2.5 bg-background-secondary border border-border rounded-lg text-sm focus:outline-none focus:border-brand-mint transition-colors w-64"
        />
      </div>
      <button @click="showAddModal = true" class="flex items-center gap-2 px-4 py-2.5 bg-brand-mint text-white rounded-lg text-sm font-medium hover:bg-brand-dark transition-colors">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        添加课程
      </button>
    </div>
    
    <div class="bg-background-primary rounded-xl border border-border overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="bg-background-secondary text-left text-sm text-text-secondary">
              <th class="px-6 py-4 font-medium">课程名称</th>
              <th class="px-6 py-4 font-medium">教师</th>
              <th class="px-6 py-4 font-medium">学分</th>
              <th class="px-6 py-4 font-medium">学期</th>
              <th class="px-6 py-4 font-medium">分类</th>
              <th class="px-6 py-4 font-medium">创建时间</th>
              <th class="px-6 py-4 font-medium text-right">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="course in courses" :key="course.id" class="border-b border-border last:border-b-0 hover:bg-background-dark/50 transition-colors">
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-lg bg-brand-light flex items-center justify-center">
                    <svg class="w-4 h-4 text-brand-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                  </div>
                  <div>
                    <span class="text-sm font-medium text-text-primary">{{ course.name }}</span>
                    <p class="text-xs text-text-light truncate max-w-xs">{{ course.description }}</p>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4 text-sm text-text-secondary">{{ course.instructor }}</td>
              <td class="px-6 py-4">
                <span class="px-2.5 py-1 bg-brand-light/30 text-brand-dark text-xs font-medium rounded-full">{{ course.credits }}学分</span>
              </td>
              <td class="px-6 py-4 text-sm text-text-secondary">{{ course.semester }}</td>
              <td class="px-6 py-4">
                <span class="px-2.5 py-1 bg-background-dark text-text-secondary text-xs font-medium rounded-full">{{ course.category }}</span>
              </td>
              <td class="px-6 py-4 text-sm text-text-secondary">{{ formatTime(course.created_at) }}</td>
              <td class="px-6 py-4">
                <div class="flex items-center justify-end gap-2">
                  <button @click="editCourse(course)" class="p-2 text-text-secondary hover:text-brand-mint hover:bg-brand-light/20 rounded-lg transition-colors">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button @click="confirmDelete(course)" class="p-2 text-text-secondary hover:text-error hover:bg-error/10 rounded-lg transition-colors">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <div v-if="total > pageSize" class="px-6 py-4 border-t border-border flex items-center justify-between">
        <span class="text-sm text-text-secondary">共 {{ total }} 条记录</span>
        <div class="flex items-center gap-2">
          <button @click="prevPage" :disabled="currentPage === 1" class="px-3 py-1.5 border border-border rounded-lg text-sm transition-colors" :class="currentPage === 1 ? 'text-text-light cursor-not-allowed' : 'text-text-secondary hover:bg-background-dark'">
            上一页
          </button>
          <span class="text-sm text-text-secondary">{{ currentPage }} / {{ totalPages }}</span>
          <button @click="nextPage" :disabled="currentPage === totalPages" class="px-3 py-1.5 border border-border rounded-lg text-sm transition-colors" :class="currentPage === totalPages ? 'text-text-light cursor-not-allowed' : 'text-text-secondary hover:bg-background-dark'">
            下一页
          </button>
        </div>
      </div>
    </div>
    
    <div v-if="showAddModal || showEditModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-background-primary rounded-xl w-full max-w-lg mx-4 shadow-2xl">
        <div class="flex items-center justify-between p-6 border-b border-border">
          <h3 class="text-lg font-semibold text-text-primary">{{ showEditModal ? '编辑课程' : '添加课程' }}</h3>
          <button @click="closeModal" class="p-1 text-text-light hover:text-text-secondary rounded-lg">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <form @submit.prevent="handleSubmit" class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-text-primary mb-1.5">课程名称 *</label>
            <input v-model="formData.name" type="text" required class="w-full px-4 py-2.5 bg-background-secondary border border-border rounded-lg text-sm focus:outline-none focus:border-brand-mint transition-colors" />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-text-primary mb-1.5">课程描述</label>
            <textarea v-model="formData.description" rows="3" class="w-full px-4 py-2.5 bg-background-secondary border border-border rounded-lg text-sm focus:outline-none focus:border-brand-mint transition-colors resize-none"></textarea>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-text-primary mb-1.5">教师 *</label>
              <input v-model="formData.instructor" type="text" required class="w-full px-4 py-2.5 bg-background-secondary border border-border rounded-lg text-sm focus:outline-none focus:border-brand-mint transition-colors" />
            </div>
            <div>
              <label class="block text-sm font-medium text-text-primary mb-1.5">学分 *</label>
              <input v-model.number="formData.credits" type="number" min="1" max="10" required class="w-full px-4 py-2.5 bg-background-secondary border border-border rounded-lg text-sm focus:outline-none focus:border-brand-mint transition-colors" />
            </div>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-text-primary mb-1.5">学期</label>
              <input v-model="formData.semester" type="text" placeholder="如：2024-2025学年第一学期" class="w-full px-4 py-2.5 bg-background-secondary border border-border rounded-lg text-sm focus:outline-none focus:border-brand-mint transition-colors" />
            </div>
            <div>
              <label class="block text-sm font-medium text-text-primary mb-1.5">分类</label>
              <input v-model="formData.category" type="text" class="w-full px-4 py-2.5 bg-background-secondary border border-border rounded-lg text-sm focus:outline-none focus:border-brand-mint transition-colors" />
            </div>
          </div>
          
          <div class="flex items-center gap-3 pt-4">
            <button type="button" @click="closeModal" class="flex-1 px-4 py-2.5 border border-border rounded-lg text-sm font-medium text-text-secondary hover:bg-background-dark transition-colors">
              取消
            </button>
            <button type="submit" class="flex-1 px-4 py-2.5 bg-brand-mint text-white rounded-lg text-sm font-medium hover:bg-brand-dark transition-colors">
              {{ showEditModal ? '保存修改' : '添加课程' }}
            </button>
          </div>
        </form>
      </div>
    </div>
    
    <div v-if="showDeleteConfirm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-background-primary rounded-xl w-full max-w-sm mx-4 shadow-2xl">
        <div class="p-6">
          <div class="w-12 h-12 bg-error/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-6 h-6 text-error" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-text-primary text-center mb-2">确认删除</h3>
          <p class="text-sm text-text-secondary text-center">确定要删除课程 <span class="font-medium text-text-primary">{{ deletingCourse?.name }}</span> 吗？此操作不可撤销。</p>
          
          <div class="flex items-center gap-3 mt-6">
            <button @click="showDeleteConfirm = false" class="flex-1 px-4 py-2.5 border border-border rounded-lg text-sm font-medium text-text-secondary hover:bg-background-dark transition-colors">
              取消
            </button>
            <button @click="deleteCourse" class="flex-1 px-4 py-2.5 bg-error text-white rounded-lg text-sm font-medium hover:bg-error-dark transition-colors">
              确认删除
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()

const courses = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = 10

const searchKeyword = ref('')

const showAddModal = ref(false)
const showEditModal = ref(false)
const showDeleteConfirm = ref(false)

const editingCourseId = ref(null)
const deletingCourse = ref(null)

const formData = ref({
  name: '',
  description: '',
  instructor: '',
  credits: 3,
  semester: '',
  category: ''
})

const totalPages = computed(() => Math.ceil(total.value / pageSize))

const formatTime = (time) => {
  if (!time) return ''
  const date = new Date(time)
  return `${date.getFullYear()}/${date.getMonth() + 1}/${date.getDate()}`
}

const fetchCourses = async () => {
  try {
    const params = new URLSearchParams({
      page: currentPage.value,
      page_size: pageSize
    })
    if (searchKeyword.value) params.append('search', searchKeyword.value)
    
    const response = await fetch(`http://localhost:8000/api/admin/courses?${params}`, {
      headers: { Authorization: `Bearer ${authStore.accessToken}` }
    })
    
    if (response.ok) {
      const data = await response.json()
      courses.value = data.data || []
      total.value = data.total || 0
    }
  } catch (error) {
    console.error('获取课程失败:', error)
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchCourses()
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    fetchCourses()
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    fetchCourses()
  }
}

const closeModal = () => {
  showAddModal.value = false
  showEditModal.value = false
  editingCourseId.value = null
  formData.value = {
    name: '',
    description: '',
    instructor: '',
    credits: 3,
    semester: '',
    category: ''
  }
}

const editCourse = (course) => {
  editingCourseId.value = course.id
  formData.value = {
    name: course.name,
    description: course.description,
    instructor: course.instructor,
    credits: course.credits,
    semester: course.semester,
    category: course.category
  }
  showEditModal.value = true
}

const confirmDelete = (course) => {
  deletingCourse.value = course
  showDeleteConfirm.value = true
}

const deleteCourse = async () => {
  try {
    const response = await fetch(`http://localhost:8000/api/admin/courses/${deletingCourse.value.id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${authStore.accessToken}` }
    })
    
    if (response.ok) {
      showDeleteConfirm.value = false
      fetchCourses()
    }
  } catch (error) {
    console.error('删除课程失败:', error)
  }
}

const handleSubmit = async () => {
  try {
    const url = showEditModal.value 
      ? `http://localhost:8000/api/admin/courses/${editingCourseId.value}`
      : 'http://localhost:8000/api/admin/courses'
    
    const method = showEditModal.value ? 'PUT' : 'POST'
    
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${authStore.accessToken}`
      },
      body: JSON.stringify(formData.value)
    })
    
    if (response.ok) {
      closeModal()
      fetchCourses()
    }
  } catch (error) {
    console.error('保存课程失败:', error)
  }
}

fetchCourses()
</script>
