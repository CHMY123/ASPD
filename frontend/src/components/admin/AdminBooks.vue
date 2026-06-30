<template>
  <div class="space-y-6">
    <div class="flex items-center justify-between">
      <div class="flex items-center gap-4">
        <div class="relative">
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-text-light" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <input 
            v-model="searchKeyword" 
            @input="handleSearch"
            type="text" 
            placeholder="搜索书名、作者..." 
            class="pl-10 pr-4 py-2.5 bg-background-secondary border border-border rounded-lg text-sm focus:outline-none focus:border-brand-mint transition-colors w-64"
          />
        </div>
        <select v-model="filterCategory" @change="handleSearch" class="px-4 py-2.5 bg-background-secondary border border-border rounded-lg text-sm focus:outline-none focus:border-brand-mint transition-colors">
          <option value="">全部分类</option>
          <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
        </select>
      </div>
      <button @click="showAddModal = true" class="flex items-center gap-2 px-4 py-2.5 bg-brand-mint text-white rounded-lg text-sm font-medium hover:bg-brand-dark transition-colors">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        添加书籍
      </button>
    </div>
    
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
      <div v-for="book in books" :key="book.id" class="bg-background-primary rounded-xl border border-border overflow-hidden hover:shadow-lg transition-all group">
        <div class="relative h-48 bg-background-secondary overflow-hidden">
          <img v-if="book.cover" :src="`http://localhost:8000${book.cover}`" :alt="book.title" class="w-full h-full object-cover" />
          <div v-else class="w-full h-full flex items-center justify-center">
            <svg class="w-12 h-12 text-text-light" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <div class="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
            <button @click="editBook(book)" class="px-4 py-2 bg-white/90 text-text-primary text-sm font-medium rounded-lg hover:bg-white transition-colors">
              编辑
            </button>
            <button @click="confirmDelete(book)" class="px-4 py-2 bg-error text-white text-sm font-medium rounded-lg hover:bg-error-dark transition-colors">
              删除
            </button>
          </div>
        </div>
        
        <div class="p-4">
          <span class="inline-block px-2 py-0.5 bg-brand-light/30 text-brand-dark text-xs font-medium rounded-full mb-2">{{ book.category }}</span>
          <h4 class="text-sm font-semibold text-text-primary truncate">{{ book.title }}</h4>
          <p class="text-xs text-text-secondary mt-1 truncate">{{ book.author }}</p>
          <p class="text-xs text-text-light mt-2 line-clamp-2">{{ book.summary }}</p>
        </div>
      </div>
    </div>
    
    <div v-if="total > pageSize" class="flex items-center justify-center gap-4 py-4">
      <span class="text-sm text-text-secondary">共 {{ total }} 条记录</span>
      <button @click="prevPage" :disabled="currentPage === 1" class="px-4 py-2 border border-border rounded-lg text-sm transition-colors" :class="currentPage === 1 ? 'text-text-light cursor-not-allowed' : 'text-text-secondary hover:bg-background-dark'">
        上一页
      </button>
      <span class="text-sm text-text-secondary">{{ currentPage }} / {{ totalPages }}</span>
      <button @click="nextPage" :disabled="currentPage === totalPages" class="px-4 py-2 border border-border rounded-lg text-sm transition-colors" :class="currentPage === totalPages ? 'text-text-light cursor-not-allowed' : 'text-text-secondary hover:bg-background-dark'">
        下一页
      </button>
    </div>
    
    <div v-if="showAddModal || showEditModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-background-primary rounded-xl w-full max-w-lg mx-4 shadow-2xl max-h-[90vh] overflow-y-auto">
        <div class="flex items-center justify-between p-6 border-b border-border sticky top-0 bg-background-primary z-10">
          <h3 class="text-lg font-semibold text-text-primary">{{ showEditModal ? '编辑书籍' : '添加书籍' }}</h3>
          <button @click="closeModal" class="p-1 text-text-light hover:text-text-secondary rounded-lg">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
        
        <form @submit.prevent="handleSubmit" class="p-6 space-y-4">
          <div>
            <label class="block text-sm font-medium text-text-primary mb-1.5">书名 *</label>
            <input v-model="formData.title" type="text" required class="w-full px-4 py-2.5 bg-background-secondary border border-border rounded-lg text-sm focus:outline-none focus:border-brand-mint transition-colors" />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-text-primary mb-1.5">作者 *</label>
            <input v-model="formData.author" type="text" required class="w-full px-4 py-2.5 bg-background-secondary border border-border rounded-lg text-sm focus:outline-none focus:border-brand-mint transition-colors" />
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-text-primary mb-1.5">译者</label>
              <input v-model="formData.translator" type="text" class="w-full px-4 py-2.5 bg-background-secondary border border-border rounded-lg text-sm focus:outline-none focus:border-brand-mint transition-colors" />
            </div>
            <div>
              <label class="block text-sm font-medium text-text-primary mb-1.5">ISBN</label>
              <input v-model="formData.isbn" type="text" class="w-full px-4 py-2.5 bg-background-secondary border border-border rounded-lg text-sm focus:outline-none focus:border-brand-mint transition-colors" />
            </div>
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium text-text-primary mb-1.5">出版社</label>
              <input v-model="formData.publisher" type="text" class="w-full px-4 py-2.5 bg-background-secondary border border-border rounded-lg text-sm focus:outline-none focus:border-brand-mint transition-colors" />
            </div>
            <div>
              <label class="block text-sm font-medium text-text-primary mb-1.5">分类</label>
              <select v-model="formData.category" class="w-full px-4 py-2.5 bg-background-secondary border border-border rounded-lg text-sm focus:outline-none focus:border-brand-mint transition-colors">
                <option value="">请选择分类</option>
                <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
              </select>
            </div>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-text-primary mb-1.5">封面图片</label>
            <div class="flex items-center gap-4">
              <div v-if="coverPreview" class="w-20 h-28 rounded-lg overflow-hidden border border-border">
                <img :src="coverPreview" class="w-full h-full object-cover" />
              </div>
              <div v-else class="w-20 h-28 rounded-lg border border-border flex items-center justify-center">
                <svg class="w-6 h-6 text-text-light" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </div>
              <div class="flex-1">
                <input type="file" ref="coverInput" accept="image/*" @change="handleCoverChange" class="hidden" />
                <button type="button" @click="coverInput.value?.click()" class="px-4 py-2 bg-background-secondary border border-border rounded-lg text-sm text-text-secondary hover:bg-background-dark transition-colors">
                  选择图片
                </button>
                <button v-if="coverPreview" type="button" @click="removeCover" class="ml-2 px-4 py-2 bg-error/10 text-error rounded-lg text-sm hover:bg-error/20 transition-colors">
                  移除
                </button>
              </div>
            </div>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-text-primary mb-1.5">简介</label>
            <textarea v-model="formData.summary" rows="4" class="w-full px-4 py-2.5 bg-background-secondary border border-border rounded-lg text-sm focus:outline-none focus:border-brand-mint transition-colors resize-none"></textarea>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-text-primary mb-1.5">目录</label>
            <textarea v-model="formData.table_of_contents" rows="4" class="w-full px-4 py-2.5 bg-background-secondary border border-border rounded-lg text-sm focus:outline-none focus:border-brand-mint transition-colors resize-none"></textarea>
          </div>
          
          <div class="flex items-center gap-3 pt-4">
            <button type="button" @click="closeModal" class="flex-1 px-4 py-2.5 border border-border rounded-lg text-sm font-medium text-text-secondary hover:bg-background-dark transition-colors">
              取消
            </button>
            <button type="submit" class="flex-1 px-4 py-2.5 bg-brand-mint text-white rounded-lg text-sm font-medium hover:bg-brand-dark transition-colors">
              {{ showEditModal ? '保存修改' : '添加书籍' }}
            </button>
          </div>
        </form>
      </div>
    </div>
    
    <div v-if="showDeleteConfirm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-background-primary rounded-xl w-full max-w-sm mx-4 shadow-2xl">
        <div class="p-6">
          <div class="w-12 h-12 bg-error/10 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-6 h-6 text-error" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-text-primary text-center mb-2">确认删除</h3>
          <p class="text-sm text-text-secondary text-center">确定要删除书籍 <span class="font-medium text-text-primary">{{ deletingBook?.title }}</span> 吗？此操作不可撤销。</p>
          
          <div class="flex items-center gap-3 mt-6">
            <button @click="showDeleteConfirm = false" class="flex-1 px-4 py-2.5 border border-border rounded-lg text-sm font-medium text-text-secondary hover:bg-background-dark transition-colors">
              取消
            </button>
            <button @click="deleteBook" class="flex-1 px-4 py-2.5 bg-error text-white rounded-lg text-sm font-medium hover:bg-error-dark transition-colors">
              确认删除
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'

const authStore = useAuthStore()

const books = ref([])
const categories = ref([
  { id: '基础理论', name: '基础理论' },
  { id: '系统与网络', name: '系统与网络' },
  { id: '数据库', name: '数据库' },
  { id: '人工智能', name: '人工智能' },
  { id: '编程语言', name: '编程语言' }
])

const total = ref(0)
const currentPage = ref(1)
const pageSize = 12

const searchKeyword = ref('')
const filterCategory = ref('')

const showAddModal = ref(false)
const showEditModal = ref(false)
const showDeleteConfirm = ref(false)

const editingBookId = ref(null)
const deletingBook = ref(null)

const coverPreview = ref('')
const coverFile = ref(null)
const coverInput = ref(null)

const formData = ref({
  title: '',
  author: '',
  translator: '',
  isbn: '',
  publisher: '',
  publish_date: '',
  cover_url: '',
  summary: '',
  category: '',
  table_of_contents: ''
})

const totalPages = computed(() => Math.ceil(total.value / pageSize))

const fetchBooks = async () => {
  try {
    const params = new URLSearchParams({
      page: currentPage.value,
      page_size: pageSize
    })
    if (searchKeyword.value) params.append('search', searchKeyword.value)
    if (filterCategory.value) params.append('category', filterCategory.value)
    
    const response = await fetch(`http://localhost:8000/api/admin/books?${params}`, {
      headers: { Authorization: `Bearer ${authStore.accessToken}` }
    })
    
    if (response.ok) {
      const data = await response.json()
      books.value = data.data || []
      total.value = data.total || 0
    }
  } catch (error) {
    console.error('获取书籍失败:', error)
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchBooks()
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    fetchBooks()
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    fetchBooks()
  }
}

const closeModal = () => {
  showAddModal.value = false
  showEditModal.value = false
  editingBookId.value = null
  coverPreview.value = ''
  coverFile.value = null
  formData.value = {
    title: '',
    author: '',
    translator: '',
    isbn: '',
    publisher: '',
    publish_date: '',
    cover_url: '',
    summary: '',
    category: '',
    table_of_contents: ''
  }
}

const handleCoverChange = (event) => {
  const file = event.target.files[0]
  if (file) {
    coverFile.value = file
    coverPreview.value = URL.createObjectURL(file)
  }
}

const removeCover = () => {
  coverPreview.value = ''
  coverFile.value = null
  formData.value.cover_url = ''
  if (coverInput.value) {
    coverInput.value.value = ''
  }
}

const editBook = (book) => {
  editingBookId.value = book.id
  coverPreview.value = book.cover ? `http://localhost:8000${book.cover}` : ''
  coverFile.value = null
  formData.value = {
    title: book.title,
    author: book.author,
    translator: book.translator || '',
    isbn: book.isbn || '',
    publisher: book.publisher || '',
    publish_date: book.publish_date || '',
    cover_url: book.cover || '',
    summary: book.summary || '',
    category: book.category || '',
    table_of_contents: book.table_of_contents || ''
  }
  showEditModal.value = true
}

const confirmDelete = (book) => {
  deletingBook.value = book
  showDeleteConfirm.value = true
}

const deleteBook = async () => {
  try {
    const response = await fetch(`http://localhost:8000/api/admin/books/${deletingBook.value.id}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${authStore.accessToken}` }
    })
    
    if (response.ok) {
      showDeleteConfirm.value = false
      fetchBooks()
    }
  } catch (error) {
    console.error('删除书籍失败:', error)
  }
}

const handleSubmit = async () => {
  try {
    let coverUrl = formData.value.cover_url
    
    if (coverFile.value) {
      const formDataToSend = new FormData()
      formDataToSend.append('file', coverFile.value)
      
      const uploadResponse = await fetch('http://localhost:8000/api/upload/image', {
        method: 'POST',
        headers: { Authorization: `Bearer ${authStore.accessToken}` },
        body: formDataToSend
      })
      
      if (uploadResponse.ok) {
        const uploadData = await uploadResponse.json()
        coverUrl = uploadData.path
      }
    }
    
    const url = showEditModal.value 
      ? `http://localhost:8000/api/admin/books/${editingBookId.value}`
      : 'http://localhost:8000/api/admin/books'
    
    const method = showEditModal.value ? 'PUT' : 'POST'
    
    const data = {
      ...formData.value,
      cover_url: coverUrl
    }
    
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${authStore.accessToken}`
      },
      body: JSON.stringify(data)
    })
    
    if (response.ok) {
      closeModal()
      fetchBooks()
    }
  } catch (error) {
    console.error('保存书籍失败:', error)
  }
}

onMounted(fetchBooks)
</script>
