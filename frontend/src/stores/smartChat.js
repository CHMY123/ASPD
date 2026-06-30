import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useSmartChatStore = defineStore('smartChat', () => {
  const messages = ref([])
  const threadId = ref(localStorage.getItem('chat_thread_id') || '')
  const conversations = ref([])
  const currentMode = ref('knowledge')
  const initialized = ref(false)
  const pendingQuestion = ref('')

  function generateId() {
    return 'chat_' + Date.now() + '_' + Math.random().toString(36).substr(2, 6)
  }

  function ensureThreadId() {
    if (!threadId.value) {
      setThreadId(generateId())
    }
  }

  function setThreadId(id) {
    threadId.value = id
    localStorage.setItem('chat_thread_id', id)
  }

  function setPendingQuestion(question) {
    pendingQuestion.value = question
  }

  function consumePendingQuestion() {
    const question = pendingQuestion.value
    pendingQuestion.value = ''
    return question
  }

  return {
    messages,
    threadId,
    conversations,
    currentMode,
    initialized,
    pendingQuestion,
    generateId,
    ensureThreadId,
    setThreadId,
    setPendingQuestion,
    consumePendingQuestion
  }
})
