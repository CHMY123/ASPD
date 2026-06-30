<template>
  <div class="book-detail">
    <div class="mb-6 flex items-center gap-4">
      <button
        @click="('back')"
        class="flex items-center gap-2 text-text-secondary hover:text-brand-mint transition-colors"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        返回书架
      </button>
    </div>

    <div class="bg-white rounded-2xl shadow-sm border border-border overflow-hidden">
      <div class="p-6">
        <div class="flex flex-col md:flex-row gap-8">
          <div class="w-48 h-64 bg-background-secondary rounded-xl flex items-center justify-center flex-shrink-0">
            <div class="text-8xl">📚</div>
          </div>
          
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-3">
              <span class="px-3 py-1.5 bg-accent-lavender/10 text-accent-lavender rounded-full text-sm font-medium">
                {{ getCategoryName(book.category) }}
              </span>
            </div>
            <h1 class="text-3xl font-bold text-text-primary mb-2">{{ book.title }}</h1>
            <p class="text-xl text-text-secondary mb-4">{{ book.author }}</p>
            
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div>
                <div class="text-sm text-text-light mb-1">ISBN</div>
                <div class="text-text-primary font-medium">{{ book.isbn }}</div>
              </div>
              <div>
                <div class="text-sm text-text-light mb-1">出版社</div>
                <div class="text-text-primary font-medium">{{ book.publisher }}</div>
              </div>
              <div>
                <div class="text-sm text-text-light mb-1">分类</div>
                <div class="text-text-primary font-medium">{{ getCategoryName(book.category) }}</div>
              </div>
              <div>
                <div class="text-sm text-text-light mb-1">章节数</div>
                <div class="text-text-primary font-medium">{{ chapters.length }} 章</div>
              </div>
            </div>

            <div class="flex items-center gap-3">
              <button class="px-6 py-3 bg-brand-mint text-white rounded-xl hover:bg-brand-dark transition-all font-medium">
                立即阅读
              </button>
              <button class="px-6 py-3 border border-border text-text-primary rounded-xl hover:bg-background-secondary transition-all font-medium flex items-center gap-2">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                收藏
              </button>
            </div>
          </div>
        </div>
      </div>

      <div class="grid md:grid-cols-3">
        <div class="md:col-span-2 p-6 border-r border-border">
          <div class="mb-8">
            <h2 class="text-xl font-semibold text-text-primary mb-4 flex items-center gap-2">
              <svg class="w-5 h-5 text-brand-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              内容简介
            </h2>
            <div class="bg-background-secondary rounded-xl p-4">
              <p class="text-text-secondary leading-relaxed">{{ book.summary }}</p>
            </div>
          </div>

          <div>
            <h2 class="text-xl font-semibold text-text-primary mb-4 flex items-center gap-2">
              <svg class="w-5 h-5 text-brand-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              目录
            </h2>
            <div class="bg-background-secondary rounded-xl p-4">
              <ul class="space-y-2">
                <li v-for="(chapter, index) in chapters" :key="index" class="flex items-center gap-3 py-2 border-b border-border last:border-0">
                  <span class="w-6 h-6 flex items-center justify-center bg-brand-mint/10 text-brand-mint rounded-full text-sm font-medium flex-shrink-0">
                    {{ index + 1 }}
                  </span>
                  <span class="text-text-primary">{{ chapter }}</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        <div class="p-6">
          <div class="bg-background-secondary rounded-xl p-5">
            <h3 class="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
              <svg class="w-5 h-5 text-brand-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              相关课程
            </h3>
            <div class="space-y-3">
              <div
                v-for="course in relatedCourses"
                :key="course.id"
                class="flex items-center justify-between p-3 bg-white rounded-lg cursor-pointer hover:bg-brand-mint/10 transition-colors"
              >
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-lg bg-accent-lavender/10 flex items-center justify-center">📖</div>
                  <div>
                    <h4 class="font-medium text-text-primary">{{ course.name }}</h4>
                    <p class="text-xs text-text-light">{{ course.count }} 本相关书籍</p>
                  </div>
                </div>
                <svg class="w-5 h-5 text-text-light" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </div>

          <div class="mt-4 bg-accent-lavender/10 rounded-xl p-5">
            <h3 class="text-lg font-semibold text-text-primary mb-3 flex items-center gap-2">
              <svg class="w-5 h-5 text-accent-lavender" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              快速问答
            </h3>
            <button
              @click="handleQuickQuestion"
              class="w-full py-3 bg-white border border-border rounded-lg hover:border-brand-mint hover:text-brand-mint transition-all text-left"
            >
              <span class="text-sm text-text-secondary">关于这本书，我可以帮您解答什么问题？</span>
            </button>
          </div>

          <div class="mt-4 bg-background-secondary rounded-xl p-5">
            <h3 class="text-lg font-semibold text-text-primary mb-3 flex items-center gap-2">
              <svg class="w-5 h-5 text-accent-orange" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              同类推荐
            </h3>
            <div class="space-y-3">
              <div
                v-for="rec in recommendations"
                :key="rec.id"
                @click="('select-other', rec)"
                class="flex items-center gap-3 p-3 bg-white rounded-lg cursor-pointer hover:bg-accent-lavender/10 transition-colors"
              >
                <div class="w-12 h-16 bg-background-secondary rounded-lg flex items-center justify-center text-xl">📖</div>
                <div class="flex-1 min-w-0">
                  <h4 class="font-medium text-text-primary truncate">{{ rec.title }}</h4>
                  <p class="text-xs text-text-light">{{ rec.author }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  book: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['back', 'select-other', 'quick-question'])

const categories = [
  { id: '基础理论', name: '基础理论' },
  { id: '系统与网络', name: '系统与网络' },
  { id: '数据库', name: '数据库' },
  { id: '人工智能', name: '人工智能' },
  { id: '编程语言', name: '编程语言' }
]

const relatedCourses = [
  { id: 'cs101', name: '数据结构', count: 12 },
  { id: 'cs201', name: '操作系统', count: 8 }
]

const recommendations = [
  { id: '9', title: '算法设计与分析', author: 'Jon Kleinberg' },
  { id: '10', title: '数据结构基础', author: 'Robert Lafore' }
]

const chapters = computed(() => {
  try {
    const toc = JSON.parse(props.book.table_of_contents)
    return toc.chapters || []
  } catch {
    return ['第1章 引言', '第2章 基础知识', '第3章 核心内容', '第4章 实践应用']
  }
})

const getCategoryName = (categoryId) => {
  const category = categories.find(c => c.id === categoryId)
  return category ? category.name : categoryId
}

const handleQuickQuestion = () => {
  emit('quick-question', props.book)
}
</script>
