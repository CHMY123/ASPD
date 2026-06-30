<template>
  <div 
    :class="[
      'message flex gap-3',
      message.role === 'user' ? 'justify-end' : 'justify-start'
    ]"
  >
    <div 
      :class="[
        'message-avatar w-10 h-10 rounded-full flex items-center justify-center text-lg flex-shrink-0 overflow-hidden',
        message.role === 'user' ? 'bg-brand-mint text-white' : 'bg-white'
      ]"
    >
      <template v-if="message.role === 'user'">👤</template>
      <img v-else src="/ai.png" alt="AI" class="w-full h-full object-cover" />
    </div>
    
    <div 
      :class="[
        'message-content max-w-[70%] rounded-2xl px-4 py-3',
        message.role === 'user' 
          ? 'bg-brand-mint text-white rounded-br-md' 
          : 'bg-background-secondary text-text-primary rounded-bl-md'
      ]"
    >
      <p class="whitespace-pre-wrap break-words" v-html="formatContent(message.content)"></p>
      
      <div v-if="message.references && message.references.length > 0" class="mt-2 flex flex-wrap gap-1">
        <span 
          v-for="(ref, idx) in message.references.slice(0, 3)" 
          :key="idx"
          class="text-xs px-2 py-1 rounded-full bg-accent-lavender/20 text-accent-lavender"
        >
          {{ ref.source || ref.title }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  message: {
    type: Object,
    required: true
  }
})

const formatContent = (content) => {
  if (!content) return ''
  return content
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/`([^`]+)`/g, '<code class="px-1.5 py-0.5 bg-black/10 rounded text-sm font-mono">$1</code>')
}
</script>