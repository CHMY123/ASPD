<template>
  <aside class="sidebar w-88 bg-white rounded-xl shadow-sm mx-4 my-4 overflow-hidden">
    <div class="sidebar-section p-4 border-b border-border">
      <h3 class="text-sm font-semibold text-text-primary mb-3 flex items-center gap-2">
        <span>📖</span>
        相关知识点
      </h3>
      <ul class="related-list space-y-2">
        <li 
          v-for="(item, index) in chatStore.relatedKnowledge" 
          :key="index"
          @click="handleKnowledgeClick(item.id)"
          class="related-item px-3 py-2 bg-background-secondary rounded-lg hover:bg-brand-mint/10 cursor-pointer transition-colors text-sm text-text-secondary truncate"
          :title="item.title"
        >
          {{ item.title }}
          <span class="text-xs text-accent-orange ml-1">{{ item.source }}</span>
        </li>
        <li v-if="chatStore.relatedKnowledge.length === 0" class="empty-state text-center text-text-light text-sm py-4">
          {{ authStore.isLoggedIn ? '开始问答以查看相关内容' : '登录后开始问答' }}
        </li>
      </ul>
    </div>
    
    <div class="sidebar-section p-4">
      <h3 class="text-sm font-semibold text-text-primary mb-3 flex items-center gap-2">
        <span>💡</span>
        学习推荐
      </h3>
      <ul class="recommendation-list space-y-2">
        <li 
          v-for="(item, index) in learningStore.recommendations" 
          :key="index"
          @click="handleKnowledgeClick(item.id)"
          class="recommendation-item px-3 py-2 bg-background-secondary rounded-lg hover:bg-accent-lavender/10 cursor-pointer transition-colors text-sm text-text-secondary truncate"
          :title="item.title"
        >
          {{ item.title }}
        </li>
        <li v-if="learningStore.recommendations.length === 0" class="empty-state text-center text-text-light text-sm py-4">
          {{ authStore.isLoggedIn ? '暂无推荐内容' : '登录后获取个性化推荐' }}
        </li>
      </ul>
    </div>
  </aside>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
import { useChatStore } from '../stores/chat'
import { useLearningStore } from '../stores/learning'

const authStore = useAuthStore()
const chatStore = useChatStore()
const learningStore = useLearningStore()

const handleKnowledgeClick = async (knowledgeId) => {
  if (!authStore.isLoggedIn) return
  
  try {
    const knowledge = await useLearningStore().getKnowledgeById(knowledgeId)
    if (knowledge) {
      const question = `请详细介绍一下"${knowledge.title}"这个知识点。`
      await chatStore.sendMessage(question)
    }
  } catch (error) {
    console.error('Failed to fetch knowledge:', error)
  }
}
</script>