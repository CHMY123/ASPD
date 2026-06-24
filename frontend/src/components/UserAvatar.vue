<template>
  <div 
    class="flex items-center justify-center rounded-full bg-brand-light text-brand-dark overflow-hidden"
    :class="sizeClasses"
  >
    <LazyImage 
      v-if="avatar" 
      :src="avatar" 
      :alt="name"
      class="w-full h-full object-cover"
    >
      <template #fallback>
        <span class="font-medium" :class="textSizeClasses">{{ initials }}</span>
      </template>
    </LazyImage>
    <span v-else class="font-medium" :class="textSizeClasses">{{ initials }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import LazyImage from './LazyImage.vue';

const props = defineProps({
  name: {
    type: String,
    default: '未知用户'
  },
  avatar: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg', 'xl'].includes(value)
  }
});

const sizeClasses = computed(() => {
  const sizes = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-14 h-14',
    xl: 'w-20 h-20'
  };
  return sizes[props.size];
});

const textSizeClasses = computed(() => {
  const sizes = {
    sm: 'text-xs',
    md: 'text-sm',
    lg: 'text-base',
    xl: 'text-lg'
  };
  return sizes[props.size];
});

const initials = computed(() => {
  const name = props.name.trim();
  if (!name) return '?';
  
  const parts = name.split(' ').filter(p => p);
  if (parts.length >= 2) {
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  }
  return name[0].toUpperCase();
});
</script>