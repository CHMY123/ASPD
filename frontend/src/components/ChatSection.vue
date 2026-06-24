<template>
  <section class="chat-section flex-1 flex flex-col bg-white rounded-xl shadow-sm mx-4 my-4 overflow-hidden">
    <div class="chat-messages flex-1 overflow-y-auto p-4 space-y-4">
      <MessageBubble 
        v-for="(message, index) in chatStore.messages" 
        :key="index"
        :message="message"
      />
      
      <div v-if="chatStore.messages.length === 0 && !authStore.isLoggedIn" class="flex flex-col items-center justify-center h-full text-center">
        <div class="text-6xl mb-4">🤖</div>
        <h3 class="text-lg font-semibold text-text-primary mb-2">欢迎使用课程学习知识库问答系统</h3>
        <p class="text-text-secondary text-sm">请先登录，然后随时向我提问</p>
      </div>
      
      <div v-if="chatStore.messages.length === 0 && authStore.isLoggedIn" class="flex flex-col items-center justify-center h-full text-center">
        <div class="text-6xl mb-4">🎯</div>
        <h3 class="text-lg font-semibold text-text-primary mb-2">开始学习之旅</h3>
        <p class="text-text-secondary text-sm">输入您的问题，我将为您提供专业解答</p>
      </div>
    </div>
    
    <ChatInput @send="handleSend" :disabled="!authStore.isLoggedIn || chatStore.isLoading" />
  </section>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
import { useChatStore } from '../stores/chat'
import { useLearningStore } from '../stores/learning'
import MessageBubble from './MessageBubble.vue'
import ChatInput from './ChatInput.vue'

const authStore = useAuthStore()
const chatStore = useChatStore()
const learningStore = useLearningStore()

const handleSend = async (message) => {
  if (!message.trim() || chatStore.isLoading) return
  
  try {
    await chatStore.sendMessage(message.trim())
  } catch (error) {
    console.error('Failed to send message:', error)
    alert('发送消息失败，请稍后重试')
  }
}
</script>