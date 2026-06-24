<template>
  <div class="course-detail">
    <div class="mb-6 flex items-center gap-4">
      <button
        @click="('back')"
        class="flex items-center gap-2 text-text-secondary hover:text-brand-mint transition-colors"
      >
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        返回课程列表
      </button>
    </div>

    <div class="bg-white rounded-2xl shadow-sm border border-border overflow-hidden">
      <div class="p-6 border-b border-border">
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-3 mb-3">
              <span
                :class="[
                  'px-3 py-1.5 rounded-full text-sm font-medium',
                  course.course_type === 'required' ? 'bg-success/10 text-success' : 'bg-accent-lavender/10 text-accent-lavender'
                ]"
              >
                {{ course.course_type === 'required' ? '必修课' : '选修课' }}
              </span>
              <span class="text-text-light">{{ course.course_code }}</span>
            </div>
            <h1 class="text-3xl font-bold text-text-primary mb-2">{{ course.course_name }}</h1>
            <p class="text-text-secondary">{{ course.description }}</p>
          </div>
          <div class="text-5xl">📖</div>
        </div>

        <div class="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div class="bg-background-secondary rounded-xl p-4 text-center">
            <div class="text-2xl font-bold text-brand-mint">{{ course.credits }}</div>
            <div class="text-sm text-text-secondary mt-1">学分</div>
          </div>
          <div class="bg-background-secondary rounded-xl p-4 text-center">
            <div class="text-2xl font-bold text-accent-orange">{{ course.hours }}</div>
            <div class="text-sm text-text-secondary mt-1">学时</div>
          </div>
          <div class="bg-background-secondary rounded-xl p-4 text-center">
            <div class="text-2xl font-bold text-accent-lavender">{{ course.semester }}</div>
            <div class="text-sm text-text-secondary mt-1">开课学期</div>
          </div>
          <div class="bg-background-secondary rounded-xl p-4 text-center">
            <div class="text-2xl font-bold text-accent-sky">{{ materials.length }}</div>
            <div class="text-sm text-text-secondary mt-1">课程资料</div>
          </div>
        </div>
      </div>

      <div class="grid md:grid-cols-3">
        <div class="md:col-span-2 p-6 border-r border-border">
          <div class="mb-8">
            <h2 class="text-xl font-semibold text-text-primary mb-4 flex items-center gap-2">
              <svg class="w-5 h-5 text-brand-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              课程大纲
            </h2>
            <div class="bg-background-secondary rounded-xl p-4">
              <ul class="space-y-3">
                <li v-for="(chapter, index) in syllabusChapters" :key="index" class="flex items-start gap-3">
                  <span class="w-6 h-6 flex items-center justify-center bg-brand-mint/10 text-brand-mint rounded-full text-sm font-medium flex-shrink-0">
                    {{ index + 1 }}
                  </span>
                  <span class="text-text-primary">{{ chapter }}</span>
                </li>
              </ul>
            </div>
          </div>

          <div class="mb-8">
            <h2 class="text-xl font-semibold text-text-primary mb-4 flex items-center gap-2">
              <svg class="w-5 h-5 text-brand-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              考核方式
            </h2>
            <div class="bg-background-secondary rounded-xl p-4">
              <div class="space-y-2">
                <div v-for="(item, index) in assessmentItems" :key="index" class="flex items-center justify-between">
                  <span class="text-text-secondary">{{ item.name }}</span>
                  <span class="font-semibold text-text-primary">{{ item.percentage }}</span>
                </div>
              </div>
            </div>
          </div>

          <div>
            <h2 class="text-xl font-semibold text-text-primary mb-4 flex items-center gap-2">
              <svg class="w-5 h-5 text-brand-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              课程资料
            </h2>
            <div class="space-y-3">
              <div
                v-for="(material, index) in materials"
                :key="index"
                class="flex items-center justify-between p-4 bg-background-secondary rounded-xl hover:bg-background-dark transition-colors cursor-pointer group"
              >
                <div class="flex items-center gap-3">
                  <div :class="[
                    'w-10 h-10 rounded-lg flex items-center justify-center',
                    material.type === 'pdf' ? 'bg-accent-coral/10 text-accent-coral' :
                    material.type === 'ppt' ? 'bg-accent-orange/10 text-accent-orange' :
                    'bg-accent-sky/10 text-accent-sky'
                  ]">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                  </div>
                  <div>
                    <h4 class="font-medium text-text-primary group-hover:text-brand-mint transition-colors">{{ material.title }}</h4>
                    <p class="text-sm text-text-light">{{ material.size }} · {{ material.upload_time }}</p>
                  </div>
                </div>
                <button class="flex items-center gap-2 px-3 py-1.5 text-sm text-brand-mint hover:bg-brand-mint/10 rounded-lg transition-colors">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  下载
                </button>
              </div>
            </div>
          </div>
        </div>

        <div class="p-6">
          <div class="bg-background-secondary rounded-xl p-5">
            <h3 class="text-lg font-semibold text-text-primary mb-4 flex items-center gap-2">
              <svg class="w-5 h-5 text-brand-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
              授课教师
            </h3>
            <div class="flex items-center gap-4 mb-4">
              <div class="w-14 h-14 rounded-full bg-brand-mint/10 flex items-center justify-center text-2xl">👨‍🏫</div>
              <div>
                <h4 class="font-semibold text-text-primary">{{ course.teacher_name }}</h4>
                <p class="text-sm text-text-secondary">{{ course.teacher_title }}</p>
              </div>
            </div>
            <div class="space-y-3 text-sm text-text-secondary">
              <div class="flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
                <span>{{ course.teacher_name }}@scnu.edu.cn</span>
              </div>
              <div class="flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
                <span>020-12345678</span>
              </div>
            </div>
          </div>

          <div class="mt-4 bg-accent-lavender/10 rounded-xl p-5">
            <h3 class="text-lg font-semibold text-text-primary mb-3 flex items-center gap-2">
              <svg class="w-5 h-5 text-accent-lavender" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
              快速问答
            </h3>
            <button
              @click="handleQuickQuestion"
              class="w-full py-3 bg-white border border-border rounded-lg hover:border-brand-mint hover:text-brand-mint transition-all text-left"
            >
              <span class="text-sm text-text-secondary">关于这门课程，我可以帮您解答什么问题？</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  course: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['back', 'quick-question'])

const materials = [
  { id: '1', title: '第1章-线性表.pdf', type: 'pdf', size: '2.3 MB', upload_time: '2024-09-01' },
  { id: '2', title: '第2章-树与二叉树.pdf', type: 'pdf', size: '3.1 MB', upload_time: '2024-09-10' },
  { id: '3', title: '数据结构课程PPT.pptx', type: 'ppt', size: '15.2 MB', upload_time: '2024-08-25' },
  { id: '4', title: '实验指导书.pdf', type: 'pdf', size: '1.8 MB', upload_time: '2024-09-05' }
]

const syllabusChapters = computed(() => {
  try {
    const syllabus = JSON.parse(props.course.syllabus)
    return syllabus.chapters || []
  } catch {
    return ['课程介绍', '核心内容', '实践应用']
  }
})

const assessmentItems = computed(() => {
  const method = props.course.assessment_method
  const items = []
  if (method.includes('考勤')) {
    const match = method.match(/考勤(\d+)%/)
    items.push({ name: '考勤', percentage: (match ? match[1] : '10') + '%' })
  }
  if (method.includes('作业')) {
    const match = method.match(/作业(\d+)%/)
    items.push({ name: '作业', percentage: (match ? match[1] : '30') + '%' })
  }
  if (method.includes('实验')) {
    const match = method.match(/实验(\d+)%/)
    items.push({ name: '实验', percentage: (match ? match[1] : '20') + '%' })
  }
  if (method.includes('考试')) {
    const match = method.match(/考试(\d+)%/)
    items.push({ name: '期末考试', percentage: (match ? match[1] : '40') + '%' })
  }
  return items
})

const handleQuickQuestion = () => {
  emit('quick-question', props.course)
}
</script>
