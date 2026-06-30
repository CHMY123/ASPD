<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <div class="relative">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-light" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input 
            v-model="searchKeyword" 
            @input="handleSearch"
            type="text" 
            placeholder="搜索用户名、邮箱、姓名..." 
            class="pl-10 pr-4 py-2.5 bg-background-secondary border border-border rounded-lg text-sm focus:outline-none focus:border-brand-mint transition-colors w-64"
          />
        </div>
        <select v-model="filterRole" @change="handleSearch" class="px-4 py-2.5 bg-background-secondary border border-border rounded-lg text-sm focus:outline-none focus:border-brand-mint transition-colors">
          <option value="">全部角色</option>
          <option value="student">学生</option>
          <option value="teacher">教师</option>
          <option value="assistant">助教</option>
          <option value="admin">管理员</option>
        </select>
      </div>
      <button @click="showAddModal = true" class="flex items-center gap-2 px-4 py-2.5 bg-brand-mint text-white rounded-lg text-sm font-medium hover:bg-brand-dark transition-colors">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        添加用户
      </button>
    </div>
    
    <div class="bg-background-primary rounded-xl border border-border overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead>
            <tr class="bg-background-secondary text-left text-sm text-text-secondary">
              <th class="px-6 py-4 font-medium">用户名</th>
              <th class="px-6 py-4 font-medium">邮箱</th>
              <th class="px-6 py-4 font-medium">真实姓名</th>
              <th class="px-6 py-4 font-medium">角色</th>
              <th class="px-6 py-4 font-medium">状态</th>
              <th class="px-6 py-4 font-medium">注册时间</th>
              <th class="px-6 py-4 font-medium text-right">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id" class="border-b border-border last:border-b-0 hover:bg-background-dark/50 transition-colors">
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div class="w-8 h-8 rounded-full bg-brand-light flex items-center justify-center">
                    <svg class="w-4 h-4 text-brand-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <span class="text-sm font-medium text-text-primary">{{ user.username }}</span>
                </div>
              </td>
              <td class="px-6 py-4 text-sm text-text-secondary">{{ user.email }}</td>
              <td class="px-6 py-4 text-sm text-text-secondary">{{ user.real_name || '-' }}</td>
              <td class="px-6 py-4">
                <span class="px-2.5 py-1 rounded-full text-xs font-medium" :class="getRoleClass(user.role)">
                  {{ getRoleLabel(user.role) }}
                </span>
              </td>
              <td class="px-6 py-4">
                <span class="flex items-center gap-1.5">
                  <span class="w-2 h-2 rounded-full" :class="user.is_active ? 'bg-success' : 'bg-error'"></span>
                  <span class="text-sm" :class="user.is_active ? 'text-success' : 'text-error'">
                    {{ user.is_active ? '活跃' : '禁用' }}
                  </span>
                </span>
              </td>
              <td class="px-6 py-4 text-sm text-text-secondary">{{ formatTime(user.created_at) }}</td>
              <td class="px-6 py-4">
                <div class="flex items-center justify-end gap-2">
                  <button @click="editUser(user)" class="p-2 text-text-secondary hover:text-brand-mint hover:bg-brand-light/20 rounded-lg transition-colors">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                    </svg>
                  </button>
                  <button @click="confirmDelete(user)" class="p-2 text-text-secondary hover:text-error hover:bg-error/10 rounded-lg transition-colors">
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
      <div class="bg-background-primary rounded-xl w-full max-w-md mx-4 shadow-2xl">
        <div class="flex items-center justify-between p-6 border-b border-border">
          <h3 class="text-lg font-semibold text-text-primary">{{ showEditModal ? '编辑用户' : '添加用户' }}</h3>
          <button @click="closeModal" class="p-1 text-text-light hover:text-text-secondary rounded-lg">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <form @submit.prevent="handleSubmit" class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-text-primary mb-1.5">用户名 *</label>
            <input v-model="formData.username" type="text" required :disabled="showEditModal" class="w-full px-4 py-2.5 bg-background-secondary border border-border rounded-lg text-sm focus:outline-none focus:border-brand-mint transition-colors disabled:opacity-50" />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-text-primary mb-1.5">邮箱 *</label>
            <input v-model="formData.email" type="email" required class="w-full px-4 py-2.5 bg-background-secondary border border-border rounded-lg text-sm focus:outline-none focus:border-brand-mint transition-colors" />
          </div>
          
          <div v-if="!showEditModal">
            <label class="block text-sm font-medium text-text-primary mb-1.5">密码 *</label>
            <input v-model="formData.password" type="password" required class="w-full px-4 py-2.5 bg-background-secondary border border-border rounded-lg text-sm focus:outline-none focus:border-brand-mint transition-colors" />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-text-primary mb-1.5">真实姓名</label>
            <input v-model="formData.real_name" type="text" class="w-full px-4 py-2.5 bg-background-secondary border border-border rounded-lg text-sm focus:outline-none focus:border-brand-mint transition-colors" />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-text-primary mb-1.5">角色 *</label>
            <select v-model="formData.role" required class="w-full px-4 py-2.5 bg-background-secondary border border-border rounded-lg text-sm focus:outline-none focus:border-brand-mint transition-colors">
              <option value="student">学生</option>
              <option value="teacher">教师</option>
              <option value="assistant">助教</option>
              <option value="admin">管理员</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-text-primary mb-1.5">状态</label>
            <div class="flex items-center gap-3">
              <label class="flex items-center gap-2 cursor-pointer">
                <input v-model="formData.is_active" type="radio" :value="true" class="w-4 h-4 text-brand-mint" />
                <span class="text-sm text-text-secondary">活跃</span>
              </label>
              <label class="flex items-center gap-2 cursor-pointer">
                <input v-model="formData.is_active" type="radio" :value="false" class="w-4 h-4 text-brand-mint" />
                <span class="text-sm text-text-secondary">禁用</span>
              </label>
            </div>
          </div>
          
          <div class="flex items-center gap-3 pt-4">
            <button type="button" @click="closeModal" class="flex-1 px-4 py-2.5 border border-border rounded-lg text-sm font-medium text-text-secondary hover:bg-background-dark transition-colors">
              取消
            </button>
            <button type="submit" class="flex-1 px-4 py-2.5 bg-brand-mint text-white rounded-lg text-sm font-medium hover:bg-brand-dark transition-colors">
              {{ showEditModal ? '保存修改' : '添加用户' }}
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
          <p class="text-sm text-text-secondary text-center">确定要删除用户 <span class="font-medium text-text-primary">{{ deletingUser?.username }}</span> 吗？此操作不可撤销。</p>
          
          <div class="flex items-center gap-3 mt-6">
            <button @click="showDeleteConfirm = false" class="flex-1 px-4 py-2.5 border border-border rounded-lg text-sm font-medium text-text-secondary hover:bg-background-dark transition-colors">
              取消
            </button>
            <button @click="deleteUser" class="flex-1 px-4 py-2.5 bg-error text-white rounded-lg text-sm font-medium hover:bg-error-dark transition-colors">
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

const users = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = 10

const searchKeyword = ref('')
const filterRole = ref('')

const showAddModal = ref(false)
const showEditModal = ref(false)
const showDeleteConfirm = ref(false)

const editingUserId = ref(null)
const deletingUser = ref(null)

const formData = ref({
  username: '',
  email: '',
  password: '',
  real_name: '',
  role: 'student',
  is_active: true
})

const totalPages = computed(() => Math.ceil(total.value / pageSize))

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
  return `${date.getFullYear()}/${date.getMonth() + 1}/${date.getDate()}`
}

const fetchUsers = async () => {
  try {
    const params = new URLSearchParams({
      page: currentPage.value,
      page_size: pageSize
    })
    if (searchKeyword.value) params.append('search', searchKeyword.value)
    if (filterRole.value) params.append('role', filterRole.value)
    
    const response = await fetch(`http://localhost:8000/api/admin/users?${params}`, {
      headers: { Authorization: `Bearer ${authStore.accessToken}` }
    })
    
    if (response.ok) {
      users.value = await response.json()
      const countResponse = await fetch(`http://localhost:8000/api/admin/users?${params.toString().replace(/page=\d+&?/, '').replace(/page_size=\d+&?/, '')}`, {
        headers: { Authorization: `Bearer ${authStore.accessToken}` }
      })
      if (countResponse.ok) {
        total.value = (await countResponse.json()).length
      }
    }
  } catch (error) {
    console.error('获取用户失败:', error)
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchUsers()
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    fetchUsers()
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    fetchUsers()
  }
}

const closeModal = () => {
  showAddModal.value = false
  showEditModal.value = false
  editingUserId.value = null
  formData.value = {
    username: '',
    email: '',
    password: '',
    real_name: '',
    role: 'student',
    is_active: true
  }
}

const editUser = (user) => {
  editingUserId.value = user.id
  formData.value = {
    username: user.username,
    email: user.email,
    password: '',
    real_name: user.real_name,
    role: user.role,
    is_active: user.is_active
  }
  showEditModal.value = true
}

const confirmDelete = (user) => {
  deletingUser.value = user
  showDeleteConfirm.value = true
}

const deleteUser = async () => {
  try {
    const response = await fetch(`http://localhost:8000/api/admin/users/${deletingUser.value.id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${authStore.accessToken}` }
    })
    
    if (response.ok) {
      showDeleteConfirm.value = false
      fetchUsers()
    }
  } catch (error) {
    console.error('删除用户失败:', error)
  }
}

const handleSubmit = async () => {
  try {
    const url = showEditModal.value 
      ? `http://localhost:8000/api/admin/users/${editingUserId.value}`
      : 'http://localhost:8000/api/admin/users'
    
    const method = showEditModal.value ? 'PUT' : 'POST'
    
    const data = showEditModal.value 
      ? { ...formData.value, password: undefined }
      : formData.value
    
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${authStore.accessToken}`
      },
      body: JSON.stringify(data)
    })
    
    if (response.ok) {
      closeModal()
      fetchUsers()
    }
  } catch (error) {
    console.error('保存用户失败:', error)
  }
}

fetchUsers()
</script>
