<template>
  <div class="app-header-wrapper">
    <header class="app-header h-18 bg-white border-b border-border flex items-center justify-between px-6 shadow-sm">
      <div class="header-left flex items-center gap-3">
        <span class="text-2xl">📚</span>
        <h1 class="text-lg font-semibold text-text-primary">课程学习知识库问答系统</h1>
      </div>
      
      <div class="header-right flex items-center gap-4">
        <div v-if="authStore.isLoggedIn" class="user-section flex items-center gap-3">
          <span class="text-text-secondary text-sm">欢迎, {{ authStore.currentUser?.username }}</span>
          <button 
            @click="showLogoutConfirm = true"
            :disabled="isLoggingOut"
            class="px-4 py-2 bg-accent-coral/10 text-accent-coral rounded-lg hover:bg-accent-coral/20 transition-colors text-sm font-medium flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg v-if="isLoggingOut" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            {{ isLoggingOut ? '退出中...' : '退出' }}
          </button>
        </div>
        
        <div v-else class="auth-section flex items-center gap-2">
          <button 
            @click="$emit('openLogin')"
            class="px-4 py-2 bg-brand-mint text-white rounded-lg hover:bg-brand-dark transition-colors text-sm font-medium"
          >
            登录
          </button>
          <button 
            @click="$emit('openRegister')"
            class="px-4 py-2 border border-brand-mint text-brand-mint rounded-lg hover:bg-brand-mint/10 transition-colors text-sm font-medium"
          >
            注册
          </button>
        </div>
      </div>
    </header>

    <!-- 登出确认对话框 -->
    <Teleport to="body">
    <div v-if="showLogoutConfirm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-background-primary rounded-xl p-6 w-full max-w-sm shadow-xl animate-scale-in">
        <div class="text-center">
          <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-accent-coral/10 flex items-center justify-center">
            <svg class="w-8 h-8 text-accent-coral" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-text-primary mb-2">确认退出</h3>
          <p class="text-sm text-text-secondary mb-6">确定要退出登录吗？您的会话将被终止。</p>
          <div class="flex gap-3">
            <button @click="showLogoutConfirm = false" class="flex-1 px-4 py-2.5 border border-border rounded-lg text-text-secondary hover:bg-background-dark transition-colors text-sm font-medium">
              取消
            </button>
            <button @click="confirmLogout" :disabled="isLoggingOut" class="flex-1 px-4 py-2.5 bg-accent-coral text-white rounded-lg hover:bg-accent-coral/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-sm font-medium">
              <svg v-if="isLoggingOut" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ isLoggingOut ? '退出中...' : '退出登录' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useChatStore } from '../stores/chat'

const authStore = useAuthStore()
const chatStore = useChatStore()

const emit = defineEmits(['openLogin', 'openRegister'])

const showLogoutConfirm = ref(false)
const isLoggingOut = ref(false)

const confirmLogout = async () => {
  isLoggingOut.value = true
  
  try {
    await authStore.logout()
    chatStore.newConversation()
    showLogoutConfirm.value = false
    emit('openLogin')
  } catch (error) {
    console.error('Logout failed:', error)
    alert('退出登录失败，请稍后重试')
  } finally {
    isLoggingOut.value = false
  }
}
</script>