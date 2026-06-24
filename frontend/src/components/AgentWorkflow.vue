<template>
  <div class="agent-workflow">
    <!-- 头部 -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h2 class="text-2xl font-semibold text-text-primary">多Agent智能问答系统</h2>
        <p class="text-sm text-text-secondary mt-1">基于多Agent协同的智能问答工作流</p>
      </div>
      <div class="flex items-center gap-3">
        <button 
          @click="refreshStatus" 
          class="px-4 py-2 bg-background-secondary rounded-lg text-sm text-text-secondary hover:bg-background-dark transition-colors flex items-center gap-2"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          刷新状态
        </button>
      </div>
    </div>

    <!-- 工作流可视化区域 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- 左侧：查询输入和结果 -->
      <div class="lg:col-span-2">
        <!-- 查询输入 -->
        <div class="bg-background-primary border border-border rounded-xl p-4 shadow-soft">
          <h3 class="text-sm font-semibold text-text-primary mb-3 flex items-center gap-2">
            <svg class="w-4 h-4 text-brand-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7" />
            </svg>
            输入查询
          </h3>
          <textarea
            v-model="inputQuery"
            @keydown.enter.exact.prevent="executeQuery"
            placeholder="请输入您的问题，多Agent系统将协同工作为您解答..."
            class="w-full px-4 py-3 border border-border rounded-xl resize-none focus:border-brand-mint focus:outline-none focus:ring-2 focus:ring-brand-mint/20 bg-background-secondary text-text-primary placeholder-text-light text-sm"
            rows="3"
          ></textarea>
          <div class="flex items-center justify-end gap-3 mt-3">
            <button 
              @click="clearQuery" 
              class="px-4 py-2 border border-border rounded-lg text-sm text-text-secondary hover:bg-background-dark transition-colors"
            >
              清空
            </button>
            <button 
              @click="executeQuery" 
              :disabled="!inputQuery.trim() || isExecuting"
              class="px-6 py-2 bg-brand-mint text-white rounded-lg hover:bg-brand-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <svg v-if="isExecuting" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              {{ isExecuting ? '执行中...' : '执行查询' }}
            </button>
          </div>
        </div>

        <!-- 工作流执行结果 -->
        <div v-if="queryResult" class="bg-background-primary border border-border rounded-xl p-4 shadow-soft mt-4">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-sm font-semibold text-text-primary flex items-center gap-2">
              <svg class="w-4 h-4 text-brand-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              回答结果
            </h3>
            <span class="text-xs text-text-secondary">执行时间: {{ queryResult.execution_time?.toFixed(2) || 0 }}s</span>
          </div>
          
          <div class="bg-background-secondary rounded-lg p-4">
            <div class="text-sm text-text-primary leading-relaxed" v-html="renderMarkdown(queryResult.answer || '暂无回答')"></div>
          </div>

          <!-- 验证分数 -->
          <div v-if="queryResult.validation_score !== undefined" class="mt-4 flex items-center gap-4">
            <div class="flex items-center gap-2">
              <span class="text-xs text-text-secondary">置信度:</span>
              <div class="w-32 h-2 bg-background-secondary rounded-full overflow-hidden">
                <div 
                  class="h-full bg-brand-mint transition-all duration-500" 
                  :style="{ width: (queryResult.confidence * 100) + '%' }"
                ></div>
              </div>
              <span class="text-xs text-text-primary font-medium">{{ (queryResult.confidence * 100).toFixed(0) }}%</span>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-xs text-text-secondary">验证分数:</span>
              <div class="w-32 h-2 bg-background-secondary rounded-full overflow-hidden">
                <div 
                  class="h-full transition-all duration-500" 
                  :class="queryResult.validation_score >= 0.7 ? 'bg-brand-mint' : queryResult.validation_score >= 0.5 ? 'bg-warning-amber' : 'bg-error-red'"
                  :style="{ width: (queryResult.validation_score * 100) + '%' }"
                ></div>
              </div>
              <span class="text-xs font-medium" :class="queryResult.validation_score >= 0.7 ? 'text-brand-mint' : queryResult.validation_score >= 0.5 ? 'text-warning-amber' : 'text-error-red'">
                {{ (queryResult.validation_score * 100).toFixed(0) }}%
              </span>
            </div>
          </div>

          <!-- 引用来源 -->
          <div v-if="queryResult.citations && queryResult.citations.length > 0" class="mt-4">
            <h4 class="text-xs font-semibold text-text-secondary mb-2 flex items-center gap-2">
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
              引用来源 ({{ queryResult.citations.length }})
            </h4>
            <div class="space-y-2">
              <div 
                v-for="(citation, idx) in queryResult.citations" 
                :key="idx"
                class="px-3 py-2 bg-background-secondary rounded-lg text-xs text-text-secondary"
              >
                <span class="text-brand-mint font-medium">{{ idx + 1 }}.</span>
                <span class="ml-2">{{ citation.title || citation.source || '未知来源' }}</span>
                <span v-if="citation.score" class="ml-2 opacity-70">(相似度: {{ (citation.score * 100).toFixed(0) }}%)</span>
              </div>
            </div>
          </div>

          <!-- 学习路径推荐 -->
          <div v-if="queryResult.learning_path && queryResult.learning_path.length > 0" class="mt-4">
            <h4 class="text-xs font-semibold text-text-secondary mb-2 flex items-center gap-2">
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              学习路径推荐
            </h4>
            <div class="space-y-2">
              <div 
                v-for="(step, idx) in queryResult.learning_path" 
                :key="idx"
                class="flex items-center gap-3 px-3 py-2 bg-background-secondary rounded-lg"
              >
                <div class="w-6 h-6 rounded-full bg-brand-mint text-white text-xs flex items-center justify-center flex-shrink-0">
                  {{ idx + 1 }}
                </div>
                <div class="text-xs">
                  <span class="text-text-primary font-medium">{{ step.description }}</span>
                  <span class="text-text-light ml-2">{{ step.estimated_time }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 相关知识推荐 -->
          <div v-if="queryResult.related_knowledge && queryResult.related_knowledge.length > 0" class="mt-4">
            <h4 class="text-xs font-semibold text-text-secondary mb-2 flex items-center gap-2">
              <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              相关知识推荐
            </h4>
            <div class="grid grid-cols-2 gap-2">
              <div 
                v-for="(knowledge, idx) in queryResult.related_knowledge" 
                :key="idx"
                class="px-3 py-2 bg-background-secondary rounded-lg text-xs cursor-pointer hover:bg-background-dark transition-colors"
              >
                <span class="text-text-primary">{{ knowledge.title }}</span>
                <span v-if="knowledge.relevance" class="text-text-light ml-1">({{ (knowledge.relevance * 100).toFixed(0) }}%)</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧：工作流可视化 -->
      <div class="lg:col-span-1">
        <!-- Agent状态 -->
        <div class="bg-background-primary border border-border rounded-xl p-4 shadow-soft">
          <h3 class="text-sm font-semibold text-text-primary mb-4 flex items-center gap-2">
            <svg class="w-4 h-4 text-brand-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            Agent状态
          </h3>
          <div class="space-y-2">
            <div 
              v-for="(status, agentId) in agentStatus" 
              :key="agentId"
              class="flex items-center gap-3 p-2 rounded-lg hover:bg-background-dark transition-colors"
            >
              <div 
                class="w-2 h-2 rounded-full"
                :class="status.running ? 'bg-success-green' : 'bg-text-light'"
              ></div>
              <div class="flex-1 min-w-0">
                <p class="text-xs text-text-primary truncate">{{ getAgentName(agentId) }}</p>
                <p class="text-xs text-text-light">{{ agentDescriptions[agentId]?.description }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 工作流步骤 -->
        <div class="bg-background-primary border border-border rounded-xl p-4 shadow-soft mt-4">
          <h3 class="text-sm font-semibold text-text-primary mb-4 flex items-center gap-2">
            <svg class="w-4 h-4 text-brand-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            工作流步骤
          </h3>
          
          <!-- 步骤流程图 -->
          <div class="space-y-1">
            <div 
              v-for="(step, idx) in workflowSteps" 
              :key="step.step"
              class="relative"
            >
              <!-- 连接线 -->
              <div v-if="idx < workflowSteps.length - 1" class="absolute left-[11px] top-6 w-0.5 h-4 bg-border"></div>
              
              <div 
                class="flex items-center gap-3 p-3 rounded-lg transition-all duration-300"
                :class="getStepClass(step.step)"
              >
                <!-- 步骤图标 -->
                <div 
                  class="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0"
                  :class="getStepIconClass(step.step)"
                >
                  <svg v-if="getStepStatus(step.step) === 'completed'" class="w-3.5 h-3.5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                  </svg>
                  <svg v-else-if="getStepStatus(step.step) === 'running'" class="w-3.5 h-3.5 text-white animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span v-else class="text-xs text-text-secondary">{{ idx + 1 }}</span>
                </div>
                
                <div class="flex-1 min-w-0">
                  <p class="text-xs font-medium" :class="getStepTextClass(step.step)">{{ step.name }}</p>
                  <p class="text-xs text-text-light truncate">{{ step.description }}</p>
                </div>
                
                <!-- 状态标签 -->
                <span 
                  class="text-xs px-2 py-0.5 rounded-full flex-shrink-0"
                  :class="getStepStatusBadgeClass(step.step)"
                >
                  {{ getStepStatusLabel(step.step) }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 工作流详情 -->
        <div v-if="queryResult?.workflow_details" class="bg-background-primary border border-border rounded-xl p-4 shadow-soft mt-4">
          <h3 class="text-sm font-semibold text-text-primary mb-3 flex items-center gap-2">
            <svg class="w-4 h-4 text-brand-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            执行详情
          </h3>
          <div class="space-y-2 max-h-64 overflow-y-auto">
            <div 
              v-for="(details, stepId) in queryResult.workflow_details" 
              :key="stepId"
              class="p-2 bg-background-secondary rounded-lg"
            >
              <div class="flex items-center justify-between mb-1">
                <span class="text-xs font-medium text-text-primary">{{ getStepName(stepId) }}</span>
                <span class="text-xs px-2 py-0.5 rounded-full" :class="details.status === 'completed' ? 'bg-success-green/20 text-success-green' : 'bg-text-light/20 text-text-light'">
                  {{ details.status }}
                </span>
              </div>
              <div v-if="details.intent" class="text-xs text-text-secondary">意图: {{ details.intent }}</div>
              <div v-if="details.question_type" class="text-xs text-text-secondary">问题类型: {{ details.question_type }}</div>
              <div v-if="details.knowledge_count" class="text-xs text-text-secondary">检索知识数: {{ details.knowledge_count }}</div>
              <div v-if="details.overall_score" class="text-xs text-text-secondary">评分: {{ (details.overall_score * 100).toFixed(0) }}%</div>
              <div v-if="details.related_count" class="text-xs text-text-secondary">推荐数: {{ details.related_count }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { marked } from 'marked';
import hljs from 'highlight.js';
import 'highlight.js/styles/github.css';

marked.use({ breaks: true, gfm: true });

const inputQuery = ref('');
const isExecuting = ref(false);
const queryResult = ref(null);
const agentStatus = reactive({});

// Agent描述
const agentDescriptions = {
  understanding: { name: '理解Agent', description: '分析用户意图和实体' },
  retrieval: { name: '检索Agent', description: '从知识库检索相关知识' },
  reasoning: { name: '推理Agent', description: '基于知识进行逻辑推理' },
  generation: { name: '生成Agent', description: '生成自然语言回答' },
  validation: { name: '验证Agent', description: '验证答案质量' },
  recommend: { name: '推荐Agent', description: '推荐相关知识' },
  coordination: { name: '协调Agent', description: '协调各Agent工作' }
};

// 工作流步骤定义
const workflowSteps = [
  { step: 'understanding', name: '理解', agent: 'understanding', description: '分析用户查询，识别意图和关键实体', dependencies: [] },
  { step: 'retrieval', name: '检索', agent: 'retrieval', description: '从知识库中检索相关知识片段', dependencies: ['understanding'] },
  { step: 'reasoning', name: '推理', agent: 'reasoning', description: '基于检索结果进行逻辑推理', dependencies: ['retrieval'] },
  { step: 'generation', name: '生成', agent: 'generation', description: '生成最终的自然语言回答', dependencies: ['understanding', 'reasoning'] },
  { step: 'validation', name: '验证', agent: 'validation', description: '验证答案质量', dependencies: ['generation'] },
  { step: 'recommend', name: '推荐', agent: 'recommend', description: '推荐相关知识和学习路径', dependencies: ['generation'] }
];

// 步骤状态（用于动画展示）
const stepStatus = reactive({
  understanding: 'pending',
  retrieval: 'pending',
  reasoning: 'pending',
  generation: 'pending',
  validation: 'pending',
  recommend: 'pending'
});

// 获取Agent名称
function getAgentName(agentId) {
  return agentDescriptions[agentId]?.name || agentId;
}

// 获取步骤名称
function getStepName(stepId) {
  const step = workflowSteps.find(s => s.step === stepId);
  return step?.name || stepId;
}

// 获取步骤状态
function getStepStatus(stepId) {
  return stepStatus[stepId] || 'pending';
}

// 获取步骤状态标签
function getStepStatusLabel(stepId) {
  const status = getStepStatus(stepId);
  const labels = {
    pending: '等待',
    running: '执行中',
    completed: '完成',
    failed: '失败'
  };
  return labels[status] || status;
}

// 获取步骤样式类
function getStepClass(stepId) {
  const status = getStepStatus(stepId);
  if (status === 'running') return 'bg-accent-orange/15 border border-accent-orange/30';
  if (status === 'completed') return 'bg-success-green/15 border border-success-green/30';
  if (status === 'failed') return 'bg-error-red/15 border border-error-red/30';
  return 'hover:bg-background-dark border border-transparent';
}

// 获取步骤图标样式类
function getStepIconClass(stepId) {
  const status = getStepStatus(stepId);
  if (status === 'running') return 'bg-brand-mint';
  if (status === 'completed') return 'bg-success-green';
  if (status === 'failed') return 'bg-error-red';
  return 'bg-background-secondary';
}

// 获取步骤文本样式类
function getStepTextClass(stepId) {
  const status = getStepStatus(stepId);
  if (status === 'running') return 'text-brand-mint';
  if (status === 'completed') return 'text-success-green';
  if (status === 'failed') return 'text-error-red';
  return 'text-text-primary';
}

// 获取步骤状态徽章样式类
function getStepStatusBadgeClass(stepId) {
  const status = getStepStatus(stepId);
  if (status === 'running') return 'bg-brand-mint/20 text-brand-mint';
  if (status === 'completed') return 'bg-success-green/20 text-success-green';
  if (status === 'failed') return 'bg-error-red/20 text-error-red';
  return 'bg-text-light/20 text-text-light';
}

// 刷新Agent状态
async function refreshStatus() {
  try {
    const response = await fetch('http://localhost:8000/api/agents/status', {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
    });
    if (response.ok) {
      const data = await response.json();
      Object.assign(agentStatus, data.agents || {});
    }
  } catch (e) {
    console.error('刷新状态失败:', e);
  }
}

// 执行查询（使用SSE流式接收状态）
async function executeQuery() {
  if (!inputQuery.value.trim() || isExecuting.value) return;

  isExecuting.value = true;
  queryResult.value = null;
  
  // 重置步骤状态
  Object.keys(stepStatus).forEach(key => stepStatus[key] = 'pending');
  console.log('=== 开始执行查询 ===');
  console.log('步骤状态已重置:', stepStatus);

  try {
    // 创建SSE连接
    console.log('正在连接到流式接口...');
    const response = await fetch('http://localhost:8000/api/agents/query/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify({
        query: inputQuery.value
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    console.log('连接成功，开始接收流式数据...');

    // 使用ReadableStream处理SSE
    const reader = response.body.getReader();
    const decoder = new TextDecoder('utf-8');
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      
      if (done) {
        console.log('流式数据接收完成');
        break;
      }

      buffer += decoder.decode(value, { stream: true });
      console.log('接收到数据片段，当前缓冲区:', buffer.length, '字符');
      
      // 处理完整的SSE消息
      while (buffer.includes('\n\n')) {
        const messageEnd = buffer.indexOf('\n\n');
        const message = buffer.substring(0, messageEnd);
        buffer = buffer.substring(messageEnd + 2);

        if (message.startsWith('data: ')) {
          try {
            const data = JSON.parse(message.substring(6));
            console.log('解析到SSE消息:', data);
            handleSSEMessage(data);
          } catch (e) {
            console.error('解析SSE消息失败:', e);
          }
        }
      }
    }

  } catch (error) {
    console.error('查询失败:', error);
    queryResult.value = {
      answer: `抱歉，系统处理您的请求时出错：${error.message}`,
      status: 'failed'
    };
  } finally {
    isExecuting.value = false;
    console.log('=== 查询执行结束 ===');
  }
}

// 处理SSE消息
function handleSSEMessage(data) {
  switch (data.type) {
    case 'step_start':
      // 步骤开始
      if (stepStatus[data.step_id] === 'pending') {
        stepStatus[data.step_id] = 'running';
      }
      break;
    case 'step_complete':
      // 步骤完成
      stepStatus[data.step_id] = 'completed';
      break;
    case 'result':
      // 最终结果
      queryResult.value = data.data;
      break;
    case 'error':
      // 错误
      console.error('SSE错误:', data.error);
      queryResult.value = {
        answer: `抱歉，系统处理您的请求时出错：${data.error}`,
        status: 'failed'
      };
      break;
  }
}

// 清空查询
function clearQuery() {
  inputQuery.value = '';
  queryResult.value = null;
  Object.keys(stepStatus).forEach(key => stepStatus[key] = 'pending');
}

// Markdown渲染
function renderMarkdown(text) {
  if (!text) return '';
  try {
    let html = marked.parse(text);
    const temp = document.createElement('div');
    temp.innerHTML = html;
    temp.querySelectorAll('pre code').forEach((el) => {
      try {
        const lang = (el.className || '').replace('language-', '') || '';
        if (lang && hljs.getLanguage(lang)) {
          el.innerHTML = hljs.highlight(el.textContent, { language: lang }).value;
        } else {
          el.innerHTML = hljs.highlightAuto(el.textContent).value;
        }
      } catch (e) { /* keep as-is */ }
    });
    return temp.innerHTML;
  } catch (e) {
    console.error('Markdown rendering error:', e);
    return text;
  }
}

// 初始化
refreshStatus();
</script>

<style scoped>
/* 自定义滚动条 */
::-webkit-scrollbar {
  width: 6px;
}
::-webkit-scrollbar-track {
  background: var(--background-secondary);
  border-radius: 3px;
}
::-webkit-scrollbar-thumb {
  background: var(--border);
  border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover {
  background: var(--text-light);
}
</style>