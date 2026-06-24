<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="authStore.authError" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[100] p-4">
        <div class="bg-background-primary rounded-2xl p-6 max-w-sm w-full shadow-2xl">
          <div class="text-center">
            <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-error-red/20 flex items-center justify-center">
              <svg class="w-8 h-8 text-error-red" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-text-primary mb-2">登录状态异常</h3>
            <p class="text-sm text-text-secondary mb-6">{{ authStore.authError }}</p>
            <div class="flex gap-3">
              <button @click="handleRefresh" :disabled="isRefreshing" class="flex-1 px-4 py-2 border border-border rounded-lg text-text-secondary hover:bg-background-dark transition-colors disabled:opacity-50">
                刷新重试
              </button>
              <button @click="handleRelogin" class="flex-1 px-4 py-2 bg-brand-mint text-white rounded-lg hover:bg-brand-dark transition-colors">
                重新登录
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';

const authStore = useAuthStore();
const isRefreshing = ref(false);

const handleRefresh = async () => {
  isRefreshing.value = true;
  try {
    const success = await authStore.refreshAccessToken();
    if (success) {
      authStore.clearAuthError();
    }
  } catch (error) {
    console.error('Refresh failed:', error);
  } finally {
    isRefreshing.value = false;
  }
};

const handleRelogin = () => {
  authStore.redirectToLogin();
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