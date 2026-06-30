<template>
  <div class="book-library">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-semibold text-text-primary">电子书库</h2>
      <div class="flex items-center gap-3">
        <div v-if="isEditMode" class="flex items-center gap-2">
          <button @click="toggleSelectAll" class="px-3 py-2 border border-border rounded-lg text-sm text-text-secondary hover:bg-background-dark transition-colors">
            {{ isAllSelected ? '取消全选' : '全选' }}
          </button>
          <button @click="confirmBatchDelete" class="px-4 py-2.5 bg-error text-white rounded-lg text-base font-black hover:bg-red-700 transition-all focus:outline-none focus:ring-2 focus:ring-error focus:ring-offset-2 shadow-lg hover:shadow-xl hover:scale-105" :disabled="selectedIds.length === 0" :class="selectedIds.length === 0 ? 'opacity-50 cursor-not-allowed' : ''" aria-label="批量删除电子书">
            批量删除 ({{ selectedIds.length }})
          </button>
        </div>
        <button @click="toggleEditMode" class="px-4 py-2 border border-border rounded-lg text-sm font-medium text-text-secondary hover:bg-background-dark transition-colors flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
          {{ isEditMode ? '完成' : '编辑' }}
        </button>
        <div class="relative">
          <input v-model="searchQuery" type="text" placeholder="搜索书名、作者、ISBN..." class="pl-10 pr-4 py-2 border border-border rounded-lg text-sm bg-background-primary focus:border-brand-mint focus:outline-none focus:ring-2 focus:ring-brand-mint/20 w-64" />
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-text-light" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <button @click="showAddModal = true" class="px-4 py-2 bg-brand-mint text-white rounded-lg hover:bg-brand-dark transition-colors text-sm font-medium flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          添加电子书
        </button>
      </div>
    </div>

    <div class="flex items-center gap-4 mb-6">
      <div class="flex items-center gap-2 flex-wrap">
        <button @click="selectedCategory = ''" class="px-4 py-2 rounded-lg text-sm font-medium transition-colors" :class="selectedCategory === '' ? 'bg-brand-mint text-white' : 'bg-background-primary border border-border text-text-secondary hover:bg-background-dark'">
          全部
        </button>
        <button v-for="category in categories" :key="category.id" @click="selectedCategory = category.id" class="px-4 py-2 rounded-lg text-sm font-medium transition-colors" :class="selectedCategory === category.id ? 'bg-brand-mint text-white' : 'bg-background-primary border border-border text-text-secondary hover:bg-background-dark'">
          {{ category.name }}
        </button>
      </div>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
      <div v-for="book in filteredBooks" :key="book.id" class="book-card bg-background-primary border border-border rounded-xl overflow-hidden shadow-soft hover:shadow-medium transition-all cursor-pointer group relative" @click="selectBook(book)">
        <div v-if="isEditMode" class="absolute top-2 left-2 z-10" @click.stop>
          <input type="checkbox" :checked="selectedIds.includes(book.id)" @change="toggleSelection(book.id)" class="w-5 h-5 rounded border-border text-brand-mint focus:ring-brand-mint cursor-pointer" />
        </div>
        <div class="relative aspect-[3/4] bg-background-dark overflow-hidden">
          <LazyImage 
            v-if="book.cover_url" 
            :src="book.cover_url" 
            :alt="book.title"
            class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          >
            <template #fallback>
              <div class="w-full h-full flex items-center justify-center">
                <svg class="w-16 h-16 text-text-light" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
            </template>
          </LazyImage>
          <div v-else class="w-full h-full flex items-center justify-center">
            <svg class="w-16 h-16 text-text-light" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <div class="absolute top-2 right-2 px-2 py-1 bg-background-primary/90 backdrop-blur-sm rounded text-xs font-medium text-text-secondary">
            {{ getCategoryName(book.category) }}
          </div>
        </div>
        <div class="p-4">
          <h3 class="text-sm font-semibold text-text-primary truncate group-hover:text-brand-mint transition-colors">{{ book.title }}</h3>
          <p class="text-xs text-text-secondary mt-1 truncate">{{ book.author }}</p>
          <div class="flex items-center gap-2 mt-2">
            <span class="text-xs text-text-light">{{ book.publisher }}</span>
            <span class="text-xs text-text-light">|</span>
            <span class="text-xs text-text-light">{{ book.publish_date }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="filteredBooks.length === 0" class="text-center py-12">
      <div class="w-20 h-20 mx-auto mb-4 rounded-full bg-background-dark flex items-center justify-center">
        <svg class="w-10 h-10 text-text-light" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
      </div>
      <p class="text-text-secondary">暂无相关书籍</p>
      <p class="text-sm text-text-light mt-1">请尝试其他搜索条件</p>
    </div>

    <div v-if="selectedBook" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4" @click.self="selectedBook = null">
      <div class="bg-background-primary rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden shadow-large animate-scale-in">
        <div class="grid grid-cols-1 md:grid-cols-3">
          <div class="aspect-[3/4] bg-background-dark">
            <LazyImage 
              v-if="selectedBook.cover_url" 
              :src="selectedBook.cover_url" 
              :alt="selectedBook.title"
              class="w-full h-full object-cover"
            >
              <template #fallback>
                <div class="w-full h-full flex items-center justify-center">
                  <svg class="w-24 h-24 text-text-light" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                </div>
              </template>
            </LazyImage>
            <div v-else class="w-full h-full flex items-center justify-center">
              <svg class="w-24 h-24 text-text-light" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
          </div>
          <div class="md:col-span-2 p-6 overflow-y-auto max-h-[90vh]">
            <div class="flex items-start justify-between mb-4">
              <div>
                <span class="inline-block px-2 py-1 text-xs font-medium rounded-full bg-brand-light text-brand-dark mb-2">
                  {{ getCategoryName(selectedBook.category) }}
                </span>
                <h2 class="text-xl font-semibold text-text-primary">{{ selectedBook.title }}</h2>
                <p v-if="selectedBook.subtitle" class="text-sm text-text-secondary mt-1">{{ selectedBook.subtitle }}</p>
              </div>
              <div class="flex gap-2">
                <button @click="editBook" class="p-2 rounded-lg hover:bg-background-dark transition-colors">
                  <svg class="w-5 h-5 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </button>
                <button @click="selectedBook = null" class="p-2 rounded-lg hover:bg-background-dark transition-colors">
                  <svg class="w-5 h-5 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <div class="space-y-3 mb-6">
              <div class="flex items-center gap-3">
                <span class="text-sm text-text-light w-20">作者</span>
                <span class="text-sm text-text-primary">{{ selectedBook.author }}</span>
              </div>
              <div class="flex items-center gap-3">
                <span class="text-sm text-text-light w-20">译者</span>
                <span class="text-sm text-text-primary">{{ selectedBook.translator || '-' }}</span>
              </div>
              <div class="flex items-center gap-3">
                <span class="text-sm text-text-light w-20">出版社</span>
                <span class="text-sm text-text-primary">{{ selectedBook.publisher }}</span>
              </div>
              <div class="flex items-center gap-3">
                <span class="text-sm text-text-light w-20">出版日期</span>
                <span class="text-sm text-text-primary">{{ selectedBook.publish_date }}</span>
              </div>
              <div class="flex items-center gap-3">
                <span class="text-sm text-text-light w-20">ISBN</span>
                <span class="text-sm text-text-primary">{{ selectedBook.isbn }}</span>
              </div>
            </div>

            <div class="mb-6">
              <h3 class="text-sm font-semibold text-text-primary mb-2">内容简介</h3>
              <p class="text-sm text-text-secondary leading-relaxed">{{ selectedBook.summary }}</p>
            </div>

            <div>
              <h3 class="text-sm font-semibold text-text-primary mb-2">目录</h3>
              <div class="space-y-1 max-h-40 overflow-y-auto">
                <div v-for="(chapter, index) in selectedBook.toc" :key="index" class="flex items-start gap-2 text-sm">
                  <span class="text-text-light w-6">{{ index + 1 }}.</span>
                  <span class="text-text-secondary truncate">{{ chapter }}</span>
                </div>
              </div>
            </div>

            <div class="flex gap-3 mt-6">
              <button class="flex-1 py-2 bg-brand-mint text-white rounded-lg hover:bg-brand-dark transition-colors text-sm font-medium">
                在线阅读
              </button>
              <button class="flex-1 py-2 border border-brand-mint text-brand-mint rounded-lg hover:bg-brand-mint hover:text-white transition-colors text-sm font-medium">
                收藏
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加/编辑电子书模态框 -->
    <Teleport to="body">
      <div v-if="showAddModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 overflow-y-auto" @click.self="showAddModal = false">
        <div class="bg-background-primary rounded-2xl w-full max-w-lg max-h-[90vh] overflow-hidden shadow-xl flex flex-col animate-scale-in">
          <!-- 头部 -->
          <div class="flex items-center justify-between p-5 border-b border-border flex-shrink-0">
            <h3 class="text-xl font-semibold text-text-primary">{{ editingBook ? '编辑电子书' : '添加电子书' }}</h3>
            <button @click="showAddModal = false" class="p-2 hover:bg-background-dark rounded-lg transition-colors">
              <svg class="w-5 h-5 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <!-- 表单内容区域 -->
          <form @submit.prevent="addBook" class="flex-1 overflow-y-auto p-5 space-y-4">
            <!-- 基础信息 -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-text-primary mb-1.5">书名 *</label>
                <input v-model="newBook.title" type="text" required class="w-full px-3.5 py-2.5 border border-border rounded-lg bg-background-primary focus:border-brand-mint focus:outline-none focus:ring-2 focus:ring-brand-mint/20 transition-all text-sm" placeholder="数据结构与算法分析" />
              </div>
              <div>
                <label class="block text-sm font-medium text-text-primary mb-1.5">副标题</label>
                <input v-model="newBook.subtitle" type="text" class="w-full px-3.5 py-2.5 border border-border rounded-lg bg-background-primary focus:border-brand-mint focus:outline-none focus:ring-2 focus:ring-brand-mint/20 transition-all text-sm" placeholder="C语言描述" />
              </div>
              <div>
                <label class="block text-sm font-medium text-text-primary mb-1.5">作者 *</label>
                <input v-model="newBook.author" type="text" required class="w-full px-3.5 py-2.5 border border-border rounded-lg bg-background-primary focus:border-brand-mint focus:outline-none focus:ring-2 focus:ring-brand-mint/20 transition-all text-sm" placeholder="Mark Allen Weiss" />
              </div>
              <div>
                <label class="block text-sm font-medium text-text-primary mb-1.5">译者</label>
                <input v-model="newBook.translator" type="text" class="w-full px-3.5 py-2.5 border border-border rounded-lg bg-background-primary focus:border-brand-mint focus:outline-none focus:ring-2 focus:ring-brand-mint/20 transition-all text-sm" placeholder="冯舜玺" />
              </div>
              <div>
                <label class="block text-sm font-medium text-text-primary mb-1.5">出版社 *</label>
                <input v-model="newBook.publisher" type="text" required class="w-full px-3.5 py-2.5 border border-border rounded-lg bg-background-primary focus:border-brand-mint focus:outline-none focus:ring-2 focus:ring-brand-mint/20 transition-all text-sm" placeholder="机械工业出版社" />
              </div>
              <div>
                <label class="block text-sm font-medium text-text-primary mb-1.5">ISBN</label>
                <input v-model="newBook.isbn" type="text" class="w-full px-3.5 py-2.5 border border-border rounded-lg bg-background-primary focus:border-brand-mint focus:outline-none focus:ring-2 focus:ring-brand-mint/20 transition-all text-sm" placeholder="978-7-111-54493-7" />
              </div>
              <div>
                <label class="block text-sm font-medium text-text-primary mb-1.5">出版日期</label>
                <input v-model="newBook.publish_date" type="month" class="w-full px-3.5 py-2.5 border border-border rounded-lg bg-background-primary focus:border-brand-mint focus:outline-none focus:ring-2 focus:ring-brand-mint/20 transition-all text-sm" />
              </div>
              <div class="md:col-span-2">
                <label class="block text-sm font-medium text-text-primary mb-1.5">分类 *</label>
                <select v-model="newBook.category" required class="w-full px-3.5 py-2.5 border border-border rounded-lg bg-background-primary focus:border-brand-mint focus:outline-none focus:ring-2 focus:ring-brand-mint/20 transition-all text-sm">
                  <option value="">请选择</option>
                  <option value="基础理论">基础理论</option>
                  <option value="系统与网络">系统与网络</option>
                  <option value="数据库">数据库</option>
                  <option value="人工智能">人工智能</option>
                  <option value="编程语言">编程语言</option>
                </select>
              </div>
            </div>
            
            <!-- 详细信息 -->
            <div>
              <label class="block text-sm font-medium text-text-primary mb-1.5">内容简介</label>
              <textarea v-model="newBook.summary" rows="3" class="w-full px-3.5 py-2.5 border border-border rounded-lg bg-background-primary focus:border-brand-mint focus:outline-none focus:ring-2 focus:ring-brand-mint/20 resize-none transition-all text-sm" placeholder="请输入书籍简介"></textarea>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-text-primary mb-1.5">目录（每行一章）</label>
              <textarea v-model="newBook.tableOfContents" rows="4" class="w-full px-3.5 py-2.5 border border-border rounded-lg bg-background-primary focus:border-brand-mint focus:outline-none focus:ring-2 focus:ring-brand-mint/20 resize-none transition-all text-sm" placeholder="第1章 引言&#10;第2章 基础概念&#10;第3章 核心内容"></textarea>
            </div>
            
            <!-- 封面上传 -->
            <div>
              <label class="block text-sm font-medium text-text-primary mb-1.5">封面图片</label>
              <div class="border-2 border-dashed border-border rounded-xl p-5 text-center hover:border-brand-mint hover:bg-brand-mint/5 transition-all cursor-pointer" @click="triggerCoverUpload" @dragover.prevent @drop.prevent="handleCoverDrop">
                <div v-if="!coverPreview" class="space-y-2">
                  <svg class="w-14 h-14 mx-auto text-text-light" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <p class="text-sm text-text-secondary">点击或拖拽上传封面图片</p>
                  <p class="text-xs text-text-light">支持 JPG/PNG 格式，最大 5MB</p>
                </div>
                <div v-else class="relative inline-block">
                  <img :src="coverPreview" class="max-h-40 max-w-full rounded-lg object-contain shadow-md" />
                  <button @click.stop="removeCover" class="absolute -top-2 -right-2 p-1.5 bg-error-red rounded-full hover:bg-error-red/90 transition-colors shadow-lg">
                    <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
              <input ref="coverInput" type="file" accept="image/jpeg,image/png" class="hidden" @change="handleCoverChange" />
            </div>
          </form>
          
          <!-- 底部操作栏 -->
          <div class="flex gap-3 p-5 border-t border-border bg-background-primary/95 backdrop-blur-sm flex-shrink-0">
            <button type="button" @click="showAddModal = false" class="flex-1 px-4 py-2.5 border border-border rounded-lg text-text-secondary hover:bg-background-dark transition-colors text-sm font-medium">
              取消
            </button>
            <button type="button" @click="editingBook ? updateBook() : addBook()" :disabled="isUploading" class="flex-1 px-4 py-2.5 bg-brand-mint text-white rounded-lg hover:bg-brand-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-sm font-medium">
              <svg v-if="isUploading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ isUploading ? (editingBook ? '保存中...' : '上传中...') : (editingBook ? '保存修改' : '添加电子书') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import LazyImage from './LazyImage.vue';

const searchQuery = ref('');
const selectedCategory = ref('');
const selectedBook = ref(null);
const showAddModal = ref(false);
const coverPreview = ref('');
const coverFile = ref(null);
const isUploading = ref(false);
const coverInput = ref(null);
const editingBook = ref(null);

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

// 编辑模式与批量删除
const isEditMode = ref(false);
const selectedIds = ref([]);
const isAllSelected = ref(false);

const toggleEditMode = () => {
  isEditMode.value = !isEditMode.value;
  if (!isEditMode.value) {
    selectedIds.value = [];
    isAllSelected.value = false;
  }
};

const toggleSelection = (id) => {
  const idx = selectedIds.value.indexOf(id);
  if (idx === -1) {
    selectedIds.value.push(id);
  } else {
    selectedIds.value.splice(idx, 1);
  }
};

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedIds.value = [];
    isAllSelected.value = false;
  } else {
    selectedIds.value = filteredBooks.value.map(b => b.id);
    isAllSelected.value = true;
  }
};

const confirmBatchDelete = () => {
  if (selectedIds.value.length === 0) return;
  const confirmed = confirm(`确定要删除选中的 ${selectedIds.value.length} 本电子书吗？此操作不可撤销。`);
  if (confirmed) {
    batchDeleteBooks();
  }
};

const batchDeleteBooks = async () => {
  try {
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    const response = await fetch('http://localhost:8000/api/knowledge/books/batch-delete', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      },
      body: JSON.stringify({ ids: selectedIds.value })
    });
    
    if (response.ok) {
      const result = await response.json();
      console.log('批量删除成功:', result.message);
      selectedIds.value = [];
      isAllSelected.value = false;
      isEditMode.value = false;
      await loadBooks();
    } else {
      const error = await response.json();
      console.error('批量删除失败:', error.detail || '未知错误');
      alert(`批量删除失败: ${error.detail || '未知错误'}`);
    }
  } catch (error) {
    console.error('批量删除异常:', error);
    alert('批量删除失败，请重试');
  }
};

const newBook = ref({
  title: '',
  subtitle: '',
  author: '',
  translator: '',
  publisher: '',
  publish_date: '',
  isbn: '',
  category: '',
  summary: '',
  tableOfContents: '',
  cover_url: ''
});

const triggerCoverUpload = () => {
  coverInput.value?.click();
};

const validateImage = (file) => {
  const validTypes = ['image/jpeg', 'image/png'];
  if (!validTypes.includes(file.type)) {
    alert('请选择 JPG 或 PNG 格式的图片');
    return false;
  }
  if (file.size > MAX_FILE_SIZE) {
    alert('图片大小不能超过 5MB');
    return false;
  }
  return true;
};

const handleCoverChange = (event) => {
  const file = event.target.files?.[0];
  if (file && validateImage(file)) {
    handleFile(file);
  }
};

const handleCoverDrop = (event) => {
  const file = event.dataTransfer?.files?.[0];
  if (file && validateImage(file)) {
    handleFile(file);
  }
};

const handleFile = (file) => {
  coverFile.value = file;
  const reader = new FileReader();
  reader.onload = (e) => {
    coverPreview.value = e.target.result;
  };
  reader.readAsDataURL(file);
};

const removeCover = () => {
  coverPreview.value = '';
  coverFile.value = null;
  newBook.value.cover_url = '';
  if (coverInput.value) {
    coverInput.value.value = '';
  }
};

const categories = ref([]);
const books = ref([]);
const isLoading = ref(true);

const categoryMapping = {
  '基础理论': '基础理论',
  '系统与网络': '系统与网络',
  '数据库': '数据库',
  '人工智能': '人工智能',
  '编程语言': '编程语言',
  '数据结构': '基础理论',
  '算法设计': '基础理论',
  '操作系统': '系统与网络',
  '数据库原理': '数据库',
  '计算机网络': '系统与网络',
  'data-structure': '基础理论',
  'algorithm': '基础理论',
  'os': '系统与网络',
  'database': '数据库',
  'ai': '人工智能',
  'programming': '编程语言',
  'network': '系统与网络'
}

// 从后端API获取书籍列表
async function loadBooks() {
  isLoading.value = true;
  try {
    const token = localStorage.getItem('access_token');
    const response = await fetch('http://localhost:8000/api/knowledge/books', {
      headers: token ? { 'Authorization': `Bearer ${token}` } : {}
    });
    if (response.ok) {
      const data = await response.json();
      const catSet = new Set();
      data.forEach(b => {
        if (b.category) catSet.add(categoryMapping[b.category] || b.category);
      });
      categories.value = Array.from(catSet).map(name => ({
        id: name,
        name: name
      }));
      books.value = data.map(b => ({
        id: b.id,
        title: b.title || '未命名书籍',
        subtitle: b.subtitle || '',
        author: b.author || '未知作者',
        translator: b.translator || '',
        publisher: b.publisher || '',
        publish_date: b.publish_date || '',
        isbn: b.isbn || '',
        category: b.category || '',
        cover_url: b.cover_url || '',
        summary: b.summary || '暂无简介',
        toc: b.toc ? (Array.isArray(b.toc) ? b.toc : b.toc.split('\n').filter(t => t.trim())) : ['第1章 引言']
      }));
    } else {
      console.error(`获取书籍列表失败: HTTP ${response.status} ${response.statusText}`);
      const errorText = await response.text().catch(() => '无法获取错误详情');
      console.error('错误详情:', errorText);
    }
  } catch (e) {
    console.error('加载书籍列表网络异常:', e.message || e);
  } finally {
    isLoading.value = false;
  }
}

// 初始化加载
loadBooks();

const filteredBooks = computed(() => {
  return books.value.filter(book => {
    const matchSearch = !searchQuery.value || book.title.toLowerCase().includes(searchQuery.value.toLowerCase()) || book.author.toLowerCase().includes(searchQuery.value.toLowerCase()) || book.isbn.includes(searchQuery.value);
    const matchCategory = !selectedCategory.value || (categoryMapping[book.category] || book.category) === selectedCategory.value;
    return matchSearch && matchCategory;
  });
});

const getCategoryName = (categoryId) => {
  return categoryMapping[categoryId] || categoryId;
};

const selectBook = (book) => {
  selectedBook.value = book;
};

const editBook = () => {
  if (!selectedBook.value) return;
  
  editingBook.value = selectedBook.value;
  newBook.value = {
    title: selectedBook.value.title,
    subtitle: selectedBook.value.subtitle,
    author: selectedBook.value.author,
    translator: selectedBook.value.translator,
    publisher: selectedBook.value.publisher,
    publish_date: selectedBook.value.publish_date,
    isbn: selectedBook.value.isbn,
    category: selectedBook.value.category,
    summary: selectedBook.value.summary,
    tableOfContents: selectedBook.value.toc ? selectedBook.value.toc.join('\n') : '',
    cover_url: selectedBook.value.cover_url
  };
  
  if (selectedBook.value.cover_url) {
    coverPreview.value = selectedBook.value.cover_url;
  }
  
  selectedBook.value = null;
  showAddModal.value = true;
};

const addBook = async () => {
  isUploading.value = true;
  
  try {
    // 上传封面（如果有）
    if (coverFile.value) {
      try {
        const formData = new FormData();
        formData.append('file', coverFile.value);
        
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        const response = await fetch('http://localhost:8000/api/upload/ebook-cover/temp', {
          method: 'POST',
          body: formData,
          headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });
        
        if (response.ok) {
          const result = await response.json();
          newBook.value.cover_url = result.url;
        } else {
          console.warn('封面上传失败，将继续添加电子书');
        }
      } catch (error) {
        console.warn('封面上传异常，将继续添加电子书:', error);
      }
    }
    
    // 调用后端API添加书籍
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    const response = await fetch('http://localhost:8000/api/knowledge/books', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      },
      body: JSON.stringify({
        title: newBook.value.title,
        subtitle: newBook.value.subtitle,
        author: newBook.value.author,
        translator: newBook.value.translator,
        publisher: newBook.value.publisher,
        isbn: newBook.value.isbn,
        publish_date: newBook.value.publish_date,
        category: newBook.value.category,
        summary: newBook.value.summary || '暂无简介',
        cover_url: newBook.value.cover_url
      })
    });
    
    if (response.ok) {
      const result = await response.json();
      console.log('书籍添加成功:', result);
      // 重新加载书籍列表
      await loadBooks();
    } else {
      const error = await response.json();
      console.error('添加书籍失败:', error.detail || '未知错误');
      alert(`添加书籍失败: ${error.detail || '未知错误'}`);
    }
  } catch (error) {
    console.error('添加书籍异常:', error);
    alert('添加书籍失败，请重试');
  } finally {
    showAddModal.value = false;
    isUploading.value = false;
    
    // 重置表单
    newBook.value = {
      title: '',
      subtitle: '',
      author: '',
      translator: '',
      publisher: '',
      publish_date: '',
      isbn: '',
      category: '',
      summary: '',
      tableOfContents: '',
      cover_url: ''
    };
    coverPreview.value = '';
    coverFile.value = null;
    editingBook.value = null;
  }
};

const updateBook = async () => {
  if (!editingBook.value) return;
  
  isUploading.value = true;
  
  try {
    // 上传封面（如果有新的封面）
    if (coverFile.value) {
      try {
        const formData = new FormData();
        formData.append('file', coverFile.value);
        
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        const response = await fetch('http://localhost:8000/api/upload/ebook-cover/temp', {
          method: 'POST',
          body: formData,
          headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });
        
        if (response.ok) {
          const result = await response.json();
          newBook.value.cover_url = result.url;
        } else {
          console.warn('封面上传失败，将继续更新电子书');
        }
      } catch (error) {
        console.warn('封面上传异常，将继续更新电子书:', error);
      }
    }
    
    // 调用后端API更新书籍
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    const response = await fetch(`http://localhost:8000/api/knowledge/books/${editingBook.value.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      },
      body: JSON.stringify({
        title: newBook.value.title,
        subtitle: newBook.value.subtitle,
        author: newBook.value.author,
        translator: newBook.value.translator,
        publisher: newBook.value.publisher,
        isbn: newBook.value.isbn,
        publish_date: newBook.value.publish_date,
        category: newBook.value.category,
        summary: newBook.value.summary || '暂无简介',
        cover_url: newBook.value.cover_url,
        table_of_contents: newBook.value.tableOfContents
      })
    });
    
    if (response.ok) {
      const result = await response.json();
      console.log('书籍更新成功:', result);
      await loadBooks();
    } else {
      const error = await response.json();
      console.error('更新书籍失败:', error.detail || '未知错误');
      alert(`更新书籍失败: ${error.detail || '未知错误'}`);
    }
  } catch (error) {
    console.error('更新书籍异常:', error);
    alert('更新书籍失败，请重试');
  } finally {
    showAddModal.value = false;
    isUploading.value = false;
    
    // 重置表单
    newBook.value = {
      title: '',
      subtitle: '',
      author: '',
      translator: '',
      publisher: '',
      publish_date: '',
      isbn: '',
      category: '',
      summary: '',
      tableOfContents: '',
      cover_url: ''
    };
    coverPreview.value = '';
    coverFile.value = null;
    editingBook.value = null;
  }
};
</script>

<style scoped>
.book-card:hover {
  transform: translateY(-4px);
}

@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to { opacity: 1; transform: scale(1); }
}

.animate-scale-in {
  animation: scaleIn 0.2s ease-out;
}
</style>
