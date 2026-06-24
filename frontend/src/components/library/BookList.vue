<template>
  <div class="library">
    <div class="mb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
      <div>
        <h2 class="text-2xl font-semibold text-text-primary">电子书库</h2>
        <p class="text-text-secondary text-sm mt-1">浏览和检索专业电子书籍</p>
      </div>
      <div class="flex items-center gap-3">
        <div class="relative">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索书籍..."
            class="w-64 pl-10 pr-4 py-2.5 border border-border rounded-lg focus:outline-none focus:border-brand-mint focus:ring-2 focus:ring-brand-mint/20 transition-all text-sm"
          />
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-text-light" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <select
          v-model="selectedCategory"
          class="px-4 py-2.5 border border-border rounded-lg focus:outline-none focus:border-brand-mint focus:ring-2 focus:ring-brand-mint/20 transition-all text-sm bg-white"
        >
          <option value="all">全部分类</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
        </select>
      </div>
    </div>

    <div class="mb-6">
      <div class="flex items-center gap-2 flex-wrap">
        <span class="text-sm font-medium text-text-secondary">按课程关联：</span>
        <button
          v-for="course in relatedCourses"
          :key="course.id"
          @click="filterByCourse(course)"
          :class="[
            'px-4 py-2 rounded-full text-sm font-medium transition-all',
            selectedCourse?.id === course.id
              ? 'bg-brand-mint text-white'
              : 'bg-background-secondary text-text-secondary hover:bg-background-dark'
          ]"
        >
          {{ course.name }}
        </button>
        <button
          v-if="selectedCourse"
          @click="selectedCourse = null"
          class="px-3 py-2 text-sm text-accent-coral hover:bg-accent-coral/10 rounded-full transition-all"
        >
          清除筛选
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      <div
        v-for="book in filteredBooks"
        :key="book.id"
        @click="selectBook(book)"
        class="book-card bg-white rounded-xl border border-border overflow-hidden cursor-pointer hover:shadow-medium hover:border-brand-mint/30 transition-all group"
      >
        <div class="aspect-[3/4] bg-background-secondary relative overflow-hidden">
          <div class="absolute inset-0 flex items-center justify-center text-6xl">📚</div>
          <div class="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
        </div>
        <div class="p-4">
          <div class="flex items-center gap-2 mb-2">
            <span class="text-xs px-2 py-1 bg-accent-lavender/10 text-accent-lavender rounded-full">
              {{ getCategoryName(book.category) }}
            </span>
          </div>
          <h3 class="text-lg font-semibold text-text-primary mb-1 line-clamp-1 group-hover:text-brand-mint transition-colors">
            {{ book.title }}
          </h3>
          <p class="text-sm text-text-secondary mb-3">{{ book.author }}</p>
          <div class="flex items-center justify-between">
            <span class="text-xs text-text-light">{{ book.publisher }}</span>
            <svg class="w-5 h-5 text-text-light group-hover:text-brand-mint group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <div v-if="filteredBooks.length === 0" class="text-center py-16">
      <div class="text-6xl mb-4">📖</div>
      <h3 class="text-lg font-semibold text-text-primary mb-2">暂无书籍</h3>
      <p class="text-text-secondary text-sm">{{ searchQuery ? '未找到匹配的书籍' : '电子书库正在建设中' }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const emit = defineEmits(['select-book'])

const categories = [
  { id: 'data-structure', name: '数据结构' },
  { id: 'algorithm', name: '算法设计' },
  { id: 'os', name: '操作系统' },
  { id: 'network', name: '计算机网络' },
  { id: 'database', name: '数据库原理' },
  { id: 'ai', name: '人工智能' },
  { id: 'programming', name: '编程语言' }
]

const relatedCourses = [
  { id: 'cs101', name: '数据结构', count: 12 },
  { id: 'cs102', name: '算法设计', count: 8 },
  { id: 'cs201', name: '操作系统', count: 10 },
  { id: 'cs202', name: '计算机网络', count: 6 }
]

const books = ref([
  {
    id: '1',
    title: '数据结构与算法分析',
    author: 'Mark Allen Weiss',
    publisher: '机械工业出版社',
    isbn: '978-7-111-22706-9',
    category: 'data-structure',
    summary: '本书采用面向对象的观点，详细介绍了各种数据结构的设计和实现。',
    cover_url: '',
    table_of_contents: '{"chapters": ["引论", "链表", "栈和队列", "树", "散列"]}'
  },
  {
    id: '2',
    title: '算法导论',
    author: 'Thomas H. Cormen',
    publisher: 'MIT Press',
    isbn: '978-0-262-03384-8',
    category: 'algorithm',
    summary: '算法领域的经典教材，全面介绍了常用算法的设计与分析方法。',
    cover_url: '',
    table_of_contents: '{"chapters": ["算法基础", "分治策略", "动态规划", "贪心算法"]}'
  },
  {
    id: '3',
    title: '深入理解计算机系统',
    author: 'Randal E. Bryant',
    publisher: '机械工业出版社',
    isbn: '978-7-111-54493-7',
    category: 'os',
    summary: '从程序员的视角详细阐述计算机系统的本质概念。',
    cover_url: '',
    table_of_contents: '{"chapters": ["计算机系统漫游", "信息的表示和处理", "程序的机器级表示"]}'
  },
  {
    id: '4',
    title: '操作系统概念',
    author: 'Abraham Silberschatz',
    publisher: 'John Wiley & Sons',
    isbn: '978-1-119-32176-7',
    category: 'os',
    summary: '操作系统领域的经典教材，涵盖操作系统的基本概念和原理。',
    cover_url: '',
    table_of_contents: '{"chapters": ["操作系统概述", "进程管理", "内存管理", "文件系统"]}'
  },
  {
    id: '5',
    title: '计算机网络：自顶向下方法',
    author: 'James F. Kurose',
    publisher: 'Pearson',
    isbn: '978-0-13-359414-0',
    category: 'network',
    summary: '采用自顶向下方法讲解计算机网络的原理和协议。',
    cover_url: '',
    table_of_contents: '{"chapters": ["应用层", "运输层", "网络层", "数据链路层"]}'
  },
  {
    id: '6',
    title: '数据库系统概念',
    author: 'Abraham Silberschatz',
    publisher: 'McGraw-Hill',
    isbn: '978-1-259-66103-4',
    category: 'database',
    summary: '全面介绍数据库系统的基本概念、设计和实现。',
    cover_url: '',
    table_of_contents: '{"chapters": ["引言", "关系模型", "SQL", "事务管理"]}'
  },
  {
    id: '7',
    title: 'Python编程：从入门到实践',
    author: 'Eric Matthes',
    publisher: '人民邮电出版社',
    isbn: '978-7-115-42857-7',
    category: 'programming',
    summary: '一本针对所有层次Python读者的经典编程入门书籍。',
    cover_url: '',
    table_of_contents: '{"chapters": ["起步", "变量和简单数据类型", "列表", "函数"]}'
  },
  {
    id: '8',
    title: '机器学习实战',
    author: 'Peter Harrington',
    publisher: '人民邮电出版社',
    isbn: '978-7-115-28160-4',
    category: 'ai',
    summary: '通过实例详细介绍机器学习算法的实现方法。',
    cover_url: '',
    table_of_contents: '{"chapters": ["机器学习基础", "k近邻算法", "决策树", "朴素贝叶斯"]}'
  }
])

const searchQuery = ref('')
const selectedCategory = ref('all')
const selectedCourse = ref(null)

const filteredBooks = computed(() => {
  return books.value.filter(book => {
    const matchesSearch = book.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                         book.author.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                         book.isbn.includes(searchQuery.value)
    const matchesCategory = selectedCategory.value === 'all' || book.category === selectedCategory.value
    return matchesSearch && matchesCategory
  })
})

const getCategoryName = (categoryId) => {
  const category = categories.find(c => c.id === categoryId)
  return category ? category.name : categoryId
}

const filterByCourse = (course) => {
  selectedCourse.value = selectedCourse.value?.id === course.id ? null : course
}

const selectBook = (book) => {
  emit('select-book', book)
}
</script>
