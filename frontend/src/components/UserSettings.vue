<template>
  <div class="user-settings">
    <div class="mb-6">
      <h2 class="text-2xl font-semibold text-text-primary">个人设置</h2>
      <p class="text-text-secondary text-sm mt-1">管理您的账户信息和偏好设置</p>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 space-y-6">
        <div class="bg-white rounded-xl border border-border p-6">
          <h3 class="text-lg font-semibold text-text-primary mb-4">基本信息</h3>
          <div class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-text-primary mb-1.5">用户名</label>
                <input 
                  v-model="form.username"
                  type="text" 
                  readonly
                  class="w-full px-4 py-2.5 border border-border rounded-lg bg-background-secondary text-text-primary"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-text-primary mb-1.5">学号</label>
                <input 
                  v-model="form.studentId"
                  type="text" 
                  readonly
                  class="w-full px-4 py-2.5 border border-border rounded-lg bg-background-secondary text-text-primary"
                />
              </div>
            </div>
            
            <div>
              <label class="block text-sm font-medium text-text-primary mb-1.5">邮箱</label>
              <input 
                v-model="form.email"
                type="email" 
                class="w-full px-4 py-2.5 border border-border rounded-lg focus:outline-none focus:border-brand-mint focus:ring-2 focus:ring-brand-mint/20 transition-all"
              />
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-text-primary mb-1.5">真实姓名</label>
                <input 
                  v-model="form.realName"
                  type="text" 
                  class="w-full px-4 py-2.5 border border-border rounded-lg focus:outline-none focus:border-brand-mint focus:ring-2 focus:ring-brand-mint/20 transition-all"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-text-primary mb-1.5">专业</label>
                <input 
                  v-model="form.major"
                  type="text" 
                  class="w-full px-4 py-2.5 border border-border rounded-lg focus:outline-none focus:border-brand-mint focus:ring-2 focus:ring-brand-mint/20 transition-all"
                />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-text-primary mb-1.5">年级</label>
              <select 
                v-model="form.grade"
                class="w-full px-4 py-2.5 border border-border rounded-lg focus:outline-none focus:border-brand-mint focus:ring-2 focus:ring-brand-mint/20 transition-all bg-white"
              >
                <option value="">请选择年级</option>
                <option value="2021">2021级</option>
                <option value="2022">2022级</option>
                <option value="2023">2023级</option>
                <option value="2024">2024级</option>
                <option value="2025">2025级</option>
              </select>
            </div>
          </div>

          <button 
            @click="saveProfile"
            :disabled="isSaving"
            class="mt-6 px-6 py-2.5 bg-brand-mint text-white rounded-lg hover:bg-brand-dark disabled:opacity-50 disabled:cursor-not-allowed transition-all font-medium"
          >
            {{ isSaving ? "保存中..." : "保存更改" }}
          </button>
        </div>

        <div class="bg-white rounded-xl border border-border p-6">
          <h3 class="text-lg font-semibold text-text-primary mb-4">修改密码</h3>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-text-primary mb-1.5">当前密码</label>
              <input 
                v-model="passwordForm.currentPassword"
                type="password" 
                placeholder="请输入当前密码"
                class="w-full px-4 py-2.5 border border-border rounded-lg focus:outline-none focus:border-brand-mint focus:ring-2 focus:ring-brand-mint/20 transition-all"
              />
            </div>
            
            <div>
              <label class="block text-sm font-medium text-text-primary mb-1.5">新密码</label>
              <input 
                v-model="passwordForm.newPassword"
                type="password" 
                placeholder="请输入新密码（至少6位）"
                class="w-full px-4 py-2.5 border border-border rounded-lg focus:outline-none focus:border-brand-mint focus:ring-2 focus:ring-brand-mint/20 transition-all"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-text-primary mb-1.5">确认新密码</label>
              <input 
                v-model="passwordForm.confirmPassword"
                type="password" 
                placeholder="再次输入新密码"
                class="w-full px-4 py-2.5 border border-border rounded-lg focus:outline-none focus:border-brand-mint focus:ring-2 focus:ring-brand-mint/20 transition-all"
              />
            </div>
          </div>

          <button 
            @click="changePassword"
            :disabled="isChangingPassword"
            class="mt-6 px-6 py-2.5 bg-accent-coral text-white rounded-lg hover:bg-error disabled:opacity-50 disabled:cursor-not-allowed transition-all font-medium"
          >
            {{ isChangingPassword ? "修改中..." : "修改密码" }}
          </button>

          <div v-if="passwordError" class="mt-4 p-3 bg-accent-coral/10 text-accent-coral rounded-lg text-sm">
            {{ passwordError }}
          </div>
        </div>
      </div>

      <div class="space-y-6">
        <div class="bg-white rounded-xl border border-border p-6">
          <div class="flex flex-col items-center">
            <div class="w-24 h-24 rounded-full bg-brand-mint/10 flex items-center justify-center text-4xl mb-4">👤</div>
            <h4 class="font-semibold text-text-primary text-lg">{{ authStore.currentUser?.username }}</h4>
            <p class="text-sm text-text-secondary">{{ authStore.currentUser?.role }}</p>
            
            <button class="mt-4 px-4 py-2 border border-border text-text-secondary rounded-lg hover:bg-background-secondary transition-all text-sm">
              更换头像
            </button>
          </div>
        </div>

        <div class="bg-white rounded-xl border border-border p-6">
          <h3 class="text-lg font-semibold text-text-primary mb-4">账户安全</h3>
          <div class="space-y-4">
            <div class="flex items-center justify-between">
              <div>
                <p class="font-medium text-text-primary">双因素认证</p>
                <p class="text-xs text-text-light">增强账户安全性</p>
              </div>
              <div class="w-12 h-6 bg-background-dark rounded-full cursor-pointer relative">
                <div class="w-5 h-5 bg-text-light rounded-full absolute top-0.5 left-0.5 transition-all"></div>
              </div>
            </div>
            
            <div class="flex items-center justify-between">
              <div>
                <p class="font-medium text-text-primary">登录通知</p>
                <p class="text-xs text-text-light">登录时发送通知</p>
              </div>
              <div class="w-12 h-6 bg-brand-mint rounded-full cursor-pointer relative">
                <div class="w-5 h-5 bg-white rounded-full absolute top-0.5 right-0.5 transition-all"></div>
              </div>
            </div>
            
            <div class="flex items-center justify-between">
              <div>
                <p class="font-medium text-text-primary">活动日志</p>
                <p class="text-xs text-text-light">记录账户活动</p>
              </div>
              <div class="w-12 h-6 bg-brand-mint rounded-full cursor-pointer relative">
                <div class="w-5 h-5 bg-white rounded-full absolute top-0.5 right-0.5 transition-all"></div>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-accent-coral/10 rounded-xl border border-accent-coral/20 p-6">
          <h3 class="text-lg font-semibold text-accent-coral mb-2">删除账户</h3>
          <p class="text-sm text-text-secondary mb-4">删除后将无法恢复，请谨慎操作</p>
          <button class="w-full px-4 py-2.5 bg-error text-white rounded-lg hover:bg-red-700 transition-all text-base font-black shadow-lg hover:shadow-xl hover:scale-105">
            删除账户
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { useAuthStore } from "../stores/auth";

const authStore = useAuthStore();

const isSaving = ref(false);
const isChangingPassword = ref(false);
const passwordError = ref("");

const form = reactive({
  username: authStore.currentUser?.username || "",
  studentId: "2021001001",
  email: authStore.currentUser?.email || "",
  realName: "张三",
  major: "计算机科学与技术",
  grade: "2021"
});

const passwordForm = reactive({
  currentPassword: "",
  newPassword: "",
  confirmPassword: ""
});

const saveProfile = async () => {
  isSaving.value = true;
  try {
    await new Promise(resolve => setTimeout(resolve, 1000));
    alert("个人信息更新成功");
  } catch (error) {
    console.error("Failed to save profile:", error);
  } finally {
    isSaving.value = false;
  }
};

const changePassword = async () => {
  passwordError.value = "";
  
  if (!passwordForm.currentPassword) {
    passwordError.value = "请输入当前密码";
    return;
  }
  
  if (!passwordForm.newPassword || passwordForm.newPassword.length < 6) {
    passwordError.value = "新密码至少需要6个字符";
    return;
  }
  
  if (passwordForm.newPassword !== passwordForm.confirmPassword) {
    passwordError.value = "两次输入的密码不一致";
    return;
  }
  
  isChangingPassword.value = true;
  try {
    await new Promise(resolve => setTimeout(resolve, 1000));
    alert("密码修改成功");
    passwordForm.currentPassword = "";
    passwordForm.newPassword = "";
    passwordForm.confirmPassword = "";
  } catch (error) {
    passwordError.value = "密码修改失败，请检查当前密码是否正确";
  } finally {
    isChangingPassword.value = false;
  }
};
</script>
