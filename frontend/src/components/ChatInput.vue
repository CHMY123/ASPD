<template>
  <div class="chat-input-container p-4 border-t border-border bg-white">
    <div class="flex gap-3">
      <textarea
        ref="textareaRef"
        v-model="inputText"
        :disabled="disabled"
        :placeholder="disabled ? '请先登录以使用问答功能...' : '输入您的问题...'"
        rows="1"
        class="flex-1 px-4 py-3 bg-background-secondary border border-border rounded-xl resize-none focus:outline-none focus:border-brand-mint focus:ring-2 focus:ring-brand-mint/20 transition-all text-text-primary placeholder:text-text-light"
        @keydown.enter.exact.prevent="handleSend"
        @input="autoResize"
      ></textarea>
      
      <button
        @click="handleSend"
        :disabled="disabled || !inputText.trim()"
        class="px-5 py-3 bg-brand-mint text-white rounded-xl hover:bg-brand-dark disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2 font-medium"
      >
        <span>发送</span>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M22 2L11 13"></path>
          <path d="M22 2L15 22L11 13L2 9L22 2Z"></path>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'

const props = defineProps({
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['send'])

const inputText = ref('')
const textareaRef = ref(null)

const handleSend = () => {
  if (!inputText.value.trim()) return
  emit('send', inputText.value)
  inputText.value = ''
  nextTick(() => {
    if (textareaRef.value) {
      textareaRef.value.style.height = 'auto'
    }
  })
}

const autoResize = () => {
  if (textareaRef.value) {
    textareaRef.value.style.height = 'auto'
    const maxHeight = 120
    const scrollHeight = textareaRef.value.scrollHeight
    textareaRef.value.style.height = Math.min(scrollHeight, maxHeight) + 'px'
  }
}
</script>