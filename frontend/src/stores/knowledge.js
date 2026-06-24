import { defineStore } from 'pinia'
import { ref } from 'vue'
import axios from 'axios'
import { useAuthStore } from './auth'

export const useKnowledgeStore = defineStore('knowledge', () => {
  const searchResults = ref([])
  const knowledgeDetail = ref(null)
  const isLoading = ref(false)

  const searchKnowledge = async (query, course = null, limit = 5) => {
    const authStore = useAuthStore()
    isLoading.value = true
    try {
      const params = { query, limit }
      if (course) params.course = course
      const response = await axios.get('/api/knowledge', {
        params,
        headers: { Authorization: `Bearer ${authStore.accessToken}` }
      })
      searchResults.value = response.data.results
      return response.data
    } finally {
      isLoading.value = false
    }
  }

  const getKnowledgeById = async (knowledgeId) => {
    const authStore = useAuthStore()
    isLoading.value = true
    try {
      const response = await axios.get(`/api/knowledge/${knowledgeId}`, {
        headers: { Authorization: `Bearer ${authStore.accessToken}` }
      })
      knowledgeDetail.value = response.data
      return response.data
    } finally {
      isLoading.value = false
    }
  }

  const importKnowledge = async (folderPath) => {
    const authStore = useAuthStore()
    isLoading.value = true
    try {
      const response = await axios.post('/api/knowledge/import', { folder_path: folderPath }, {
        headers: { Authorization: `Bearer ${authStore.accessToken}` }
      })
      return response.data
    } finally {
      isLoading.value = false
    }
  }

  const updateKnowledge = async (knowledgeId, data) => {
    const authStore = useAuthStore()
    try {
      const response = await axios.put(`/api/knowledge/${knowledgeId}`, data, {
        headers: { Authorization: `Bearer ${authStore.accessToken}` }
      })
      return response.data
    } catch (error) {
      throw error
    }
  }

  const deleteKnowledge = async (knowledgeId) => {
    const authStore = useAuthStore()
    try {
      const response = await axios.delete(`/api/knowledge/${knowledgeId}`, {
        headers: { Authorization: `Bearer ${authStore.accessToken}` }
      })
      return response.data
    } catch (error) {
      throw error
    }
  }

  return {
    searchResults,
    knowledgeDetail,
    isLoading,
    searchKnowledge,
    getKnowledgeById,
    importKnowledge,
    updateKnowledge,
    deleteKnowledge
  }
})