"""
Chroma知识库仓储实现 (Chroma Knowledge Repository)

实现KnowledgeRepository接口，基于本地Chroma向量数据库进行语义向量检索。
支持多路召回策略、RRF(Rreciprocal Rank Fusion)结果融合和Rerank重排机制。

核心特性：
1. 多路召回：向量检索 + 关键词检索
2. RRF融合：使用倒数排名融合算法合并多路召回结果
3. Rerank重排：使用BAAI/bge-reranker-v2-m3模型精排
4. Markdown智能分割：支持#到####标题级别的知识块提取
"""

from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
from pathlib import Path
import hashlib
import re
import json
import chromadb
from chromadb.config import Settings

from domain.knowledge.entity import KnowledgePoint, KnowledgeSearchResult, ImportResult
from domain.knowledge.repository import KnowledgeRepository
from infrastructure.llm_client import LLMClient, LLMError
from config import (
    RERANK_TOP_N,
    RERANK_MIN_SCORE,
    CHROMA_DB_PATH,
    CHROMA_COLLECTION_NAME,
    RRF_K,
    KNOWLEDGE_BASE_PATH,
)
import logging

logger = logging.getLogger(__name__)


# ==================== Markdown处理工具 ====================

def split_markdown_sections(content: str, filename: str) -> List[Tuple[str, str]]:
    """
    将Markdown内容智能分割为知识块

    支持##到####标题级别，按标题分割保留层级结构。

    Args:
        content: Markdown内容
        filename: 文件名（不含扩展名）

    Returns:
        List[Tuple[str, str]]: [(标题, 内容), ...]
    """
    chunks = []

    # 使用正则匹配##到####标题及其后续内容
    # 捕获标题级别、标题文本和内容
    pattern = r'(#{2,4})\s+(.+?)\n([\s\S]*?)(?=(?:\n#{2,4}\s)|$)'
    matches = re.findall(pattern, content)

    if matches:
        for level, title, body in matches:
            title = title.strip()
            body = body.strip()
            if body and len(body) > 10:  # 过滤过短内容
                chunks.append((title, body))
    else:
        # 没有标题时，按段落分割
        paragraphs = content.split("\n\n")
        for para in paragraphs:
            para = para.strip()
            if para and len(para) > 10:
                # 使用文件名前缀标记无标题块
                chunks.append((filename, para))

    return chunks


def extract_metadata_from_markdown(filepath: Path) -> Dict[str, Any]:
    """
    从Markdown文件提取元数据

    解析文件开头的YAML front matter或文件名。

    Args:
        filepath: 文件路径

    Returns:
        Dict[str, Any]: 元数据字典
    """
    metadata = {
        "course": filepath.stem,  # 默认使用文件名作为课程名
        "source_file": filepath.name,
    }

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # 检查YAML front matter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                yaml_content = parts[1]
                for line in yaml_content.split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key in ["course", "title", "category", "tags"]:
                            metadata[key] = value

    except Exception as e:
        logger.warning(f"Failed to extract metadata from {filepath}: {e}")

    return metadata


def load_knowledge_files(knowledge_dir: Path) -> List[KnowledgePoint]:
    """
    加载知识目录下的所有md文件

    Args:
        knowledge_dir: 知识库目录路径

    Returns:
        List[KnowledgePoint]: 知识点列表
    """
    knowledge_points = []

    if not knowledge_dir.exists():
        logger.error(f"Knowledge directory not found: {knowledge_dir}")
        return knowledge_points

    for md_file in sorted(knowledge_dir.glob("*.md")):
        logger.info(f"Loading knowledge file: {md_file.name}")

        try:
            # 提取元数据
            file_metadata = extract_metadata_from_markdown(md_file)

            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()

            # 分割内容为知识块
            chunks = split_markdown_sections(content, md_file.stem)
            logger.info(f"  Extracted {len(chunks)} chunks from {md_file.name}")

            for title, body in chunks:
                # 生成唯一ID
                chunk_id = KnowledgePoint.create_id(md_file.name, title)

                # 构建完整内容（包含标题前缀）
                full_content = f"【{md_file.stem}】{title}\n\n{body}"

                # 截断内容防止向量过大
                truncated_content = body[:2000] if len(body) > 2000 else body

                point = KnowledgePoint(
                    id=chunk_id,
                    title=title,
                    content=truncated_content,
                    course=file_metadata.get("course", md_file.stem),
                    chapter="",
                    source_file=md_file.name,
                )
                knowledge_points.append(point)

        except Exception as e:
            logger.error(f"Failed to load {md_file.name}: {e}")

    return knowledge_points


# ==================== RRF融合算法 ====================

def reciprocal_rank_fusion(
    result_lists: List[List[Tuple[str, float]]],
    k: int = 60
) -> List[Tuple[str, float]]:
    """
    倒数排名融合算法 (RRF)

    将多个排名列表融合为一个综合排名，用于多路召回结果合并。

    公式: RRF(d) = Σ 1/(k + rank(d))

    Args:
        result_lists: 多个排名列表，每个元素为[(doc_id, score), ...]
        k: RRF参数，默认60，值越小越依赖高排名结果

    Returns:
        List[Tuple[str, float]]: 融合后的[(doc_id, score), ...]，按分数降序
    """
    rrf_scores: Dict[str, float] = {}

    for result_list in result_lists:
        for rank, (doc_id, score) in enumerate(result_list, 1):
            if doc_id not in rrf_scores:
                rrf_scores[doc_id] = 0.0
            # RRF公式：1/(k + rank)
            rrf_scores[doc_id] += 1.0 / (k + rank)

    # 按RRF分数降序排列
    sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

    return sorted_results


# ==================== ChromaKnowledgeRepository ====================

class ChromaKnowledgeRepository(KnowledgeRepository):
    """
    Chroma知识库仓储实现

    实现RAG检索增强生成的完整流程：
    1. 多路召回：向量检索 + 关键词检索
    2. RRF融合：合并多路召回结果
    3. Rerank精排：使用重排模型优化排序
    4. 上下文构建：生成适合LLM的上下文

    Attributes:
        llm_client: LLM客户端
        embedding_dimension: 向量维度
        similarity_threshold: 相似度阈值
        client: Chroma客户端
        collection: Chroma集合
        rrf_k: RRF融合参数
        rerank_min_score: Rerank最小分数阈值
    """

    def __init__(
        self,
        llm_client: LLMClient,
        embedding_dimension: int = 1024,
        similarity_threshold: float = 0.5,
        rrf_k: int = 60,
        rerank_min_score: float = 0.3,
    ):
        """
        初始化知识库仓储

        Args:
            llm_client: LLM客户端
            embedding_dimension: 向量维度（BAAI/bge-m3为1024）
            similarity_threshold: 相似度阈值
            rrf_k: RRF融合参数
            rerank_min_score: Rerank最小分数阈值
        """
        self.llm_client = llm_client
        self.embedding_dimension = embedding_dimension
        self.similarity_threshold = similarity_threshold
        self.rrf_k = rrf_k
        self.rerank_min_score = rerank_min_score

        # 初始化Chroma客户端
        self.client = chromadb.PersistentClient(
            path=CHROMA_DB_PATH,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

        # 获取或创建集合
        self.collection = self.client.get_or_create_collection(name=CHROMA_COLLECTION_NAME)

        logger.info(f"ChromaKnowledgeRepository initialized: {CHROMA_DB_PATH}/{CHROMA_COLLECTION_NAME}")

    async def init_schema(self) -> None:
        """初始化数据库模式 - Chroma自动管理schema，检测并修复向量维度"""
        try:
            await self._ensure_collection_dimension()
        except Exception as e:
            logger.error(f"向量维度检测失败: {e}")

    async def _ensure_collection_dimension(self) -> None:
        """
        检测并确保集合向量维度与Embedding模型一致
        
        如果现有集合的维度与模型不匹配（如1024 vs 384），
        删除集合并重建。
        """
        try:
            # 获取一个测试向量，确定实际维度
            test_embedding = await self.llm_client.get_embedding("test dimension detection")
            actual_dim = len(test_embedding)
            
            # 获取集合中已有数据的情况
            collection_count = self.collection.count()
            
            if collection_count > 0:
                # 从集合中读取一条已有数据来获取其维度
                sample = self.collection.get(limit=1)
                if sample and sample.get('ids'):
                    # Chroma集合隐式使用第一个被添加的向量的维度
                    # 我们可以通过尝试添加一个测试向量来检测维度问题
                    try:
                        self.collection.query(
                            query_embeddings=[[0.0] * actual_dim],
                            n_results=1
                        )
                        logger.info(f"向量维度一致: {actual_dim}维，集合已有{collection_count}条数据")
                    except Exception as dim_err:
                        logger.warning(f"向量维度不匹配！集合期望维度不同于{actual_dim}，需要重置集合: {dim_err}")
                        logger.info(f"正在重置Chroma集合 '{CHROMA_COLLECTION_NAME}'...")
                        self.client.delete_collection(name=CHROMA_COLLECTION_NAME)
                        self.collection = self.client.create_collection(name=CHROMA_COLLECTION_NAME)
                        logger.info(f"Chroma集合已重建，当前向量维度: {actual_dim}")
            else:
                logger.info(f"Chroma集合为空，将使用{actual_dim}维向量")
        except Exception as e:
            logger.warning(f"向量维度检测异常，使用默认配置: {e}")

    async def exists(self, knowledge_id: str) -> bool:
        """检查知识点是否存在"""
        try:
            result = self.collection.get(ids=[knowledge_id])
            return len(result['ids']) > 0
        except Exception:
            return False

    async def save(self, knowledge_point: KnowledgePoint) -> bool:
        """
        保存知识点

        使用passage:前缀进行向量化（符合BGE模型非对称检索规范）
        """
        if knowledge_point.embedding is None:
            try:
                # 使用passage:前缀，符合BGE模型规范
                passage_text = f"passage: {knowledge_point.title}\n{knowledge_point.content}"
                embedding = await self.llm_client.get_embedding(passage_text)
                knowledge_point = knowledge_point.with_embedding(embedding)
            except LLMError as e:
                logger.error(f"Embedding failed for {knowledge_point.id}: {e}")
                return False

        try:
            # 构建元数据
            metadata = {
                "title": knowledge_point.title,
                "course": knowledge_point.course,
                "chapter": knowledge_point.chapter or "",
                "source_file": knowledge_point.source_file,
                "created_at": knowledge_point.created_at.isoformat(),
                "updated_at": datetime.now().isoformat(),
            }

            # 添加可选字段
            if knowledge_point.tags:
                metadata["tags"] = json.dumps(knowledge_point.tags)
            if knowledge_point.prerequisites:
                metadata["prerequisites"] = json.dumps(knowledge_point.prerequisites)
            if knowledge_point.successors:
                metadata["successors"] = json.dumps(knowledge_point.successors)
            if knowledge_point.related_ids:
                metadata["related_ids"] = json.dumps(knowledge_point.related_ids)

            # 存入Chroma
            self.collection.upsert(
                ids=[knowledge_point.id],
                embeddings=[knowledge_point.embedding],
                documents=[knowledge_point.content],
                metadatas=[metadata]
            )

            logger.debug(f"Saved knowledge point: {knowledge_point.id}")
            return True

        except Exception as e:
            logger.error(f"Save failed for {knowledge_point.id}: {e}")
            return False

    async def load_all(self, knowledge_points: List[KnowledgePoint]) -> ImportResult:
        """
        批量导入知识点

        逐个向量化并保存，支持断点续传
        """
        result = ImportResult()

        for point in knowledge_points:
            if point.embedding is None:
                try:
                    passage_text = f"passage: {point.title}\n{point.content}"
                    embedding = await self.llm_client.get_embedding(passage_text)
                    point = point.with_embedding(embedding)
                except LLMError as e:
                    result.add_failure(point.source_file, 0, f"Embedding failed: {e}")
                    continue

            success = await self.save(point)
            if success:
                result.add_success()
            else:
                result.add_failure(point.source_file, 0, "Save failed")

        return result

    async def load_knowledge_base(self) -> ImportResult:
        """
        加载整个知识库目录

        从配置的KNOWLEDGE_BASE_PATH目录加载所有md文件

        Returns:
            ImportResult: 导入结果
        """
        knowledge_dir = Path(KNOWLEDGE_BASE_PATH)
        knowledge_points = load_knowledge_files(knowledge_dir)

        logger.info(f"Loaded {len(knowledge_points)} knowledge points from {knowledge_dir}")

        return await self.load_all(knowledge_points)

    async def search(
        self,
        query: str,
        course: Optional[str] = None,
        limit: int = 5,
        use_rerank: bool = True
    ) -> List[KnowledgeSearchResult]:
        """
        语义检索知识点

        完整RAG检索流程：
        1. 向量检索（query:前缀）
        2. 关键词检索
        3. RRF融合
        4. Rerank精排（可选）

        Args:
            query: 查询文本
            course: 课程过滤
            limit: 返回数量
            use_rerank: 是否启用Rerank

        Returns:
            List[KnowledgeSearchResult]: 检索结果列表
        """
        logger.info(f"Searching: '{query}' (course={course}, limit={limit}, rerank={use_rerank})")

        try:
            # 多路召回
            vector_results = await self._vector_search(query, course, limit * 3)
            keyword_results = await self._keyword_search(query, course, limit * 2)

            # 构建RRF输入格式
            vector_ranked = [(r.knowledge_point.id, r.score) for r in vector_results]
            keyword_ranked = [(r.knowledge_point.id, r.score) for r in keyword_results]

            # RRF融合
            fused_ids = reciprocal_rank_fusion([vector_ranked, keyword_ranked], k=self.rrf_k)

            # 获取融合后的完整结果
            fused_results = []
            for idx, (doc_id, rrf_score) in enumerate(fused_ids[:limit * 2], 1):
                # 找到对应的KnowledgePoint
                point = None
                for vr in vector_results:
                    if vr.knowledge_point.id == doc_id:
                        point = vr.knowledge_point
                        break
                if point is None:
                    for kr in keyword_results:
                        if kr.knowledge_point.id == doc_id:
                            point = kr.knowledge_point
                            break

                if point:
                    # 融合原始分数和RRF分数
                    final_score = (rrf_score + self._get_original_score(doc_id, vector_results, keyword_results)) / 2
                    fused_results.append(KnowledgeSearchResult(
                        knowledge_point=point,
                        score=final_score,
                        rank=idx
                    ))

            # Rerank精排
            if use_rerank and len(fused_results) > 1:
                fused_results = await self._rerank_results(query, fused_results)

            # 最终过滤
            final_results = [
                r for r in fused_results[:limit]
                if r.score >= self.similarity_threshold
            ]

            logger.info(f"Search returned {len(final_results)} results")
            return final_results

        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def _get_original_score(
        self,
        doc_id: str,
        vector_results: List[KnowledgeSearchResult],
        keyword_results: List[KnowledgeSearchResult]
    ) -> float:
        """获取文档在原始列表中的分数"""
        for vr in vector_results:
            if vr.knowledge_point.id == doc_id:
                return vr.score
        for kr in keyword_results:
            if kr.knowledge_point.id == doc_id:
                return kr.score
        return 0.0

    async def _vector_search(
        self,
        query: str,
        course: Optional[str] = None,
        limit: int = 10
    ) -> List[KnowledgeSearchResult]:
        """
        向量相似度检索

        使用query:前缀，符合BGE模型非对称检索规范
        """
        try:
            # 使用query:前缀进行查询
            query_input = f"query: {query}"
            query_embedding = await self.llm_client.get_embedding(query_input)

            # 构建过滤条件
            where = {"course": course} if course else None

            # 执行向量检索
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=limit,
                where=where,
                include=["documents", "metadatas", "distances"]
            )

            # 处理结果
            knowledge_results = []
            for i, (doc_id, document, metadata, distance) in enumerate(zip(
                results['ids'][0],
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                # 距离转相似度（Chroma使用余弦距离或L2距离）
                similarity = 1.0 - min(distance, 1.0)

                knowledge = self._build_knowledge_point(doc_id, document, metadata)

                knowledge_results.append(KnowledgeSearchResult(
                    knowledge_point=knowledge,
                    score=similarity,
                    rank=i + 1
                ))

            return knowledge_results

        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []

    async def _keyword_search(
        self,
        query: str,
        course: Optional[str] = None,
        limit: int = 10
    ) -> List[KnowledgeSearchResult]:
        """
        关键词全文检索

        使用Chroma的文档内容搜索
        """
        try:
            where = {"course": course} if course else None

            results = self.collection.query(
                query_texts=[query],
                n_results=limit,
                where=where,
                include=["documents", "metadatas", "distances"]
            )

            knowledge_results = []
            for i, (doc_id, document, metadata, distance) in enumerate(zip(
                results['ids'][0],
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            )):
                similarity = 1.0 - min(distance, 1.0)

                knowledge = self._build_knowledge_point(doc_id, document, metadata)

                knowledge_results.append(KnowledgeSearchResult(
                    knowledge_point=knowledge,
                    score=similarity,
                    rank=i + 1
                ))

            return knowledge_results

        except Exception as e:
            logger.error(f"Keyword search failed: {e}")
            return []

    def _build_knowledge_point(
        self,
        doc_id: str,
        document: str,
        metadata: dict
    ) -> KnowledgePoint:
        """从Chroma结果构建KnowledgePoint"""
        return KnowledgePoint(
            id=doc_id,
            title=metadata.get("title", ""),
            content=document,
            course=metadata.get("course", ""),
            chapter=metadata.get("chapter", ""),
            tags=json.loads(metadata.get("tags", "[]")) if metadata.get("tags") else [],
            source_file=metadata.get("source_file", ""),
            prerequisites=json.loads(metadata.get("prerequisites", "[]")) if metadata.get("prerequisites") else [],
            successors=json.loads(metadata.get("successors", "[]")) if metadata.get("successors") else [],
            related_ids=json.loads(metadata.get("related_ids", "[]")) if metadata.get("related_ids") else [],
        )

    async def _rerank_results(
        self,
        query: str,
        results: List[KnowledgeSearchResult]
    ) -> List[KnowledgeSearchResult]:
        """
        Rerank重排

        使用BAAI/bge-reranker-v2-m3模型对检索结果进行精排
        """
        if len(results) < 2:
            return results

        try:
            # 准备文档列表（截断到合理长度）
            documents = []
            for r in results:
                doc_text = f"{r.knowledge_point.title}\n{r.knowledge_point.content[:500]}"
                documents.append(doc_text)

            # 调用Rerank API
            rerank_pairs = await self.llm_client.rerank(
                query=query,
                documents=documents,
                top_n=min(len(results), RERANK_TOP_N * 2)
            )

            # 根据Rerank分数重新排序
            reranked = []
            for idx, rerank_score in rerank_pairs:
                if idx < len(results) and rerank_score >= self.rerank_min_score:
                    result = results[idx]
                    # 融合原始分数和Rerank分数
                    result.score = (result.score + rerank_score) / 2
                    result.rank = len(reranked) + 1
                    reranked.append(result)

            return reranked

        except Exception as e:
            logger.warning(f"Rerank failed, using original results: {e}")
            return results

    # ==================== 基础CRUD操作 ====================

    async def get_by_id(self, knowledge_id: str) -> Optional[KnowledgePoint]:
        """根据ID获取知识点"""
        try:
            result = self.collection.get(
                ids=[knowledge_id],
                include=["documents", "metadatas"]
            )

            if not result['ids']:
                return None

            return self._build_knowledge_point(
                result['ids'][0],
                result['documents'][0],
                result['metadatas'][0]
            )

        except Exception as e:
            logger.error(f"Get by id failed: {e}")
            return None

    async def get_by_ids(self, knowledge_ids: List[str]) -> List[KnowledgePoint]:
        """根据ID列表批量获取知识点"""
        if not knowledge_ids:
            return []

        try:
            result = self.collection.get(
                ids=knowledge_ids,
                include=["documents", "metadatas"]
            )

            return [
                self._build_knowledge_point(doc_id, document, metadata)
                for doc_id, document, metadata in zip(
                    result['ids'],
                    result['documents'],
                    result['metadatas']
                )
            ]

        except Exception as e:
            logger.error(f"Get by ids failed: {e}")
            return []

    async def get_by_course(self, course: str) -> List[KnowledgePoint]:
        """根据课程获取知识点列表"""
        try:
            result = self.collection.get(
                where={"course": course},
                include=["documents", "metadatas"]
            )

            return [
                self._build_knowledge_point(doc_id, document, metadata)
                for doc_id, document, metadata in zip(
                    result['ids'],
                    result['documents'],
                    result['metadatas']
                )
            ]

        except Exception as e:
            logger.error(f"Get by course failed: {e}")
            return []

    async def get_prerequisites(self, knowledge_id: str) -> List[KnowledgePoint]:
        """获取知识点的前置知识点"""
        knowledge = await self.get_by_id(knowledge_id)
        if not knowledge or not knowledge.prerequisites:
            return []
        return await self.get_by_ids(knowledge.prerequisites)

    async def get_successors(self, knowledge_id: str) -> List[KnowledgePoint]:
        """获取知识点的后置知识点"""
        knowledge = await self.get_by_id(knowledge_id)
        if not knowledge or not knowledge.successors:
            return []
        return await self.get_by_ids(knowledge.successors)

    async def get_related(self, knowledge_id: str) -> List[KnowledgePoint]:
        """获取知识点的相关知识点"""
        knowledge = await self.get_by_id(knowledge_id)
        if not knowledge or not knowledge.related_ids:
            return []
        return await self.get_by_ids(knowledge.related_ids)

    async def update(self, knowledge_point: KnowledgePoint) -> bool:
        """更新知识点"""
        return await self.save(knowledge_point)

    async def delete(self, knowledge_id: str) -> bool:
        """删除知识点"""
        try:
            self.collection.delete(ids=[knowledge_id])
            return True
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return False

    async def count(self) -> int:
        """获取知识点总数"""
        return self.collection.count()

    async def get_courses(self) -> List[str]:
        """获取所有课程名称"""
        try:
            result = self.collection.get(include=["metadatas"])
            courses = set()

            for metadata in result['metadatas']:
                if metadata and 'course' in metadata:
                    courses.add(metadata['course'])

            return sorted(list(courses))

        except Exception as e:
            logger.error(f"Get courses failed: {e}")
            return []

    # ==================== 辅助方法 ====================

    def build_context(
        self,
        results: List[KnowledgeSearchResult],
        max_content_length: int = 800
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        构建RAG上下文

        将检索结果转换为适合LLM的上下文格式，使用真实文档名称作为引用标识。

        Args:
            results: 检索结果列表
            max_content_length: 最大内容长度

        Returns:
            Tuple[str, List[Dict]]: (上下文文本, 参考来源列表)
        """
        context_parts = []
        references = []
        doc_names_seen = set()

        for idx, result in enumerate(results, 1):
            kp = result.knowledge_point
            doc_name = self._get_original_document_name(kp.source_file)

            # 截断内容
            content = kp.content[:max_content_length]
            if len(kp.content) > max_content_length:
                content += "..."

            # 使用原始文档名称作为引用标识
            context_parts.append(
                f"【{doc_name}】\n"
                f"标题: {kp.title}\n"
                f"课程: {kp.course}\n"
                f"内容: {content}\n"
            )

            # 构建参考来源（去重）
            if doc_name not in doc_names_seen:
                references.append({
                    "id": kp.id,
                    "title": kp.title,
                    "source": kp.source_file,
                    "course": kp.course,
                    "score": round(result.score, 3),
                    "original_doc": doc_name
                })
                doc_names_seen.add(doc_name)

        context = "\n\n".join(context_parts)
        return context, references

    def _get_original_document_name(self, source_file: str) -> str:
        """
        从源文件路径中提取原始文档名称
        
        Args:
            source_file: 源文件路径
            
        Returns:
            原始文档名称（不含路径和扩展名）
        """
        if not source_file:
            return "未知来源"
        import os
        return os.path.splitext(os.path.basename(source_file))[0]
