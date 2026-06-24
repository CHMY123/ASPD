<template>
  <div class="modal-overlay fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="$emit('close')">
    <div class="modal bg-white rounded-2xl w-full max-w-md mx-4 overflow-hidden shadow-xl">
      <div class="modal-header px-6 py-4 border-b border-border flex items-center justify-between">
        <h2 class="text-lg font-semibold text-text-primary">用户注册</h2>
        <button @click="$emit('close')" class="modal-close text-text-secondary hover:text-text-primary transition-colors">
          &times;
        </button>
      </div>
      
      <div class="modal-body px-6 py-4">
        <form @submit.prevent="handleSubmit">
          <div class="form-group mb-4">
            <label for="username" class="block text-sm font-medium text-text-primary mb-1.5">用户名</label>
            <input 
              v-model="username"
              type="text" 
              id="username" 
              placeholder="请输入用户名"
              class="w-full px-4 py-2.5 border border-border rounded-lg focus:outline-none focus:border-brand-mint focus:ring-2 focus:ring-brand-mint/20 transition-all"
              required
            />
          </div>
          
          <div class="form-group mb-4">
            <label for="email" class="block text-sm font-medium text-text-primary mb-1.5">邮箱</label>
            <input 
              v-model="email"
              type="email" 
              id="email" 
              placeholder="请输入邮箱"
              class="w-full px-4 py-2.5 border border-border rounded-lg focus:outline-none focus:border-brand-mint focus:ring-2 focus:ring-brand-mint/20 transition-all"
              required
            />
          </div>
          
          <div class="form-group mb-4">
            <label for="real_name" class="block text-sm font-medium text-text-primary mb-1.5">真实姓名</label>
            <input 
              v-model="realName"
              type="text" 
              id="real_name" 
              placeholder="请输入真实姓名"
              class="w-full px-4 py-2.5 border border-border rounded-lg focus:outline-none focus:border-brand-mint focus:ring-2 focus:ring-brand-mint/20 transition-all"
              required
            />
          </div>
          
          <div class="form-group mb-4">
            <label for="password" class="block text-sm font-medium text-text-primary mb-1.5">密码</label>
            <input 
              v-model="password"
              type="password" 
              id="password" 
              placeholder="请输入密码（至少6位）"
              class="w-full px-4 py-2.5 border border-border rounded-lg focus:outline-none focus:border-brand-mint focus:ring-2 focus:ring-brand-mint/20 transition-all"
              required
            />
          </div>
          
          <div class="form-group">
            <button 
              type="submit"
              :disabled="isLoading"
              class="w-full py-3 bg-brand-mint text-white rounded-lg hover:bg-brand-dark disabled:opacity-50 disabled:cursor-not-allowed transition-all font-medium"
            >
              {{ isLoading ? '注册中...' : '注册' }}
            </button>
          </div>
          
          <p class="form-link text-center text-text-secondary text-sm mt-4">
            已有账号？
            <a href="#" @click.prevent="$emit('switchToLogin')" class="text-brand-mint hover:underline">
              立即登录
            </a>
          </p>
        </form>
        
        <div v-if="error" class="form-error mt-4 p-3 bg-accent-coral/10 text-accent-coral rounded-lg text-sm">
          {{ error }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'

const authStore = useAuthStore()

const emit = defineEmits(['close', 'switchToLogin', 'registerSuccess'])

const username = ref('')
const email = ref('')
const realName = ref('')
const password = ref('')
const isLoading = ref(false)
const error = ref('')

const handleSubmit = async () => {
  error.value = ''
  
  if (!username.value.trim() || !email.value.trim() || !realName.value.trim() || !password.value) {
    error.value = '请填写所有字段'
    return
  }
  
  if (password.value.length < 8) {
    error.value = '密码至少需要8个字符'
    return
  }
  
  isLoading.value = true
  
  try {
    await authStore.register(username.value.trim(), email.value.trim(), password.value, realName.value.trim())
    emit('registerSuccess')
  } catch (err) {
    error.value = err.response?.data?.detail || err.message || '注册失败，请稍后重试'
  } finally {
    isLoading.value = false
  }
}
</script>