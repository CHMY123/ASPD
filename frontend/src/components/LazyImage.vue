<template>
  <div class="relative w-full h-full">
    <!-- 占位图 -->
    <div 
      v-if="!loaded && !error" 
      class="absolute inset-0 flex items-center justify-center bg-background-dark rounded-lg"
    >
      <svg class="w-8 h-8 text-text-light animate-pulse" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
    </div>
    
    <!-- 加载错误时显示默认图 -->
    <div 
      v-else-if="error" 
      class="absolute inset-0 flex items-center justify-center bg-background-dark rounded-lg"
    >
      <slot name="fallback">
        <svg class="w-12 h-12 text-text-light" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </slot>
    </div>
    
    <!-- 实际图片 -->
    <img
      ref="imageRef"
      :src="src"
      :alt="alt"
      :class="[
        'w-full h-full object-cover rounded-lg transition-opacity duration-300',
        loaded && !error ? 'opacity-100' : 'opacity-0'
      ]"
      @load="handleLoad"
      @error="handleError"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  src: {
    type: String,
    required: true
  },
  alt: {
    type: String,
    default: ''
  },
  lazy: {
    type: Boolean,
    default: true
  }
});

const emit = defineEmits(['load', 'error']);

const imageRef = ref(null);
const loaded = ref(false);
const error = ref(false);
const observer = ref(null);

const handleLoad = () => {
  loaded.value = true;
  emit('load');
};

const handleError = () => {
  error.value = true;
  emit('error');
};

const loadImage = () => {
  if (imageRef.value && !loaded.value && !error.value) {
    imageRef.value.src = props.src;
  }
};

onMounted(() => {
  if (!props.lazy) {
    loadImage();
    return;
  }

  if ('IntersectionObserver' in window) {
    observer.value = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            loadImage();
            observer.value?.disconnect();
          }
        });
      },
      {
        rootMargin: '50px',
        threshold: 0.1
      }
    );

    if (imageRef.value) {
      observer.value.observe(imageRef.value);
    }
  } else {
    // 不支持IntersectionObserver时直接加载
    loadImage();
  }
});

onUnmounted(() => {
  observer.value?.disconnect();
});
</script>