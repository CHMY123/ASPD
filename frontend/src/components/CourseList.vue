<template>
  <div class="course-list">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-semibold text-text-primary">我的课程</h2>
      <div class="flex items-center gap-3">
        <div v-if="isEditMode" class="flex items-center gap-2">
          <button @click="toggleSelectAll" class="px-3 py-2 border border-border rounded-lg text-sm text-text-secondary hover:bg-background-dark transition-colors">
            {{ isAllSelected ? '取消全选' : '全选' }}
          </button>
          <button @click="confirmBatchDelete" class="px-4 py-2.5 bg-error text-white rounded-lg text-base font-black hover:bg-red-700 transition-all focus:outline-none focus:ring-2 focus:ring-error focus:ring-offset-2 shadow-lg hover:shadow-xl hover:scale-105" :disabled="selectedIds.length === 0" :class="selectedIds.length === 0 ? 'opacity-50 cursor-not-allowed' : ''" aria-label="批量删除课程">
            批量删除 ({{ selectedIds.length }})
          </button>
        </div>
        <button @click="toggleEditMode" class="px-4 py-2 border border-border rounded-lg text-sm font-medium text-text-secondary hover:bg-background-dark transition-colors flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
          {{ isEditMode ? '完成' : '编辑' }}
        </button>
        <select v-model="selectedSemester" class="px-4 py-2 border border-border rounded-lg text-sm bg-background-primary">
          <option value="">全部学期</option>
          <option value="2023-2024-1">2023-2024学年第一学期</option>
          <option value="2023-2024-2">2023-2024学年第二学期</option>
          <option value="2024-2025-1">2024-2025学年第一学期</option>
          <option value="2024-2025-2">2024-2025学年第二学期</option>
          <option value="2025-2026-1">2025-2026学年第一学期</option>
          <option value="2025-2026-2">2025-2026学年第二学期</option>
          <option value="2026-2027-1">2026-2027学年第一学期</option>
          <option value="2026-2027-2">2026-2027学年第二学期</option>
        </select>
        <select v-model="selectedType" class="px-4 py-2 border border-border rounded-lg text-sm bg-background-primary">
          <option value="">全部类型</option>
          <option value="required">必修课</option>
          <option value="elective">选修课</option>
        </select>
        <div class="relative">
          <input v-model="searchQuery" type="text" placeholder="搜索课程或教师..." class="pl-10 pr-4 py-2 border border-border rounded-lg text-sm bg-background-primary focus:border-brand-mint focus:outline-none focus:ring-2 focus:ring-brand-mint/20" />
          <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-text-light" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>
        <button @click="showAddModal = true" class="px-4 py-2 bg-brand-mint text-white rounded-lg hover:bg-brand-dark transition-colors text-sm font-medium flex items-center gap-2">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          添加课程
        </button>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="course in filteredCourses" :key="course.id" class="course-card bg-background-primary border border-border rounded-xl overflow-hidden shadow-soft hover:shadow-medium transition-all cursor-pointer group relative" @click="showCourseDetail(course)">
        <div v-if="isEditMode" class="absolute top-2 left-2 z-10 flex gap-2" @click.stop>
          <input type="checkbox" :checked="selectedIds.includes(course.id)" @change="toggleSelection(course.id)" class="w-5 h-5 rounded border-border text-brand-mint focus:ring-brand-mint cursor-pointer" />
          <button @click="editCourse(course)" class="p-1.5 bg-brand-mint/90 text-white rounded-lg hover:bg-brand-mint transition-colors shadow-md" title="编辑课程">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
        </div>
        <div class="relative h-32 bg-background-dark overflow-hidden">
          <LazyImage 
            v-if="course.cover" 
            :src="course.cover" 
            :alt="course.course_name"
            class="w-full h-full object-cover"
          >
            <template #fallback>
              <div class="w-full h-full flex items-center justify-center">
                <svg class="w-12 h-12 text-text-light" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
            </template>
          </LazyImage>
          <div v-else class="w-full h-full flex items-center justify-center">
            <svg class="w-12 h-12 text-text-light" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <span class="absolute top-2 left-2 px-2 py-1 text-xs font-medium rounded-full" :class="course.course_type === 'required' ? 'bg-brand-mint text-white' : 'bg-accent-lavender/30 text-accent-lavender'">
            {{ course.course_type === 'required' ? '必修课' : '选修课' }}
          </span>
        </div>
        <div class="p-4">
          <h3 class="text-lg font-semibold text-text-primary group-hover:text-brand-mint transition-colors">{{ course.course_name }}</h3>
          <p class="text-sm text-text-secondary mt-1">{{ course.course_code }}</p>
          <div class="flex items-center justify-between mt-3">
            <span class="text-sm font-medium text-brand-mint">{{ course.credits }} 学分</span>
            <span class="text-xs text-text-light">{{ course.hours }} 学时</span>
          </div>
        </div>
        
        <div class="flex items-center gap-3 px-4 pb-4 pt-0 border-t border-border">
          <div class="w-10 h-10 rounded-full bg-brand-light flex items-center justify-center">
            <svg class="w-5 h-5 text-brand-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <div>
            <p class="text-sm font-medium text-text-primary">{{ course.teacher_name }}</p>
            <p class="text-xs text-text-light">{{ course.teacher_title }}</p>
          </div>
        </div>

        <div class="px-4 pb-4 text-xs text-text-light space-y-1">
          <div v-if="course.class_time || course.schedule" class="flex items-center gap-2">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{{ course.class_time || course.schedule }}</span>
          </div>
          <div v-if="course.class_location || course.location" class="flex items-center gap-2">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <span>{{ course.class_location || course.location }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="filteredCourses.length === 0" class="text-center py-12">
      <div class="w-20 h-20 mx-auto mb-4 rounded-full bg-background-dark flex items-center justify-center">
        <svg class="w-10 h-10 text-text-light" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      </div>
      <p class="text-text-secondary">暂无课程</p>
      <p class="text-sm text-text-light mt-1">请联系教务系统确认选课情况</p>
    </div>

    <!-- 添加/编辑课程模态框 -->
    <Teleport to="body">
      <div v-if="showAddModal || showEditModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="closeCourseModal">
        <div class="bg-background-primary rounded-xl p-6 w-full max-w-lg mx-4 shadow-xl max-h-[90vh] overflow-y-auto">
          <div class="flex items-center justify-between mb-6">
            <h3 class="text-xl font-semibold text-text-primary">{{ editingCourse ? '编辑课程' : '添加课程' }}</h3>
            <button @click="closeCourseModal" class="p-2 hover:bg-background-dark rounded-lg transition-colors">
              <svg class="w-5 h-5 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <form @submit.prevent="editingCourse ? updateCourse() : addCourse()" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-text-primary mb-1">课程代码 <span class="text-error-red">*</span></label>
              <input v-model="newCourse.course_code" type="text" required class="w-full px-4 py-2 border rounded-lg bg-background-primary focus:border-brand-mint focus:outline-none focus:ring-2 focus:ring-brand-mint/20 transition-colors" :class="errors.course_code ? 'border-error-red' : 'border-border'" placeholder="如: CS101" />
              <p v-if="errors.course_code" class="text-xs text-error-red mt-1">{{ errors.course_code }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-text-primary mb-1">课程名称 <span class="text-error-red">*</span></label>
              <input v-model="newCourse.course_name" type="text" required class="w-full px-4 py-2 border rounded-lg bg-background-primary focus:border-brand-mint focus:outline-none focus:ring-2 focus:ring-brand-mint/20 transition-colors" :class="errors.course_name ? 'border-error-red' : 'border-border'" placeholder="如: 数据结构" />
              <p v-if="errors.course_name" class="text-xs text-error-red mt-1">{{ errors.course_name }}</p>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-text-primary mb-1">学分 <span class="text-error-red">*</span></label>
                <input v-model.number="newCourse.credits" type="number" step="0.5" min="0.5" max="10" required class="w-full px-4 py-2 border rounded-lg bg-background-primary focus:border-brand-mint focus:outline-none focus:ring-2 focus:ring-brand-mint/20 transition-colors" :class="errors.credits ? 'border-error-red' : 'border-border'" placeholder="如: 4.0" />
                <p v-if="errors.credits" class="text-xs text-error-red mt-1">{{ errors.credits }}</p>
              </div>
              <div>
                <label class="block text-sm font-medium text-text-primary mb-1">学时 <span class="text-error-red">*</span></label>
                <input v-model.number="newCourse.hours" type="number" min="1" max="200" required class="w-full px-4 py-2 border rounded-lg bg-background-primary focus:border-brand-mint focus:outline-none focus:ring-2 focus:ring-brand-mint/20 transition-colors" :class="errors.hours ? 'border-error-red' : 'border-border'" placeholder="如: 64" />
                <p v-if="errors.hours" class="text-xs text-error-red mt-1">{{ errors.hours }}</p>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-text-primary mb-1">课程类型 <span class="text-error-red">*</span></label>
              <select v-model="newCourse.course_type" required class="w-full px-4 py-2 border rounded-lg bg-background-primary focus:border-brand-mint focus:outline-none focus:ring-2 focus:ring-brand-mint/20 transition-colors" :class="errors.course_type ? 'border-error-red' : 'border-border'">
                <option value="">请选择</option>
                <option value="required">必修课</option>
                <option value="elective">选修课</option>
              </select>
              <p v-if="errors.course_type" class="text-xs text-error-red mt-1">{{ errors.course_type }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-text-primary mb-1">开学学期 <span class="text-error-red">*</span></label>
              <select v-model="newCourse.semester" required class="w-full px-4 py-2 border rounded-lg bg-background-primary focus:border-brand-mint focus:outline-none focus:ring-2 focus:ring-brand-mint/20 transition-colors" :class="errors.semester ? 'border-error-red' : 'border-border'">
                <option value="">请选择</option>
                <option value="2023-2024-1">2023-2024学年第一学期</option>
                <option value="2023-2024-2">2023-2024学年第二学期</option>
                <option value="2024-2025-1">2024-2025学年第一学期</option>
                <option value="2024-2025-2">2024-2025学年第二学期</option>
                <option value="2025-2026-1">2025-2026学年第一学期</option>
                <option value="2025-2026-2">2025-2026学年第二学期</option>
                <option value="2026-2027-1">2026-2027学年第一学期</option>
                <option value="2026-2027-2">2026-2027学年第二学期</option>
              </select>
              <p v-if="errors.semester" class="text-xs text-error-red mt-1">{{ errors.semester }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-text-primary mb-1">授课教师 <span class="text-error-red">*</span></label>
              <input v-model="newCourse.teacher_name" type="text" required class="w-full px-4 py-2 border rounded-lg bg-background-primary focus:border-brand-mint focus:outline-none focus:ring-2 focus:ring-brand-mint/20 transition-colors" :class="errors.teacher_name ? 'border-error-red' : 'border-border'" placeholder="如: 张教授" />
              <p v-if="errors.teacher_name" class="text-xs text-error-red mt-1">{{ errors.teacher_name }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-text-primary mb-1">教师职称 <span class="text-error-red">*</span></label>
              <select v-model="newCourse.teacher_title" required class="w-full px-4 py-2 border rounded-lg bg-background-primary focus:border-brand-mint focus:outline-none focus:ring-2 focus:ring-brand-mint/20 transition-colors" :class="errors.teacher_title ? 'border-error-red' : 'border-border'">
                <option value="">请选择</option>
                <option value="助教">助教</option>
                <option value="讲师">讲师</option>
                <option value="副教授">副教授</option>
                <option value="教授">教授</option>
                <option value="高级讲师">高级讲师</option>
              </select>
              <p v-if="errors.teacher_title" class="text-xs text-error-red mt-1">{{ errors.teacher_title }}</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-text-primary mb-1">课程简介 <span class="text-error-red">*</span></label>
              <textarea v-model="newCourse.description" rows="3" required class="w-full px-4 py-2 border rounded-lg bg-background-primary focus:border-brand-mint focus:outline-none focus:ring-2 focus:ring-brand-mint/20 transition-colors resize-none" :class="errors.description ? 'border-error-red' : 'border-border'" placeholder="请简要介绍课程内容、教学目标和学习要求..."></textarea>
              <p v-if="errors.description" class="text-xs text-error-red mt-1">{{ errors.description }}</p>
              <p class="text-xs text-text-light mt-1">最少50字，最多500字</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-text-primary mb-1">上课地点</label>
              <input v-model="newCourse.class_location" type="text" class="w-full px-4 py-2 border border-border rounded-lg bg-background-primary focus:border-brand-mint focus:outline-none focus:ring-2 focus:ring-brand-mint/20" placeholder="如: 教学楼A301" />
            </div>
            <div>
              <label class="block text-sm font-medium text-text-primary mb-1">上课时间</label>
              <input v-model="newCourse.class_time" type="text" class="w-full px-4 py-2 border border-border rounded-lg bg-background-primary focus:border-brand-mint focus:outline-none focus:ring-2 focus:ring-brand-mint/20" placeholder="如: 周一1-2节,周三3-4节" />
            </div>
            <div>
              <label class="block text-sm font-medium text-text-primary mb-1">课程封面</label>
              <div class="border-2 border-dashed border-border rounded-lg p-4 text-center hover:border-brand-mint transition-colors cursor-pointer" @click="triggerCoverUpload" @dragover.prevent @drop.prevent="handleCoverDrop">
                <div v-if="!coverPreview" class="space-y-2">
                  <svg class="w-12 h-12 mx-auto text-text-light" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <p class="text-sm text-text-secondary">点击或拖拽上传封面图片</p>
                  <p class="text-xs text-text-light">支持 JPG/PNG 格式，最大 5MB</p>
                </div>
                <div v-else class="relative">
                  <img :src="coverPreview" class="max-h-40 mx-auto rounded-lg" />
                  <button @click.stop="removeCover" class="absolute top-2 right-2 p-1 bg-background-dark rounded-full hover:bg-error-red transition-colors">
                    <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
              <input ref="coverInput" type="file" accept="image/jpeg,image/png" class="hidden" @change="handleCoverChange" />
            </div>
            <div class="flex gap-3">
              <button type="button" @click="closeCourseModal" class="flex-1 px-4 py-2 border border-border rounded-lg text-text-secondary hover:bg-background-dark transition-colors">
                取消
              </button>
              <button type="button" @click="editingCourse ? updateCourse() : addCourse()" :disabled="isUploading" class="flex-1 px-4 py-2 bg-brand-mint text-white rounded-lg hover:bg-brand-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2">
                <svg v-if="isUploading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ isUploading ? '保存中...' : (editingCourse ? '保存' : '添加') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- 课程详情模态框 -->
    <Teleport to="body">
      <div v-if="showDetailModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" @click.self="showDetailModal = false">
        <div class="bg-background-primary rounded-xl w-full max-w-2xl mx-4 shadow-xl overflow-hidden">
          <div class="relative h-48">
            <img v-if="selectedCourse?.cover" :src="selectedCourse.cover" class="w-full h-full object-cover" />
            <div v-else class="w-full h-full bg-background-dark flex items-center justify-center">
              <svg class="w-16 h-16 text-text-light" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <button @click="showDetailModal = false" class="absolute top-4 right-4 p-2 bg-black/50 hover:bg-black/70 rounded-full transition-colors">
              <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
            <span class="absolute top-4 left-4 px-3 py-1 text-sm font-medium rounded-full" :class="selectedCourse?.course_type === 'required' ? 'bg-brand-mint text-white' : 'bg-accent-lavender/30 text-accent-lavender'">
              {{ selectedCourse?.course_type === 'required' ? '必修课' : '选修课' }}
            </span>
          </div>
          <div class="p-6">
            <div class="flex items-start justify-between mb-4">
              <div>
                <h2 class="text-2xl font-bold text-text-primary">{{ selectedCourse?.course_name }}</h2>
                <p class="text-text-secondary mt-1">{{ selectedCourse?.course_code }}</p>
              </div>
              <div class="flex items-center gap-2">
                <span class="px-3 py-1 bg-brand-mint/10 text-brand-mint rounded-full text-sm font-medium">{{ selectedCourse?.credits }} 学分</span>
                <span class="px-3 py-1 bg-background-dark text-text-secondary rounded-full text-sm">{{ selectedCourse?.hours }} 学时</span>
              </div>
            </div>
            
            <div class="grid grid-cols-2 gap-4 mb-6">
              <div class="p-4 bg-background-secondary rounded-lg">
                <p class="text-xs text-text-light mb-1">授课教师</p>
                <p class="font-medium text-text-primary">{{ selectedCourse?.teacher_name }} <span class="text-text-secondary">{{ selectedCourse?.teacher_title }}</span></p>
              </div>
              <div class="p-4 bg-background-secondary rounded-lg">
                <p class="text-xs text-text-light mb-1">开学学期</p>
                <p class="font-medium text-text-primary">{{ formatSemester(selectedCourse?.semester) }}</p>
              </div>
              <div class="p-4 bg-background-secondary rounded-lg">
                <p class="text-xs text-text-light mb-1">上课时间</p>
                <p class="font-medium text-text-primary">{{ selectedCourse?.schedule || selectedCourse?.class_time || '暂无' }}</p>
              </div>
              <div class="p-4 bg-background-secondary rounded-lg">
                <p class="text-xs text-text-light mb-1">上课地点</p>
                <p class="font-medium text-text-primary">{{ selectedCourse?.location || selectedCourse?.class_location || '暂无' }}</p>
              </div>
            </div>
            
            <div class="mb-6">
              <h3 class="text-sm font-semibold text-text-primary mb-2">课程简介</h3>
              <p class="text-text-secondary leading-relaxed">{{ selectedCourse?.description || '暂无课程简介' }}</p>
            </div>
            
            <div class="flex gap-3">
              <button @click="showDetailModal = false" class="flex-1 px-4 py-2 border border-border rounded-lg text-text-secondary hover:bg-background-dark transition-colors">
                关闭
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import LazyImage from './LazyImage.vue';

const emit = defineEmits(['select-course']);

const searchQuery = ref('');
const selectedSemester = ref('');
const selectedType = ref('');
const showAddModal = ref(false);
const showEditModal = ref(false);
const editingCourse = ref(null);
const coverPreview = ref('');
const coverFile = ref(null);
const isUploading = ref(false);
const coverInput = ref(null);

// 课程详情相关
const showDetailModal = ref(false);
const selectedCourse = ref(null);

// 编辑模式与批量删除
const isEditMode = ref(false);
const selectedIds = ref([]);
const isAllSelected = ref(false);

// 表单错误状态
const errors = ref({});

const toggleEditMode = () => {
  isEditMode.value = !isEditMode.value;
  if (!isEditMode.value) {
    selectedIds.value = [];
    isAllSelected.value = false;
  }
};

const editCourse = (course) => {
  editingCourse.value = course;
  newCourse.value = {
    course_code: course.course_code || '',
    course_name: course.course_name || '',
    credits: course.credits || 3.0,
    hours: course.hours || 48,
    semester: course.semester || '2024-2025-1',
    course_type: course.course_type || '',
    teacher_name: course.teacher_name || '',
    teacher_title: course.teacher_title || '',
    description: course.description || '',
    schedule: course.schedule || course.class_time || '',
    location: course.location || course.class_location || '',
    class_location: course.class_location || course.location || '',
    class_time: course.class_time || course.schedule || '',
    cover: course.cover || ''
  };
  coverPreview.value = course.cover || '';
  coverFile.value = null;
  showEditModal.value = true;
};

const closeCourseModal = () => {
  showAddModal.value = false;
  showEditModal.value = false;
  editingCourse.value = null;
  errors.value = {};
  coverPreview.value = '';
  coverFile.value = null;
  if (coverInput.value) {
    coverInput.value.value = '';
  }
  newCourse.value = {
    course_code: '',
    course_name: '',
    credits: 0,
    hours: 0,
    semester: '2024-2025-1',
    course_type: '',
    teacher_name: '',
    teacher_title: '',
    description: '',
    schedule: '',
    location: '',
    class_location: '',
    class_time: '',
    cover: ''
  };
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
    selectedIds.value = filteredCourses.value.map(c => c.id);
    isAllSelected.value = true;
  }
};

const confirmBatchDelete = () => {
  if (selectedIds.value.length === 0) return;
  const confirmed = confirm(`确定要删除选中的 ${selectedIds.value.length} 门课程吗？此操作不可撤销。`);
  if (confirmed) {
    batchDeleteCourses();
  }
};

const batchDeleteCourses = async () => {
  try {
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    const response = await fetch('http://localhost:8000/api/knowledge/courses/batch-delete', {
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
      await loadCourses();
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

const newCourse = ref({
  course_code: '',
  course_name: '',
  credits: 0,
  hours: 0,
  semester: '2024-2025-1',
  course_type: '',
  teacher_name: '',
  teacher_title: '',
  description: '',
  schedule: '',
  location: '',
  class_location: '',
  class_time: '',
  cover: ''
});

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

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
  if (coverInput.value) {
    coverInput.value.value = '';
  }
};

// 表单验证
const validateForm = () => {
  errors.value = {};
  
  if (!newCourse.value.course_code.trim()) {
    errors.value.course_code = '请输入课程代码';
  }
  
  if (!newCourse.value.course_name.trim()) {
    errors.value.course_name = '请输入课程名称';
  }
  
  if (!newCourse.value.credits || newCourse.value.credits <= 0) {
    errors.value.credits = '请输入有效的学分（大于0）';
  }
  
  if (!newCourse.value.hours || newCourse.value.hours <= 0) {
    errors.value.hours = '请输入有效的学时（大于0）';
  }
  
  if (!newCourse.value.course_type) {
    errors.value.course_type = '请选择课程类型';
  }
  
  if (!newCourse.value.semester) {
    errors.value.semester = '请选择开学学期';
  }
  
  if (!newCourse.value.teacher_name.trim()) {
    errors.value.teacher_name = '请输入授课教师';
  }
  
  if (!newCourse.value.teacher_title) {
    errors.value.teacher_title = '请选择教师职称';
  }
  
  if (!newCourse.value.description.trim()) {
    errors.value.description = '请输入课程简介';
  } else if (newCourse.value.description.length < 50) {
    errors.value.description = '课程简介至少需要50字';
  } else if (newCourse.value.description.length > 500) {
    errors.value.description = '课程简介不能超过500字';
  }
  
  return Object.keys(errors.value).length === 0;
};

const addCourse = async () => {
  if (!validateForm()) {
    return;
  }
  
  isUploading.value = true;
  
  try {
    if (coverFile.value) {
      try {
        const formData = new FormData();
        formData.append('file', coverFile.value);
        
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        const response = await fetch('http://localhost:8000/api/upload/course-cover/temp', {
          method: 'POST',
          body: formData,
          headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });
        
        if (response.ok) {
          const result = await response.json();
          newCourse.value.cover = result.url;
        } else {
          console.warn('封面上传失败，将继续添加课程');
        }
      } catch (error) {
        console.warn('封面上传异常，将继续添加课程:', error);
      }
    }
    
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    const response = await fetch('http://localhost:8000/api/knowledge/courses', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      },
      body: JSON.stringify({
        course_code: newCourse.value.course_code,
        course_name: newCourse.value.course_name,
        credits: newCourse.value.credits,
        hours: newCourse.value.hours,
        semester: newCourse.value.semester,
        course_type: newCourse.value.course_type,
        description: newCourse.value.description,
        teacher_name: newCourse.value.teacher_name,
        teacher_title: newCourse.value.teacher_title,
        schedule: newCourse.value.schedule || newCourse.value.class_time || '',
        location: newCourse.value.location || newCourse.value.class_location || '',
        class_location: newCourse.value.class_location,
        class_time: newCourse.value.class_time,
        cover: newCourse.value.cover
      })
    });
    
    if (response.ok) {
      const result = await response.json();
      console.log('课程添加成功:', result);
      await loadCourses();
    } else {
      const error = await response.json();
      console.error('添加课程失败:', error.detail || '未知错误');
      alert(`添加课程失败: ${error.detail || '未知错误'}`);
    }
  } catch (error) {
    console.error('添加课程异常:', error);
    alert('添加课程失败，请重试');
  } finally {
    closeCourseModal();
    isUploading.value = false;
  }
};

const updateCourse = async () => {
  if (!validateForm()) {
    return;
  }
  
  isUploading.value = true;
  
  try {
    if (coverFile.value) {
      try {
        const formData = new FormData();
        formData.append('file', coverFile.value);
        
        const token = localStorage.getItem('access_token') || localStorage.getItem('token');
        const response = await fetch('http://localhost:8000/api/upload/course-cover/temp', {
          method: 'POST',
          body: formData,
          headers: token ? { 'Authorization': `Bearer ${token}` } : {}
        });
        
        if (response.ok) {
          const result = await response.json();
          newCourse.value.cover = result.url;
        } else {
          console.warn('封面上传失败，将继续更新课程');
        }
      } catch (error) {
        console.warn('封面上传异常，将继续更新课程:', error);
      }
    }
    
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    const response = await fetch(`http://localhost:8000/api/knowledge/courses/${editingCourse.value.id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      },
      body: JSON.stringify({
        course_code: newCourse.value.course_code,
        course_name: newCourse.value.course_name,
        credits: newCourse.value.credits,
        hours: newCourse.value.hours,
        semester: newCourse.value.semester,
        course_type: newCourse.value.course_type,
        description: newCourse.value.description,
        teacher_name: newCourse.value.teacher_name,
        teacher_title: newCourse.value.teacher_title,
        schedule: newCourse.value.class_time || newCourse.value.schedule || '',
        location: newCourse.value.class_location || newCourse.value.location || '',
        class_location: newCourse.value.class_location || newCourse.value.location || '',
        class_time: newCourse.value.class_time || newCourse.value.schedule || '',
        cover: newCourse.value.cover
      })
    });
    
    if (response.ok) {
      const result = await response.json();
      console.log('课程更新成功:', result);
      await loadCourses();
    } else {
      const error = await response.json();
      console.error('更新课程失败:', error.detail || '未知错误');
      alert(`更新课程失败: ${error.detail || '未知错误'}`);
    }
  } catch (error) {
    console.error('更新课程异常:', error);
    alert('更新课程失败，请重试');
  } finally {
    closeCourseModal();
    isUploading.value = false;
  }
};

const courses = ref([]);
const isLoading = ref(true);

// 从后端API获取课程列表
async function loadCourses() {
  isLoading.value = true;
  try {
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    const response = await fetch('http://localhost:8000/api/knowledge/courses', {
      headers: token ? { 'Authorization': `Bearer ${token}` } : {}
    });
    if (response.ok) {
      const data = await response.json();
      courses.value = data.map((c, idx) => ({
        id: c.id || String(idx + 1),
        course_code: c.course_code || '',
        course_name: c.course_name || c.id || '未知课程',
        credits: c.credits || 3.0,
        hours: c.hours || 48,
        semester: c.semester || '2024-2025-1',
        course_type: c.course_type || 'elective',
        teacher_name: c.teacher_name || '待定',
        teacher_title: c.teacher_title || '讲师',
        description: c.description || '',
        schedule: c.schedule || c.class_time || '',
        location: c.location || c.class_location || '',
        class_time: c.class_time || c.schedule || '',
        class_location: c.class_location || c.location || '',
        cover: c.cover || ''
      }));
    } else {
      console.warn('获取课程列表失败，使用空列表');
      courses.value = [];
    }
  } catch (e) {
    console.warn('加载课程列表异常:', e);
    courses.value = [];
  } finally {
    isLoading.value = false;
  }
}

// 初始化加载
loadCourses();

const filteredCourses = computed(() => {
  return courses.value.filter(course => {
    const matchSearch = !searchQuery.value || course.course_name.toLowerCase().includes(searchQuery.value.toLowerCase()) || course.teacher_name.toLowerCase().includes(searchQuery.value.toLowerCase()) || course.course_code.toLowerCase().includes(searchQuery.value.toLowerCase());
    const matchSemester = !selectedSemester.value || course.semester === selectedSemester.value;
    const matchType = !selectedType.value || course.course_type === selectedType.value;
    return matchSearch && matchSemester && matchType;
  });
});

// 显示课程详情
const showCourseDetail = (course) => {
  selectedCourse.value = course;
  showDetailModal.value = true;
};

// 格式化学期显示
const formatSemester = (semester) => {
  if (!semester) return '暂无';
  const parts = semester.split('-');
  if (parts.length === 3) {
    return `${parts[0]}-${parts[1]}学年第${parts[2] === '1' ? '一' : '二'}学期`;
  }
  return semester;
};
</script>

<style scoped>
.course-card:hover {
  transform: translateY(-2px);
}
</style>