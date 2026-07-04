# 多Agent智能问答系统架构设计

## 一、系统概述

### 1.1 系统目标
基于优化后的知识文档库，构建多Agent协同的智能问答系统，为学生提供准确、全面、个性化的计算机专业知识解答。

### 1.2 核心特性
- **多Agent协作**：多个专业Agent协同工作，各司其职
- **知识驱动**：基于向量化的知识库进行检索和推理
- **上下文感知**：理解对话历史，提供连贯的回答
- **个性化推荐**：根据学生水平推荐相关知识
- **可解释性**：提供答案来源和推理过程

---

## 二、Agent架构设计

### 2.1 Agent分类

```
┌─────────────────────────────────────────────────────────┐
│                    协调层 (Coordination Layer)           │
│              Coordination Agent (协调Agent)              │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼──────┐ ┌────▼─────┐ ┌──────▼──────┐
│  理解Agent   │ │ 推理Agent │ │验证Agent    │
│ Understanding│ │ Reasoning │ │Validation  │
└──────────────┘ └──────────┘ └─────────────┘
        │              │              ▲
        │              │              │
        │    ┌─────────┴─────────┐    │
        │    │                   │    │
        └───▶│课程电子书检索Agent │───▶│个性化推荐Agent│
            │CourseEbookRetrieval│    │PersonalizedRec│
            └────────────────────┘    └────────────────┘
```

### 2.2 Agent职责定义

#### 2.2.1 协调Agent (Coordination Agent)

**职责**
- 任务分解与分配
- Agent间通信协调
- 工作流控制
- 异常处理与重试
- 结果聚合与输出

**核心能力**
```python
class CoordinationAgent:
    def __init__(self):
        self.agents = {
            'understanding': UnderstandingAgent(),
            'reasoning': ReasoningAgent(),
            'generation': GenerationAgent(),
            'validation': ValidationAgent(),
            # 【新增】课程业务专用Agent
            'course_retrieval': CourseEbookRetrievalAgent(),
            'personalized_rec': PersonalizedRecommendationAgent()
        }
        self.workflow_graph = self._build_workflow()
    
    def _build_workflow(self):
        """构建工作流图【调整】：更新为课程业务专用链路"""
        return {
            'start': ['understanding'],
            'understanding': ['course_retrieval'],
            'course_retrieval': ['personalized_rec'],
            'personalized_rec': ['validation'],
            'validation': ['end']
        }
    
    async def process_query(self, query: str, context: dict) -> dict:
        """处理用户查询"""
        # 1. 任务分解
        tasks = self._decompose_task(query, context)
        
        # 2. 执行工作流
        result = await self._execute_workflow(tasks)
        
        # 3. 结果聚合
        return self._aggregate_result(result)
```

**信息传递机制**
- 使用消息队列进行Agent间通信
- 每个消息包含：sender、receiver、payload、timestamp、correlation_id
- 支持同步和异步通信模式

---

#### 2.2.2 理解Agent (Understanding Agent)

**职责**
- 用户意图识别
- 关键信息提取
- 问题分类与路由
- 上下文理解

**核心能力**
```python
class UnderstandingAgent:
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()
        self.question_analyzer = QuestionAnalyzer()
    
    async def understand(self, query: str, context: dict) -> UnderstandingResult:
        """理解用户查询"""
        # 1. 意图识别
        intent = await self.intent_classifier.classify(query)
        
        # 2. 实体提取
        entities = await self.entity_extractor.extract(query)
        
        # 3. 问题分析
        question_type = await self.question_analyzer.analyze(query)
        
        # 4. 上下文整合
        context_info = self._integrate_context(context)
        
        return UnderstandingResult(
            intent=intent,
            entities=entities,
            question_type=question_type,
            context_info=context_info,
            query_embedding=self._encode_query(query)
        )
```

**输出格式**
```json
{
  "intent": "explain",
  "question_type": "how_to",
  "entities": {
    "concepts": ["二叉搜索树"],
    "properties": ["查找", "插入", "删除"]
  },
  "keywords": ["二叉搜索树", "查找"],
  "complexity": "中等",
  "requires_knowledge_base_search": true,
  "requires_database_query": false,
  "context_info": {
    "previous_topics": ["数组", "链表"],
    "user_level": "intermediate"
  },
  "query_embedding": [0.1, 0.2, ...]
}
```

> **字段说明**：
> - `intent`：意图分类（`recommend`/`explain`/`how_to`/`compare`/`troubleshoot`/`general_query`）
> - `requires_knowledge_base_search`：是否需要从向量知识库检索文档
> - `requires_database_query`：是否需要查询数据库中的课程/书籍（为True时触发下游Agent的数据库查询路径）

---

#### 2.2.3 检索Agent (Retrieval Agent)

**职责【调整】**
- 向量数据库检索（通用知识库）
- **数据库查询（课程/电子书表）**【新增】
- 多路召回策略
- 结果重排序
- 相关性评分
- **数据来源标注**【新增】

**核心能力**
```python
class RetrievalAgent:
    def __init__(self):
        self.vector_db = VectorDatabase()
        self.retrievers = {
            'semantic': SemanticRetriever(),
            'keyword': KeywordRetriever(),
            'hybrid': HybridRetriever()
        }
        self.reranker = Reranker()
    
    async def retrieve(self, understanding_result: UnderstandingResult) -> RetrievalResult:
        """检索相关知识 - 根据requires_database_query选择路径"""
        if understanding_result.requires_database_query:
            return await self._database_retrieval(understanding_result)
        else:
            return await self._vector_retrieval(understanding_result)
    
    async def _vector_retrieval(self, understanding_result) -> RetrievalResult:
        """向量知识库检索（原逻辑）"""
        # 1. 多路召回
        semantic_results = await self.retrievers['semantic'].retrieve(
            understanding_result.query_embedding
        )
        keyword_results = await self.retrievers['keyword'].retrieve(
            understanding_result.entities
        )
        
        # 2. 结果融合
        combined_results = self._fuse_results(
            semantic_results, 
            keyword_results
        )
        
        # 3. 重排序
        reranked_results = await self.reranker.rerank(
            combined_results,
            understanding_result
        )
        
        return RetrievalResult(
            knowledge_chunks=reranked_results,
            retrieval_metadata=self._build_metadata(reranked_results)
        )
    
    async def _database_retrieval(self, understanding_result) -> RetrievalResult:
        """数据库查询路径【新增】
        
        当requires_database_query=True时触发。
        从courses表和books表进行模糊匹配，返回含data_source标注的结果。
        """
        courses = await self.course_db.search(
            understanding_result.keywords
        )
        ebooks = await self.ebook_db.search(
            understanding_result.keywords
        )
        return DatabaseRetrievalResult(
            knowledge_chunks=[...],  # 含data_source字段
            retrieval_metadata={'source_type': 'database_query'}
        )
```

**检索策略**
- **语义检索**：基于向量相似度
- **关键词检索**：基于实体匹配
- **混合检索**：结合语义和关键词
- **分层检索**：先粗检索再精检索
- **数据库查询**【新增】：基于意图标记路由到courses/books表

---

#### 2.2.4 推理Agent (Reasoning Agent)

**职责**
- 知识推理与综合
- 逻辑一致性检查
- 缺失信息推断
- 多角度分析

**核心能力**
```python
class ReasoningAgent:
    def __init__(self):
        self.knowledge_graph = KnowledgeGraph()
        self.reasoner = LogicalReasoner()
        self.inferrer = InformationInferrer()
    
    async def reason(self, retrieval_result: RetrievalResult, 
                    understanding_result: UnderstandingResult) -> ReasoningResult:
        """基于检索知识进行推理"""
        # 1. 知识图谱构建
        kg = await self.knowledge_graph.build(retrieval_result.knowledge_chunks)
        
        # 2. 逻辑推理
        logical_conclusions = await self.reasoner.reason(
            kg,
            understanding_result.question_type
        )
        
        # 3. 信息推断
        inferred_info = await self.inferrer.infer(
            retrieval_result.knowledge_chunks,
            understanding_result.entities
        )
        
        # 4. 多角度分析
        perspectives = self._analyze_perspectives(
            retrieval_result.knowledge_chunks
        )
        
        return ReasoningResult(
            logical_conclusions=logical_conclusions,
            inferred_info=inferred_info,
            perspectives=perspectives,
            reasoning_trace=self._build_trace()
        )
```

**推理类型**
- **演绎推理**：从一般到特殊
- **归纳推理**：从特殊到一般
- **类比推理**：基于相似性推理
- **因果推理**：分析因果关系

---

#### 2.2.5 生成Agent (Generation Agent)

**职责**
- 答案生成
- 多样化表达
- 格式化输出
- 引用标注
- **根据requires_database_query切换系统提示词**【新增】

**核心能力**
```python
class GenerationAgent:
    def __init__(self):
        self.generator = AnswerGenerator()
        self.formatter = OutputFormatter()
        self.citation_manager = CitationManager()
    
    async def generate(self, reasoning_result: ReasoningResult,
                      understanding_result: UnderstandingResult) -> GenerationResult:
        """生成答案 - 根据requires_database_query选择提示词路径"""
        # 选择系统提示词
        if understanding_result.requires_database_query:
            system_prompt = self._build_db_query_prompt()
        else:
            system_prompt = self._build_knowledge_prompt()
        
        # 答案生成
        answer = await self.generator.generate(
            reasoning_result,
            understanding_result,
            system_prompt=system_prompt
        )
        
        # 引用标注（含data_source字段）
        citations = await self.citation_manager.add_citations(
            formatted_answer,
            reasoning_result.knowledge_sources,
            include_data_source=True  # 【新增】包含数据来源标注
        )
        
        return GenerationResult(
            answer=formatted_answer,
            citations=citations,
            answer_metadata={
                'data_source_type': 'database_query' if requires_database_query else 'knowledge_base'
            }
        )
    
    def _build_db_query_prompt(self) -> str:
        """构建数据库查询结果呈现提示词【新增】"""
        return '''
【核心职责】清晰呈现来自数据库的课程/电子书查询结果
【数据来源说明】必须标注每条信息的来源类型
【回答约束】
1. 只能使用检索到的参考文档中的信息
2. 必须标注数据来源类型（课程数据库/电子书库/通用知识库）
3. 意图为recommend时以列表或卡片形式呈现
4. 无匹配时回答"数据库中暂未找到与您查询相关的资源。"
5. 严禁编造不存在的课程或电子书信息
        '''
    
    def _build_knowledge_prompt(self) -> str:
        """构建标准知识库问答提示词"""
        return '''
【核心职责】回答课程知识问题、解释概念、提供学习建议
【回答约束】
1. 只能使用检索到的参考文档中的信息
2. 无相关信息时回答"知识库中未找到"
3. 严禁使用训练数据或编造信息
4. 回答完成后列出引用来源标题
        '''
```

**生成策略**
- **模板生成**：基于预定义模板
- **自由生成**：基于语言模型
- **混合生成**：结合模板和自由生成
- **迭代优化**：多轮生成优化
- **智能提示词切换**【新增】：根据意图分类标记自动选择系统提示词

---

#### 2.2.6 验证Agent (Validation Agent)

**职责**
- 答案准确性验证
- 完整性检查
- 一致性验证
- 质量评分

**核心能力**
```python
class ValidationAgent:
    def __init__(self):
        self.accuracy_checker = AccuracyChecker()
        self.completeness_checker = CompletenessChecker()
        self.consistency_checker = ConsistencyChecker()
        self.quality_scorer = QualityScorer()
    
    async def validate(self, generation_result: GenerationResult,
                      reasoning_result: ReasoningResult) -> ValidationResult:
        """验证答案质量"""
        # 1. 准确性检查
        accuracy_score = await self.accuracy_checker.check(
            generation_result.answer,
            reasoning_result.knowledge_sources
        )
        
        # 2. 完整性检查
        completeness_score = await self.completeness_checker.check(
            generation_result.answer,
            reasoning_result.logical_conclusions
        )
        
        # 3. 一致性检查
        consistency_score = await self.consistency_checker.check(
            generation_result.answer
        )
        
        # 4. 质量评分
        overall_score = await self.quality_scorer.score({
            'accuracy': accuracy_score,
            'completeness': completeness_score,
            'consistency': consistency_score
        })
        
        return ValidationResult(
            accuracy_score=accuracy_score,
            completeness_score=completeness_score,
            consistency_score=consistency_score,
            overall_score=overall_score,
            validation_feedback=self._generate_feedback()
        )
```

**验证维度**
- **准确性**：答案是否正确
- **完整性**：是否回答了所有问题
- **一致性**：答案内部是否一致
- **清晰性**：表达是否清晰易懂
- **实用性**：答案是否有实际价值

---

#### 2.2.7 推荐Agent (Recommend Agent)

**职责【调整】**
- 通用知识推荐（保留原有通用逻辑）
- 学习路径建议（通用）
- 个性化内容推荐（通用）
- 扩展阅读推荐

**核心能力**
```python
class RecommendAgent:
    def __init__(self):
        self.recommender = KnowledgeRecommender()
        self.path_planner = LearningPathPlanner()
        self.personalizer = ContentPersonalizer()
    
    async def recommend(self, generation_result: GenerationResult,
                       understanding_result: UnderstandingResult) -> RecommendResult:
        """推荐相关内容"""
        # 1. 相关知识推荐
        related_knowledge = await self.recommender.recommend_related(
            generation_result.citations
        )
        
        # 2. 学习路径规划
        learning_path = await self.path_planner.plan(
            understanding_result.context_info['user_level'],
            generation_result.answer
        )
        
        # 3. 个性化推荐
        personalized_content = await self.personalizer.personalize(
            related_knowledge,
            understanding_result.context_info
        )
        
        return RecommendResult(
            related_knowledge=related_knowledge,
            learning_path=learning_path,
            personalized_content=personalized_content
        )
```

**推荐策略**
- **协同过滤**：基于用户行为
- **内容推荐**：基于内容相似度
- **知识图谱**：基于知识关联
- **混合推荐**：结合多种策略

---

#### 2.2.8 课程电子书检索Agent (Course Ebook Retrieval Agent)【新增】

**职责**
- 对接课程/电子书数据库
- 多路召回（关键词/语义/分类/用户历史）
- 资源重排序
- 课程相关性评分

**核心能力**
```python
class CourseEbookRetrievalAgent:
    """课程电子书检索Agent - 专注于课程和电子书资源的精准检索"""
    
    def __init__(self):
        self.course_db = CourseDatabase()
        self.ebook_db = EbookDatabase()
        self.retrieval_strategies = {
            'keyword': KeywordRetrieval(),
            'semantic': SemanticRetrieval(),
            'category': CategoryRetrieval(),
            'user_history': UserHistoryRetrieval()
        }
        self.reranker = CourseReranker()
    
    async def retrieve(self, understanding_result: UnderstandingResult) -> CourseRetrievalResult:
        """检索相关课程和电子书资源
        
        Args:
            understanding_result: 理解Agent的输出结果，包含意图、实体、问题类型等
            
        Returns:
            CourseRetrievalResult: 包含课程列表、电子书列表和检索元数据
        """
        # 1. 多路召回执行
        keyword_results = await self.retrieval_strategies['keyword'].retrieve(
            understanding_result.entities
        )
        semantic_results = await self.retrieval_strategies['semantic'].retrieve(
            understanding_result.query_embedding
        )
        category_results = await self.retrieval_strategies['category'].retrieve(
            understanding_result.context_info.get('category', '')
        )
        history_results = await self.retrieval_strategies['user_history'].retrieve(
            understanding_result.context_info.get('user_id', '')
        )
        
        # 2. 结果融合（RRF算法）
        fused_results = self._fuse_results_with_rrf([
            keyword_results,
            semantic_results,
            category_results,
            history_results
        ])
        
        # 3. 资源重排序
        reranked_results = await self.reranker.rerank(
            fused_results,
            understanding_result
        )
        
        # 4. 分类整理结果
        courses, ebooks = self._classify_results(reranked_results)
        
        return CourseRetrievalResult(
            courses=courses,
            ebooks=ebooks,
            retrieval_metadata=self._build_metadata(reranked_results)
        )
    
    def _fuse_results_with_rrf(self, results_list: List[List[Resource]]) -> List[Resource]:
        """使用RRF（Reciprocal Rank Fusion）算法融合多路召回结果"""
        fused_scores = {}
        k = 60  # RRF参数
        
        for results in results_list:
            for rank, resource in enumerate(results, 1):
                if resource.id not in fused_scores:
                    fused_scores[resource.id] = 0
                fused_scores[resource.id] += 1 / (k + rank)
        
        # 按融合分数排序
        sorted_resources = sorted(
            fused_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [self._get_resource_by_id(id) for id, _ in sorted_resources]
    
    def _classify_results(self, results: List[Resource]) -> Tuple[List[Course], List[Ebook]]:
        """将检索结果分类为课程和电子书"""
        courses = []
        ebooks = []
        
        for resource in results:
            if resource.type == 'course':
                courses.append(resource)
            elif resource.type == 'ebook':
                ebooks.append(resource)
        
        return courses, ebooks
```

**输入输出结构**

**输入**
```python
@dataclass
class CourseRetrievalInput:
    intent: str                    # 用户意图
    entities: dict                 # 提取的实体
    query_embedding: List[float]   # 查询向量
    context_info: dict             # 上下文信息
    user_profile: UserProfile      # 用户画像
```

**输出**
```python
@dataclass
class CourseRetrievalResult:
    courses: List[CourseResource]    # 匹配的课程列表
    ebooks: List[EbookResource]      # 匹配的电子书列表
    retrieval_metadata: dict         # 检索元数据
    
@dataclass
class CourseResource:
    id: str                          # 课程ID
    title: str                       # 课程标题
    category: str                    # 分类
    difficulty: str                  # 难度级别
    relevance_score: float           # 相关性评分
    cover_url: str                   # 封面图片
    duration: str                    # 课程时长
    instructor: str                  # 讲师
    rating: float                    # 评分

@dataclass
class EbookResource:
    id: str                          # 电子书ID
    title: str                       # 书名
    author: str                      # 作者
    category: str                    # 分类
    relevance_score: float           # 相关性评分
    cover_url: str                   # 封面图片
    publication_year: int            # 出版年份
    rating: float                    # 评分
```

**检索策略说明**
- **关键词检索**：基于实体匹配课程标题、描述
- **语义检索**：基于查询向量与课程内容向量相似度
- **分类检索**：基于用户指定或推断的课程分类
- **用户历史检索**：基于用户历史学习记录推荐

---

#### 2.2.9 个性化推荐Agent (Personalized Recommendation Agent)【新增】

**职责**
- 基于检索结果+用户画像进行个性化打分
- 多策略融合生成课程/电子书推荐
- 学习路径规划
- 推荐理由生成

**核心能力**
```python
class PersonalizedRecommendationAgent:
    """个性化推荐Agent - 基于用户画像和检索结果生成个性化推荐"""
    
    def __init__(self):
        self.user_profile_manager = UserProfileManager()
        self.recommendation_strategies = {
            'collaborative_filtering': CollaborativeFilteringStrategy(),
            'content_based': ContentBasedStrategy(),
            'knowledge_graph': KnowledgeGraphStrategy(),
            'sequential_pattern': SequentialPatternStrategy()
        }
        self.strategy_fuser = StrategyFuser()
        self.reason_generator = RecommendationReasonGenerator()
    
    async def recommend(self, 
                       retrieval_result: CourseRetrievalResult,
                       understanding_result: UnderstandingResult) -> PersonalizedRecommendResult:
        """生成个性化推荐
        
        Args:
            retrieval_result: 课程电子书检索Agent的输出
            understanding_result: 理解Agent的输出
            
        Returns:
            PersonalizedRecommendResult: 包含推荐列表和学习路径
        """
        # 1. 获取用户画像
        user_profile = await self.user_profile_manager.get_profile(
            understanding_result.context_info.get('user_id', '')
        )
        
        # 2. 多策略推荐打分
        strategy_scores = await self._apply_strategies(
            retrieval_result,
            user_profile,
            understanding_result
        )
        
        # 3. 策略融合
        fused_recommendations = self.strategy_fuser.fuse(strategy_scores)
        
        # 4. 生成推荐理由
        recommendations_with_reasons = await self._add_reasons(
            fused_recommendations,
            user_profile,
            understanding_result
        )
        
        # 5. 学习路径规划
        learning_path = await self._plan_learning_path(
            recommendations_with_reasons,
            user_profile
        )
        
        return PersonalizedRecommendResult(
            recommended_courses=recommendations_with_reasons[:5],
            recommended_ebooks=recommendations_with_reasons[5:10],
            learning_path=learning_path,
            recommendation_metadata=self._build_metadata(fused_recommendations)
        )
    
    async def _apply_strategies(self, retrieval_result: CourseRetrievalResult,
                               user_profile: UserProfile,
                               understanding_result: UnderstandingResult) -> dict:
        """应用多种推荐策略"""
        scores = {}
        
        for strategy_name, strategy in self.recommendation_strategies.items():
            scores[strategy_name] = await strategy.score(
                retrieval_result,
                user_profile,
                understanding_result
            )
        
        return scores
    
    async def _add_reasons(self, recommendations: List[RecommendedItem],
                          user_profile: UserProfile,
                          understanding_result: UnderstandingResult) -> List[RecommendedItem]:
        """为每个推荐项生成个性化推荐理由"""
        for item in recommendations:
            item.reason = await self.reason_generator.generate(
                item,
                user_profile,
                understanding_result
            )
        
        return recommendations
    
    async def _plan_learning_path(self, recommendations: List[RecommendedItem],
                                  user_profile: UserProfile) -> List[LearningStep]:
        """基于推荐结果和用户画像规划学习路径"""
        # 按难度排序
        sorted_items = sorted(
            recommendations,
            key=lambda x: self._get_difficulty_score(x.difficulty)
        )
        
        # 生成学习路径步骤
        learning_path = []
        for idx, item in enumerate(sorted_items[:6], 1):
            learning_path.append(LearningStep(
                step=idx,
                resource_id=item.id,
                resource_type=item.type,
                title=item.title,
                difficulty=item.difficulty,
                estimated_time=self._estimate_time(item)
            ))
        
        return learning_path
```

**输入输出结构**

**输入**
```python
@dataclass
class PersonalizedRecommendInput:
    courses: List[CourseResource]    # 检索到的课程列表
    ebooks: List[EbookResource]      # 检索到的电子书列表
    user_profile: UserProfile        # 用户画像
    understanding_result: UnderstandingResult  # 理解结果
```

**输出**
```python
@dataclass
class PersonalizedRecommendResult:
    recommended_courses: List[RecommendedItem]  # 推荐课程列表
    recommended_ebooks: List[RecommendedItem]   # 推荐电子书列表
    learning_path: List[LearningStep]           # 学习路径
    recommendation_metadata: dict               # 推荐元数据

@dataclass
class RecommendedItem:
    id: str                          # 资源ID
    title: str                       # 标题
    type: str                        # 类型(course/ebook)
    category: str                    # 分类
    difficulty: str                  # 难度
    score: float                     # 推荐分数
    reason: str                      # 推荐理由
    cover_url: str                   # 封面图片

@dataclass
class LearningStep:
    step: int                        # 步骤序号
    resource_id: str                 # 资源ID
    resource_type: str               # 资源类型
    title: str                       # 标题
    difficulty: str                  # 难度
    estimated_time: str              # 预计学习时间
```

**推荐策略说明**
- **协同过滤**：基于相似用户的学习行为
- **内容推荐**：基于内容相似度
- **知识图谱**：基于知识关联路径
- **序列模式**：基于学习序列模式挖掘

---

#### 2.2.10 意图分类与数据源路由机制【新增】

**概述**

为了将UnderstandingAgent优化后的意图分类结果贯穿整个下游Agent链路，我们引入了`requires_database_query`标记和对应的数据源路由机制。该机制使系统能够根据用户查询的意图，自动选择合适的数据源和处理路径。

**意图分类体系**

UnderstandingAgent输出的意图分类包含以下有限特定意图：

| 意图 | 含义 | 触发关键词 | requires_database_query |
|------|------|-----------|------------------------|
| `recommend` | 用户希望获得推荐、建议或列表 | 推荐、建议、有哪些、给我看、展示、列出 | `True` |
| `explain` | 用户希望理解概念、原理或过程 | 什么是、解释、说明、介绍、定义 | `False` |
| `how_to` | 用户希望学习操作方法或步骤 | 如何、怎么、怎样、方法、步骤 | `False` |
| `compare` | 用户希望对比两个或多个事物 | 区别、对比、比较、差异、不同 | `False` |
| `troubleshoot` | 用户报告错误或寻求解决方案 | 错误、问题、bug、异常、解决 | `False` |
| `general_query` | 一般性提问，不含明确意图 | — | `False` |

**核心标记字段**

每个理解结果包含两个关键布尔标记，控制下游Agent行为：

```json
{
  "intent": "recommend",
  "requires_knowledge_base_search": true,
  "requires_database_query": true,
  ...
}
```

- `requires_knowledge_base_search`：是否需要从向量知识库检索文档
- `requires_database_query`：是否需要查询数据库中的课程/书籍

**标记判定规则（回退方案）**

```python
# 判断是否需要数据库查询：recommend意图或包含课程/书籍相关词
recommend_triggers = ['课程', '电子书', '书籍', '书', '教材', '学习资料', '资源']
requires_database_query = (
    intent == 'recommend' or
    any(word in query for word in recommend_triggers)
)
```

**下游Agent处理流程**

```
UnderstandingAgent 输出
    │
    ├── intent, entities, question_type
    ├── requires_knowledge_base_search: bool
    └── requires_database_query: bool ← 核心路由标记
                │
                ▼
        [CoordinationAgent] 传递标记
                │
                ▼
        [RetrievalAgent]
            ├── requires_database_query=True  → _database_retrieval() 
            │    从 courses/books 表动态查询
            │    返回含 data_source 标注的结果
            │
            └── requires_database_query=False → 向量知识库检索
                 从 ChromaDB 语义检索
                 返回向量知识库结果
                │
                ▼
        [GenerationAgent]
            ├── requires_database_query=True  → 数据库查询结果呈现提示词
            │    • 明确标注每条信息的来源类型
            │    • 以列表/卡片形式呈现资源
            │    • 禁止编造课程/电子书信息
            │
            └── requires_database_query=False → 标准知识库问答提示词
                 • 基于检索到的参考文档回答
                 • 列出引用来源标题
                 • 严格禁止使用训练数据
```

**数据来源标注规范**

数据库查询路径（`_database_retrieval`）返回的每条知识块包含 `data_source` 字段，用于区分数据来源：

| data_source | 来源表 | 含义 | 显示标签 |
|-------------|--------|------|----------|
| `course_db` | `courses` | 课程数据库 | 📚 课程 |
| `book_db` | `books` | 电子书库 | 📖 电子书 |
| `general` | — | 通用知识库 | 💡 通用 |

**GenerationAgent 系统提示词双路径**

当 `requires_database_query=True` 时，GenerationAgent 使用"数据库查询结果呈现"专用系统提示词：

```
【核心职责】清晰、有吸引力地呈现来自数据库的查询结果
【数据来源说明】必须在回答中标注每条信息的来源类型
【回答约束】
1. 只能使用检索到的参考文档中的信息
2. 必须标注数据来源类型（课程数据库/电子书库/通用知识库）
3. 意图为recommend时以列表或卡片形式呈现资源
4. 无匹配结果时回答："数据库中暂未找到与您查询相关的资源。"
5. 严禁编造不存在的课程或电子书信息
```

当 `requires_database_query=False` 时，使用标准知识库问答提示词：

```
【核心职责】回答课程知识问题、解释概念、提供学习建议
【回答约束】
1. 只能使用检索到的参考文档中的信息
2. 无相关信息时回答"知识库中未找到"
3. 严禁使用训练数据或编造信息
4. 回答完成后列出引用来源标题
```

---

## 三、工作流设计

### 3.1 主工作流【调整】

```
用户查询
    ↓
[协调Agent] 任务分解
    ↓
[理解Agent] 意图识别、实体提取
    ↓
[课程电子书检索Agent] 多路召回、资源重排序
    ↓
[个性化推荐Agent] 个性化打分、学习路径规划
    ↓
[验证Agent] 质量验证、评分
    ↓
[协调Agent] 结果聚合
    ↓
返回答案（含推荐结果）
```

### 3.2 子工作流

#### 3.2.1 课程检索子工作流【新增】

```
理解结果
    ↓
┌──────────┬──────────┬──────────┬────────────┐
│关键词检索│语义检索  │分类检索  │用户历史检索│
└──────────┴──────────┴──────────┴────────────┘
    ↓          ↓          ↓          ↓
    └──────────┴──────────┴──────────┘
            ↓
    [RRF融合] 融合多路结果
            ↓
    [重排序] 基于相关性重排序
            ↓
    [分类整理] 课程/电子书分类
            ↓
    检索结果
```

#### 3.2.2 个性化推荐子工作流【新增】

```
检索结果 + 用户画像
    ↓
┌──────────────┬───────────┬─────────────┬──────────────┐
│协同过滤策略  │内容推荐策略│知识图谱策略  │序列模式策略  │
└──────────────┴───────────┴─────────────┴──────────────┘
    ↓              ↓            ↓              ↓
    └──────────────┴────────────┴──────────────┘
            ↓
    [策略融合] 多策略打分融合
            ↓
    [理由生成] 生成个性化推荐理由
            ↓
    [路径规划] 构建学习路径
            ↓
    推荐结果
```

#### 3.2.3 检索子工作流（通用）

```
理解结果
    ↓
[语义检索] 向量相似度检索
    ↓
[关键词检索] 实体匹配检索
    ↓
[结果融合] 合并多路结果
    ↓
[重排序] 基于相关性重排序
    ↓
检索结果
```

#### 3.2.4 验证子工作流

```
生成结果
    ↓
[准确性检查] 验证答案正确性
    ↓
[完整性检查] 验证答案完整性
    ↓
[一致性检查] 验证答案一致性
    ↓
[质量评分] 综合质量评分
    ↓
验证结果
```

### 3.3 异常处理工作流

```
正常流程
    ↓
检测到异常
    ↓
[协调Agent] 异常分类
    ↓
┌──────────┬──────────┬──────────┐
│  重试    │  降级    │  转人工  │
└──────────┴──────────┴──────────┘
    ↓          ↓          ↓
继续流程    简化答案    人工介入
```

---

## 四、Agent间通信机制

### 4.1 消息格式

```python
@dataclass
class AgentMessage:
    sender: str                    # 发送者Agent ID
    receiver: str                  # 接收者Agent ID
    message_type: str              # 消息类型
    payload: dict                  # 消息内容
    timestamp: datetime            # 时间戳
    correlation_id: str            # 关联ID
    priority: int = 0              # 优先级
    retry_count: int = 0           # 重试次数
    timeout: int = 30              # 超时时间(秒)
```

### 4.2 通信模式

#### 4.2.1 同步通信
```python
async def sync_communicate(message: AgentMessage) -> AgentMessage:
    """同步通信，等待响应"""
    response = await message_queue.send_and_wait(message)
    return response
```

#### 4.2.2 异步通信
```python
async def async_communicate(message: AgentMessage):
    """异步通信，不等待响应"""
    await message_queue.send(message)
```

#### 4.2.3 广播通信
```python
async def broadcast(message: AgentMessage):
    """广播消息给多个Agent"""
    for receiver in message.receivers:
        await message_queue.send_to(receiver, message)
```

### 4.3 消息队列

```python
class MessageQueue:
    def __init__(self):
        self.queues = defaultdict(asyncio.Queue)
        self.subscribers = defaultdict(set)
    
    async def send(self, message: AgentMessage):
        """发送消息"""
        queue = self.queues[message.receiver]
        await queue.put(message)
    
    async def send_and_wait(self, message: AgentMessage) -> AgentMessage:
        """发送消息并等待响应"""
        response_queue = asyncio.Queue()
        self.subscribers[message.correlation_id].add(response_queue)
        
        await self.send(message)
        response = await asyncio.wait_for(
            response_queue.get(),
            timeout=message.timeout
        )
        
        return response
    
    async def receive(self, agent_id: str) -> AgentMessage:
        """接收消息"""
        queue = self.queues[agent_id]
        return await queue.get()
```

### 4.4 课程资源消息格式【新增】

**课程检索请求消息**
```json
{
  "message_type": "course_retrieval_request",
  "payload": {
    "intent": "find_course",
    "entities": {
      "concept": "数据结构",
      "keywords": ["算法", "编程"]
    },
    "query_embedding": [0.1, 0.2, ...],
    "context_info": {
      "user_id": "user_001",
      "user_level": "beginner",
      "category": "计算机基础"
    }
  }
}
```

**课程检索响应消息**
```json
{
  "message_type": "course_retrieval_response",
  "payload": {
    "courses": [
      {
        "id": "course_001",
        "title": "数据结构与算法入门",
        "category": "计算机基础",
        "difficulty": "beginner",
        "relevance_score": 0.92,
        "cover_url": "https://example.com/course1.jpg",
        "duration": "12小时",
        "instructor": "张教授",
        "rating": 4.8
      }
    ],
    "ebooks": [
      {
        "id": "ebook_001",
        "title": "数据结构与算法分析",
        "author": "Mark Allen Weiss",
        "category": "计算机基础",
        "relevance_score": 0.88,
        "cover_url": "https://example.com/ebook1.jpg",
        "publication_year": 2020,
        "rating": 4.9
      }
    ],
    "metadata": {
      "total_count": 15,
      "retrieval_time_ms": 120
    }
  }
}
```

**个性化推荐请求消息**
```json
{
  "message_type": "personalized_recommend_request",
  "payload": {
    "courses": [...],
    "ebooks": [...],
    "user_profile": {
      "user_id": "user_001",
      "level": "beginner",
      "interests": ["数据结构", "算法", "Python"],
      "learning_history": ["course_002", "course_005"],
      "completed_courses": ["course_003"]
    },
    "understanding_result": {...}
  }
}
```

**个性化推荐响应消息**
```json
{
  "message_type": "personalized_recommend_response",
  "payload": {
    "recommended_courses": [
      {
        "id": "course_001",
        "title": "数据结构与算法入门",
        "type": "course",
        "category": "计算机基础",
        "difficulty": "beginner",
        "score": 0.95,
        "reason": "根据您的学习历史，推荐从基础数据结构开始学习，这将为后续算法学习打下坚实基础",
        "cover_url": "https://example.com/course1.jpg"
      }
    ],
    "recommended_ebooks": [...],
    "learning_path": [
      {
        "step": 1,
        "resource_id": "course_001",
        "resource_type": "course",
        "title": "数据结构与算法入门",
        "difficulty": "beginner",
        "estimated_time": "12小时"
      },
      {
        "step": 2,
        "resource_id": "ebook_001",
        "resource_type": "ebook",
        "title": "数据结构与算法分析",
        "difficulty": "intermediate",
        "estimated_time": "20小时"
      }
    ]
  }
}
```

---

## 五、SSE流式接口

### 5.1 接口概述

为实现多Agent工作流的实时状态展示，系统提供SSE（Server-Sent Events）流式接口，前端通过EventSource接收工作流步骤的实时状态更新。

### 5.2 API端点

```http
POST /api/agents/query/stream
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
    "query": "推荐一些数据结构相关的课程",
    "context": {}
}
```

### 5.3 SSE事件类型

| 事件类型 | 说明 | 数据结构 |
|----------|------|---------|
| `step_start` | 步骤开始 | `{"agent": "understanding", "step_name": "意图识别", "timestamp": ...}` |
| `step_complete` | 步骤完成 | `{"agent": "understanding", "step_name": "意图识别", "result": {...}, "duration_ms": ...}` |
| `step_error` | 步骤错误 | `{"agent": "understanding", "step_name": "意图识别", "error": "..."}` |
| `token` | 回答片段 | `{"content": "..."}` |
| `references` | 引用来源 | `[{"id": "...", "title": "...", "source": "..."}]` |
| `result` | 最终结果 | `{"answer": "...", "recommended_courses": [...], "recommended_ebooks": [...]}` |
| `done` | 流程结束 | `{}` |

### 5.4 前端集成示例

```javascript
const eventSource = new EventSource('/api/agents/query/stream', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + token
    },
    body: JSON.stringify({ query: userQuery })
});

eventSource.addEventListener('step_start', (event) => {
    const data = JSON.parse(event.data);
    updateAgentStatus(data.agent, 'running');
});

eventSource.addEventListener('step_complete', (event) => {
    const data = JSON.parse(event.data);
    updateAgentStatus(data.agent, 'completed');
});

eventSource.addEventListener('token', (event) => {
    const data = JSON.parse(event.data);
    appendToAnswer(data.content);
});

eventSource.addEventListener('done', () => {
    eventSource.close();
});
```

### 5.5 CORS配置

流式接口需要特殊的CORS配置，后端已在StreamingResponse中添加以下响应头：

```python
headers={
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
    "Access-Control-Allow-Origin": "http://localhost:5173",
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization"
}
```

---

## 六、任务分配逻辑

### 6.1 任务分解

```python
class TaskDecomposer:
    def decompose(self, query: str, context: dict) -> List[Task]:
        """将用户查询分解为子任务【调整】：添加课程业务专用任务"""
        tasks = []
        
        # 1. 理解任务
        tasks.append(Task(
            id='understanding',
            agent='understanding',
            input={'query': query, 'context': context},
            dependencies=[]
        ))
        
        # 2. 课程电子书检索任务【新增】
        tasks.append(Task(
            id='course_retrieval',
            agent='course_retrieval',
            input={'understanding_result': 'understanding.output'},
            dependencies=['understanding']
        ))
        
        # 3. 个性化推荐任务【新增】
        tasks.append(Task(
            id='personalized_rec',
            agent='personalized_rec',
            input={
                'retrieval_result': 'course_retrieval.output',
                'understanding_result': 'understanding.output'
            },
            dependencies=['course_retrieval']
        ))
        
        # 4. 验证任务
        tasks.append(Task(
            id='validation',
            agent='validation',
            input={
                'recommend_result': 'personalized_rec.output',
                'understanding_result': 'understanding.output'
            },
            dependencies=['personalized_rec']
        ))
        
        return tasks
```

### 6.2 任务调度

```python
class TaskScheduler:
    def __init__(self):
        self.task_queue = PriorityQueue()
        self.running_tasks = {}
        self.completed_tasks = {}
    
    async def schedule(self, tasks: List[Task]):
        """调度任务执行"""
        # 1. 构建依赖图
        dependency_graph = self._build_dependency_graph(tasks)
        
        # 2. 拓扑排序
        execution_order = self._topological_sort(dependency_graph)
        
        # 3. 并行执行无依赖任务
        for level in execution_order:
            await asyncio.gather(*[
                self._execute_task(task)
                for task in level
            ])
    
    async def _execute_task(self, task: Task):
        """执行单个任务"""
        # 1. 检查依赖
        await self._check_dependencies(task)
        
        # 2. 执行任务
        agent = self.agents[task.agent]
        result = await agent.execute(task.input)
        
        # 3. 保存结果
        self.completed_tasks[task.id] = result
        
        return result
```

### 6.3 负载均衡

```python
class LoadBalancer:
    def __init__(self):
        self.agent_loads = defaultdict(int)
        self.agent_instances = {}
    
    def select_agent(self, agent_type: str) -> str:
        """选择负载最低的Agent实例"""
        instances = self.agent_instances[agent_type]
        
        # 选择负载最低的实例
        selected = min(
            instances,
            key=lambda x: self.agent_loads[x.id]
        )
        
        # 更新负载
        self.agent_loads[selected.id] += 1
        
        return selected.id
    
    def release_agent(self, agent_id: str):
        """释放Agent"""
        self.agent_loads[agent_id] -= 1
```

---

## 七、协作决策过程

### 7.1 决策机制

```python
class DecisionMaker:
    def __init__(self):
        self.voting_system = VotingSystem()
        self.consensus_engine = ConsensusEngine()
    
    async def make_decision(self, proposals: List[Proposal]) -> Decision:
        """协作决策"""
        # 1. 投票
        votes = await self.voting_system.vote(proposals)
        
        # 2. 达成共识
        consensus = await self.consensus_engine.reach_consensus(votes)
        
        # 3. 决策
        decision = Decision(
            selected_proposal=consensus.selected,
            confidence=consensus.confidence,
            reasoning=consensus.reasoning
        )
        
        return decision
```

### 7.2 冲突解决

```python
class ConflictResolver:
    def __init__(self):
        self.strategies = {
            'priority': PriorityStrategy(),
            'voting': VotingStrategy(),
            'negotiation': NegotiationStrategy()
        }
    
    async def resolve_conflict(self, conflict: Conflict) -> Resolution:
        """解决Agent间冲突"""
        # 1. 分析冲突类型
        conflict_type = self._analyze_conflict(conflict)
        
        # 2. 选择解决策略
        strategy = self.strategies[conflict_type]
        
        # 3. 执行解决策略
        resolution = await strategy.resolve(conflict)
        
        return resolution
```

---

## 八、成果输出路径

### 8.1 输出格式

```python
@dataclass
class FinalOutput:
    # 基本信息
    query: str                              # 用户查询
    answer: str                             # 主要答案
    
    # 引用信息
    citations: List[Citation]               # 引用来源
    references: List[Reference]             # 参考知识
    
    # 推理过程
    reasoning_trace: List[ReasoningStep]    # 推理步骤
    confidence: float                       # 置信度
    
    # 验证信息
    validation_score: float                 # 验证分数
    validation_feedback: str                # 验证反馈
    
    # 推荐信息【调整】：新增课程/电子书推荐字段
    recommended_courses: List[RecommendedItem]  # 推荐课程
    recommended_ebooks: List[RecommendedItem]   # 推荐电子书
    learning_path: List[LearningStep]       # 学习路径
    
    # 元数据
    metadata: dict                          # 元数据
```

### 8.2 输出示例

```json
{
  "query": "推荐一些数据结构相关的课程和电子书",
  "answer": "根据您的学习需求，为您推荐以下课程和电子书资源：",
  "citations": [],
  "reasoning_trace": [
    {
      "step": 1,
      "agent": "understanding",
      "action": "识别意图：查找课程",
      "result": "intent=find_course"
    },
    {
      "step": 2,
      "agent": "course_retrieval",
      "action": "多路召回检索",
      "result": "检索到10个相关课程，5本电子书"
    },
    {
      "step": 3,
      "agent": "personalized_rec",
      "action": "个性化推荐",
      "result": "生成5个课程推荐和3个电子书推荐"
    },
    {
      "step": 4,
      "agent": "validation",
      "action": "质量验证",
      "result": "验证通过"
    }
  ],
  "confidence": 0.95,
  "validation_score": 0.92,
  "recommended_courses": [
    {
      "id": "course_001",
      "title": "数据结构与算法入门",
      "type": "course",
      "category": "计算机基础",
      "difficulty": "beginner",
      "score": 0.95,
      "reason": "根据您的初学者水平，推荐从基础数据结构开始学习",
      "cover_url": "https://example.com/course1.jpg"
    }
  ],
  "recommended_ebooks": [
    {
      "id": "ebook_001",
      "title": "数据结构与算法分析",
      "type": "ebook",
      "category": "计算机基础",
      "difficulty": "intermediate",
      "score": 0.88,
      "reason": "经典教材，适合系统学习数据结构",
      "cover_url": "https://example.com/ebook1.jpg"
    }
  ],
  "learning_path": [
    {
      "step": 1,
      "resource_id": "course_001",
      "resource_type": "course",
      "title": "数据结构与算法入门",
      "difficulty": "beginner",
      "estimated_time": "12小时"
    },
    {
      "step": 2,
      "resource_id": "ebook_001",
      "resource_type": "ebook",
      "title": "数据结构与算法分析",
      "difficulty": "intermediate",
      "estimated_time": "20小时"
    }
  ],
  "metadata": {
    "total_retrieved": 15,
    "recommendation_strategy": "hybrid",
    "execution_time_ms": 450
  }
}
```

---

## 九、系统优化

### 9.1 性能优化

**并行处理**
- 无依赖任务并行执行
- 多Agent实例负载均衡
- 异步I/O操作

**缓存策略**
- 查询结果缓存
- 知识块缓存
- Agent输出缓存

**资源管理**
- Agent实例池
- 连接池管理
- 内存优化

### 9.2 可靠性优化

**容错机制**
- Agent故障检测
- 自动重试
- 降级策略

**监控告警**
- Agent状态监控
- 性能指标监控
- 异常告警

**日志追踪**
- 完整的执行日志
- 分布式追踪
- 问题定位

---

## 十、系统健康优化

### 10.1 缓存策略

**多级缓存架构**
```python
class CacheManager:
    def __init__(self):
        self.local_cache = LRUCache(maxsize=1000)      # 进程级缓存
        self.redis_cache = RedisCache()                 # 分布式缓存
        self.ttl_config = {
            'course_retrieval': 300,    # 课程检索结果缓存5分钟
            'recommendation': 600,      # 推荐结果缓存10分钟
            'user_profile': 1800,       # 用户画像缓存30分钟
            'knowledge_chunks': 3600    # 知识块缓存1小时
        }
    
    async def get(self, key: str, source_func=None, ttl=None):
        """获取缓存，不存在则调用源函数获取"""
        # 先查本地缓存
        if key in self.local_cache:
            return self.local_cache[key]
        
        # 再查分布式缓存
        value = await self.redis_cache.get(key)
        if value:
            self.local_cache[key] = value
            return value
        
        # 调用源函数获取
        if source_func:
            value = await source_func()
            await self.set(key, value, ttl)
            return value
        
        return None
    
    async def set(self, key: str, value, ttl=None):
        """设置缓存"""
        ttl = ttl or self.ttl_config.get(key.split(':')[0], 300)
        
        self.local_cache[key] = value
        await self.redis_cache.set(key, value, ttl)
    
    async def invalidate(self, pattern: str):
        """按模式失效缓存"""
        await self.redis_cache.delete_pattern(pattern)
```

**缓存更新策略**
- **写穿透**：数据写入时同时更新缓存
- **定时刷新**：关键数据定时重新计算
- **事件驱动**：数据变更时触发缓存失效

### 10.2 容错降级

**降级策略**
```python
class DegradationManager:
    def __init__(self):
        self.degradation_level = 'normal'  # normal / warning / critical
        self.fallback_handlers = {
            'course_retrieval': self._fallback_course_retrieval,
            'personalized_rec': self._fallback_personalized_rec,
            'llm_service': self._fallback_llm
        }
    
    async def execute_with_degradation(self, agent_id: str, input_data: dict):
        """带降级的Agent执行"""
        try:
            agent = self.agents[agent_id]
            return await agent.execute(input_data)
        except Exception as e:
            logger.error(f"Agent {agent_id} failed: {e}")
            
            if agent_id in self.fallback_handlers:
                return await self.fallback_handlers[agent_id](input_data)
            
            raise
    
    async def _fallback_course_retrieval(self, input_data: dict):
        """课程检索降级：使用本地缓存或默认结果"""
        cached_result = await self.cache_manager.get(
            f"fallback:course_retrieval:{input_data.get('query_hash')}"
        )
        if cached_result:
            return cached_result
        
        # 返回默认热门课程
        return CourseRetrievalResult(
            courses=self._get_hot_courses(),
            ebooks=self._get_hot_ebooks(),
            retrieval_metadata={'degraded': True}
        )
    
    async def _fallback_personalized_rec(self, input_data: dict):
        """个性化推荐降级：返回基于内容的简单推荐"""
        retrieval_result = input_data.get('retrieval_result')
        
        if retrieval_result:
            # 直接返回检索结果前几项作为推荐
            return PersonalizedRecommendResult(
                recommended_courses=retrieval_result.courses[:3],
                recommended_ebooks=retrieval_result.ebooks[:2],
                learning_path=[],
                recommendation_metadata={'degraded': True}
            )
        
        return PersonalizedRecommendResult(
            recommended_courses=[],
            recommended_ebooks=[],
            learning_path=[],
            recommendation_metadata={'degraded': True}
        )
    
    async def _fallback_llm(self, input_data: dict):
        """LLM降级：使用规则模板响应"""
        intent = input_data.get('intent', '')
        
        templates = {
            'find_course': "抱歉，当前服务繁忙，请稍后重试。您可以尝试搜索课程关键词。",
            'explain_concept': "抱歉，当前服务繁忙，请查看知识库文档获取相关信息。",
            'default': "抱歉，当前服务暂时不可用，请稍后重试。"
        }
        
        return templates.get(intent, templates['default'])
```

**熔断机制**
- 基于失败率的熔断：连续失败超过阈值触发熔断
- 熔断状态：关闭→半开→打开→关闭循环
- 自动恢复：熔断一段时间后自动尝试恢复

### 10.3 监控指标

**关键指标定义**
```python
@dataclass
class AgentMetrics:
    agent_id: str                  # Agent ID
    request_count: int             # 请求总数
    success_count: int             # 成功请求数
    error_count: int               # 错误请求数
    avg_latency_ms: float          # 平均延迟(毫秒)
    p95_latency_ms: float          # P95延迟(毫秒)
    p99_latency_ms: float          # P99延迟(毫秒)
    active_tasks: int              # 活跃任务数
    queue_length: int              # 队列长度

@dataclass
class SystemMetrics:
    total_requests: int            # 系统总请求数
    success_rate: float            # 成功率
    avg_response_time_ms: float    # 平均响应时间
    degradation_level: str         # 降级级别
    cache_hit_rate: float          # 缓存命中率
    resource_usage: dict           # 资源使用情况
```

**监控采集与上报**
```python
class MetricsCollector:
    def __init__(self):
        self.agent_metrics = defaultdict(AgentMetrics)
        self.system_metrics = SystemMetrics()
        self.prometheus_client = PrometheusClient()
    
    async def record_request(self, agent_id: str, success: bool, latency_ms: float):
        """记录Agent请求指标"""
        metrics = self.agent_metrics[agent_id]
        metrics.request_count += 1
        
        if success:
            metrics.success_count += 1
        else:
            metrics.error_count += 1
        
        # 更新延迟统计
        self._update_latency_stats(metrics, latency_ms)
    
    def _update_latency_stats(self, metrics: AgentMetrics, latency_ms: float):
        """更新延迟统计"""
        # 简化实现，实际应使用更精确的统计方法
        current_total = metrics.avg_latency_ms * (metrics.request_count - 1)
        metrics.avg_latency_ms = (current_total + latency_ms) / metrics.request_count
        metrics.p95_latency_ms = max(metrics.p95_latency_ms, latency_ms)
        metrics.p99_latency_ms = max(metrics.p99_latency_ms, latency_ms)
    
    async def report(self):
        """上报指标到监控系统"""
        await self.prometheus_client.push(self.agent_metrics)
        await self.prometheus_client.push_system(self.system_metrics)
```

**告警规则**
- **延迟告警**：P95延迟超过500ms触发警告，超过1000ms触发严重告警
- **错误率告警**：错误率超过5%触发警告，超过10%触发严重告警
- **降级告警**：系统进入降级状态时触发告警
- **资源告警**：CPU/内存使用率超过80%触发警告

---

## 十一、扩展性设计

### 11.1 Agent扩展

**新增Agent**
```python
# 1. 定义Agent接口
class NewAgent(BaseAgent):
    async def execute(self, input: dict) -> dict:
        # 实现Agent逻辑
        pass

# 2. 注册Agent
coordination_agent.register_agent('new_agent', NewAgent())

# 3. 更新工作流
coordination_agent.update_workflow({
    'previous_step': ['new_agent'],
    'new_agent': ['next_step']
})
```

### 11.2 工作流扩展

**自定义工作流**
```python
# 1. 定义工作流
custom_workflow = {
    'start': ['agent1'],
    'agent1': ['agent2', 'agent3'],
    'agent2': ['agent4'],
    'agent3': ['agent4'],
    'agent4': ['end']
}

# 2. 注册工作流
coordination_agent.register_workflow('custom', custom_workflow)

# 3. 使用工作流
result = await coordination_agent.process_with_workflow(
    query,
    context,
    workflow='custom'
)
```

---

## 十二、总结

本多Agent智能问答系统通过以下机制实现高效协作：

1. **明确的职责分工**：每个Agent专注于特定领域，新增的课程电子书检索Agent和个性化推荐Agent专门处理课程业务场景
2. **高效的信息传递**：基于消息队列的异步通信，支持课程资源专用消息格式
3. **智能的任务分配**：基于依赖图的并行调度，适配课程业务工作流
4. **协作的决策机制**：投票和共识算法
5. **完整的输出路径**：从理解到推荐的全流程，包含课程/电子书推荐和学习路径规划
6. **完善的健康保障**：多级缓存、容错降级、全面监控

系统能够基于优化后的知识文档库，为学生提供准确、全面、个性化的专业知识解答和课程推荐。

---

**文档版本**: v2.1  
**创建日期**: 2026年7月  
**适用项目**: 华南师范大学计算机专业课程管理系统  
**作者**: AI系统架构师  
**修订说明**: 新增SSE流式接口，支持工作流实时状态展示；更新章节编号；完善CORS配置说明
