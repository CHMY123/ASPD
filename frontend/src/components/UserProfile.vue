<template>
  <div class="profile-page">
    <div class="bg-gradient-to-br from-brand-mint to-brand-dark rounded-2xl p-6 mb-6">
      <div class="flex items-center gap-6">
        <div class="w-20 h-20 rounded-full overflow-hidden bg-white/20 backdrop-blur-sm flex-shrink-0">
          <img v-if="userData.avatar" :src="userData.avatar" alt="头像" class="w-full h-full object-cover" />
          <div v-else class="w-full h-full flex items-center justify-center">
            <svg class="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
        </div>
        <div class="text-white">
          <h2 class="text-xl font-semibold">{{ userData.real_name || '未设置' }}</h2>
          <p class="text-white/80 text-sm mt-1">{{ userData.student_id || '未设置' }}</p>
          <p class="text-white/60 text-xs mt-1">{{ userData.major || '未设置' }} · {{ userData.grade || '' }}级</p>
        </div>
        <div class="ml-auto flex flex-col gap-2">
          <button @click="openEditModal" class="px-4 py-2 bg-white/20 hover:bg-white/30 rounded-lg text-white text-sm font-medium transition-colors flex items-center gap-2 whitespace-nowrap">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
            编辑资料
          </button>
          <button @click="showLogoutConfirm = true" class="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-white text-sm font-medium transition-colors flex items-center gap-2 whitespace-nowrap">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            退出登录
          </button>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
      <div class="bg-background-primary border border-border rounded-xl p-4 shadow-soft">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-text-secondary">已修课程</span>
          <svg class="w-5 h-5 text-brand-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <p class="text-2xl font-semibold text-text-primary">{{ stats.completedCourses }}</p>
        <p class="text-xs text-text-light mt-1">共 {{ stats.totalCourses }} 门课程</p>
      </div>
      <div class="bg-background-primary border border-border rounded-xl p-4 shadow-soft">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-text-secondary">获得学分</span>
          <svg class="w-5 h-5 text-accent-coral" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
          </svg>
        </div>
        <p class="text-2xl font-semibold text-text-primary">{{ stats.creditsEarned }}</p>
        <p class="text-xs text-text-light mt-1">还需 {{ stats.creditsRequired - stats.creditsEarned }} 学分</p>
      </div>
      <div class="bg-background-primary border border-border rounded-xl p-4 shadow-soft">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-text-secondary">学习时长</span>
          <svg class="w-5 h-5 text-accent-lavender" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <p class="text-2xl font-semibold text-text-primary">{{ stats.studyHours }}</p>
        <p class="text-xs text-text-light mt-1">本学期累计</p>
      </div>
      <div class="bg-background-primary border border-border rounded-xl p-4 shadow-soft">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm text-text-secondary">平均绩点</span>
          <svg class="w-5 h-5 text-accent-orange" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
          </svg>
        </div>
        <p class="text-2xl font-semibold text-text-primary">{{ stats.gpa }}</p>
        <p class="text-xs text-text-light mt-1">专业排名前 {{ stats.rankPercent }}%</p>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 space-y-6">
        <div class="bg-background-primary border border-border rounded-xl p-6 shadow-soft">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-text-primary">学习进度</h3>
            <span class="text-xs text-text-light bg-background-secondary px-2 py-1 rounded-full">本学年</span>
          </div>
          <div class="space-y-4">
            <div v-for="course in recentCourses" :key="course.id">
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-lg bg-brand-light flex items-center justify-center">
                    <svg class="w-5 h-5 text-brand-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                    </svg>
                  </div>
                  <div>
                    <p class="text-sm font-medium text-text-primary">{{ course.name }}</p>
                    <p class="text-xs text-text-light">{{ course.teacher }}</p>
                  </div>
                </div>
                <span class="text-sm font-medium" :class="course.progress === 100 ? 'text-brand-mint' : 'text-text-secondary'">
                  {{ course.progress }}%
                </span>
              </div>
              <div class="w-full bg-background-secondary rounded-full h-2">
                <div class="h-2 rounded-full transition-all duration-500" :class="course.progress === 100 ? 'bg-brand-mint' : 'bg-brand-light'" :style="{ width: course.progress + '%' }"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-background-primary border border-border rounded-xl p-6 shadow-soft">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-lg font-semibold text-text-primary">学习记录</h3>
            <button class="text-sm text-brand-mint hover:text-brand-dark transition-colors">查看全部</button>
          </div>
          <div class="space-y-3">
            <div v-for="record in learningRecords" :key="record.id" class="flex items-center gap-4 p-3 rounded-lg hover:bg-background-secondary transition-colors">
              <div class="w-10 h-10 rounded-lg flex items-center justify-center" :class="record.type === 'course' ? 'bg-brand-light' : 'bg-accent-lavender/30'">
                <svg v-if="record.type === 'course'" class="w-5 h-5 text-brand-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <svg v-else class="w-5 h-5 text-accent-lavender" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
                </svg>
              </div>
              <div class="flex-1">
                <p class="text-sm font-medium text-text-primary">{{ record.title }}</p>
                <p class="text-xs text-text-light">{{ record.description }} · {{ record.time }}</p>
              </div>
              <span class="text-xs text-text-light">{{ record.duration }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="space-y-6">
        <div class="bg-background-primary border border-border rounded-xl p-6 shadow-soft">
          <h3 class="text-lg font-semibold text-text-primary mb-4">学习成就</h3>
          <div class="grid grid-cols-3 gap-3">
            <div v-for="achievement in achievements" :key="achievement.id" class="flex flex-col items-center p-3 rounded-lg" :class="achievement.unlocked ? 'bg-background-secondary' : 'bg-background-dark opacity-50'">
              <div class="text-2xl mb-1">{{ achievement.icon }}</div>
              <p class="text-xs text-text-secondary text-center">{{ achievement.name }}</p>
              <p v-if="achievement.unlocked" class="text-xs text-brand-mint mt-1">{{ achievement.date }}</p>
            </div>
          </div>
        </div>

        <div class="bg-background-primary border border-border rounded-xl p-6 shadow-soft">
          <h3 class="text-lg font-semibold text-text-primary mb-4">快捷设置</h3>
          <div class="space-y-2">
            <button v-for="setting in settings" :key="setting.id" class="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-background-secondary transition-colors text-left">
              <div class="w-10 h-10 rounded-lg flex items-center justify-center" :class="setting.iconBg">
                <svg class="w-5 h-5" :class="setting.iconColor" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path :d="setting.iconPath" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" />
                </svg>
              </div>
              <div class="flex-1">
                <p class="text-sm font-medium text-text-primary">{{ setting.name }}</p>
                <p class="text-xs text-text-light">{{ setting.description }}</p>
              </div>
              <svg class="w-5 h-5 text-text-light" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>

        <div class="bg-background-primary border border-border rounded-xl p-6 shadow-soft">
          <h3 class="text-lg font-semibold text-text-primary mb-4">安全设置</h3>
          <div class="space-y-2">
            <button class="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-background-secondary transition-colors text-left">
              <div class="w-10 h-10 rounded-lg bg-accent-coral/30 flex items-center justify-center">
                <svg class="w-5 h-5 text-accent-coral" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <div class="flex-1">
                <p class="text-sm font-medium text-text-primary">修改密码</p>
                <p class="text-xs text-text-light">定期更新密码以保证安全</p>
              </div>
              <svg class="w-5 h-5 text-text-light" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
            <button class="w-full flex items-center gap-3 p-3 rounded-lg hover:bg-background-secondary transition-colors text-left">
              <div class="w-10 h-10 rounded-lg bg-accent-orange/30 flex items-center justify-center">
                <svg class="w-5 h-5 text-accent-orange" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <div class="flex-1">
                <p class="text-sm font-medium text-text-primary">通知设置</p>
                <p class="text-xs text-text-light">管理消息推送偏好</p>
              </div>
              <svg class="w-5 h-5 text-text-light" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 编辑资料模态框 -->
    <div v-if="isModalOpen" class="modal-overlay fixed inset-0 bg-black/50 flex items-center justify-center z-50" @click.self="closeEditModal">
      <div class="modal bg-white rounded-2xl w-full max-w-md mx-4 overflow-hidden shadow-xl">
        <div class="modal-header px-6 py-4 border-b border-border flex items-center justify-between">
          <h2 class="text-lg font-semibold text-text-primary">编辑资料</h2>
          <button @click="closeEditModal" class="modal-close text-text-secondary hover:text-text-primary transition-colors">
            &times;
          </button>
        </div>
        
        <div class="modal-body px-6 py-4">
          <!-- 头像上传 -->
          <div class="flex flex-col items-center mb-4">
            <div class="relative">
              <div class="w-24 h-24 rounded-full overflow-hidden border-4 border-background-dark">
                <img 
                  :src="editAvatarPreview || userData.avatar || ''" 
                  alt="头像"
                  class="w-full h-full object-cover"
                  @error="onAvatarError"
                />
                <div v-if="!editAvatarPreview && !userData.avatar" class="w-full h-full bg-background-secondary flex items-center justify-center">
                  <svg class="w-10 h-10 text-text-light" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
              </div>
              <button 
                type="button"
                @click="triggerEditAvatarUpload"
                class="absolute bottom-0 right-0 w-8 h-8 rounded-full bg-brand-mint text-white flex items-center justify-center hover:bg-brand-dark transition-colors shadow-lg"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
              </button>
            </div>
            <input ref="editAvatarInput" type="file" accept="image/jpeg,image/png" class="hidden" @change="handleEditAvatarChange" />
            <p v-if="editAvatarFile" class="mt-2 text-xs text-text-secondary">{{ editAvatarFile.name }}</p>
          </div>
          <div class="space-y-4">
            <div class="form-group">
              <label for="edit_real_name" class="block text-sm font-medium text-text-primary mb-1.5">真实姓名</label>
              <input 
                v-model="editingProfile.real_name"
                type="text" 
                id="edit_real_name" 
                placeholder="请输入真实姓名"
                class="w-full px-4 py-2.5 border border-border rounded-lg focus:outline-none focus:border-brand-mint focus:ring-2 focus:ring-brand-mint/20 transition-all"
                required
              />
            </div>
            
            <div class="form-group">
              <label for="edit_student_id" class="block text-sm font-medium text-text-primary mb-1.5">学号</label>
              <input 
                v-model="editingProfile.student_id"
                type="text" 
                id="edit_student_id" 
                placeholder="请输入学号"
                class="w-full px-4 py-2.5 border border-border rounded-lg focus:outline-none focus:border-brand-mint focus:ring-2 focus:ring-brand-mint/20 transition-all"
              />
            </div>
            
            <div class="form-group">
              <label for="edit_major" class="block text-sm font-medium text-text-primary mb-1.5">专业</label>
              <input 
                v-model="editingProfile.major"
                type="text" 
                id="edit_major" 
                placeholder="请输入专业"
                class="w-full px-4 py-2.5 border border-border rounded-lg focus:outline-none focus:border-brand-mint focus:ring-2 focus:ring-brand-mint/20 transition-all"
              />
            </div>
            
            <div class="form-group">
              <label for="edit_grade" class="block text-sm font-medium text-text-primary mb-1.5">年级</label>
              <input 
                v-model="editingProfile.grade"
                type="text" 
                id="edit_grade" 
                placeholder="请输入年级（如：2021）"
                class="w-full px-4 py-2.5 border border-border rounded-lg focus:outline-none focus:border-brand-mint focus:ring-2 focus:ring-brand-mint/20 transition-all"
              />
            </div>
          </div>
          
          <div v-if="editError" class="form-error mt-4 p-3 bg-accent-coral/10 text-accent-coral rounded-lg text-sm">
            {{ editError }}
          </div>
          
          <div class="flex gap-3 mt-4">
            <button 
              @click="closeEditModal"
              class="flex-1 py-2.5 border border-border rounded-lg text-text-secondary hover:bg-background-secondary transition-all font-medium"
            >
              取消
            </button>
            <button 
              @click="saveProfile"
              :disabled="isLoading"
              class="flex-1 py-2.5 bg-brand-mint text-white rounded-lg hover:bg-brand-dark disabled:opacity-50 disabled:cursor-not-allowed transition-all font-medium"
            >
              {{ isLoading ? '保存中...' : '保存' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 退出登录确认对话框 -->
    <Teleport to="body">
      <div v-if="showLogoutConfirm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <div class="bg-background-primary rounded-xl p-6 w-full max-w-sm shadow-xl animate-scale-in">
          <div class="text-center">
            <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-accent-coral/10 flex items-center justify-center">
              <svg class="w-8 h-8 text-accent-coral" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-text-primary mb-2">确认退出</h3>
            <p class="text-sm text-text-secondary mb-6">确定要退出登录吗？</p>
            <div class="flex gap-3">
              <button @click="showLogoutConfirm = false" class="flex-1 px-4 py-2.5 border border-border rounded-lg text-text-secondary hover:bg-background-dark transition-colors text-sm font-medium">
                取消
              </button>
              <button @click="handleLogout" :disabled="isLoggingOut" class="flex-1 px-4 py-2.5 bg-accent-coral text-white rounded-lg hover:bg-accent-coral/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-sm font-medium">
                <svg v-if="isLoggingOut" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ isLoggingOut ? '退出中...' : '退出登录' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useAuthStore } from '../stores/auth';

const authStore = useAuthStore();

const userData = computed(() => authStore.user || {});
const isModalOpen = ref(false);
const editingProfile = ref({
  real_name: '',
  student_id: '',
  major: '',
  grade: ''
});
const editError = ref('');
const isLoading = ref(false);

// 头像上传相关
const editAvatarInput = ref(null);
const editAvatarFile = ref(null);
const editAvatarPreview = ref('');
const editUploadProgress = ref(0);

const defaultAvatar = '';

// 登出相关
const showLogoutConfirm = ref(false);
const isLoggingOut = ref(false);

onMounted(() => {
  if (authStore.isAuthenticated && !authStore.user) {
    authStore.fetchUser();
  }
});

const openEditModal = () => {
  editingProfile.value = {
    real_name: userData.value.real_name || '',
    student_id: userData.value.student_id || '',
    major: userData.value.major || '',
    grade: userData.value.grade || ''
  };
  editError.value = '';
  editAvatarFile.value = null;
  editAvatarPreview.value = '';
  isModalOpen.value = true;
};

const closeEditModal = () => {
  isModalOpen.value = false;
  editError.value = '';
  editAvatarFile.value = null;
  editAvatarPreview.value = '';
};

const triggerEditAvatarUpload = () => {
  editAvatarInput.value?.click();
};

const handleEditAvatarChange = (event) => {
  const file = event.target.files?.[0];
  if (file) {
    if (!['image/jpeg', 'image/png'].includes(file.type)) {
      editError.value = '请选择 JPG 或 PNG 格式的图片';
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      editError.value = '图片大小不能超过 5MB';
      return;
    }
    editAvatarFile.value = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      editAvatarPreview.value = e.target.result;
    };
    reader.readAsDataURL(file);
  }
};

const onAvatarError = (e) => {
  // 头像加载失败时静默处理
};

const saveProfile = async () => {
  editError.value = '';
  
  if (!editingProfile.value.real_name.trim()) {
    editError.value = '请填写真实姓名';
    return;
  }
  
  isLoading.value = true;
  
  try {
    // 先上传头像（如果有）
    if (editAvatarFile.value) {
      editUploadProgress.value = 0;
      const formData = new FormData();
      formData.append('file', editAvatarFile.value);
      
      const xhr = new XMLHttpRequest();
      xhr.open('POST', 'http://localhost:8000/api/upload/avatar');
      xhr.setRequestHeader('Authorization', `Bearer ${authStore.accessToken}`);
      
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          editUploadProgress.value = Math.round((e.loaded / e.total) * 100);
        }
      });
      
      const uploadResult = await new Promise((resolve, reject) => {
        xhr.onload = () => {
          if (xhr.status === 200) {
            resolve(JSON.parse(xhr.responseText));
          } else {
            reject(new Error('头像上传失败'));
          }
        };
        xhr.onerror = () => reject(new Error('网络错误'));
        xhr.send(formData);
      });
      
      editingProfile.value.avatar = uploadResult.url;
      editUploadProgress.value = 0;
    }
    
    const result = await authStore.updateUserProfile(editingProfile.value);
    if (result) {
      closeEditModal();
    } else {
      editError.value = '更新失败，请稍后重试';
    }
  } catch (err) {
    editError.value = err.message || '更新失败';
    editUploadProgress.value = 0;
  } finally {
    isLoading.value = false;
  }
};

const stats = ref({
  completedCourses: 23,
  totalCourses: 32,
  creditsEarned: 78,
  creditsRequired: 140,
  studyHours: '128h',
  gpa: '3.85',
  rankPercent: 15
});

const recentCourses = ref([
  { id: '1', name: '数据结构', teacher: '李老师', progress: 85 },
  { id: '2', name: '操作系统', teacher: '王老师', progress: 60 },
  { id: '3', name: '计算机网络', teacher: '张老师', progress: 100 },
  { id: '4', name: '人工智能导论', teacher: '陈老师', progress: 30 }
]);

const learningRecords = ref([
  { id: '1', type: 'course', title: '数据结构', description: '学习了第7章 图算法', time: '今天', duration: '45分钟' },
  { id: '2', type: 'chat', title: '智能问答', description: '提问: TCP三次握手', time: '今天', duration: '10分钟' },
  { id: '3', type: 'course', title: '操作系统', description: '学习了第4章 进程管理', time: '昨天', duration: '60分钟' },
  { id: '4', type: 'chat', title: '智能问答', description: '提问: 什么是二叉树', time: '昨天', duration: '15分钟' },
  { id: '5', type: 'course', title: '计算机网络', description: '完成课程学习', time: '3天前', duration: '120分钟' }
]);

const achievements = ref([
  { id: '1', icon: '🎉', name: '初出茅庐', unlocked: true, date: '2023.09' },
  { id: '2', icon: '📚', name: '知识渊博', unlocked: true, date: '2025.06' },
  { id: '3', icon: '🏆', name: '学霸', unlocked: true, date: '2026.01' },
  { id: '4', icon: '💻', name: '代码大师', unlocked: false },
  { id: '5', icon: '🎯', name: '学习达人', unlocked: true, date: '2025.06' },
  { id: '6', icon: '⭐', name: '全勤奖', unlocked: false }
]);

const settings = ref([
  { id: '1', name: '学习计划', description: '制定学习目标', iconBg: 'bg-brand-light', iconColor: 'text-brand-dark', iconPath: 'M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z' },
  { id: '2', name: '课程收藏', description: '管理收藏课程', iconBg: 'bg-accent-coral/30', iconColor: 'text-accent-coral', iconPath: 'M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z' },
  { id: '3', name: '学习报告', description: '查看学习统计', iconBg: 'bg-accent-sky/30', iconColor: 'text-accent-sky', iconPath: 'M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z' },
  { id: '4', name: '帮助中心', description: '获取使用帮助', iconBg: 'bg-accent-lavender/30', iconColor: 'text-accent-lavender', iconPath: 'M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z' }
]);

// 登出处理
const handleLogout = async () => {
  isLoggingOut.value = true;
  try {
    await authStore.logout();
    showLogoutConfirm.value = false;
    window.location.href = '/';
  } catch (error) {
    console.error('Logout failed:', error);
  } finally {
    isLoggingOut.value = false;
  }
};
</script>
