"""
多Agent智能问答系统 - Agent实现（集成真实LLM和向量检索）
"""

import asyncio
import sys
import os
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import logging

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from .base import (
    BaseAgent, AgentType, MessageType, AgentMessage,
    MessageBus, TaskScheduler, WorkflowEngine, Task
)

# 导入真实的LLM客户端和向量数据库
from infrastructure.llm_client import LLMClient, LLMError
from infrastructure.knowledge_repository import ChromaKnowledgeRepository

logger = logging.getLogger(__name__)

# 强制输出调试信息到 stdout
def force_print(msg: str):
    """强制输出调试信息到标准输出（同时写 stderr 兜底）"""
    text = f"[AGENT] {msg}"
    print(text, flush=True, file=sys.stdout)
    print(text, flush=True, file=sys.stderr)  # stderr 兜底确保可见


# ==================== JSON提取工具函数 ====================

def _extract_json(text: str) -> Optional[dict]:
    """
    从LLM输出中提取JSON对象

    支持格式：
    1. 纯JSON: {"key": "value"}
    2. Markdown代码块: ```json\n{"key": "value"}\n```
    3. 被文字包裹的JSON: 文字...{"key": "value"}...文字

    Args:
        text: LLM输出的原始文本

    Returns:
        Optional[dict]: 解析成功的JSON字典，失败返回None
    """
    if not text:
        logger.warning("_extract_json: 输入文本为空")
        return None

    # 步骤1: 从Markdown代码块中提取 ```json ... ```
    code_block_pattern = r'```(?:json)?\s*\n?([\s\S]*?)\n?```'
    code_blocks = re.findall(code_block_pattern, text)
    if code_blocks:
        for block in code_blocks:
            block = block.strip()
            if block.startswith('{') and block.endswith('}'):
                try:
                    return json.loads(block)
                except json.JSONDecodeError:
                    continue

    # 步骤2: 尝试直接解析整个文本
    cleaned = text.strip()
    if cleaned.startswith('{') and cleaned.endswith('}'):
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

    # 步骤3: 查找第一个 { 到最后一个 } 之间的内容
    start = cleaned.find('{')
    end = cleaned.rfind('}')
    if start != -1 and end != -1 and end > start:
        json_str = cleaned[start:end + 1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

    # 步骤4: 尝试修复常见问题后重试
    try:
        # 移除注释（// 或 /* */）
        no_comments = re.sub(r'//[^\n]*', '', cleaned)
        no_comments = re.sub(r'/\*[\s\S]*?\*/', '', no_comments)
        # 移除尾随逗号
        no_trailing = re.sub(r',\s*([}\]])', r'\1', no_comments)
        # 修复单引号为双引号
        fixed = no_trailing.replace("'", '"')
        if fixed.startswith('{') and fixed.endswith('}'):
            return json.loads(fixed)
    except (json.JSONDecodeError, Exception):
        pass

    logger.debug(f"_extract_json: 无法从文本中提取JSON: {text[:200]}")
    return None


def _strengthen_json_prompt(original_prompt: str) -> str:
    """
    强化JSON输出约束的提示词包装

    Args:
        original_prompt: 原始提示词

    Returns:
        str: 强化后的提示词
    """
    json_enforcement = """

【重要！输出格式约束 - 必须严格遵守】
你必须只输出一个有效的JSON对象，不要包含任何其他文字、说明或Markdown格式标记。
不要使用```json代码块，直接输出JSON文本。
确保JSON格式正确：属性名用双引号，没有尾随逗号，没有注释。

"""
    return original_prompt + json_enforcement


class UnderstandingAgent(BaseAgent):
    """理解Agent - 使用真实LLM进行用户意图识别和关键信息提取"""
    
    def __init__(
        self, 
        agent_id: str = "understanding_agent",
        llm_client: Optional[LLMClient] = None
    ):
        super().__init__(agent_id, AgentType.UNDERSTANDING)
        self.llm_client = llm_client
        
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行理解任务 - 使用LLM进行深度分析"""
        query = input_data.get('query', '')
        context = input_data.get('context', {})
        
        force_print("=" * 60)
        force_print("【UnderstandingAgent.execute】开始处理")
        force_print(f"  查询内容: '{query[:80]}{'...' if len(query) > 80 else ''}'")
        force_print(f"  上下文: {json.dumps(context, ensure_ascii=False)[:150]}")
        
        logger.info(f"[UnderstandingAgent] 开始处理查询: '{query[:100]}...'")
        logger.debug(f"[UnderstandingAgent] 上下文信息: {json.dumps(context, ensure_ascii=False)[:200]}")
        
        # 1. 使用LLM进行意图识别和实体提取
        force_print("  调用 _analyze_with_llm()...")
        understanding_result = await self._analyze_with_llm(query, context)
        force_print(f"  _analyze_with_llm() 返回: {json.dumps(understanding_result, ensure_ascii=False)[:300]}")
        
        # 2. 获取查询向量（用于后续检索）
        force_print("  调用 _get_query_embedding()...")
        query_embedding = await self._get_query_embedding(query)
        force_print(f"  向量长度: {len(query_embedding)}")
        
        result = {
            **understanding_result,
            'query_embedding': query_embedding,
            'original_query': query,
            'debug_info': {
                'llm_used': self.llm_client is not None,
                'query_length': len(query),
                'timestamp': datetime.now().isoformat()
            }
        }
        
        force_print(f"  最终结果:")
        force_print(f"    intent: {result.get('intent')}")
        force_print(f"    requires_database_query: {result.get('requires_database_query')}")
        force_print(f"    requires_knowledge_base_search: {result.get('requires_knowledge_base_search')}")
        force_print(f"    entities: {json.dumps(result.get('entities', {}), ensure_ascii=False)}")
        force_print(f"    keywords: {result.get('keywords', [])}")
        force_print("【UnderstandingAgent.execute】完成")
        force_print("=" * 60)
        
        logger.info(f"[UnderstandingAgent] 理解结果: intent={result.get('intent')}, requires_db={result.get('requires_database_query')}, requires_kb={result.get('requires_knowledge_base_search')}")
        logger.debug(f"[UnderstandingAgent] 提取的实体: {json.dumps(result.get('entities', {}), ensure_ascii=False)}")
        logger.debug(f"[UnderstandingAgent] 关键词: {result.get('keywords', [])}")
        
        return result
    
    async def _analyze_with_llm(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """使用LLM分析用户查询"""
        if not self.llm_client:
            # 回退到规则匹配
            return await self._fallback_analysis(query, context)
        
        base_prompt = """
你是一个智能问答系统的意图识别专家。请分析用户的查询，并从以下维度提取信息。

**意图分类（intent）必须从以下列表中选择一个：**
- `recommend`: 用户希望获得推荐、建议或列表（例如："推荐电子书"、"有哪些课程"、"给我看看"）
- `explain`: 用户希望理解概念、原理或过程（例如："什么是二叉树"、"TCP/IP如何工作"）
- `how_to`: 用户希望学习操作方法或步骤（例如："如何配置环境"、"怎样安装"）
- `compare`: 用户希望对比两个或多个事物（例如："数组和链表的区别"）
- `troubleshoot`: 用户报告错误或寻求问题解决方案
- `general_query`: 用户进行一般性提问，不包含以上明确意图

**重要决策：`requires_database_query` 字段**
这个字段控制后续是查询课程/电子书数据库（True）还是知识库（False）。
- 设置为 `true` 的情况：用户明确在**查找资源列表**，如"推荐课程"、"有哪些电子书"、"展示书籍"
- 设置为 `false` 的情况：用户询问**知识概念**（即使提到了"课程"或"书"），如"课程中讲到的数组"、"解释书中的概念"
- 默认值：`false`

**重要决策：`requires_knowledge_base_search` 字段**
- 设置为 `true`：用户询问的内容需要通过向量知识库检索知识
- 设置为 `false`：仅当用户问题不涉及任何知识内容时（如纯问好）

【输出格式 - 严格JSON】
{
  "intent": "推断出的意图",
  "question_type": "问题类型（what/how/why/compare/general）",
  "entities": {
    "concepts": ["提取的核心概念"],
    "properties": ["属性"],
    "actions": ["动作"]
  },
  "keywords": ["用于检索的关键词"],
  "requires_knowledge_base_search": true,
  "requires_database_query": false,
  "complexity": "简单"
}

用户查询："""
        
        system_prompt = _strengthen_json_prompt(base_prompt)
        
        # 最多重试2次
        for attempt in range(2):
            try:
                response = await self.llm_client.chat_completion(
                    prompt=query,
                    system_prompt=system_prompt
                )
                
                result = _extract_json(response)
                if result is not None:
                    logger.debug(f"意图识别成功: {json.dumps(result, ensure_ascii=False)[:200]}")
                    return result
                    
                logger.warning(f"第{attempt+1}次JSON解析失败: {response[:150]}")
                if attempt == 0:
                    system_prompt += "\n\n【严重警告】上一次输出格式不符合要求！只输出纯JSON对象，不要包含任何其他文字！"
                    
            except LLMError as e:
                logger.error(f"LLM分析失败（第{attempt+1}次）: {e}")
                if attempt == 0:
                    continue
                return await self._fallback_analysis(query, context)
        
        # 所有重试均失败，使用回退方案
        logger.warning("LLM意图识别全部重试失败，使用规则回退")
        return await self._fallback_analysis(query, context)
    
    async def _fallback_analysis(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """规则匹配回退方案"""
        intent_keywords = {
            'recommend': ['推荐', '建议', '有哪些', '给我看', '展示', '列出', '有什么', '看看', '给我推荐'],
            'explain': ['什么是', '解释', '说明', '介绍', '定义'],
            'how_to': ['如何', '怎么', '怎样', '方法', '步骤'],
            'compare': ['区别', '对比', '比较', '差异', '不同'],
            'troubleshoot': ['错误', '问题', 'bug', '异常', '解决']
        }
        
        intent = 'general_query'
        for intent_type, keywords in intent_keywords.items():
            if any(keyword in query for keyword in keywords):
                intent = intent_type
                break
        
        # 问题类型
        if '为什么' in query or '原因' in query:
            question_type = 'why'
        elif '如何' in query or '怎么' in query:
            question_type = 'how'
        elif '什么' in query or '什么是' in query:
            question_type = 'what'
        elif '区别' in query or '对比' in query:
            question_type = 'compare'
        else:
            question_type = 'general'
        
        # 提取常见概念
        common_concepts = [
            '数组', '链表', '栈', '队列', '树', '图', '算法',
            '排序', '查找', '递归', '动态规划', '进程', '线程',
            '内存', '文件', '网络', '数据库', 'SQL', '事务', '索引'
        ]
        
        entities = {
            'concepts': [c for c in common_concepts if c in query],
            'properties': [],
            'actions': []
        }
        
        # 提取关键词
        keywords = entities['concepts'].copy()
        
        # 判断是否需要数据库查询
        # 规则：必须是明确寻找/列出资源的意图，而不是提问中偶然包含相关词汇
        # "推荐一些课程" → True  |  "课程中讲到的数组" → False
        resource_lookup_patterns = [
            '推荐.*课程', '推荐.*电子书', '推荐.*书', '推荐.*学习',
            '有哪些课程', '有哪些电子书', '有什么课程', '有什么书',
            '给我看.*课程', '给我看.*书', '展示.*课程', '展示.*书',
            '列出.*课程', '列出.*书', '查找.*课程', '搜索.*课程',
            '我要.*课程', '我需要.*课程', '给我推荐',
            'course', 'book', 'ebook'
        ]
        
        # 使用正则检查是否是明确的资源查找
        is_resource_lookup = any(
            re.search(pattern, query, re.IGNORECASE) for pattern in resource_lookup_patterns
        )
        
        # 只有当上述模式匹配时才标记为数据库查询
        requires_database_query = is_resource_lookup
        
        # 如果 LLM 分析已返回 recommend 意图，也走数据库查询
        # 但 fallback 中不直接将包含"课程"的普通问题当成数据库查询
        
        return {
            'intent': intent,
            'question_type': question_type,
            'entities': entities,
            'keywords': keywords,
            'complexity': '中等',
            'requires_knowledge_base_search': len(entities['concepts']) > 0 or not is_resource_lookup,
            'requires_database_query': requires_database_query
        }
    
    async def _get_query_embedding(self, query: str) -> List[float]:
        """获取查询向量"""
        if not self.llm_client:
            # 回退到hash编码
            import hashlib
            hash_obj = hashlib.md5(query.encode())
            hash_hex = hash_obj.hexdigest()
            vector = []
            for i in range(0, len(hash_hex), 2):
                byte_val = int(hash_hex[i:i+2], 16)
                vector.append(byte_val / 255.0)
            return vector
        
        try:
            return await self.llm_client.get_embedding(f"query: {query}")
        except LLMError as e:
            logger.error(f"获取向量失败: {e}")
            # 返回空向量
            return []


class RetrievalAgent(BaseAgent):
    """检索Agent - 使用真实向量数据库进行知识检索"""
    
    def __init__(
        self, 
        agent_id: str = "retrieval_agent", 
        knowledge_repo: Optional[ChromaKnowledgeRepository] = None
    ):
        super().__init__(agent_id, AgentType.RETRIEVAL)
        self.knowledge_repo = knowledge_repo
        self.top_k = 5
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行检索任务 - 根据意图标记执行差异化检索"""
        understanding_result = input_data.get('understanding_result', {})
        query = understanding_result.get('original_query', '')
        entities = understanding_result.get('entities', {})
        requires_database_query = understanding_result.get('requires_database_query', False)
        intent = understanding_result.get('intent', 'general_query')
        
        force_print("=" * 60)
        force_print("【RetrievalAgent.execute】开始处理")
        force_print(f"  查询内容: '{query[:80]}{'...' if len(query) > 80 else ''}'")
        force_print(f"  intent: {intent}")
        force_print(f"  requires_database_query: {requires_database_query}")
        force_print(f"  knowledge_repo可用: {self.knowledge_repo is not None}")
        force_print(f"  entities: {json.dumps(entities, ensure_ascii=False)}")
        
        logger.info(f"[RetrievalAgent] 开始检索: query='{query[:80]}...', intent={intent}, requires_db={requires_database_query}, kb_available={self.knowledge_repo is not None}")
        logger.debug(f"[RetrievalAgent] 实体信息: {json.dumps(entities, ensure_ascii=False)}")
        
        # 路径A：requires_database_query=True → 执行数据库查询（课程/电子书）
        if requires_database_query:
            force_print("  选择路径A：数据库查询")
            logger.info(f"[RetrievalAgent] 选择路径A：数据库查询")
            result = await self._database_retrieval(understanding_result)
            force_print(f"  数据库查询完成: 结果数={len(result.get('knowledge_chunks', []))}")
            force_print(f"  来源类型: {result.get('retrieval_metadata', {}).get('source_type')}")
            logger.info(f"[RetrievalAgent] 数据库查询完成: 结果数={len(result.get('knowledge_chunks', []))}, 来源类型={result.get('retrieval_metadata', {}).get('source_type')}")
            force_print("【RetrievalAgent.execute】完成")
            force_print("=" * 60)
            return result
        
        # 路径B：requires_database_query=False → 标准向量知识库检索
        if not self.knowledge_repo:
            force_print("  选择路径B回退：知识库不可用，降级到数据库查询")
            logger.warning(f"[RetrievalAgent] 选择路径B回退：知识库不可用，降级到数据库查询")
            result = await self._database_retrieval(understanding_result)
            force_print("【RetrievalAgent.execute】完成（回退）")
            force_print("=" * 60)
            return result
        
        try:
            # 执行真实的向量检索
            force_print(f"  选择路径B：向量知识库检索")
            force_print(f"    query: '{query[:50]}{'...' if len(query) > 50 else ''}'")
            force_print(f"    top_k: {self.top_k}")
            logger.info(f"[RetrievalAgent] 选择路径B：向量知识库检索, query='{query[:50]}...', top_k={self.top_k}")
            
            search_results = await self.knowledge_repo.search(
                query=query,
                limit=self.top_k,
                use_rerank=True
            )
            
            force_print(f"  向量检索返回 {len(search_results)} 条结果")
            logger.info(f"[RetrievalAgent] 向量检索返回 {len(search_results)} 条结果")
            
            # 转换结果格式
            knowledge_chunks = []
            for idx, result in enumerate(search_results):
                kp = result.knowledge_point
                chunk = {
                    'knowledge_id': kp.id,
                    'content': kp.content,
                    'metadata': {
                        'title': kp.title,
                        'course': kp.course,
                        'chapter': kp.chapter,
                        'source_file': kp.source_file,
                        'tags': kp.tags
                    },
                    'similarity': result.score,
                    'rank': result.rank,
                    'data_source': 'vector_knowledge_base'
                }
                knowledge_chunks.append(chunk)
                force_print(f"    结果[{idx+1}]: id={kp.id[:30]}..., score={result.score:.4f}, title={kp.title[:50]}")
                logger.debug(f"[RetrievalAgent] 检索结果[{idx+1}]: id={kp.id[:20]}..., score={result.score:.4f}, title={kp.title}")
            
            result = {
                'knowledge_chunks': knowledge_chunks,
                'retrieval_metadata': {
                    'total_retrieved': len(search_results),
                    'semantic_count': len(search_results),
                    'keyword_count': len(search_results),
                    'rerank_applied': True,
                    'source_type': 'vector_knowledge_base',
                    'debug_info': {
                        'query': query,
                        'top_k': self.top_k,
                        'has_knowledge_repo': True
                    }
                }
            }
            
            force_print("【RetrievalAgent.execute】完成")
            force_print("=" * 60)
            return result
            
        except Exception as e:
            force_print(f"  ❌ 向量检索失败: {e}")
            logger.error(f"[RetrievalAgent] 向量检索失败，回退到数据库查询: {e}", exc_info=True)
            result = await self._database_retrieval(understanding_result)
            force_print("【RetrievalAgent.execute】完成（异常回退）")
            force_print("=" * 60)
            return result
    
    async def _database_retrieval(self, understanding_result: Dict[str, Any]) -> Dict[str, Any]:
        """数据库查询路径 - 从TiDB动态查询课程和电子书内容

当understanding_result中的requires_database_query=True时被调用。
通过关键词模糊匹配查询courses表和books表，返回结构化的课程/书籍信息。

优化策略：
1. 优先使用UnderstandingAgent识别的实体关键词进行LIKE匹配
2. 支持从entities.concepts和keywords中提取关键词
3. 确保能够匹配到包含核心技术词汇的资源（如《计算机网络（第8版）》）

数据来源标注规范：
- source_type='course_db'：数据来自课程数据库（courses表）
- source_type='book_db'：数据来自电子书库（books表）
- source_type='general'：无匹配数据时的通用知识
"""
        entities = understanding_result.get('entities', {})
        concepts = entities.get('concepts', [])
        keywords = understanding_result.get('keywords', [])
        query = understanding_result.get('original_query', '')
        intent = understanding_result.get('intent', 'general_query')
        
        # 合并所有可用的关键词：优先使用实体和关键词列表，然后使用原始查询
        search_keywords = []
        
        # 添加概念作为关键词
        if concepts:
            search_keywords.extend(concepts)
        
        # 添加关键词列表中的关键词
        if keywords:
            search_keywords.extend(keywords)
        
        # 去重但保持顺序
        search_keywords = list(dict.fromkeys(search_keywords))
        
        logger.info(f"[_database_retrieval] 开始数据库查询: query='{query[:50]}...', intent={intent}")
        logger.info(f"[_database_retrieval] 提取的搜索关键词: {search_keywords}")
        
        results = []
        seen_content = set()
        db_queries_executed = []
        
        try:
            from infrastructure.database import fetch_sql
            
            # 步骤1：优先使用提取的关键词进行搜索（支持匹配《计算机网络（第8版）》这类包含核心技术词汇的资源）
            if search_keywords:
                logger.info(f"[_database_retrieval] 步骤1：使用提取的关键词进行搜索")
                for keyword in search_keywords[:5]:  # 最多使用5个关键词
                    # 查询课程表
                    course_rows = await fetch_sql(
                        "SELECT course_name, description FROM courses WHERE course_name LIKE %s OR description LIKE %s LIMIT 3",
                        f"%{keyword}%", f"%{keyword}%"
                    )
                    db_queries_executed.append(f"courses LIKE '%{keyword}%' -> {len(course_rows)} rows")
                    
                    for row in course_rows:
                        content = row.get("description") or f"{row.get('course_name')}课程相关内容"
                        title = row.get('course_name', '')
                        if content and content not in seen_content:
                            seen_content.add(content)
                            results.append({
                                'knowledge_id': f"course_{title}",
                                'content': content,
                                'data_source': 'course_db',
                                'metadata': {
                                    'title': title,
                                    'source': 'course_db',
                                    'source_type': '课程数据库',
                                    'source_file': '课程数据库',
                                    'is_real_data': True
                                },
                                'similarity': 0.85,
                                'rank': len(results) + 1,
                                'matched_keyword': keyword
                            })
                            logger.debug(f"[_database_retrieval] 关键词[{keyword}]匹配课程: {title}")
                    
                    # 查询电子书表（支持书名中包含版本号的匹配，如《计算机网络（第8版）》）
                    book_rows = await fetch_sql(
                        "SELECT title, summary, author FROM books WHERE title LIKE %s OR summary LIKE %s OR author LIKE %s LIMIT 3",
                        f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"
                    )
                    db_queries_executed.append(f"books LIKE '%{keyword}%' -> {len(book_rows)} rows")
                    
                    for row in book_rows:
                        content = row.get("summary") or f"《{row.get('title')}》- {row.get('author')}"
                        title = row.get('title', '')
                        if content and content not in seen_content:
                            seen_content.add(content)
                            results.append({
                                'knowledge_id': f"book_{title}",
                                'content': content,
                                'data_source': 'book_db',
                                'metadata': {
                                    'title': title,
                                    'author': row.get('author', ''),
                                    'source': 'book_db',
                                    'source_type': '电子书库',
                                    'source_file': f"《{title}》",
                                    'is_real_data': True
                                },
                                'similarity': 0.80,
                                'rank': len(results) + 1,
                                'matched_keyword': keyword
                            })
                            logger.debug(f"[_database_retrieval] 关键词[{keyword}]匹配书籍: {title}")
            
            # 步骤2：如果关键词搜索没有结果，使用原始查询进行搜索
            if not results and query:
                logger.info(f"[_database_retrieval] 步骤2：关键词搜索无结果，使用原始查询搜索")
                
                # 查询课程表
                course_rows = await fetch_sql(
                    "SELECT course_name, description FROM courses WHERE course_name LIKE %s OR description LIKE %s LIMIT 5",
                    f"%{query}%", f"%{query}%"
                )
                db_queries_executed.append(f"courses LIKE '%{query}%' -> {len(course_rows)} rows")
                
                for row in course_rows:
                    content = row.get("description") or f"{row.get('course_name')}课程相关内容"
                    title = row.get('course_name', '')
                    if content and content not in seen_content:
                        seen_content.add(content)
                        results.append({
                            'knowledge_id': f"course_{title}",
                            'content': content,
                            'data_source': 'course_db',
                            'metadata': {
                                'title': title,
                                'source': 'course_db',
                                'source_type': '课程数据库',
                                'source_file': '课程数据库',
                                'is_real_data': True
                            },
                            'similarity': 0.75,
                            'rank': len(results) + 1,
                            'matched_keyword': 'query'
                        })
                
                # 查询电子书表
                book_rows = await fetch_sql(
                    "SELECT title, summary, author FROM books WHERE title LIKE %s OR summary LIKE %s OR author LIKE %s LIMIT 5",
                    f"%{query}%", f"%{query}%", f"%{query}%"
                )
                db_queries_executed.append(f"books LIKE '%{query}%' -> {len(book_rows)} rows")
                
                for row in book_rows:
                    content = row.get("summary") or f"《{row.get('title')}》- {row.get('author')}"
                    title = row.get('title', '')
                    if content and content not in seen_content:
                        seen_content.add(content)
                        results.append({
                            'knowledge_id': f"book_{title}",
                            'content': content,
                            'data_source': 'book_db',
                            'metadata': {
                                'title': title,
                                'author': row.get('author', ''),
                                'source': 'book_db',
                                'source_type': '电子书库',
                                'source_file': f"《{title}》",
                                'is_real_data': True
                            },
                            'similarity': 0.70,
                            'rank': len(results) + 1,
                            'matched_keyword': 'query'
                        })
        except Exception as db_err:
            logger.error(f"[_database_retrieval] 数据库查询失败，使用通用提示: {db_err}", exc_info=True)
            db_queries_executed.append(f"ERROR: {str(db_err)[:50]}")

        # 如果还是没有结果，返回"无结果"标记（不再插入让LLM自行发挥的通用知识提示）
        if not results:
            logger.warning(f"[_database_retrieval] 数据库无匹配结果，返回空结果（不再使用通用知识回退）")
            results.append({
                'knowledge_id': 'no_results_found',
                'content': '',  # 内容为空，让GenerationAgent直接回答无结果
                'data_source': 'no_results',
                'metadata': {
                    'title': '无匹配结果',
                    'source': 'no_results',
                    'source_type': '无数据',
                    'source_file': '',
                    'is_real_data': False,
                    'no_results': True  # 标记为无结果
                },
                'similarity': 0.0,
                'rank': 1
            })
        
        logger.info(f"[_database_retrieval] 查询完成: 总结果数={len(results)}, 来源分布={[r['data_source'] for r in results]}")
        
        return {
            'knowledge_chunks': results[:self.top_k],
            'retrieval_metadata': {
                'total_retrieved': len(results),
                'semantic_count': len(results),
                'keyword_count': len(results),
                'rerank_applied': False,
                'source_type': 'database_query',
                'debug_info': {
                    'query': query,
                    'intent': intent,
                    'concepts': concepts,
                    'db_queries': db_queries_executed,
                    'has_real_data': any(r.get('metadata', {}).get('is_real_data') for r in results)
                }
            }
        }


class ReasoningAgent(BaseAgent):
    """推理Agent - 使用LLM进行知识推理和综合"""
    
    def __init__(
        self, 
        agent_id: str = "reasoning_agent",
        llm_client: Optional[LLMClient] = None
    ):
        super().__init__(agent_id, AgentType.REASONING)
        self.llm_client = llm_client
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行推理任务 - 使用LLM进行深度推理"""
        retrieval_result = input_data.get('retrieval_result', {})
        understanding_result = input_data.get('understanding_result', {})
        
        knowledge_chunks = retrieval_result.get('knowledge_chunks', [])
        question_type = understanding_result.get('question_type', 'general')
        original_query = understanding_result.get('original_query', '')
        
        if not self.llm_client or not knowledge_chunks:
            return await self._fallback_reasoning(knowledge_chunks, question_type)
        
        # 使用LLM进行推理（带JSON格式强化和自动重试）
        base_prompt = """
你是一个智能推理助手。请基于提供的知识片段，对用户的问题进行深度分析和推理。

分析维度：
1. 逻辑推理：从知识中推导结论
2. 信息推断：发现缺失或隐含的信息
3. 多角度分析：从不同角度看待问题

【输出格式 - 严格JSON】
{
  "logical_conclusions": ["结论1", "结论2"],
  "inferred_info": {
    "missing_concepts": ["缺失概念1"],
    "related_topics": ["相关主题1"],
    "key_insights": ["关键洞察1"]
  },
  "perspectives": [
    {"perspective": "视角名称", "description": "描述"}
  ],
  "confidence": 0.95
}

知识片段：
"""
        
        knowledge_text = "\n\n".join([
            f"【知识{idx+1}】{chunk.get('content', '')[:300]}"
            for idx, chunk in enumerate(knowledge_chunks)
        ])
        
        system_prompt = _strengthen_json_prompt(base_prompt)
        prompt = f"{system_prompt}\n{knowledge_text}\n\n用户问题: {original_query}"
        
        for attempt in range(2):
            try:
                response = await self.llm_client.chat_completion(
                    prompt=prompt,
                    system_prompt=""
                )
                
                result = _extract_json(response)
                if result is not None:
                    return {
                        **result,
                        'knowledge_sources': knowledge_chunks,
                        'reasoning_trace': self._build_trace(knowledge_chunks)
                    }
                
                logger.warning(f"推理第{attempt+1}次JSON解析失败: {response[:150]}")
                if attempt == 0:
                    prompt += "\n\n【严重警告】上一次输出格式不符合要求！只输出纯JSON对象，不要包含任何其他文字！"
                
            except LLMError as e:
                logger.error(f"推理LLM调用失败（第{attempt+1}次）: {e}")
                if attempt == 0:
                    continue
                return await self._fallback_reasoning(knowledge_chunks, question_type)
        
        logger.warning("推理JSON解析失败，使用回退方案")
        return await self._fallback_reasoning(knowledge_chunks, question_type)
    
    async def _fallback_reasoning(self, knowledge_chunks: List[Dict], question_type: str) -> Dict[str, Any]:
        """规则匹配回退方案"""
        conclusions = []
        
        if question_type == 'compare':
            conclusions.append("基于检索到的知识，可以从多个维度进行对比分析")
        elif question_type == 'how':
            conclusions.append("检索到的知识包含了详细的操作步骤和方法")
        elif question_type == 'why':
            conclusions.append("可以从原理和机制角度解释原因")
        else:
            conclusions.append("基于检索到的知识进行综合分析")
        
        # 构建知识图谱
        graph = {'nodes': [], 'edges': []}
        for chunk in knowledge_chunks:
            graph['nodes'].append({
                'id': chunk['knowledge_id'],
                'content': chunk['content'][:100]
            })
        
        # 推断相关主题
        related_topics = []
        for chunk in knowledge_chunks:
            metadata = chunk.get('metadata', {})
            chapter = metadata.get('chapter', '')
            if chapter and chapter not in related_topics:
                related_topics.append(chapter)
        
        return {
            'logical_conclusions': conclusions,
            'inferred_info': {
                'missing_concepts': [],
                'related_topics': related_topics,
                'key_insights': []
            },
            'perspectives': [
                {'perspective': '综合视角', 'description': '结合多个知识块进行全面分析'}
            ],
            'knowledge_sources': knowledge_chunks,
            'reasoning_trace': self._build_trace(knowledge_chunks),
            'confidence': 0.7
        }
    
    def _build_trace(self, knowledge_chunks: List[Dict]) -> List[Dict[str, Any]]:
        """构建推理轨迹"""
        trace = []
        for i, chunk in enumerate(knowledge_chunks):
            trace.append({
                'step': i + 1,
                'action': '分析知识块',
                'knowledge_id': chunk['knowledge_id'],
                'content_preview': chunk['content'][:50]
            })
        return trace


class GenerationAgent(BaseAgent):
    """生成Agent - 使用真实LLM生成答案"""
    
    def __init__(
        self, 
        agent_id: str = "generation_agent",
        llm_client: Optional[LLMClient] = None
    ):
        super().__init__(agent_id, AgentType.GENERATION)
        self.llm_client = llm_client
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行生成任务 - 使用LLM生成高质量答案
        
        根据understanding_result中的requires_database_query标记选择系统提示词路径：
        - True：使用【数据库查询结果呈现】提示词，聚焦课程/电子书数据展示
        - False：使用【知识库问答】提示词，基于向量知识库生成
        """
        reasoning_result = input_data.get('reasoning_result', {})
        understanding_result = input_data.get('understanding_result', {})
        
        knowledge_sources = reasoning_result.get('knowledge_sources', [])
        logical_conclusions = reasoning_result.get('logical_conclusions', [])
        original_query = understanding_result.get('original_query', '')
        requires_database_query = understanding_result.get('requires_database_query', False)
        intent = understanding_result.get('intent', 'general_query')
        
        force_print("=" * 60)
        force_print("【GenerationAgent.execute】开始处理")
        force_print(f"  查询内容: '{original_query[:80]}{'...' if len(original_query) > 80 else ''}'")
        force_print(f"  intent: {intent}")
        force_print(f"  requires_database_query: {requires_database_query}")
        force_print(f"  knowledge_sources数量: {len(knowledge_sources)}")
        force_print(f"  LLM客户端可用: {self.llm_client is not None}")
        
        logger.info(f"[GenerationAgent] 开始生成答案: query='{original_query[:80]}...', intent={intent}, requires_db={requires_database_query}, source_count={len(knowledge_sources)}")
        
        # 记录输入的知识源
        force_print("  知识源详情:")
        for idx, source in enumerate(knowledge_sources):
            data_source = source.get('data_source', 'unknown')
            title = source.get('metadata', {}).get('title', '')
            is_real = source.get('metadata', {}).get('is_real_data', False)
            content_len = len(source.get('content', ''))
            force_print(f"    [{idx+1}] data_source={data_source}, title='{title[:30]}', is_real={is_real}, content_len={content_len}")
            logger.debug(f"[GenerationAgent] 知识源[{idx+1}]: data_source={data_source}, title='{title}', is_real_data={is_real}, content_len={len(source.get('content', ''))}")
        
        if not self.llm_client:
            force_print("  ⚠️ LLM客户端不可用，使用回退方案")
            logger.warning("[GenerationAgent] LLM客户端不可用，使用回退方案")
            result = await self._fallback_generation(original_query, knowledge_sources, logical_conclusions, requires_database_query, intent)
            force_print("【GenerationAgent.execute】完成（回退）")
            force_print("=" * 60)
            return result
        
        # 构建上下文
        force_print("  构建上下文...")
        context_parts = []
        has_real_data = False
        for i, source in enumerate(knowledge_sources, 1):
            content = source.get('content', '')
            metadata = source.get('metadata', {})
            data_source = source.get('data_source', metadata.get('source_type', '知识库'))
            is_real = metadata.get('is_real_data', False)
            if is_real:
                has_real_data = True
            
            context_parts.append(
                f"【参考文档{i}】（数据来源: {data_source}）\n"
                f"标题: {metadata.get('title', '')}\n"
                f"内容: {content}"
            )
        
        context_str = "\n\n".join(context_parts)
        force_print(f"  上下文长度: {len(context_str)} 字符")
        force_print(f"  has_real_data: {has_real_data}")
        logger.debug(f"[GenerationAgent] 构建的上下文长度: {len(context_str)}字符")
        
        # === 关键检测：如果知识源为空或全部为无结果标记，跳过LLM直接返回无结果 ===
        # 注意：空列表 [] 也必须拦截！否则LLM在空上下文下会用自己的训练数据生成答案
        should_skip_llm = False
        skip_reason = ""
        
        if not knowledge_sources:
            should_skip_llm = True
            skip_reason = "知识源为空（向量检索或数据库查询均无返回）"
        elif all(s.get('metadata', {}).get('no_results', False) for s in knowledge_sources):
            should_skip_llm = True
            skip_reason = "所有知识源均为 no_results 标记"
        
        if should_skip_llm:
            force_print(f"  ⚠️ 跳过LLM: {skip_reason}")
            logger.warning(f"[GenerationAgent] 跳过LLM: {skip_reason}")
            
            return {
                'answer': '抱歉，目前知识库中暂未找到与您查询相关的信息。请尝试换个问法或联系管理员添加相关内容。',
                'citations': [],
                'answer_metadata': {
                    'length': 0,
                    'source_count': 0,
                    'generation_time': datetime.now().isoformat(),
                    'data_source_type': 'no_results',
                    'has_real_data': False,
                    'no_results': True,
                    'debug_info': {
                        'intent': intent,
                        'requires_database_query': requires_database_query,
                        'skip_reason': skip_reason
                    }
                }
            }
        
        # 根据requires_database_query选择系统提示词
        if requires_database_query:
            force_print("  使用数据库查询提示词模板")
            logger.info(f"[GenerationAgent] 使用数据库查询提示词模板")
            system_prompt = """
你是课程学习平台的数据库查询结果呈现助手。

【核心职责】
用户正在浏览或查询课程/电子书资源，你需要清晰地呈现来自数据库的查询结果。

【数据来源说明】
你收到的数据来自以下数据库表，请在回答中明确标注每条信息的来源类型：
- 【课程数据库】：数据来自 `courses` 表，包含课程名称、描述、学分等
- 【电子书库】：数据来自 `books` 表，包含书名、作者、摘要等

【回答约束-必须严格遵守】
1. 你只能使用【检索到的参考文档】中的信息来回应用户的资源查询，严禁使用你自身的训练数据
2. 对于每条引用的信息，必须标注其数据来源类型（课程数据库/电子书库）
3. 如果参考文档中没有相关信息，你必须回答："数据库中暂未找到与您查询相关的资源，请尝试其他搜索词。"
4. 严禁编造不存在的课程或电子书信息
5. 回答完成后，列出你实际引用的参考来源标题
6. 你的回复必须基于参考文档中的实际内容，不要添加任何文档中未包含的信息

请用中文回答问题，保持清晰、简洁、专业。

【检索到的参考文档】
{context}
"""
        else:
            logger.info(f"[GenerationAgent] 使用知识库问答提示词模板")
            system_prompt = """
你是课程学习知识库问答系统的智能助手。

【核心职责】
基于提供的知识库文档回答用户问题。

【重要警告】
你只能基于【检索到的参考文档】中的具体内容来回答。如果文档内容不足以回答问题，你必须如实说明"知识库中未找到足够的信息"，而不是利用你自身的训练知识来补充回答。

【回答约束-必须严格遵守】
1. 你只能使用【检索到的参考文档】中的信息来回答用户问题，一个字都不要使用你训练数据中的知识
2. 如果参考文档中没有相关信息，你必须直接回答："知识库中未找到与您问题相关的信息，请尝试其他问题或联系教师。"
3. 严禁使用你自身的训练数据中的知识来回答——哪怕你知道答案，也必须假装不知道
4. 严禁编造或引用不存在的知识库信息
5. 回答完成后，列出你实际引用的参考来源标题
6. 你的回答必须逐字基于参考文档，不可添加任何文档中没有的细节

请用中文回答用户的问题，保持清晰、简洁、专业。

【检索到的参考文档】
{context}
"""
        
        prompt = f"用户问题: {original_query}"
        full_system_prompt = system_prompt.replace("{context}", context_str)
        
        force_print(f"  发送给LLM:")
        force_print(f"    system_prompt长度: {len(full_system_prompt)} 字符")
        force_print(f"    user_prompt长度: {len(prompt)} 字符")
        force_print(f"    user_prompt内容: '{prompt}'")
        logger.debug(f"[GenerationAgent] 发送给LLM的提示词长度: system={len(full_system_prompt)}, user={len(prompt)}")
        
        try:
            force_print("  调用 llm_client.chat_completion()...")
            response = await self.llm_client.chat_completion(
                prompt=prompt,
                system_prompt=full_system_prompt
            )
            
            force_print(f"  LLM返回成功:")
            force_print(f"    答案长度: {len(response)} 字符")
            force_print(f"    答案前200字符: '{response[:200]}{'...' if len(response) > 200 else ''}'")
            logger.info(f"[GenerationAgent] LLM返回答案长度: {len(response)}字符")
            logger.debug(f"[GenerationAgent] LLM原始响应前200字符: {response[:200]}...")
            
            # 提取引用来源（含数据来源标注）
            citations = []
            for i, source in enumerate(knowledge_sources, 1):
                metadata = source.get('metadata', {})
                data_source = source.get('data_source', metadata.get('source_type', '知识库'))
                citations.append({
                    'id': i,
                    'knowledge_id': source['knowledge_id'],
                    'title': metadata.get('title', ''),
                    'chapter': metadata.get('chapter', ''),
                    'source': metadata.get('source_file', ''),
                    'data_source': data_source,
                    'confidence': source.get('similarity', 0.8),
                    'is_real_data': metadata.get('is_real_data', False)
                })
            
            force_print(f"  引用数量: {len(citations)}")
            for i, citation in enumerate(citations[:3]):
                force_print(f"    citation[{i+1}]: knowledge_id={citation['knowledge_id'][:30]}, data_source={citation['data_source']}, is_real={citation['is_real_data']}")
            
            force_print("【GenerationAgent.execute】完成")
            force_print("=" * 60)
            
            return {
                'answer': response,
                'citations': citations,
                'answer_metadata': {
                    'length': len(response),
                    'source_count': len(knowledge_sources),
                    'generation_time': datetime.now().isoformat(),
                    'data_source_type': 'database_query' if requires_database_query else 'knowledge_base',
                    'has_real_data': has_real_data,
                    'debug_info': {
                        'intent': intent,
                        'requires_database_query': requires_database_query,
                        'knowledge_sources_summary': [
                            {'id': s['knowledge_id'], 'data_source': s.get('data_source'), 'is_real': s.get('metadata', {}).get('is_real_data', False)}
                            for s in knowledge_sources
                        ]
                    }
                }
            }
            
        except LLMError as e:
            force_print(f"  ❌ LLM生成失败: {e}")
            logger.error(f"[GenerationAgent] LLM生成失败，使用回退方案: {e}", exc_info=True)
            result = await self._fallback_generation(original_query, knowledge_sources, logical_conclusions, requires_database_query, intent)
            force_print("【GenerationAgent.execute】完成（异常回退）")
            force_print("=" * 60)
            return result
    
    async def _fallback_generation(self, query: str, knowledge_sources: List[Dict], conclusions: List[str],
                                    requires_database_query: bool = False, intent: str = 'general_query') -> Dict[str, Any]:
        """规则匹配回退方案 - 根据requires_database_query选择生成模式"""
        answer_parts = []
        
        # 路径A：数据库查询结果呈现
        if requires_database_query:
            answer_parts.append(f"根据您的查询，以下是为您找到的相关资源：\n\n")
            
            for i, source in enumerate(knowledge_sources[:5], 1):
                content = source.get('content', '')
                metadata = source.get('metadata', {})
                title = metadata.get('title', '')
                source_type = source.get('data_source', metadata.get('source_type', '知识库'))
                source_label = {'course_db': '📚 课程', 'book_db': '📖 电子书', 'general': '💡 通用'}.get(source_type, '📄 资料')
                
                if title:
                    answer_parts.append(f"**{i}. {source_label}：{title}**\n")
                answer_parts.append(f"{content[:200]}\n\n")
            
            if not knowledge_sources:
                answer_parts.append("数据库中暂未找到与您查询相关的资源。")
            
            answer = ''.join(answer_parts)
        else:
            # 路径B：标准知识库问答
            answer_parts.append(f"根据您的问题\"{query}\"，我为您整理了以下解答：\n")
            
            for i, source in enumerate(knowledge_sources[:3], 1):
                content = source.get('content', '')
                metadata = source.get('metadata', {})
                chapter = metadata.get('chapter', '')
                title = metadata.get('title', '')
                
                if chapter:
                    answer_parts.append(f"\n**{chapter} {title}**\n")
                answer_parts.append(content[:300] + "...\n")
            
            # 添加结论
            if conclusions:
                answer_parts.append("\n**总结**\n")
                for conclusion in conclusions:
                    answer_parts.append(f"- {conclusion}\n")
            
            answer = ''.join(answer_parts)
        
        # 构建引用
        citations = []
        for i, source in enumerate(knowledge_sources, 1):
            metadata = source.get('metadata', {})
            citations.append({
                'id': i,
                'knowledge_id': source['knowledge_id'],
                'title': metadata.get('title', ''),
                'chapter': metadata.get('chapter', ''),
                'confidence': source.get('similarity', 0.8)
            })
        
        return {
            'answer': answer,
            'citations': citations,
            'answer_metadata': {
                'length': len(answer),
                'source_count': len(knowledge_sources),
                'generation_time': datetime.now().isoformat()
            }
        }


class ValidationAgent(BaseAgent):
    """验证Agent - 使用LLM进行答案质量验证"""
    
    def __init__(
        self, 
        agent_id: str = "validation_agent",
        llm_client: Optional[LLMClient] = None
    ):
        super().__init__(agent_id, AgentType.VALIDATION)
        self.llm_client = llm_client
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行验证任务"""
        generation_result = input_data.get('generation_result', {})
        reasoning_result = input_data.get('reasoning_result', {})
        
        answer = generation_result.get('answer', '')
        knowledge_sources = reasoning_result.get('knowledge_sources', [])
        
        # === 第一步：基于内容的事实准确性检查（不依赖LLM）===
        factual_check = self._content_accuracy_check(answer, knowledge_sources)
        
        if not self.llm_client:
            return await self._fallback_validation(answer, knowledge_sources, factual_check)
        
        # 如果内容检查已发现明显问题，直接返回低分
        if not factual_check['has_any_real_content']:
            logger.warning(f"[ValidationAgent] 答案中无任何来自知识源的内容，直接判定为无效")
            return {
                'accuracy_score': factual_check['accuracy_score'],
                'completeness_score': 0.0,
                'consistency_score': 0.5,
                'overall_score': factual_check['accuracy_score'],
                'validation_feedback': factual_check['feedback'],
                'is_valid': False
            }
        
        # 使用LLM进行验证（带JSON格式强化和自动重试）
        base_prompt = """
你是一个答案质量验证助手。请严格评估生成的答案质量。

评估维度：
1. 准确性（最重要）：答案是否严格基于提供的知识，有无编造或添加知识中不存在的信息
2. 完整性：答案是否覆盖了问题的关键方面
3. 一致性：答案内部是否一致，有无矛盾

【关键要求】
- 如果答案中包含了知识来源中没有的信息，accuracy_score 必须打低分（低于0.3）
- 只有答案完全基于提供的知识来源，才能给高分

【输出格式 - 严格JSON】
{
  "accuracy_score": 0.95,
  "completeness_score": 0.85,
  "consistency_score": 0.90,
  "overall_score": 0.90,
  "feedback": "具体的改进建议，指出哪些内容不是来自知识来源",
  "is_valid": true
}

知识来源：
{knowledge}

答案：
{answer}
"""
        
        system_prompt = _strengthen_json_prompt(base_prompt)
        knowledge_text = "\n\n".join([
            f"【知识{idx+1}】{chunk.get('content', '')}"
            for idx, chunk in enumerate(knowledge_sources)
        ])
        prompt = system_prompt.replace("{knowledge}", knowledge_text).replace("{answer}", answer)
        
        for attempt in range(2):
            try:
                response = await self.llm_client.chat_completion(
                    prompt=prompt,
                    system_prompt=""
                )
                
                result = _extract_json(response)
                if result is not None:
                    # 结合内容检查和LLM验证结果
                    combined_score = (factual_check['accuracy_score'] * 0.6 + 
                                     result.get('accuracy_score', 0.5) * 0.4)
                    result['accuracy_score'] = combined_score
                    result['overall_score'] = (combined_score * 0.4 + 
                                               result.get('completeness_score', 0.5) * 0.3 +
                                               result.get('consistency_score', 0.5) * 0.3)
                    result['is_valid'] = result['overall_score'] >= 0.6
                    result['factual_check'] = factual_check
                    return result
                
                logger.warning(f"验证第{attempt+1}次JSON解析失败: {response[:150]}")
                if attempt == 0:
                    prompt += "\n\n【严重警告】上一次输出格式不符合要求！只输出纯JSON对象，不要包含任何其他文字！"
                
            except LLMError as e:
                logger.error(f"验证LLM调用失败（第{attempt+1}次）: {e}")
                if attempt == 0:
                    continue
                return await self._fallback_validation(answer, knowledge_sources, factual_check)
        
        logger.warning("验证JSON解析失败，使用回退方案")
        return await self._fallback_validation(answer, knowledge_sources, factual_check)
    
    def _content_accuracy_check(self, answer: str, knowledge_sources: List[Dict]) -> Dict[str, Any]:
        """基于内容的事实准确性检查 - 不依赖LLM
        
        原理：提取知识源中的关键短语/句子，检查答案中是否包含了这些内容。
        如果答案内容完全不在知识源中出现，则判定为编造。
        """
        if not knowledge_sources or not answer:
            return {
                'accuracy_score': 0.0,
                'has_any_real_content': False,
                'feedback': '答案或知识源为空'
            }
        
        # 提取所有知识源的内容文本
        source_texts = []
        for source in knowledge_sources:
            content = source.get('content', '')
            if content:
                source_texts.append(content)
        
        if not source_texts:
            return {
                'accuracy_score': 0.0,
                'has_any_real_content': False,
                'feedback': '知识源内容为空'
            }
        
        combined_source = ' '.join(source_texts)
        
        # 如果知识源内容为空（no_results标记），直接返回
        if not combined_source.strip():
            return {
                'accuracy_score': 0.0,
                'has_any_real_content': False,
                'feedback': '知识源内容为空（数据库无匹配结果）'
            }
        
        # 将答案分成句子，检查每个句子是否在知识源中有依据
        import re as _re
        sentences = _re.split(r'[。！？\n]', answer)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
        
        if not sentences:
            return {
                'accuracy_score': 0.3,
                'has_any_real_content': True,
                'feedback': '答案太短无法有效验证'
            }
        
        # 检查每个句子是否包含知识源中的关键词或短语
        supported_count = 0
        for sentence in sentences:
            # 提取句子中的关键名词短语（简单做法：取2-4个字的词）
            words = [w for w in sentence if len(w) >= 2]
            # 检查这些词是否在知识源中出现
            matched = sum(1 for w in words if w in combined_source)
            if matched >= max(1, len(words) * 0.3):  # 至少30%的词汇匹配
                supported_count += 1
        
        accuracy = supported_count / len(sentences) if sentences else 0.0
        
        feedback = []
        if accuracy < 0.3:
            feedback.append(f"警告：答案中仅 {accuracy:.0%} 的内容能在知识源中找到依据，可能存在编造")
        elif accuracy < 0.7:
            feedback.append(f"部分内容（{accuracy:.0%}）有知识源支持，但部分内容需要核实")
        else:
            feedback.append(f"答案内容基本有知识源支持（{accuracy:.0%}）")
        
        return {
            'accuracy_score': max(0.1, accuracy),
            'has_any_real_content': accuracy > 0.1,
            'feedback': '; '.join(feedback)
        }
    
    async def _fallback_validation(self, answer: str, knowledge_sources: List[Dict], 
                                     factual_check: Optional[Dict] = None) -> Dict[str, Any]:
        """规则匹配回退方案 - 使用内容检查结果"""
        # 使用内容检查结果（如果有）
        if factual_check:
            accuracy_score = factual_check['accuracy_score']
            has_real_content = factual_check['has_any_real_content']
        else:
            # 如果没有内容检查结果，执行基本检查
            source_content = ' '.join([s.get('content', '') for s in knowledge_sources if s.get('content')])
            answer_words = set(answer.split())
            source_words = set(source_content.split())
            matched = answer_words & source_words
            accuracy_score = len(matched) / max(len(source_words), 1) if source_words else 0.0
            has_real_content = accuracy_score > 0.05
        
        # 完整性检查
        min_length = 50
        max_length = 3000
        if len(answer) < min_length:
            completeness_score = max(0.1, len(answer) / min_length)
        elif len(answer) > max_length:
            completeness_score = 0.9
        else:
            completeness_score = 0.5 + (len(answer) - min_length) / (max_length - min_length) * 0.4
        
        # 一致性检查
        consistency_score = 0.85
        
        # 综合评分
        overall_score = accuracy_score * 0.5 + completeness_score * 0.25 + consistency_score * 0.25
        
        # 生成反馈
        feedback_parts = []
        if factual_check:
            feedback_parts.append(factual_check.get('feedback', ''))
        if accuracy_score < 0.3:
            feedback_parts.append("答案准确率极低，内容可能为编造")
        if completeness_score < 0.5:
            feedback_parts.append("答案不够完整")
        if not feedback_parts:
            feedback_parts.append("答案质量良好")
        
        return {
            'accuracy_score': accuracy_score,
            'completeness_score': completeness_score,
            'consistency_score': consistency_score,
            'overall_score': overall_score,
            'validation_feedback': "; ".join(f for f in feedback_parts if f),
            'is_valid': overall_score >= 0.5 and has_real_content
        }


class RecommendAgent(BaseAgent):
    """推荐Agent - 使用向量数据库进行相关知识推荐"""
    
    def __init__(
        self, 
        agent_id: str = "recommend_agent",
        knowledge_repo: Optional[ChromaKnowledgeRepository] = None,
        llm_client: Optional[LLMClient] = None
    ):
        super().__init__(agent_id, AgentType.RECOMMEND)
        self.knowledge_repo = knowledge_repo
        self.llm_client = llm_client
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行推荐任务"""
        generation_result = input_data.get('generation_result', {})
        understanding_result = input_data.get('understanding_result', {})
        
        citations = generation_result.get('citations', [])
        context_info = understanding_result.get('context_info', {})
        
        if not self.knowledge_repo:
            return await self._fallback_recommend(citations, context_info)
        
        try:
            # 获取引用来源的相关知识
            related_knowledge = []
            user_level = context_info.get('user_level', 'intermediate')
            
            # 基于引用来源的关键词进行推荐
            keywords = set()
            for citation in citations:
                keywords.add(citation.get('title', ''))
                keywords.add(citation.get('chapter', ''))
            
            if keywords:
                # 使用第一个关键词进行相关检索
                query = " ".join(list(keywords)[:3])
                search_results = await self.knowledge_repo.search(
                    query=query,
                    limit=5,
                    use_rerank=False
                )
                
                for result in search_results:
                    kp = result.knowledge_point
                    # 过滤掉已引用的内容
                    is_cited = any(c.get('knowledge_id') == kp.id for c in citations)
                    if not is_cited:
                        related_knowledge.append({
                            'knowledge_id': kp.id,
                            'title': kp.title,
                            'course': kp.course,
                            'chapter': kp.chapter,
                            'relevance': result.score
                        })
            
            # 规划学习路径
            learning_path = await self._plan_learning_path(user_level, citations)
            
            return {
                'related_knowledge': related_knowledge[:5],
                'learning_path': learning_path,
                'personalized_content': related_knowledge[:3]
            }
            
        except Exception as e:
            logger.error(f"推荐失败，使用回退方案: {e}")
            return await self._fallback_recommend(citations, context_info)
    
    async def _fallback_recommend(self, citations: List[Dict], context_info: Dict[str, Any]) -> Dict[str, Any]:
        """规则匹配回退方案 - 返回空结果，不再编造虚假知识"""
        # 不使用硬编码的mock数据，返回空结果
        related_knowledge = []
        
        # 规划学习路径（基于实际引用内容，而非硬编码）
        learning_path = []
        if citations:
            learning_path = await self._plan_learning_path(
                context_info.get('user_level', 'intermediate'), 
                citations
            )
        
        return {
            'related_knowledge': related_knowledge,
            'learning_path': learning_path,
            'personalized_content': []
        }
    
    async def _plan_learning_path(self, user_level: str, citations: List[Dict]) -> List[Dict[str, Any]]:
        """规划学习路径 - 基于实际引用内容"""
        if not citations:
            return []
            
        path = []
        levels_map = {
            '基础': '基础', 'intermediate': '中等', '中等': '中等',
            'advanced': '较难', '较难': '较难'
        }
        level_label = levels_map.get(user_level, '中等')
        
        # 从引用内容中提取章节信息
        chapters = []
        for citation in citations:
            chapter = citation.get('chapter', '')
            title = citation.get('title', '')
            if chapter:
                chapters.append(f"{chapter}: {title}" if title else chapter)
        
        if not chapters:
            chapters = [citation.get('title', '相关知识') for citation in citations[:3]]
        
        for i, chapter in enumerate(chapters[:3], 1):
            path.append({
                'step': i,
                'level': level_label,
                'description': f'深入学习: {chapter}',
                'estimated_time': f'{10 + i * 5}分钟',
                'source': citation.get('knowledge_id', '') if i <= len(citations) else ''
            })
        
        return path


class CoordinationAgent(BaseAgent):
    """协调Agent - 负责整体协调和任务分配"""
    
    def __init__(
        self, 
        agent_id: str = "coordination_agent",
        llm_client: Optional[LLMClient] = None,
        knowledge_repo: Optional[ChromaKnowledgeRepository] = None
    ):
        super().__init__(agent_id, AgentType.COORDINATION)
        self.llm_client = llm_client
        self.knowledge_repo = knowledge_repo
        self.agents = {}
        self.message_bus = MessageBus()
        self.scheduler = TaskScheduler(self.message_bus)
        self.workflow_engine = WorkflowEngine(self.message_bus, self.scheduler)
        self.task_history = []
        
        self._initialize_agents()
        self._register_workflows()
    
    def _initialize_agents(self):
        """初始化所有Agent（集成真实LLM和向量数据库）"""
        self.agents = {
            'understanding': UnderstandingAgent(llm_client=self.llm_client),
            'retrieval': RetrievalAgent(knowledge_repo=self.knowledge_repo),
            'reasoning': ReasoningAgent(llm_client=self.llm_client),
            'generation': GenerationAgent(llm_client=self.llm_client),
            'validation': ValidationAgent(llm_client=self.llm_client),
            'recommend': RecommendAgent(
                knowledge_repo=self.knowledge_repo,
                llm_client=self.llm_client
            )
        }
        
        # 注册Agent到消息总线
        for agent_id, agent in self.agents.items():
            self.message_bus.register_agent(agent_id, agent)
    
    def _register_workflows(self):
        """注册工作流"""
        qa_workflow = {
            'name': 'question_answering',
            'description': '智能问答工作流',
            'steps': {
                'understanding': {
                    'agent': 'understanding',
                    'input_params': {},
                    'dependencies': []
                },
                'retrieval': {
                    'agent': 'retrieval',
                    'input_params': {},
                    'dependencies': ['understanding']
                },
                'reasoning': {
                    'agent': 'reasoning',
                    'input_params': {},
                    'dependencies': ['retrieval']
                },
                'generation': {
                    'agent': 'generation',
                    'input_params': {},
                    'dependencies': ['understanding', 'reasoning']
                },
                'validation': {
                    'agent': 'validation',
                    'input_params': {},
                    'dependencies': ['generation']
                },
                'recommend': {
                    'agent': 'recommend',
                    'input_params': {},
                    'dependencies': ['generation']
                }
            }
        }
        
        self.workflow_engine.register_workflow('qa', qa_workflow)
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行协调任务"""
        query = input_data.get('query', '')
        context = input_data.get('context', {})
        return await self.process_query(query, context)
    
    async def process_query(self, query: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """处理用户查询 - 执行完整的多Agent工作流"""
        context = context or {}
        
        # 记录开始时间
        start_time = datetime.now()
        logger.info(f"[CoordinationAgent] ====== 开始处理查询 ======")
        logger.info(f"[CoordinationAgent] 查询内容: '{query[:100]}{'...' if len(query) > 100 else ''}'")
        logger.info(f"[CoordinationAgent] 查询长度: {len(query)} 字符")
        logger.info(f"[CoordinationAgent] 上下文信息: {json.dumps(context, ensure_ascii=False)[:200]}")
        
        try:
            # 执行问答工作流
            input_data = {
                'query': query,
                'context': context
            }
            
            logger.info(f"[CoordinationAgent] 开始执行问答工作流...")
            results = await self.workflow_engine.execute_workflow('qa', input_data)
            logger.info(f"[CoordinationAgent] 工作流执行完成")
            
            # 详细记录每个Agent的执行结果
            for step_id, step_result in results.items():
                status = step_result.get('status', 'unknown')
                output = step_result.get('output', {})
                logger.debug(f"[CoordinationAgent] Step {step_id}: status={status}, output_keys={list(output.keys())}")
            
            # 记录任务历史（包含完整调试信息）
            self.task_history.append({
                'query': query,
                'timestamp': start_time.isoformat(),
                'results': results,
                'full_debug': self._build_debug_report(results)
            })
            
            # 聚合结果
            final_output = self._aggregate_results(results, query)
            
            # 添加执行时间
            execution_time = (datetime.now() - start_time).total_seconds()
            final_output['execution_time'] = execution_time
            
            # 关键信息摘要日志
            answer = final_output.get('answer', '')
            citations = final_output.get('citations', [])
            has_real_data = any(c.get('is_real_data') for c in citations)
            
            logger.info(f"[CoordinationAgent] ====== 查询处理完成 ======")
            logger.info(f"[CoordinationAgent] 耗时: {execution_time:.2f}秒")
            logger.info(f"[CoordinationAgent] 答案长度: {len(answer)} 字符")
            logger.info(f"[CoordinationAgent] 引用数量: {len(citations)}")
            logger.info(f"[CoordinationAgent] 包含真实数据: {has_real_data}")
            logger.info(f"[CoordinationAgent] 验证分数: {final_output.get('validation_score', 0.0):.2f}")
            
            # 如果没有真实数据，发出警告
            if citations and not has_real_data:
                logger.warning(f"[CoordinationAgent] ⚠️ 警告：所有引用都不是真实数据！")
            
            return final_output
            
        except Exception as e:
            logger.error(f"[CoordinationAgent] ❌ 协调Agent执行失败: {e}", exc_info=True)
            return {
                'error': str(e),
                'query': query,
                'status': 'failed',
                'execution_time': (datetime.now() - start_time).total_seconds()
            }
    
    def _build_debug_report(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """构建完整的调试报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'steps': {}
        }
        
        for step_id, step_result in results.items():
            status = step_result.get('status', 'unknown')
            output = step_result.get('output', {})
            
            report['steps'][step_id] = {
                'status': status,
                'output_keys': list(output.keys()),
                'debug_info': output.get('debug_info', {}),
                'metadata': output.get('retrieval_metadata', output.get('answer_metadata', {}))
            }
            
            # 特别记录检索结果
            if step_id == 'retrieval' and 'knowledge_chunks' in output:
                chunks = output['knowledge_chunks']
                report['steps']['retrieval']['knowledge_chunks_summary'] = [
                    {
                        'knowledge_id': c['knowledge_id'],
                        'data_source': c.get('data_source', 'unknown'),
                        'is_real_data': c.get('metadata', {}).get('is_real_data', False),
                        'similarity': c.get('similarity', 0.0),
                        'title': c.get('metadata', {}).get('title', '')
                    }
                    for c in chunks
                ]
            
            # 特别记录生成结果
            if step_id == 'generation' and 'citations' in output:
                report['steps']['generation']['citations_summary'] = [
                    {
                        'knowledge_id': c['knowledge_id'],
                        'data_source': c.get('data_source', 'unknown'),
                        'is_real_data': c.get('is_real_data', False),
                        'title': c.get('title', '')
                    }
                    for c in output['citations']
                ]
        
        return report
    
    def _aggregate_results(self, results: Dict[str, Any], query: str) -> Dict[str, Any]:
        """聚合所有Agent的结果"""
        # 获取各Agent的执行结果
        understanding_result = results.get('understanding', {}).get('output', {})
        retrieval_result = results.get('retrieval', {}).get('output', {})
        reasoning_result = results.get('reasoning', {}).get('output', {})
        generation_result = results.get('generation', {}).get('output', {})
        validation_result = results.get('validation', {}).get('output', {})
        recommend_result = results.get('recommend', {}).get('output', {})
        
        # 获取检索到的知识块
        knowledge_chunks = retrieval_result.get('knowledge_chunks', [])
        
        # 分析数据来源分布
        data_source_distribution = {}
        has_real_data = False
        for chunk in knowledge_chunks:
            source = chunk.get('data_source', 'unknown')
            data_source_distribution[source] = data_source_distribution.get(source, 0) + 1
            if chunk.get('metadata', {}).get('is_real_data', False):
                has_real_data = True
        
        # 构建工作流执行详情（包含完整调试信息）
        workflow_details = {
            'understanding': {
                'status': results.get('understanding', {}).get('status', 'unknown'),
                'intent': understanding_result.get('intent'),
                'question_type': understanding_result.get('question_type'),
                'entities': understanding_result.get('entities', {}).get('concepts', []),
                'requires_database_query': understanding_result.get('requires_database_query', False),
                'requires_knowledge_base_search': understanding_result.get('requires_knowledge_base_search', False),
                'debug_info': understanding_result.get('debug_info', {})
            },
            'retrieval': {
                'status': results.get('retrieval', {}).get('status', 'unknown'),
                'knowledge_count': len(knowledge_chunks),
                'data_source_distribution': data_source_distribution,
                'has_real_data': has_real_data,
                'metadata': retrieval_result.get('retrieval_metadata', {}),
                'knowledge_chunks_summary': [
                    {
                        'knowledge_id': c['knowledge_id'],
                        'data_source': c.get('data_source', 'unknown'),
                        'is_real_data': c.get('metadata', {}).get('is_real_data', False),
                        'title': c.get('metadata', {}).get('title', ''),
                        'similarity': c.get('similarity', 0.0)
                    }
                    for c in knowledge_chunks
                ]
            },
            'reasoning': {
                'status': results.get('reasoning', {}).get('status', 'unknown'),
                'conclusions': reasoning_result.get('logical_conclusions', []),
                'perspectives': reasoning_result.get('perspectives', []),
                'confidence': reasoning_result.get('confidence', 0.0)
            },
            'generation': {
                'status': results.get('generation', {}).get('status', 'unknown'),
                'answer_length': len(generation_result.get('answer', '')),
                'has_real_data': generation_result.get('answer_metadata', {}).get('has_real_data', False),
                'debug_info': generation_result.get('answer_metadata', {}).get('debug_info', {})
            },
            'validation': {
                'status': results.get('validation', {}).get('status', 'unknown'),
                'overall_score': validation_result.get('overall_score', 0.0),
                'accuracy_score': validation_result.get('accuracy_score', 0.0),
                'completeness_score': validation_result.get('completeness_score', 0.0),
                'consistency_score': validation_result.get('consistency_score', 0.0),
                'feedback': validation_result.get('validation_feedback', '')
            },
            'recommend': {
                'status': results.get('recommend', {}).get('status', 'unknown'),
                'related_count': len(recommend_result.get('related_knowledge', []))
            }
        }
        
        # 获取引用列表并标记真实数据来源
        citations = generation_result.get('citations', [])
        enhanced_citations = []
        for citation in citations:
            enhanced_citations.append({
                **citation,
                'warning': '⚠️ 非真实数据' if not citation.get('is_real_data', False) else ''
            })
        
        final_output = {
            'query': query,
            'answer': generation_result.get('answer', ''),
            'citations': enhanced_citations,
            'confidence': validation_result.get('overall_score', 0.0),
            'validation_score': validation_result.get('overall_score', 0.0),
            'validation_feedback': validation_result.get('validation_feedback', ''),
            'related_knowledge': recommend_result.get('related_knowledge', []),
            'learning_path': recommend_result.get('learning_path', []),
            'workflow_details': workflow_details,
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'debug_info': {
                'has_real_data': has_real_data,
                'data_source_distribution': data_source_distribution,
                'knowledge_chunk_count': len(knowledge_chunks),
                'understanding_intent': understanding_result.get('intent'),
                'requires_database_query': understanding_result.get('requires_database_query', False),
                'retrieval_source_type': retrieval_result.get('retrieval_metadata', {}).get('source_type', 'unknown')
            }
        }
        
        # 如果没有真实数据，添加警告标记
        if not has_real_data and knowledge_chunks:
            final_output['debug_info']['warning'] = '所有知识源都不是真实数据，答案可能包含虚构内容'
        
        return final_output
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            'agents': {
                agent_id: agent.get_status()
                for agent_id, agent in self.agents.items()
            },
            'tasks': self.scheduler.get_all_tasks(),
            'workflows': list(self.workflow_engine.workflows.keys()),
            'task_history_count': len(self.task_history)
        }
    
    def get_task_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取任务历史"""
        return self.task_history[-limit:]


# 导出所有Agent类
__all__ = [
    'UnderstandingAgent',
    'RetrievalAgent',
    'ReasoningAgent',
    'GenerationAgent',
    'ValidationAgent',
    'RecommendAgent',
    'CoordinationAgent'
]