# RAG深度知识检索模块技术文档

## 概述

本文档描述课程学习知识库问答系统中RAG（Retrieval-Augmented Generation）深度知识检索模块的技术架构、核心实现和配置说明。

**版本**: v2.1
**更新日期**: 2026-06-24
**参考实现**: `backend/demo.py`

---

## 1. 系统架构

### 1.1 整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户请求层                                │
│  (前端Vue3 → 后端FastAPI → ChatService → AgentGraph)           │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      RAG检索增强层                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐ │
│  │   多路召回        │  │    RRF融合       │  │   Rerank精排   │ │
│  │  ├─向量检索      │  │                 │  │               │ │
│  │  └─关键词检索    │  │  排名分数融合     │  │ BAAI/reranker │ │
│  └─────────────────┘  └─────────────────┘  └───────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LLM生成层                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Qwen/Qwen3-8B  (SiliconFlow API - 多模型回退支持)      │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                      知识存储层                                  │
│  ┌─────────────────────────┐  ┌─────────────────────────────┐ │
│  │   Chroma向量数据库       │  │      TiDB Cloud关系数据库    │ │
│  │   (语义向量存储/检索)    │  │      (会话/消息存储)         │ │
│  └─────────────────────────┘  └─────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 模块依赖关系

```
┌─────────────────────────────────────────────────────────────┐
│                      domain/                                │
│  ├─ knowledge/entity.py     (KnowledgePoint实体定义)        │
│  └─ conversation/entity.py  (Conversation/Message实体)        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  infrastructure/                             │
│  ├─ knowledge_repository.py  (Chroma实现 - 核心RAG逻辑)     │
│  ├─ llm_client.py            (LLM/Embedding/Rerank封装)    │
│  └─ agent/graph.py            (LangGraph Agent编排)         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   application/                               │
│  ├─ knowledge_service.py     (知识库应用服务)               │
│  └─ chat_service.py          (问答应用服务 - RAG流程)       │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    interfaces/                              │
│  └─ routers/chat_router.py   (API路由 - SSE流式输出)        │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. 核心流程

### 2.1 RAG检索流程

```
用户问题
    │
    ▼
┌──────────────────────────────────────────────────────────────┐
│ 步骤1: 多路召回 (Multi-path Recall)                          │
├──────────────────────────────────────────────────────────────┤
│ 1.1 向量检索                                                  │
│     • 使用 query: 前缀向量化用户问题 (BGE模型规范)              │
│     • 在Chroma中执行余弦相似度搜索                            │
│     • 返回 top_k*3 个候选结果                                │
│                                                              │
│ 1.2 关键词检索                                                │
│     • 使用Chroma全文搜索功能                                  │
│     • 返回 top_k*2 个候选结果                                │
└──────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────┐
│ 步骤2: RRF融合 (Reciprocal Rank Fusion)                      │
├──────────────────────────────────────────────────────────────┤
│ 公式: RRF(d) = Σ 1/(k + rank(d))                             │
│                                                              │
│ • k=60: RRF参数，值越小越依赖高排名结果                       │
│ • 融合向量检索和关键词检索的排名分数                          │
│ • 输出单一综合排名列表                                        │
└──────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────┐
│ 步骤3: Rerank精排 (Reranking)                                │
├──────────────────────────────────────────────────────────────┤
│ • 使用 BAAI/bge-reranker-v2-m3 模型                          │
│ • 对RRF融合后的top结果重新排序                               │
│ • 计算相关性分数 (0-1)                                       │
│ • 过滤分数 < 0.3 的结果                                       │
└──────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────┐
│ 步骤4: 上下文构建 (Context Building)                          │
├──────────────────────────────────────────────────────────────┤
│ • 截断每篇文档到800字符                                      │
│ • 格式化输出: [参考文档N] 标题/课程/内容                       │
│ • 生成参考来源列表                                            │
└──────────────────────────────────────────────────────────────┘
    │
    ▼
最终检索结果 → LLM生成回答
```

### 2.2 知识库导入流程

```
docs/knowledge/*.md
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ Markdown解析                                                  │
├──────────────────────────────────────────────────────────────┤
│ • 读取YAML front matter (可选)                               │
│ • 按 ##~#### 标题分割文档                                     │
│ • 无标题时按段落分割                                          │
│ • 过滤 < 10字符的短内容                                      │
└──────────────────────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────────────────────┐
│ 向量化存储                                                    │
├──────────────────────────────────────────────────────────────┤
│ • 使用 passage: 前缀向量化 (BGE模型规范)                      │
│ • 生成1024维向量                                              │
│ • 存入Chroma向量库                                            │
│ • 存储元数据: title/course/chapter/source_file              │
└──────────────────────────────────────────────────────────────┘
```

---

## 3. 核心算法

### 3.1 RRF (Reciprocal Rank Fusion)

```python
def reciprocal_rank_fusion(result_lists, k=60):
    """
    倒数排名融合算法

    参数:
        result_lists: 多个排名列表 [(doc_id, score), ...]
        k: RRF参数，默认60

    返回:
        List[(doc_id, rrf_score)]: 融合后的排名列表
    """
    rrf_scores = {}

    for result_list in result_lists:
        for rank, (doc_id, score) in enumerate(result_list, 1):
            if doc_id not in rrf_scores:
                rrf_scores[doc_id] = 0.0
            rrf_scores[doc_id] += 1.0 / (k + rank)

    return sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
```

**RRF优势**:
- 无需调优：k=60适用于大多数场景
- 鲁棒性：对单一检索器噪声不敏感
- 简单高效：O(n)时间复杂度

### 3.2 向量检索策略

**BGE模型前缀规范**:
- 文档入库: `passage: {title}\n{content}`
- 查询向量: `query: {user_question}`

**相似度计算**:
```python
# Chroma返回的是L2距离或余弦距离
similarity = 1.0 - min(distance, 1.0)
```

### 3.3 Markdown智能分割

```python
def split_markdown_sections(content, filename):
    """
    按标题级别分割Markdown

    支持: ## / ### / ####
    每个标题作为一个独立知识块
    """
    pattern = r'(#{2,4})\s+(.+?)\n([\s\S]*?)(?=(?:\n#{2,4}\s)|$)'
    matches = re.findall(pattern, content)

    chunks = []
    for level, title, body in matches:
        if len(body.strip()) > 10:
            chunks.append((title.strip(), body.strip()))

    return chunks
```

---

## 4. 配置参数

### 4.1 环境变量配置

```env
# LLM配置
LLM_API_KEY=sk-xxx                    # SiliconFlow API密钥
LLM_API_BASE=https://api.siliconflow.cn/v1
LLM_MODEL=Qwen/Qwen3-8B
LLM_MAX_TOKENS=1000
LLM_TEMPERATURE=0.7

# Embedding配置
EMBEDDING_MODEL=BAAI/bge-m3
EMBEDDING_DIMENSION=1024

# Rerank配置
RERANK_API_BASE=https://api.siliconflow.cn/v1
RERANK_MODEL=BAAI/bge-reranker-v2-m3
RERANK_MAX_LENGTH=512
RERANK_TOP_N=5
RERANK_MIN_SCORE=0.3

# RRF配置
RRF_K=60

# 检索配置
SIMILARITY_THRESHOLD=0.5
MAX_SEARCH_RESULTS=5

# Chroma配置
CHROMA_DB_PATH=./cs_know_db
CHROMA_COLLECTION_NAME=cs_collection

# 知识库路径
KNOWLEDGE_BASE_PATH=../docs/knowledge
```

### 4.2 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `RERANK_TOP_N` | 5 | Rerank返回的最大结果数 |
| `RERANK_MIN_SCORE` | 0.3 | Rerank最小相关度阈值 |
| `RRF_K` | 60 | RRF融合参数，越小越依赖高排名 |
| `SIMILARITY_THRESHOLD` | 0.5 | 检索结果最小相似度 |
| `MAX_CONTENT_LENGTH` | 800 | 上下文构建时单文档最大长度 |

---

## 5. API接口

### 5.1 聊天接口 (流式)

```http
POST /api/chat/stream
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
    "message": "二叉树的定义是什么？",
    "thread_id": "conv-123",
    "mode": "knowledge"
}
```

**SSE响应格式**:
```
event: references
data: [{"id":"xxx","title":"二叉树","source":"computer_science.md","score":0.95}]

event: token
data: 二

event: token
data: 叉

event: token
data: 树

event: done
data:
```

### 5.2 知识检索接口

```http
POST /api/knowledge/search
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
    "query": "排序算法",
    "course": "数据结构",
    "limit": 5
}
```

**响应**:
```json
{
    "results": [
        {
            "id": "abc123",
            "title": "快速排序",
            "content": "快速排序是一种高效的排序算法...",
            "course": "数据结构",
            "score": 0.95
        }
    ],
    "count": 1
}
```

### 5.3 知识导入接口

```http
POST /api/knowledge/import
Authorization: Bearer <jwt_token>
```

**响应**:
```json
{
    "total": 100,
    "imported": 98,
    "failed": 2,
    "errors": [
        {"file": "invalid.md", "line": 0, "error": "解析失败"}
    ]
}
```

---

## 6. 技术栈

| 组件 | 技术选型 | 说明 |
|------|----------|------|
| **向量数据库** | Chroma | 本地持久化向量存储 |
| **Embedding** | BAAI/bge-m3 | 1024维向量，中英双语优化 |
| **Rerank** | BAAI/bge-reranker-v2-m3 | 文档重排序 |
| **LLM** | Qwen/Qwen3-8B | SiliconFlow API调用 |
| **关系数据库** | TiDB Cloud | 会话/消息存储 |
| **API框架** | FastAPI | 异步API + SSE支持 |

---

## 7. 性能优化

### 7.1 检索优化
- 多路召回：向量 + 关键词，提高召回率
- RRF融合：无超参数，简单高效
- Rerank精排：仅对top结果重排，控制计算量

### 7.2 LLM优化
- 多模型回退：Qwen → DeepSeek → GPT
- 自动重试：指数退避，最多重试3次
- 流式输出：SSE边检索边生成

### 7.3 存储优化
- 内容截断：单文档最大800字符
- 向量维度：1024维（BGE-m3）
- Chroma持久化：避免重复向量化

---

## 8. 已知问题与限制

1. **中文分词**：当前使用简单字符级分割，可考虑jieba分词优化
2. **长文本处理**：单文档最大2000字符截断
3. **多语言支持**：当前优化中英双语，其他语言效果可能不佳
4. **知识库更新**：增量更新机制待完善

---

## 9. 变更日志

### v2.1 (2026-06-24)
- 优化数据库搜索功能：基于UnderstandingAgent识别的实体关键词进行LIKE匹配
- 修复MessageResponse验证错误：references.id字段类型转换为字符串
- 优化会话标题显示：限制长度24字符并添加省略号
- 修复删除按钮样式问题：添加bg-background-secondary和text-text-secondary
- 优化工作流展示：恢复色彩显示（运行中-橙色/完成-绿色/失败-红色）
- 修复前端JavaScript错误：hasReceivedToken变量作用域问题
- 修复流式API CORS配置：为StreamingResponse添加完整CORS响应头
- 日志配置优化：从DEBUG改为INFO级别

### v2.0 (2026-06-22)
- 新增RRF融合算法替代简单分数平均
- 新增Markdown智能分割（支持##~####标题）
- 新增YAML front matter元数据解析
- 新增`build_context`方法统一上下文格式
- 新增`load_knowledge_base`方法批量导入
- 优化系统提示词，强化知识库约束

### v1.0 (2026-06-21)
- 初始版本
- 基础多路召回 + Rerank流程

---

## 10. 参考资料

1. [BGE模型文档](https://github.com/FlagOpen/FlagEmbedding)
2. [Chroma向量数据库](https://docs.trychroma.com/)
3. [RRF算法论文](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)
4. [SiliconFlow API](https://docs.siliconflow.cn/)
