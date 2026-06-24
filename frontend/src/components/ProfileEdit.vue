<template>
  <div class="profile-edit max-w-2xl mx-auto p-6">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-semibold text-text-primary">编辑个人资料</h2>
      <button @click="$emit('back')" class="px-4 py-2 text-sm text-text-secondary hover:text-text-primary transition-colors">
        返回
      </button>
    </div>

    <form @submit.prevent="saveProfile" class="space-y-6">
      <!-- 头像上传 -->
      <div class="flex flex-col items-center">
        <label class="block text-sm font-medium text-text-primary mb-3">头像</label>
        <div class="relative">
          <div class="w-32 h-32 rounded-full overflow-hidden border-4 border-background-dark">
            <img 
              :src="avatarPreview || croppedPreview || (authStore.user?.avatar || defaultAvatar)" 
              :alt="authStore.user?.username"
              class="w-full h-full object-cover"
            />
          </div>
          
          <!-- 上传进度指示器 -->
          <div v-if="uploadProgress > 0 && uploadProgress < 100" class="absolute inset-0 bg-black/60 rounded-full flex items-center justify-center">
            <div class="text-center">
              <svg class="w-8 h-8 text-white animate-spin mx-auto mb-1" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span class="text-xs text-white">{{ uploadProgress }}%</span>
            </div>
          </div>
          
          <button 
            type="button"
            @click="triggerAvatarUpload"
            :disabled="uploadProgress > 0 && uploadProgress < 100"
            class="absolute bottom-0 right-0 w-10 h-10 rounded-full bg-brand-mint text-white flex items-center justify-center hover:bg-brand-dark transition-colors shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </button>
        </div>
        <input ref="avatarInput" type="file" accept="image/jpeg,image/png" class="hidden" @change="handleAvatarChange" />
        
        <!-- 头像操作按钮 -->
        <div v-if="avatarFile" class="flex items-center gap-2 mt-3">
          <span class="text-xs text-text-secondary">{{ avatarFile.name }} · {{ formatFileSize(avatarFile.size) }}</span>
          <button type="button" @click="openCropper" class="px-3 py-1 text-xs bg-brand-mint/10 text-brand-mint rounded-lg hover:bg-brand-mint/20 transition-colors">
            裁剪
          </button>
          <button type="button" @click="removeAvatar" class="px-3 py-1 text-xs bg-error-red/10 text-error-red rounded-lg hover:bg-error-red/20 transition-colors">
            移除
          </button>
        </div>
        <p class="mt-1 text-xs text-text-light">支持 JPG/PNG 格式，最大 5MB · 建议尺寸 200x200px</p>
      </div>

      <!-- 用户名 -->
      <div>
        <label class="block text-sm font-medium text-text-primary mb-1">用户名</label>
        <input 
          v-model="formData.username" 
          type="text" 
          required 
          class="w-full px-4 py-2 border border-border rounded-lg bg-background-primary focus:border-brand-mint focus:outline-none focus:ring-2 focus:ring-brand-mint/20"
          placeholder="请输入用户名"
        />
      </div>

      <!-- 邮箱 -->
      <div>
        <label class="block text-sm font-medium text-text-primary mb-1">邮箱</label>
        <input 
          v-model="formData.email" 
          type="email" 
          required 
          class="w-full px-4 py-2 border border-border rounded-lg bg-background-primary focus:border-brand-mint focus:outline-none focus:ring-2 focus:ring-brand-mint/20"
          placeholder="请输入邮箱"
        />
      </div>

      <!-- 真实姓名 -->
      <div>
        <label class="block text-sm font-medium text-text-primary mb-1">真实姓名</label>
        <input 
          v-model="formData.real_name" 
          type="text" 
          class="w-full px-4 py-2 border border-border rounded-lg bg-background-primary focus:border-brand-mint focus:outline-none focus:ring-2 focus:ring-brand-mint/20"
          placeholder="请输入真实姓名"
        />
      </div>

      <!-- 保存按钮 -->
      <div class="flex gap-3">
        <button 
          type="button" 
          @click="$emit('back')" 
          class="flex-1 px-4 py-2 border border-border rounded-lg text-text-secondary hover:bg-background-dark transition-colors"
        >
          取消
        </button>
        <button 
          type="submit" 
          :disabled="isSaving"
          class="flex-1 px-4 py-2 bg-brand-mint text-white rounded-lg hover:bg-brand-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
        >
          <svg v-if="isSaving" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          {{ isSaving ? '保存中...' : '保存' }}
        </button>
      </div>
    </form>

    <!-- 登出按钮区域 -->
    <div class="mt-8 pt-6 border-t border-border">
      <button 
        @click="showLogoutConfirm = true"
        :disabled="isLoggingOut"
        class="w-full px-4 py-3 bg-accent-coral/10 text-accent-coral rounded-lg hover:bg-accent-coral/20 transition-colors font-medium flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <svg v-if="isLoggingOut" class="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
        </svg>
        {{ isLoggingOut ? '退出中...' : '退出登录' }}
      </button>
    </div>

    <!-- 提示消息 -->
    <Transition name="fade">
      <div v-if="message" :class="['mt-4 p-3 rounded-lg text-sm', messageType === 'success' ? 'bg-success-green/20 text-success-green' : 'bg-error-red/20 text-error-red']">
        {{ message }}
      </div>
    </Transition>

    <!-- 图片裁剪模态框 -->
    <Teleport to="body">
      <div v-if="showCropper" class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
        <div class="bg-background-primary rounded-xl w-full max-w-2xl max-h-[90vh] overflow-hidden shadow-xl">
          <div class="flex items-center justify-between p-4 border-b border-border">
            <h3 class="text-lg font-semibold text-text-primary">裁剪头像</h3>
            <button @click="closeCropper" class="p-2 hover:bg-background-dark rounded-lg transition-colors">
              <svg class="w-5 h-5 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          <div class="p-6">
            <div class="relative overflow-hidden bg-background-dark rounded-lg mx-auto" 
                 :style="{ width: '100%', maxWidth: '500px' }"
                 @mousemove="handleCropMouseMove"
                 @mouseup="handleCropMouseUp"
                 @mouseleave="handleCropMouseUp"
                 @wheel="handleWheel">
              <img v-if="cropperImage" :src="cropperImage" class="max-w-full max-h-[400px] object-contain" />
              
              <!-- 裁剪框 -->
              <div 
                v-if="cropperImage"
                class="absolute border-2 border-brand-mint bg-brand-mint/20 cursor-move"
                :style="{
                  left: cropArea.x + 'px',
                  top: cropArea.y + 'px',
                  width: cropArea.size + 'px',
                  height: cropArea.size + 'px'
                }"
                @mousedown="handleCropMouseDown">
                <!-- 四角标记 -->
                <div class="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-brand-mint -mt-1 -ml-1"></div>
                <div class="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-brand-mint -mt-1 -mr-1"></div>
                <div class="absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 border-brand-mint -mb-1 -ml-1"></div>
                <div class="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-brand-mint -mb-1 -mr-1"></div>
              </div>
            </div>
            
            <p class="text-center text-sm text-text-light mt-3">拖动裁剪框选择区域 · 滚轮调整大小</p>
            
            <div class="flex gap-3 mt-6">
              <button @click="closeCropper" class="flex-1 px-4 py-2 border border-border rounded-lg text-text-secondary hover:bg-background-dark transition-colors">
                取消
              </button>
              <button @click="applyCrop" class="flex-1 px-4 py-2 bg-brand-mint text-white rounded-lg hover:bg-brand-dark transition-colors">
                应用裁剪
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 登出确认对话框 -->
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
            <p class="text-sm text-text-secondary mb-6">确定要退出登录吗？您的会话将被终止。</p>
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
import { ref, reactive, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useChatStore } from '../stores/chat';

const emit = defineEmits(['back', 'logout']);

const authStore = useAuthStore();
const chatStore = useChatStore();
const avatarInput = ref(null);
const avatarPreview = ref('');
const croppedPreview = ref('');
const avatarFile = ref(null);
const isSaving = ref(false);
const message = ref('');
const messageType = ref('success');
const uploadProgress = ref(0);
const showCropper = ref(false);
const cropperImage = ref(null);
const cropArea = reactive({
  x: 0,
  y: 0,
  size: 200
});
const isDragging = ref(false);
const dragStart = reactive({ x: 0, y: 0 });
const cropStart = reactive({ x: 0, y: 0 });

// 登出相关状态
const showLogoutConfirm = ref(false);
const isLoggingOut = ref(false);

const MAX_FILE_SIZE = 5 * 1024 * 1024; // 5MB

const defaultAvatar = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="%239CA3AF" stroke-width="2"%3E%3Cpath d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/%3E%3Ccircle cx="12" cy="7" r="4"/%3E%3C/svg%3E';

const formData = reactive({
  username: '',
  email: '',
  real_name: ''
});

onMounted(() => {
  if (authStore.user) {
    formData.username = authStore.user.username || '';
    formData.email = authStore.user.email || '';
    formData.real_name = authStore.user.real_name || '';
  }
});

const triggerAvatarUpload = () => {
  avatarInput.value?.click();
};

const validateImage = (file) => {
  const validTypes = ['image/jpeg', 'image/png'];
  if (!validTypes.includes(file.type)) {
    showMessage('请选择 JPG 或 PNG 格式的图片', 'error');
    return false;
  }
  if (file.size > MAX_FILE_SIZE) {
    showMessage('图片大小不能超过 5MB', 'error');
    return false;
  }
  return true;
};

const handleAvatarChange = (event) => {
  const file = event.target.files?.[0];
  if (file && validateImage(file)) {
    avatarFile.value = file;
    croppedPreview.value = '';
    const reader = new FileReader();
    reader.onload = (e) => {
      avatarPreview.value = e.target.result;
    };
    reader.readAsDataURL(file);
  }
};

const formatFileSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
};

const showMessage = (msg, type = 'success') => {
  message.value = msg;
  messageType.value = type;
  setTimeout(() => {
    message.value = '';
  }, 3000);
};

const removeAvatar = () => {
  avatarFile.value = null;
  avatarPreview.value = '';
  croppedPreview.value = '';
  if (avatarInput.value) {
    avatarInput.value.value = '';
  }
};

const openCropper = () => {
  if (!avatarPreview.value) return;
  cropperImage.value = avatarPreview.value;
  // 初始化裁剪区域
  const img = new Image();
  img.onload = () => {
    const minDimension = Math.min(img.width, img.height);
    cropArea.size = Math.min(minDimension, 200);
    cropArea.x = (img.width - cropArea.size) / 2;
    cropArea.y = (img.height - cropArea.size) / 2;
  };
  img.src = avatarPreview.value;
  showCropper.value = true;
};

const closeCropper = () => {
  showCropper.value = false;
};

const handleCropMouseDown = (e) => {
  isDragging.value = true;
  dragStart.x = e.clientX;
  dragStart.y = e.clientY;
  cropStart.x = cropArea.x;
  cropStart.y = cropArea.y;
};

const handleCropMouseMove = (e) => {
  if (!isDragging.value || !cropperImage.value) return;
  
  const img = new Image();
  img.src = cropperImage.value;
  
  const deltaX = e.clientX - dragStart.x;
  const deltaY = e.clientY - dragStart.y;
  
  let newX = cropStart.x + deltaX;
  let newY = cropStart.y + deltaY;
  
  // 边界限制
  newX = Math.max(0, Math.min(newX, img.width - cropArea.size));
  newY = Math.max(0, Math.min(newY, img.height - cropArea.size));
  
  cropArea.x = newX;
  cropArea.y = newY;
};

const handleCropMouseUp = () => {
  isDragging.value = false;
};

const handleWheel = (e) => {
  e.preventDefault();
  const delta = e.deltaY > 0 ? -10 : 10;
  const img = new Image();
  img.src = cropperImage.value;
  
  const newSize = Math.max(50, Math.min(Math.min(img.width, img.height), cropArea.size + delta));
  
  // 调整位置以保持中心
  const sizeDelta = newSize - cropArea.size;
  cropArea.x = Math.max(0, Math.min(cropArea.x - sizeDelta / 2, img.width - newSize));
  cropArea.y = Math.max(0, Math.min(cropArea.y - sizeDelta / 2, img.height - newSize));
  cropArea.size = newSize;
};

const applyCrop = async () => {
  if (!cropperImage.value) return;
  
  const img = new Image();
  img.crossOrigin = 'anonymous';
  
  img.onload = () => {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    const outputSize = 200;
    
    canvas.width = outputSize;
    canvas.height = outputSize;
    
    ctx.drawImage(
      img,
      cropArea.x,
      cropArea.y,
      cropArea.size,
      cropArea.size,
      0,
      0,
      outputSize,
      outputSize
    );
    
    croppedPreview.value = canvas.toDataURL('image/jpeg', 0.9);
    
    // 将裁剪后的图片转换为文件
    canvas.toBlob((blob) => {
      if (blob) {
        avatarFile.value = new File([blob], 'avatar_cropped.jpg', { type: 'image/jpeg' });
      }
    }, 'image/jpeg', 0.9);
    
    showCropper.value = false;
    showMessage('头像裁剪成功');
  };
  
  img.src = cropperImage.value;
};

const saveProfile = async () => {
  isSaving.value = true;
  
  try {
    // 上传头像（如果有）
    if (avatarFile.value) {
      uploadProgress.value = 0;
      
      const uploadFormData = new FormData();
      uploadFormData.append('file', avatarFile.value);
      
      const xhr = new XMLHttpRequest();
      xhr.open('POST', 'http://localhost:8000/api/upload/avatar');
      xhr.setRequestHeader('Authorization', `Bearer ${authStore.accessToken}`);
      
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          uploadProgress.value = Math.round((e.loaded / e.total) * 100);
        }
      });
      
      await new Promise((resolve, reject) => {
        xhr.onload = () => {
          uploadProgress.value = 100;
          if (xhr.status === 200) {
            const result = JSON.parse(xhr.responseText);
            formData.avatar = result.url;
            resolve(result);
          } else {
            reject(new Error('头像上传失败'));
          }
        };
        xhr.onerror = () => {
          uploadProgress.value = 0;
          reject(new Error('网络错误'));
        };
        xhr.send(uploadFormData);
      });
      
      setTimeout(() => {
        uploadProgress.value = 0;
      }, 1000);
    }
    
    // 更新用户资料
    const profileData = {
      username: formData.username,
      email: formData.email,
      real_name: formData.real_name
    };
    
    // 包含头像 URL（如果有）
    if (formData.avatar) {
      profileData.avatar = formData.avatar;
    }
    
    const response = await authStore.updateUserProfile(profileData);
    
    if (response) {
      showMessage('资料更新成功');
    } else {
      showMessage('更新失败', 'error');
    }
  } catch (error) {
    uploadProgress.value = 0;
    console.error('Profile update error:', error);
    showMessage('更新失败，请稍后重试', 'error');
  } finally {
    isSaving.value = false;
  }
};

// 登出处理
const handleLogout = async () => {
  isLoggingOut.value = true;
  
  try {
    await authStore.logout();
    chatStore.newConversation();
    showLogoutConfirm.value = false;
    emit('logout');
  } catch (error) {
    console.error('Logout failed:', error);
    showMessage('退出登录失败，请稍后重试', 'error');
  } finally {
    isLoggingOut.value = false;
  }
};
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>