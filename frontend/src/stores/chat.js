import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import axios from 'axios'
import { useAuthStore } from './auth'

export const useChatStore = defineStore('chat', () => {
  const messages = ref([])
  const threadId = ref(generateUUID())
  const isLoading = ref(false)
  const relatedKnowledge = ref([])

  function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0
      const v = c === 'x' ? r : (r & 0x3 | 0x8)
      return v.toString(16)
    })
  }

  const sendMessage = async (content) => {
    const authStore = useAuthStore()
    if (!authStore.isLoggedIn) {
      throw new Error('请先登录')
    }

    isLoading.value = true
    messages.value.push({
      role: 'user',
      content,
      timestamp: new Date()
    })

    try {
      const response = await axios.post('/api/chat', {
        message: content,
        thread_id: threadId.value,
        user_id: authStore.currentUser.id
      }, {
        headers: { Authorization: `Bearer ${authStore.accessToken}` }
      })

      messages.value.push({
        role: 'assistant',
        content: response.data.reply,
        references: response.data.references || [],
        timestamp: new Date()
      })

      relatedKnowledge.value = response.data.references || []
      return response.data
    } catch (error) {
      if (error.response?.status === 401) {
        try {
          await authStore.refreshAccessToken()
          return sendMessage(content)
        } catch (refreshError) {
          authStore.logout()
          throw new Error('登录已过期，请重新登录')
        }
      }
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const newConversation = () => {
    messages.value = []
    threadId.value = generateUUID()
    relatedKnowledge.value = []
  }

  const getConversationHistory = async (threadIdToFetch) => {
    const authStore = useAuthStore()
    const response = await axios.get(`/api/chat/${threadIdToFetch}/history`, {
      headers: { Authorization: `Bearer ${authStore.accessToken}` }
    })
    return response.data
  }

  const deleteConversation = async (threadIdToDelete) => {
    const authStore = useAuthStore()
    await axios.delete(`/api/chat/${threadIdToDelete}`, {
      headers: { Authorization: `Bearer ${authStore.accessToken}` }
    })
  }

  return {
    messages,
    threadId,
    isLoading,
    relatedKnowledge,
    sendMessage,
    newConversation,
    getConversationHistory,
    deleteConversation
  }
})