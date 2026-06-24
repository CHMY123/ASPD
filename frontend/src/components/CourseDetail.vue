<template>
  <div class="course-detail">
    <div class="flex items-center gap-4 mb-6">
      <button @click="$emit('back')" class="p-2 rounded-lg hover:bg-background-dark transition-colors">
        <svg class="w-5 h-5 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <h2 class="text-2xl font-semibold text-text-primary">{{ course?.course_name }}</h2>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 space-y-6">
        <div class="bg-background-primary border border-border rounded-xl p-6 shadow-soft">
          <h3 class="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
            <svg class="w-5 h-5 text-brand-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            课程信息
          </h3>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="p-4 bg-background-secondary rounded-lg">
              <p class="text-xs text-text-light mb-1">课程编号</p>
              <p class="text-sm font-medium text-text-primary">{{ course?.course_code }}</p>
            </div>
            <div class="p-4 bg-background-secondary rounded-lg">
              <p class="text-xs text-text-light mb-1">学分</p>
              <p class="text-sm font-medium text-brand-mint">{{ course?.credits }}</p>
            </div>
            <div class="p-4 bg-background-secondary rounded-lg">
              <p class="text-xs text-text-light mb-1">学时</p>
              <p class="text-sm font-medium text-text-primary">{{ course?.hours }}</p>
            </div>
            <div class="p-4 bg-background-secondary rounded-lg">
              <p class="text-xs text-text-light mb-1">课程类型</p>
              <span class="inline-block px-2 py-1 text-xs font-medium rounded-full" :class="course?.course_type === 'required' ? 'bg-brand-light text-brand-dark' : 'bg-accent-lavender/30 text-accent-lavender'">
                {{ course?.course_type === 'required' ? '必修课' : '选修课' }}
              </span>
            </div>
          </div>
        </div>

        <div class="bg-background-primary border border-border rounded-xl p-6 shadow-soft">
          <h3 class="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
            <svg class="w-5 h-5 text-brand-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
            课程大纲
          </h3>
          <p class="text-text-secondary leading-relaxed">{{ course?.description || '本课程介绍数据结构的基本概念、常用数据结构（线性表、树、图等）及其操作算法，培养学生的算法思维和程序设计能力。' }}</p>
        </div>

        <div class="bg-background-primary border border-border rounded-xl p-6 shadow-soft">
          <h3 class="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
            <svg class="w-5 h-5 text-brand-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            教学进度
          </h3>
          <div class="space-y-3">
            <div v-for="(week, index) in courseSchedule" :key="index" class="flex items-start gap-4 p-3 bg-background-secondary rounded-lg">
              <div class="w-8 h-8 rounded-full bg-brand-mint text-white flex items-center justify-center text-sm font-medium flex-shrink-0">{{ index + 1 }}</div>
              <div>
                <p class="text-sm font-medium text-text-primary">{{ week.topic }}</p>
                <p class="text-xs text-text-light mt-1">{{ week.content }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-background-primary border border-border rounded-xl p-6 shadow-soft">
          <h3 class="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
            <svg class="w-5 h-5 text-brand-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            考核方式
          </h3>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="text-center p-4 bg-background-secondary rounded-lg">
              <div class="text-2xl font-bold text-brand-mint">{{ assessment.attendance }}%</div>
              <div class="text-xs text-text-light mt-1">考勤</div>
            </div>
            <div class="text-center p-4 bg-background-secondary rounded-lg">
              <div class="text-2xl font-bold text-accent-orange">{{ assessment.homework }}%</div>
              <div class="text-xs text-text-light mt-1">作业</div>
            </div>
            <div class="text-center p-4 bg-background-secondary rounded-lg">
              <div class="text-2xl font-bold text-accent-lavender">{{ assessment.experiment }}%</div>
              <div class="text-xs text-text-light mt-1">实验</div>
            </div>
            <div class="text-center p-4 bg-background-secondary rounded-lg">
              <div class="text-2xl font-bold text-accent-coral">{{ assessment.exam }}%</div>
              <div class="text-xs text-text-light mt-1">期末考试</div>
            </div>
          </div>
        </div>
      </div>

      <div class="space-y-6">
        <div class="bg-background-primary border border-border rounded-xl p-6 shadow-soft sticky top-6">
          <h3 class="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
            <svg class="w-5 h-5 text-brand-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            授课教师
          </h3>
          <div class="flex items-center gap-4">
            <div class="w-16 h-16 rounded-full bg-brand-light flex items-center justify-center">
              <svg class="w-8 h-8 text-brand-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div>
              <p class="font-semibold text-text-primary">{{ course?.teacher_name }}</p>
              <p class="text-sm text-text-secondary">{{ course?.teacher_title }}</p>
              <p class="text-xs text-text-light mt-1">计算机科学与技术学院</p>
            </div>
          </div>
          <button class="mt-4 w-full py-2 border border-brand-mint text-brand-mint rounded-lg hover:bg-brand-mint hover:text-white transition-colors text-sm font-medium">
            联系教师
          </button>
        </div>

        <div class="bg-background-primary border border-border rounded-xl p-6 shadow-soft">
          <h3 class="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
            <svg class="w-5 h-5 text-brand-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            课程资料
          </h3>
          <div class="space-y-2">
            <div v-for="material in materials" :key="material.id" class="flex items-center justify-between p-3 bg-background-secondary rounded-lg hover:bg-background-dark transition-colors cursor-pointer group" @click="downloadMaterial(material)">
              <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-lg flex items-center justify-center" :class="getMaterialIconClass(material.type)">
                  <svg class="w-5 h-5" :class="getMaterialIconColor(material.type)" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                </div>
                <div>
                  <p class="text-sm font-medium text-text-primary group-hover:text-brand-mint transition-colors">{{ material.name }}</p>
                  <p class="text-xs text-text-light">{{ material.size }} - {{ material.date }}</p>
                </div>
              </div>
              <svg class="w-5 h-5 text-text-light group-hover:text-brand-mint transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
            </div>
          </div>
        </div>

        <div class="bg-background-primary border border-border rounded-xl p-6 shadow-soft">
          <h3 class="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
            <svg class="w-5 h-5 text-brand-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            上课时间
          </h3>
          <div class="space-y-2">
            <div v-if="course?.schedule" class="flex items-center gap-2 text-sm text-text-secondary">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ course.schedule }}
            </div>
            <div v-if="course?.location" class="flex items-center gap-2 text-sm text-text-secondary">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              {{ course.location }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

defineProps({
  course: { type: Object, default: () => ({}) }
});

defineEmits(['back']);

const courseSchedule = ref([
  { topic: '课程介绍', content: '课程概述、教学目标、学习要求' },
  { topic: '线性表', content: '数组、链表、栈、队列的概念与实现' },
  { topic: '树与二叉树', content: '二叉树性质、遍历算法、应用场景' },
  { topic: '图', content: '图的表示、深度优先和广度优先遍历' },
  { topic: '排序算法', content: '快速排序、归并排序、堆排序' },
  { topic: '查找算法', content: '二分查找、哈希查找、B+树' },
  { topic: '综合复习', content: '知识点回顾、答疑、考试指导' }
]);

const assessment = ref({ attendance: 10, homework: 20, experiment: 20, exam: 50 });

const materials = ref([
  { id: '1', name: '数据结构课程大纲.pdf', type: 'pdf', size: '256 KB', date: '2024-09-01' },
  { id: '2', name: '第1章 线性表.pptx', type: 'ppt', size: '1.2 MB', date: '2024-09-05' },
  { id: '3', name: '实验指导书.docx', type: 'doc', size: '512 KB', date: '2024-09-03' },
  { id: '4', name: '习题集.pdf', type: 'pdf', size: '768 KB', date: '2024-09-10' }
]);

const getMaterialIconClass = (type) => {
  const classes = { pdf: 'bg-accent-coral/20', ppt: 'bg-accent-orange/20', doc: 'bg-accent-sky/20', zip: 'bg-accent-lavender/20' };
  return classes[type] || 'bg-background-dark';
};

const getMaterialIconColor = (type) => {
  const colors = { pdf: 'text-accent-coral', ppt: 'text-accent-orange', doc: 'text-accent-sky', zip: 'text-accent-lavender' };
  return colors[type] || 'text-text-secondary';
};

const downloadMaterial = (material) => {
  alert('下载: ' + material.name);
};
</script>
