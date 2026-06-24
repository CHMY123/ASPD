<template>
  <div class="smart-chat">
    <div class="flex items-center justify-between mb-6">
      <h2 class="text-2xl font-semibold text-text-primary">智能问答</h2>
      <div class="flex items-center gap-3">
        <div class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-background-primary border border-border">
          <span class="text-sm text-text-secondary">模式:</span>
          <button @click="currentMode = 'knowledge'" class="px-3 py-1 rounded-full text-sm font-medium transition-colors" :class="currentMode === 'knowledge' ? 'bg-brand-mint text-white' : 'text-text-secondary hover:bg-background-dark'">
            知识检索
          </button>
          <button @click="currentMode = 'multi_agent'" class="px-3 py-1 rounded-full text-sm font-medium transition-colors" :class="currentMode === 'multi_agent' ? 'bg-accent-orange text-white' : 'text-text-secondary hover:bg-background-dark'">
            多Agent协同对话
          </button>
        </div>
      </div>
    </div>

    <div class="flex gap-6">
      <div class="flex-1">
        <div class="bg-background-primary border border-border rounded-xl h-[calc(100vh-200px)] flex flex-col shadow-soft">
          <div class="flex-1 overflow-y-auto p-4 space-y-4" ref="chatContainer">
            <div v-for="message in messages" :key="message.id" class="flex gap-3" :class="message.role === 'user' ? 'justify-end' : 'justify-start'">
              <div v-if="message.role === 'user'" class="flex-shrink-0 w-10 h-10 rounded-full overflow-hidden">
                <img v-if="userAvatarUrl" :src="userAvatarUrl" alt="用户头像" class="w-full h-full object-cover" />
                <div v-else class="w-full h-full bg-brand-mint flex items-center justify-center">
                  <svg class="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                  </svg>
                </div>
              </div>
              <div v-else class="flex-shrink-0 w-10 h-10 rounded-full bg-brand-light flex items-center justify-center">
                <svg class="w-5 h-5 text-brand-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
                </svg>
              </div>
              <div class="max-w-[70%]" :class="message.role === 'user' ? 'text-right' : ''">
                <div class="inline-block px-4 py-3 rounded-2xl" :class="message.role === 'user' ? 'bg-brand-mint text-white rounded-br-md' : 'bg-background-secondary text-text-primary rounded-bl-md'">
                  <div v-if="message.agent" class="text-xs mb-1 opacity-70">
                    <span>{{ message.agent }}</span>
                  </div>
                  <!-- 用户消息纯文本 -->
                  <p v-if="message.role === 'user'" class="text-sm leading-relaxed whitespace-pre-wrap">{{ message.content }}</p>
                  <!-- 助手消息 Markdown 渲染 -->
                  <div v-else class="text-sm leading-relaxed markdown-body" v-html="renderMarkdown(message.content)"></div>
                  
                  <!-- 多Agent工作流可视化 - 低代码风格 -->
                  <div v-if="message.workflow_details" class="mt-3 pt-3 border-t border-border/50">
                    <!-- 展开/收起按钮 -->
                    <div class="flex items-center justify-between mb-2">
                      <button @click="toggleWorkflow(message.id)" class="text-xs font-semibold text-text-secondary flex items-center gap-1 hover:text-text-primary transition-colors">
                        <svg class="w-3.5 h-3.5" :class="message._workflowExpanded ? 'rotate-90' : ''" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                        </svg>
                        {{ message._workflowExpanded ? '收回工作流' : '展开工作流' }}
                      </button>
                      <!-- 整体进度条 -->
                      <div class="flex items-center gap-2">
                        <span class="text-xs text-text-light">{{ getWorkflowProgress(message.workflow_details) }}%</span>
                        <div class="w-20 h-1.5 bg-background-dark rounded-full overflow-hidden">
                          <div class="h-full bg-brand-mint transition-all duration-500 rounded-full" :style="{ width: getWorkflowProgress(message.workflow_details) + '%' }"></div>
                        </div>
                      </div>
                    </div>

                    <!-- 折叠状态：仅显示迷你进度条概要 -->
                    <div v-if="!message._workflowExpanded" class="flex items-center gap-1.5 flex-wrap">
                      <span v-for="(detail, stepName) in message.workflow_details" :key="stepName" class="flex items-center gap-1">
                        <div class="flex items-center">
                          <div class="px-2 py-0.5 rounded text-xs font-medium whitespace-nowrap"
                            :class="detail.status === 'success' || detail.status === 'completed' ? 'bg-success-green/20 text-success-green' : detail.status === 'running' ? 'bg-accent-orange/20 text-accent-orange' : 'bg-background-dark text-text-light'">
                            {{ getWorkflowStepName(stepName) }}
                          </div>
                          <svg v-if="stepName !== Object.keys(message.workflow_details).pop()" class="w-3 h-3 text-text-light mx-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                          </svg>
                        </div>
                      </span>
                    </div>

                    <!-- 展开状态：低代码风格流程图 -->
                    <div v-if="message._workflowExpanded" class="space-y-1.5 mt-1">
                      <div v-for="(detail, stepName, idx) in message.workflow_details" :key="stepName" class="relative">
                        <!-- 连接线 -->
                        <div v-if="idx < Object.keys(message.workflow_details).length - 1" class="absolute left-[19px] top-8 w-0.5 h-3 bg-border"></div>
                        
                        <div class="flex items-start gap-3 p-2.5 rounded-lg transition-all duration-300"
                          :class="getWorkflowBlockClass(detail)">
                          <!-- 步骤图标 -->
                          <div class="w-[38px] h-[38px] rounded-lg flex items-center justify-center flex-shrink-0 text-sm font-bold"
                            :class="getWorkflowIconClass(detail)">
                            <svg v-if="detail.status === 'completed' || detail.status === 'success'" class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7" />
                            </svg>
                            <svg v-else-if="detail.status === 'running'" class="w-4 h-4 text-white animate-spin" fill="none" viewBox="0 0 24 24">
                              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            <span v-else class="text-xs text-text-secondary font-medium">{{ idx + 1 }}</span>
                          </div>
                          
                          <div class="flex-1 min-w-0">
                            <div class="flex items-center justify-between">
                              <span class="text-xs font-semibold text-text-primary">{{ getWorkflowStepName(stepName) }}</span>
                              <span class="text-xs px-1.5 py-0.5 rounded-full"
                                :class="detail.status === 'completed' || detail.status === 'success' ? 'bg-success-green/15 text-success-green' : detail.status === 'running' ? 'bg-accent-orange/15 text-accent-orange' : 'bg-background-dark text-text-light'">
                                {{ detail.status === 'completed' || detail.status === 'success' ? '完成' : detail.status === 'running' ? '执行中' : '待处理' }}
                              </span>
                            </div>
                            
                            <!-- 各Agent特有的信息展示 -->
                            <div class="mt-1 space-y-0.5">
                              <template v-if="stepName === 'understanding'">
                                <p v-if="detail.intent" class="text-xs text-text-light">意图: {{ detail.intent }}</p>
                                <p v-if="detail.question_type" class="text-xs text-text-light">问题类型: {{ detail.question_type }}</p>
                                <p v-if="detail.entities?.length" class="text-xs text-text-light">实体: {{ detail.entities.slice(0, 3).join(', ') }}</p>
                              </template>
                              <template v-if="stepName === 'retrieval'">
                                <p v-if="detail.knowledge_count !== undefined" class="text-xs text-text-light">检索到 {{ detail.knowledge_count }} 条相关知识</p>
                              </template>
                              <template v-if="stepName === 'generation'">
                                <p v-if="detail.answer_length" class="text-xs text-text-light">生成回答 {{ detail.answer_length }} 字</p>
                              </template>
                              <template v-if="stepName === 'validation'">
                                <div v-if="detail.overall_score !== undefined" class="flex items-center gap-2">
                                  <span class="text-xs text-text-light">质量评分:</span>
                                  <div class="w-16 h-1.5 bg-background-dark rounded-full overflow-hidden">
                                    <div class="h-full rounded-full transition-all duration-500" 
                                      :class="detail.overall_score >= 0.7 ? 'bg-success-green' : detail.overall_score >= 0.5 ? 'bg-accent-orange' : 'bg-error-red'"
                                      :style="{ width: (detail.overall_score * 100) + '%' }"></div>
                                  </div>
                                  <span class="text-xs font-medium"
                                    :class="detail.overall_score >= 0.7 ? 'text-success-green' : detail.overall_score >= 0.5 ? 'text-accent-orange' : 'text-error-red'">
                                    {{ (detail.overall_score * 100).toFixed(0) }}%
                                  </span>
                                </div>
                                <p v-if="detail.feedback" class="text-xs text-text-light">{{ detail.feedback }}</p>
                              </template>
                              <template v-if="stepName === 'recommend'">
                                <p v-if="detail.related_count" class="text-xs text-text-light">推荐 {{ detail.related_count }} 个相关知识</p>
                              </template>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                    
                    <!-- 置信度/验证分（展开收起都显示） -->
                    <div v-if="message.confidence > 0 || message.validation_score > 0" class="flex items-center gap-3 mt-2 pt-1">
                      <span v-if="message.confidence > 0" class="text-xs text-text-light">置信度: {{ (message.confidence * 100).toFixed(0) }}%</span>
                      <span v-if="message.validation_score > 0" class="text-xs text-text-light">验证分: {{ (message.validation_score * 100).toFixed(0) }}%</span>
                    </div>
                  </div>
                  
                  <div v-if="message.references && message.references.length > 0" class="mt-2 pt-2 border-t border-border/50">
                    <p class="text-xs text-text-light mb-1">引用来源:</p>
                    <div class="space-y-1">
                      <div v-for="(ref, idx) in message.references.slice(0, 3)" :key="idx" class="text-xs text-text-secondary">
                        {{ formatReference(ref) }}
                      </div>
                    </div>
                  </div>
                  <div v-if="message.reasoning" class="mt-2 pt-2 border-t border-border/50">
                    <div class="text-xs text-text-light">
                      <div class="flex items-center gap-2 mb-1">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                        </svg>
                        推理过程
                      </div>
                      <div class="text-text-secondary">{{ message.reasoning }}</div>
                    </div>
                  </div>
                </div>
                <p class="text-xs text-text-light mt-1">{{ message.time }}</p>
              </div>
            </div>

            <!-- 流式加载中的光标闪烁效果 -->
            <div v-if="isTyping" class="flex gap-3 justify-start">
              <div class="flex-shrink-0 w-10 h-10 rounded-full bg-brand-light flex items-center justify-center">
                <svg class="w-5 h-5 text-brand-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <div class="bg-background-secondary rounded-2xl rounded-bl-md px-4 py-3">
                <div class="flex gap-1">
                  <span class="w-2 h-2 bg-text-light rounded-full animate-bounce" style="animation-delay: 0ms"></span>
                  <span class="w-2 h-2 bg-text-light rounded-full animate-bounce" style="animation-delay: 150ms"></span>
                  <span class="w-2 h-2 bg-text-light rounded-full animate-bounce" style="animation-delay: 300ms"></span>
                </div>
              </div>
            </div>

            <div v-if="messages.length === 0" class="flex flex-col items-center justify-center h-full text-center">
              <div class="w-20 h-20 rounded-full bg-brand-light flex items-center justify-center mb-4">
                <svg class="w-10 h-10 text-brand-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <h3 class="text-lg font-semibold text-text-primary mb-2">{{ currentMode === 'knowledge' ? '智能知识助手' : '多Agent协同对话助手' }}</h3>
              <p class="text-sm text-text-secondary mb-6">
                {{ currentMode === 'knowledge' ? '基于课程知识库，为您提供精准的专业知识解答' : '多Agent协同工作，为您提供全面准确的知识解答' }}
              </p>
              <div class="flex flex-wrap justify-center gap-2">
                <button v-for="example in examples" :key="example" @click="sendMessage(example)" class="px-4 py-2 bg-background-secondary rounded-full text-sm text-text-secondary hover:bg-background-dark hover:text-text-primary transition-colors">
                  {{ example }}
                </button>
              </div>
            </div>
          </div>

          <!-- 输入框区域：紧凑布局，按钮在右侧 -->
          <div class="p-3 border-t border-border">
            <div class="flex items-center gap-2 justify-end">
              <textarea
                v-model="inputMessage"
                @keydown.enter.exact.prevent="sendMessage(inputMessage)"
                placeholder="输入问题..."
                class="px-3 py-2 border border-border rounded-xl resize-none focus:border-brand-mint focus:outline-none focus:ring-2 focus:ring-brand-mint/20 bg-background-primary text-text-primary placeholder-text-light text-sm flex-1"
                rows="1"
                style="min-width: 300px;"
              ></textarea>
              <button @click="sendMessage(inputMessage)" :disabled="!inputMessage.trim() || isTyping" class="px-4 py-2 bg-brand-mint text-white rounded-xl hover:bg-brand-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-1 flex-shrink-0">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
                <span class="text-sm">发送</span>
              </button>
            </div>
            <p class="text-xs text-text-light mt-2 text-center">
              {{ currentMode === 'knowledge' ? '知识检索模式：基于知识库提供精准解答' : '多Agent协同对话模式：6个Agent协同工作，提供全面解答' }}
              · Enter 发送
            </p>
          </div>
        </div>
      </div>

      <div class="w-80 hidden lg:block">
        <div class="bg-background-primary border border-border rounded-xl p-4 shadow-soft">
          <h3 class="text-sm font-semibold text-text-primary mb-4 flex items-center gap-2">
            <svg class="w-4 h-4 text-brand-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            推荐问题
          </h3>
          <div class="space-y-2">
            <button v-for="question in recommendedQuestions" :key="question" @click="sendMessage(question)" class="w-full text-left px-3 py-2 rounded-lg hover:bg-background-dark transition-colors text-sm text-text-secondary">
              <svg class="w-4 h-4 inline-block mr-2 text-brand-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ question }}
            </button>
          </div>
        </div>

        <div class="bg-background-primary border border-border rounded-xl p-4 shadow-soft mt-4">
          <h3 class="text-sm font-semibold text-text-primary mb-4 flex items-center gap-2">
            <svg class="w-4 h-4 text-brand-mint" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            最近会话
          </h3>
          <div class="space-y-2 max-h-64 overflow-y-auto group">
            <div v-if="conversations.length === 0" class="text-sm text-text-light text-center py-4">
              暂无历史会话
            </div>
            <div
              v-for="conv in conversations.slice(0, 3)"
              :key="conv.id"
              class="flex items-center justify-between px-3 py-2.5 rounded-lg hover:bg-background-dark transition-colors"
            >
              <button
                @click="switchConversation(conv.id)"
                class="flex-1 text-left text-sm"
                :class="conv.id === threadId ? 'text-brand-dark font-medium' : 'text-text-secondary'"
              >
                <div class="flex items-center gap-2">
                  <svg class="w-4 h-4 flex-shrink-0" :class="conv.id === threadId ? 'text-brand-mint' : 'text-text-light'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  <span class="truncate" :title="conv.title || '新会话'">{{ (conv.title || '新会话').length > 24 ? (conv.title || '新会话').substring(0, 24) + '...' : conv.title || '新会话' }}</span>
                </div>
                <p class="text-xs text-text-light mt-1 pl-6">{{ formatTime(conv.updated_at) }} · {{ conv.message_count }}条消息</p>
              </button>
              <button
                  v-if="conv.id !== threadId"
                  @click.stop="showDeleteConfirmation(conv.id)"
                  class="p-1.5 rounded bg-background-secondary hover:bg-error-red text-text-secondary hover:text-white transition-colors opacity-0 group-hover:opacity-100 focus:opacity-100 focus:outline-none focus:ring-2 focus:ring-error-red focus:ring-offset-2"
                  :disabled="deletingConvId === conv.id"
                  title="删除会话"
                  aria-label="删除会话"
                >
                  <svg v-if="deletingConvId !== conv.id" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                  <svg v-else class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                </button>
            </div>
            <button @click="newConversation" class="w-full mt-2 px-3 py-2 rounded-lg border border-dashed border-border text-sm text-brand-mint hover:bg-background-dark transition-colors">
              + 新建会话
            </button></div>
          </div>
        </div>
      </div>

    <!-- 删除会话确认对话框 -->
    <Teleport to="body">
      <div v-if="showDeleteConfirm" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <div class="bg-background-primary rounded-xl p-6 w-full max-w-sm shadow-xl animate-scale-in">
          <div class="text-center">
            <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-error-red/10 flex items-center justify-center">
              <svg class="w-8 h-8 text-error-red" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h3 class="text-lg font-semibold text-text-primary mb-2">确认删除</h3>
            <p id="delete-confirm-message" class="text-sm text-text-secondary mb-6">确定要删除这个会话吗？此操作无法撤销。</p>
            <div class="flex gap-3">
              <button @click="cancelDelete" class="flex-1 px-4 py-2.5 border border-border rounded-lg text-text-secondary hover:bg-background-dark transition-colors text-sm font-medium">
                取消
              </button>
              <button @click="confirmDelete" :disabled="deletingConvId" class="flex-1 px-4 py-2.5 bg-error-red text-white rounded-lg hover:bg-error-red-dark transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-sm font-medium font-semibold focus:outline-none focus:ring-2 focus:ring-error-red focus:ring-offset-2" aria-describedby="delete-confirm-message">
                <svg v-if="deletingConvId" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                {{ deletingConvId ? '删除中...' : '删除' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, nextTick, watch, computed } from 'vue';
import { useAuthStore } from '../stores/auth';
import { marked } from 'marked';
import hljs from 'highlight.js';
import 'highlight.js/styles/github.css';

// marked v18 配置
marked.use({ breaks: true, gfm: true });

const authStore = useAuthStore();

// 用户头像 URL（优先使用真实头像）
const userAvatarUrl = computed(() => {
  return authStore.user?.avatar || '';
});

const currentMode = ref('knowledge');
const inputMessage = ref('');
const isTyping = ref(false);
const chatContainer = ref(null);

const messages = ref([]);

// 从 localStorage 恢复会话
const savedThreadId = localStorage.getItem('chat_thread_id');
const threadId = ref(savedThreadId || generateId());

const conversations = ref([]);

function generateId() {
  return 'chat_' + Date.now() + '_' + Math.random().toString(36).substr(2, 6);
}

// 加载会话列表
async function loadConversations() {
  if (!authStore.accessToken) return;
  try {
    const res = await fetch('http://localhost:8000/api/chat/my?limit=10', {
      headers: { 'Authorization': `Bearer ${authStore.accessToken}` }
    });
    if (res.ok) {
      const data = await res.json();
      conversations.value = data;
    }
  } catch (e) {
    console.warn('加载会话列表失败:', e);
  }
}

// 加载会话历史消息
async function loadHistory(convId) {
  if (!authStore.accessToken) return;
  try {
    const res = await fetch(`http://localhost:8000/api/chat/${convId}/history?limit=50`, {
      headers: { 'Authorization': `Bearer ${authStore.accessToken}` }
    });
    if (res.ok) {
      const data = await res.json();
      messages.value = data.map(msg => ({
        id: msg.id,
        role: msg.role === 'user' ? 'user' : 'assistant',
        content: msg.content,
        time: formatTime(msg.created_at),
        agent: msg.role === 'assistant' ? '知识讲解Agent' : undefined,
        references: msg.references || []
      }));
      await nextTick();
      scrollToBottom();
    }
  } catch (e) {
    console.warn('加载历史消息失败:', e);
  }
}

// 切换会话
async function switchConversation(convId) {
  threadId.value = convId;
  localStorage.setItem('chat_thread_id', convId);
  messages.value = [];
  isTyping.value = false;
  await loadHistory(convId);
  await nextTick();
  scrollToBottom();
}

// 新建会话
async function newConversation() {
  threadId.value = generateId();
  localStorage.setItem('chat_thread_id', threadId.value);
  messages.value = [];
  messages.value.push({
    id: 'welcome-' + Date.now(),
    role: 'assistant',
    content: '您好！我是您的智能学习助手。请问有什么可以帮助您的吗？',
    time: '刚刚',
    agent: '知识讲解Agent'
  });
}

// 删除会话相关状态
const deletingConvId = ref(null);
const showDeleteConfirm = ref(false);
const confirmDeleteConvId = ref(null);

// 显示删除确认对话框
function showDeleteConfirmation(convId) {
  confirmDeleteConvId.value = convId;
  showDeleteConfirm.value = true;
}

// 取消删除
function cancelDelete() {
  showDeleteConfirm.value = false;
  confirmDeleteConvId.value = null;
}

// 确认删除会话
async function confirmDelete() {
  const convId = confirmDeleteConvId.value;
  if (!convId) return;
  
  deletingConvId.value = convId;
  
  try {
    const res = await fetch(`http://localhost:8000/api/chat/${convId}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${authStore.accessToken}` }
    });
    if (res.ok) {
      conversations.value = conversations.value.filter(c => c.id !== convId);
      await loadConversations();
      
      // 如果删除的是当前会话，新建一个
      if (threadId.value === convId) {
        newConversation();
      }
      
      showDeleteConfirm.value = false;
      confirmDeleteConvId.value = null;
    } else {
      throw new Error('删除失败');
    }
  } catch (e) {
    console.error('删除会话失败:', e);
    alert('删除会话失败，请稍后重试');
  } finally {
    deletingConvId.value = null;
  }
}

function formatTime(dateStr) {
  if (!dateStr) return '';
  try {
    const d = new Date(dateStr);
    const now = new Date();
    const diffMs = now - d;
    const diffMin = Math.floor(diffMs / 60000);
    if (diffMin < 1) return '刚刚';
    if (diffMin < 60) return diffMin + '分钟前';
    const diffHour = Math.floor(diffMin / 60);
    if (diffHour < 24) return diffHour + '小时前';
    return `${d.getMonth() + 1}月${d.getDate()}日`;
  } catch { return ''; }
}

const examples = ref([
  '什么是二叉树？',
  '如何实现快速排序？',
  'TCP三次握手的过程',
  '推荐一本数据结构的书'
]);

const recommendedQuestions = ref([
  '数据结构中栈和队列的区别是什么？',
  '什么是时间复杂度和空间复杂度？',
  '操作系统中的进程和线程有什么区别？',
  'HTTP和HTTPS的区别是什么？',
  '什么是数据库的ACID特性？'
]);

// 初始化
(async function init() {
  if (authStore.accessToken) {
    await loadConversations();
    // 如果当前 threadId 在会话列表中，加载历史
    const exists = conversations.value.find(c => c.id === threadId.value);
    if (exists) {
      await loadHistory(threadId.value);
    }
  }
  if (messages.value.length === 0) {
    messages.value.push({
      id: 'welcome-' + Date.now(),
      role: 'assistant',
      content: '您好！我是您的智能学习助手。请问有什么可以帮助您的吗？',
      time: '刚刚',
      agent: '知识讲解Agent'
    });
  }
})();

// Markdown 渲染函数（含代码高亮和数学公式）
function renderMarkdown(text) {
  if (!text) return '';
  try {
    // 预处理：仅转换完全明确的数学表达式（不做泛化匹配）
    let processedText = preprocessMathExpressions(text);
    
    let html = marked.parse(processedText);
    
    // 后处理：highlight.js 高亮代码块
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
    
    // 渲染 KaTeX 公式（自动查找 $...$ 和 $$...$$ 分隔符）
    renderMathInElement(temp, {
      delimiters: [
        { left: '$$', right: '$$', display: true },
        { left: '$', right: '$', display: false }
      ],
      throwOnError: false,
      strict: false
    });
    
    return temp.innerHTML;
  } catch (e) {
    console.error('Markdown rendering error:', e);
    return text;
  }
}

// 预处理数学表达式 — 仅转换明确的数学模式，绝不破坏正常文本
function preprocessMathExpressions(text) {
  // 1. 指数形式：数字^(表达式) 如 2^(k-1) → $2^{k-1}$
  text = text.replace(/(\d+)\^\(([^)]+)\)/g, '$$$1^{$2}$$');
  // 单字母^数字：x^2 → $x^2$
  text = text.replace(/\b([a-zA-Z])\^(\d+)\b/g, '$$$1^{$2}$$');
  
  // 2. sqrt(x) → $\sqrt{x}$
  text = text.replace(/\bsqrt\(([^)]+)\)/gi, '$\\sqrt{$1}$');
  
  // 3. 简单分数：数字/数字 → $\frac{数字}{数字}$（仅纯数字分数）
  text = text.replace(/\b(\d+)\/(\d+)\b/g, '$\\frac{$1}{$2}$');
  
  return text;
}

// KaTeX 渲染辅助函数（带多次重试）
function renderMathInElement(element, options) {
  if (typeof window.renderMathInElement === 'function') {
    window.renderMathInElement(element, options);
  } else {
    // 如果 KaTeX 还未加载，多次延迟重试
    let retries = 0;
    const maxRetries = 20;
    const retry = () => {
      if (typeof window.renderMathInElement === 'function') {
        window.renderMathInElement(element, options);
      } else if (retries < maxRetries) {
        retries++;
        setTimeout(retry, 200);
      }
    };
    setTimeout(retry, 200);
  }
}

// 手动 kaTeX 渲染（备用）
function renderKaTeXInline(formula) {
  if (typeof window.katex === 'undefined') return formula;
  try {
    return window.katex.renderToString(formula, { throwOnError: false });
  } catch(e) {
    return formula;
  }
}

// 获取工作流步骤中文名
function getWorkflowStepName(stepName) {
  const nameMap = {
    'understanding': '理解',
    'retrieval': '检索',
    'reasoning': '推理',
    'generation': '生成',
    'validation': '验证',
    'recommend': '推荐'
  };
  return nameMap[stepName] || stepName;
}

// 切换工作流展开/收起
function toggleWorkflow(messageId) {
  const msg = messages.value.find(m => m.id === messageId);
  if (msg) {
    msg._workflowExpanded = !msg._workflowExpanded;
  }
}

// 计算工作流整体进度百分比
function getWorkflowProgress(workflowDetails) {
  if (!workflowDetails) return 0;
  const steps = Object.values(workflowDetails);
  const completed = steps.filter(s => s.status === 'completed' || s.status === 'success').length;
  return Math.round((completed / steps.length) * 100);
}

// 获取工作流块的样式类
function getWorkflowBlockClass(detail) {
  if (detail.status === 'running') return 'bg-accent-orange/8 border border-accent-orange/20';
  if (detail.status === 'completed' || detail.status === 'success') return 'bg-success-green/8 border border-success-green/15';
  return 'bg-background-dark/30';
}

// 获取工作流图标样式类
function getWorkflowIconClass(detail) {
  if (detail.status === 'running') return 'bg-accent-orange';
  if (detail.status === 'completed' || detail.status === 'success') return 'bg-success-green';
  return 'bg-background-dark';
}

// 格式化引用来源
function formatReference(ref) {
  if (!ref) return '未知来源';
  
  // 获取可用的来源字段
  let source = ref.original_doc || ref.source || ref.title || ref.text || ref.filename || '';
  
  // 如果是对象，尝试获取更多字段
  if (typeof source === 'object') {
    source = source.title || source.name || JSON.stringify(source);
  }
  
  // 清理字符串：去除多余空格和换行
  if (typeof source === 'string') {
    source = source.replace(/\s+/g, ' ').trim();
  }
  
  // 如果为空，尝试其他字段
  if (!source) {
    const fields = ['original_doc', 'source', 'title', 'text', 'filename'];
    for (const field of fields) {
      if (ref[field] && typeof ref[field] === 'string') {
        source = ref[field].replace(/\s+/g, ' ').trim();
        if (source) break;
      }
    }
  }
  
  // 仍然为空则返回默认值
  if (!source) {
    source = '来源资料';
  }
  
  // 截断过长的来源名称
  if (source.length > 50) {
    source = source.substring(0, 50) + '...';
  }
  
  return source;
}

const sendMessage = async (message) => {
  if (!message.trim() || isTyping.value) return;

  inputMessage.value = '';

  messages.value.push({
    id: Date.now().toString(),
    role: 'user',
    content: message,
    time: '刚刚'
  });

  // 知识检索模式使用流式+弹跳动画
  if (currentMode.value === 'knowledge') {
    isTyping.value = true;
    await nextTick();
    scrollToBottom();
    await streamApi(message);
    isTyping.value = false;
  } else {
    // 多Agent模式：直接插入工作流占位消息，不显示弹跳动画
    await nextTick();
    scrollToBottom();
    await callMultiAgentApi(message);
  }

  await nextTick();
  scrollToBottom();
};

// 多Agent协同API调用
const callMultiAgentApi = async (message) => {
  // 先插入一个"执行中"的占位消息，展示工作流动画
  const placeholderId = 'agent-' + Date.now();
  const runningWorkflow = {
    'understanding': { status: 'running', intent: '', question_type: '', entities: [], timestamp: new Date().toISOString() },
    'retrieval': { status: 'pending', knowledge_count: 0, metadata: {}, timestamp: '' },
    'reasoning': { status: 'pending', conclusions: [], perspectives: [], timestamp: '' },
    'generation': { status: 'pending', answer_length: 0, timestamp: '' },
    'validation': { status: 'pending', overall_score: 0, feedback: '', timestamp: '' },
    'recommend': { status: 'pending', related_count: 0, timestamp: '' }
  };

  messages.value.push({
    id: placeholderId,
    role: 'assistant',
    content: '',
    time: '刚刚',
    agent: '多Agent协同系统',
    workflow_details: runningWorkflow,
    _workflowExpanded: true,
    confidence: 0,
    validation_score: 0
  });

  await nextTick();
  scrollToBottom();

  try {
    const url = 'http://localhost:8000/api/chat/multi-agent';

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': authStore.accessToken ? `Bearer ${authStore.accessToken}` : ''
      },
      body: JSON.stringify({
        message: message,
        thread_id: threadId.value
      })
    });

    if (!response.ok) {
      throw new Error('Multi-agent API request failed');
    }

    const data = await response.json();
    
    // 更新占位消息为真实结果（默认收起工作流）
    const idx = messages.value.findIndex(m => m.id === placeholderId);
    if (idx !== -1) {
      messages.value[idx] = {
        id: placeholderId,
        role: 'assistant',
        content: data.response || data.message || '抱歉，我无法回答这个问题。',
        time: '刚刚',
        agent: data.agent || '多Agent协同系统',
        references: data.references || [],
        workflow_details: data.workflow_details || {},
        confidence: data.confidence || 0,
        validation_score: data.validation_score || 0,
        related_knowledge: data.related_knowledge || [],
        learning_path: data.learning_path || [],
        execution_time: data.execution_time || 0,
        _workflowExpanded: false
      };
    }
  } catch (error) {
    console.error('Multi-agent API error:', error);
    // 更新占位消息为错误状态
    const idx = messages.value.findIndex(m => m.id === placeholderId);
    if (idx !== -1) {
      // 将所有步骤标记为失败
      const failedWorkflow = { ...messages.value[idx].workflow_details };
      Object.keys(failedWorkflow).forEach(key => {
        failedWorkflow[key] = { ...failedWorkflow[key], status: 'failed' };
      });
      messages.value[idx].workflow_details = failedWorkflow;
      messages.value[idx].content = `抱歉，多Agent协同系统暂时无法处理您的问题。错误：${error.message}`;
    }
  }
};

// 流式API调用（SSE）
const streamApi = async (message) => {
  const assistantMsg = {
    id: (Date.now() + 1).toString(),
    role: 'assistant',
    content: '',
    time: '刚刚',
    agent: '知识讲解Agent',
    references: []
  };
  
  // 将hasReceivedToken移到函数作用域，避免catch块中无法访问
  let hasReceivedToken = false;

  try {
    const response = await fetch('http://localhost:8000/api/chat/knowledge/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': authStore.accessToken ? `Bearer ${authStore.accessToken}` : ''
      },
      body: JSON.stringify({
        message: message,
        thread_id: threadId.value
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const event = JSON.parse(line.slice(6));
            if (event.type === 'token') {
              // 第一个 token 到来时：推入消息、取消加载态
              if (!hasReceivedToken) {
                hasReceivedToken = true;
                isTyping.value = false;
                messages.value.push(assistantMsg);
              }
              assistantMsg.content += event.data;
              messages.value = [...messages.value];
              scrollToBottom();
            } else if (event.type === 'references') {
              assistantMsg.references = event.data;
            } else if (event.type === 'error') {
              if (!hasReceivedToken) {
                assistantMsg.content = `抱歉，系统处理您的请求时出错：${event.data}`;
                isTyping.value = false;
                messages.value.push(assistantMsg);
              } else {
                assistantMsg.content += `\n\n[错误] ${event.data}`;
                messages.value = [...messages.value];
              }
            }
          } catch (e) {
            console.warn('SSE parse error:', e);
          }
        }
      }
    }

    // 流结束但从未收到 token（可能知识库为空导致 LLM 无输出）
    if (!hasReceivedToken) {
      assistantMsg.content = '抱歉，知识库中未找到与您问题相关的信息，请尝试其他问题。';
      isTyping.value = false;
      messages.value.push(assistantMsg);
      scrollToBottom();
    }
  } catch (error) {
    console.error('Stream API error:', error);
    if (!hasReceivedToken) {
      assistantMsg.content = `抱歉，暂时无法回答您的问题。错误：${error.message}`;
      isTyping.value = false;
      messages.value.push(assistantMsg);
    } else {
      assistantMsg.content += `\n\n[连接错误] ${error.message}`;
      messages.value = [...messages.value];
    }
  }
};

// 非流式API调用（对话模式）
const callApi = async (message) => {
  try {
    const url = 'http://localhost:8000/api/chat/message';

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': authStore.accessToken ? `Bearer ${authStore.accessToken}` : ''
      },
      body: JSON.stringify({
        message: message,
        thread_id: threadId.value
      })
    });

    if (!response.ok) {
      throw new Error('API request failed');
    }

    const data = await response.json();

    messages.value.push({
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: data.response || data.message || '抱歉，我无法回答这个问题。',
      time: '刚刚',
      references: data.references || []
    });
  } catch (error) {
    console.error('Chat API error:', error);
    messages.value.push({
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: `抱歉，暂时无法回答您的问题。错误：${error.message}`,
      time: '刚刚'
    });
  }
};

const scrollToBottom = () => {
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
  }
};

watch(currentMode, () => {
  const hasUserMessages = messages.value.some(m => m.role === 'user');
  if (!hasUserMessages) {
    const modeMessages = {
      'knowledge': {
        content: '您好！我是您的智能知识助手。基于课程知识库，为您提供精准的专业知识解答。',
        agent: '知识讲解Agent'
      },
      'multi_agent': {
        content: '您好！多Agent协同对话系统已就绪。我将协调理解、检索、推理、生成、验证、推荐等多个Agent为您协同工作，提供全面准确的知识解答。',
        agent: '多Agent协同系统'
      }
    };
    const modeInfo = modeMessages[currentMode.value] || modeMessages.multi_agent;
    messages.value = [{
      id: 'mode-' + Date.now(),
      role: 'assistant',
      content: modeInfo.content,
      time: '刚刚',
      agent: modeInfo.agent
    }];
  }
});
</script>

<style>
/* Markdown 样式（全局，因为 v-html 渲染在 scoped 外） */
.markdown-body {
  font-size: 0.875rem;
  line-height: 1.7;
  word-break: break-word;
}
.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4 {
  margin-top: 1em;
  margin-bottom: 0.5em;
  font-weight: 600;
  line-height: 1.3;
}
.markdown-body h1 { font-size: 1.3em; }
.markdown-body h2 { font-size: 1.15em; }
.markdown-body h3 { font-size: 1.05em; }
.markdown-body p { margin: 0.5em 0; }
.markdown-body p:first-child { margin-top: 0; }
.markdown-body ul,
.markdown-body ol {
  padding-left: 1.5em;
  margin: 0.5em 0;
}
.markdown-body li { margin: 0.25em 0; }
.markdown-body code {
  background: rgba(0,0,0,0.06);
  border-radius: 3px;
  padding: 0.15em 0.3em;
  font-size: 0.85em;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
}
.markdown-body pre {
  background: #f5f5f5;
  border-radius: 6px;
  padding: 12px;
  overflow-x: auto;
  margin: 0.5em 0;
}
.markdown-body pre code {
  background: none;
  padding: 0;
  font-size: 0.8em;
}
.markdown-body blockquote {
  border-left: 3px solid #ddd;
  padding-left: 12px;
  color: #666;
  margin: 0.5em 0;
}
.markdown-body table {
  border-collapse: collapse;
  width: 100%;
  margin: 0.5em 0;
}
.markdown-body th,
.markdown-body td {
  border: 1px solid #ddd;
  padding: 6px 10px;
  text-align: left;
}
.markdown-body th {
  background: #f5f5f5;
  font-weight: 600;
}
.markdown-body a {
  color: #1890ff;
  text-decoration: underline;
}
/* KaTeX 公式显示优化 */
.markdown-body .katex {
  font-size: 1.05em;
  line-height: 1.4;
}
.markdown-body .katex-display {
  margin: 0.5em 0;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 0.25em 0;
}
.markdown-body .katex .katex-html {
  white-space: nowrap;
}
.markdown-body .katex-error {
  color: #e74c3c;
  font-size: 0.85em;
}
</style>

<style scoped>
@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.animate-bounce {
  animation: bounce 1.4s infinite ease-in-out;
}
</style>
