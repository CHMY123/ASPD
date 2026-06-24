import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('access_token') || '');
  const refreshToken = ref(localStorage.getItem('refresh_token') || '');
  const user = ref(null);
  const loading = ref(false);
  const error = ref(null);
  const userInitialized = ref(false);
  const authError = ref(null);
  const showLoginModal = ref(false);

  const hasToken = computed(() => !!accessToken.value);
  
  const isAuthenticated = computed(() => {
    return !!accessToken.value && !!user.value;
  });

  // 检测登录状态异常
  function detectAuthError(response) {
    if (response.status === 401 || response.status === 403) {
      authError.value = '登录状态已过期，请重新登录';
      showLoginModal.value = true;
      return true;
    }
    return false;
  }

  // 清除错误状态
  function clearAuthError() {
    authError.value = null;
    showLoginModal.value = false;
  }

  // 自动跳转到登录页
  async function redirectToLogin() {
    await logout();
    window.location.href = '/login';
  }

  async function login(username, password) {
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch('http://localhost:8000/api/auth/login/json', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }
      
      const data = await response.json();
      accessToken.value = data.access_token;
      refreshToken.value = data.refresh_token;
      
      localStorage.setItem('access_token', accessToken.value);
      localStorage.setItem('refresh_token', refreshToken.value);
      
      user.value = data.user;
      userInitialized.value = true;
      return true;
    } catch (err) {
      error.value = err.message;
      console.error('Login error:', err);
      return false;
    } finally {
      loading.value = false;
    }
  }

  async function register(username, email, password, realName) {
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch('http://localhost:8000/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
          username, 
          email, 
          password,
          real_name: realName
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Registration failed');
      }
      
      const data = await response.json();
      return data;
    } catch (err) {
      error.value = err.message;
      console.error('Registration error:', err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function logout() {
    try {
      await fetch('http://localhost:8000/api/auth/logout', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken.value}`
        }
      });
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      accessToken.value = '';
      refreshToken.value = '';
      user.value = null;
      userInitialized.value = false;
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  }

  async function fetchUser() {
    if (!accessToken.value) {
      return null;
    }
    
    loading.value = true;
    error.value = null;
    try {
      console.log('Fetching user with token:', accessToken.value.substring(0, 20) + '...');
      
      const response = await fetch('http://localhost:8000/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${accessToken.value}`
        }
      });
      
      console.log('Response status:', response.status);
      
      if (!response.ok) {
        if (response.status === 401) {
          console.log('Token expired, trying to refresh...');
          const refreshed = await refreshAccessToken();
          if (refreshed) {
            console.log('Token refreshed successfully');
            return await fetchUser();
          }
        }
        throw new Error(`Failed to fetch user: ${response.status}`);
      }
      
      const userData = await response.json();
      console.log('User data received:', userData);
      
      user.value = userData;
      userInitialized.value = true;
      return user.value;
    } catch (err) {
      error.value = err.message;
      console.error('Fetch user error:', err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function refreshAccessToken() {
    if (!refreshToken.value) {
      return false;
    }
    
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch('http://localhost:8000/api/auth/refresh', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ refresh_token: refreshToken.value })
      });
      
      if (!response.ok) {
        throw new Error('Failed to refresh token');
      }
      
      const data = await response.json();
      accessToken.value = data.access_token;
      localStorage.setItem('access_token', accessToken.value);
      
      return true;
    } catch (err) {
      error.value = err.message;
      console.error('Refresh token error:', err);
      await logout();
      return false;
    } finally {
      loading.value = false;
    }
  }

  async function updateUserProfile(data) {
    loading.value = true;
    error.value = null;
    try {
      const response = await fetch('http://localhost:8000/api/auth/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken.value}`
        },
        body: JSON.stringify(data)
      });
      
      if (!response.ok) {
        throw new Error('Failed to update profile');
      }
      
      user.value = await response.json();
      return user.value;
    } catch (err) {
      error.value = err.message;
      console.error('Update profile error:', err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  return {
    accessToken,
    refreshToken,
    user,
    loading,
    error,
    userInitialized,
    authError,
    showLoginModal,
    hasToken,
    isAuthenticated,
    login,
    register,
    logout,
    fetchUser,
    refreshAccessToken,
    updateUserProfile,
    detectAuthError,
    clearAuthError,
    redirectToLogin
  };
});
