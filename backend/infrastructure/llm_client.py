"""
LLM客户端封装 (LLM Client Wrapper)

封装OpenAI兼容API，提供Chat、Embedding和Rerank调用。
支持多模型回退、自动重试、流式输出。

核心特性：
1. 多模型回退：支持Qwen、DeepSeek、GPT等多个模型
2. 自动重试：指数退避重试机制
3. 流式输出：支持SSE流式响应
4. Rerank支持：集成重排模型进行结果优化
"""

from typing import List, Optional, Dict, Any, Tuple, AsyncGenerator
import httpx
import asyncio
import json
import logging

from config import (
    LLM_API_KEY,
    LLM_API_BASE,
    LLM_MODEL,
    LLM_MAX_TOKENS,
    LLM_TEMPERATURE,
    EMBEDDING_MODEL,
    EMBEDDING_API_BASE,
    RERANK_API_BASE,
    RERANK_MODEL,
    RERANK_MAX_LENGTH,
    RERANK_TOP_N,
)

logger = logging.getLogger(__name__)

# 多模型回退列表，按优先级排列
FALLBACK_MODELS = [
    "Qwen/Qwen3-8B",
    "Qwen/Qwen2.5-7B-Instruct",
    "deepseek-ai/DeepSeek-V3",
    "gpt-3.5-turbo",
]


def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """重试装饰器 —— 指数退避"""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    if attempt < max_retries - 1:
                        wait = delay * (2 ** attempt)
                        print(f"  ⚠️ 重试 ({attempt+1}/{max_retries}): {e}，等待{wait:.1f}s...")
                        await asyncio.sleep(wait)
                    else:
                        print(f"  ❌ 全部重试失败 ({max_retries}次): {e}")
            raise last_exc
        return wrapper
    return decorator


class LLMClient:
    """
    LLM客户端

    封装OpenAI兼容API调用，支持多模型回退、自动重试。

    Attributes:
        api_key: API密钥
        api_base: API基础URL
        model: 模型名称（主模型）
        max_tokens: 最大令牌数
        temperature: 温度参数
        embedding_model: Embedding模型名称
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        embedding_model: Optional[str] = None,
        fallback_models: Optional[List[str]] = None,
    ):
        """
        初始化LLM客户端

        Args:
            api_key: API密钥
            api_base: API基础URL
            model: 模型名称
            max_tokens: 最大令牌数
            temperature: 温度参数
            embedding_model: Embedding模型名称
            fallback_models: 回退模型列表
        """
        self.api_key = api_key or LLM_API_KEY
        self.api_base = api_base or LLM_API_BASE
        self.model = model or LLM_MODEL
        self.max_tokens = max_tokens or LLM_MAX_TOKENS
        self.temperature = temperature or LLM_TEMPERATURE
        self.embedding_model = embedding_model or EMBEDDING_MODEL
        self.fallback_models = fallback_models or FALLBACK_MODELS
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """
        获取HTTP客户端

        Returns:
            httpx.AsyncClient: HTTP客户端
        """
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.api_base,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=60.0,
            )
        return self._client

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stream: bool = False,
        use_fallback: bool = True,
    ) -> Dict[str, Any]:
        """
        发送聊天请求（非流式）—— 支持多模型回退（参照demo.py）

        Args:
            messages: 消息列表
            model: 模型名称
            max_tokens: 最大令牌数
            temperature: 温度参数
            stream: 是否流式返回
            use_fallback: 是否启用多模型回退

        Returns:
            Dict: API响应
        """
        models_to_try = [model or self.model]
        if use_fallback:
            models_to_try.extend([
                m for m in self.fallback_models if m != (model or self.model)
            ])

        last_error = None
        for attempt_model in models_to_try:
            try:
                logger.info(f"正在调用模型: {attempt_model}")
                result = await self._chat_single(
                    messages, attempt_model, max_tokens, temperature, stream
                )
                logger.info(f"模型 {attempt_model} 调用成功")
                return result
            except Exception as e:
                last_error = e
                logger.warning(f"模型 {attempt_model} 调用失败: {e}")
                logger.info("尝试下一个模型...")
                continue

        error_msg = f"所有模型({len(models_to_try)}个)均调用失败，最后错误: {last_error}"
        logger.error(error_msg)
        raise LLMError(error_msg)

    async def _chat_single(
        self,
        messages: List[Dict[str, str]],
        model: str,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """单个模型的聊天请求（含重试机制和详细日志）"""
        client = await self._get_client()

        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens or self.max_tokens,
            "temperature": temperature if temperature is not None else self.temperature,
            "stream": stream,
        }

        max_retries = 2
        for attempt in range(max_retries):
            try:
                start_time = __import__('time').time()
                response = await client.post("/chat/completions", json=payload)
                elapsed = __import__('time').time() - start_time
                
                if response.status_code != 200:
                    error_body = response.text[:500] if response.text else "无响应体"
                    logger.warning(f"模型{model}返回非200状态码: {response.status_code}，耗时{elapsed:.1f}s，响应: {error_body}")
                
                response.raise_for_status()
                result = response.json()
                logger.info(f"模型{model}调用成功，耗时{elapsed:.1f}s，输入{len(messages)}条消息")
                return result
                
            except httpx.TimeoutException as e:
                logger.warning(f"模型{model}请求超时（{attempt+1}/{max_retries}）: {e}")
                if attempt < max_retries - 1:
                    wait = 2.0 * (2 ** attempt)
                    logger.info(f"等待{wait:.1f}s后重试...")
                    await asyncio.sleep(wait)
                else:
                    raise LLMError(f"模型{model}请求超时，已重试{max_retries}次")
                    
            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                error_text = ""
                try:
                    error_text = e.response.text[:300]
                except Exception:
                    pass
                logger.warning(f"模型{model}HTTP错误({status})（{attempt+1}/{max_retries}）: {error_text}")
                if attempt < max_retries - 1:
                    wait = 1.0 * (2 ** attempt)
                    await asyncio.sleep(wait)
                else:
                    raise LLMError(f"模型{model}HTTP {status}: {error_text}")
                    
            except httpx.HTTPError as e:
                logger.warning(f"模型{model}请求失败（{attempt+1}/{max_retries}）: {e}")
                if attempt < max_retries - 1:
                    wait = 1.0 * (2 ** attempt)
                    await asyncio.sleep(wait)
                else:
                    raise LLMError(f"模型{model}请求失败: {e}")

    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        use_fallback: bool = True,
    ):
        """
        流式聊天请求 —— 返回异步生成器，支持多模型回退

        Args:
            messages: 消息列表
            model: 模型名称
            max_tokens: 最大令牌数
            temperature: 温度参数
            use_fallback: 是否启用多模型回退

        Yields:
            str: 每次一个 token
        """
        models_to_try = [model or self.model]
        if use_fallback:
            models_to_try.extend([
                m for m in self.fallback_models if m != (model or self.model)
            ])

        last_error = None
        for attempt_model in models_to_try:
            try:
                client = await self._get_client()

                payload = {
                    "model": attempt_model,
                    "messages": messages,
                    "max_tokens": max_tokens or self.max_tokens,
                    "temperature": temperature if temperature is not None else self.temperature,
                    "stream": True,
                }

                async with client.stream("POST", "/chat/completions", json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line or line.startswith(":"):
                            continue
                        if line.startswith("data: "):
                            data_str = line[6:].strip()
                            if data_str == "[DONE]":
                                break
                            try:
                                data = json.loads(data_str)
                                delta = data.get("choices", [{}])[0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                continue
                # 成功则退出
                return
            except Exception as e:
                last_error = e
                print(f"  ⚠️ 流式模型 {attempt_model} 失败: {e}")
                continue

        raise LLMError(
            f"所有模型({len(models_to_try)}个)流式调用均失败: {last_error}"
        )

    async def chat_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        context: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """
        获取聊天完成

        Args:
            prompt: 用户提示
            system_prompt: 系统提示
            context: 对话上下文

        Returns:
            str: 生成的回复
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if context:
            messages.extend(context)

        messages.append({"role": "user", "content": prompt})

        response = await self.chat(messages)

        if "choices" in response and len(response["choices"]) > 0:
            return response["choices"][0]["message"]["content"]

        return ""

    async def get_embedding(self, text: str) -> List[float]:
        """
        获取文本的向量表示

        Args:
            text: 文本内容

        Returns:
            List[float]: 向量表示
        """
        async with httpx.AsyncClient(
            base_url=EMBEDDING_API_BASE,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=httpx.Timeout(60.0)
        ) as client:
            payload = {
                "model": self.embedding_model,
                "input": text,
            }

            try:
                start_time = __import__('time').time()
                response = await client.post("/embeddings", json=payload)
                elapsed = __import__('time').time() - start_time
                response.raise_for_status()
                result = response.json()

                if "data" in result and len(result["data"]) > 0:
                    dim = len(result["data"][0]["embedding"])
                    logger.info(f"Embedding成功: 模型={self.embedding_model}, 维度={dim}, 耗时={elapsed:.1f}s")
                    return result["data"][0]["embedding"]

                raise LLMError("No embedding returned")
            except httpx.HTTPError as e:
                logger.error(f"Embedding API请求失败: 模型={self.embedding_model}, 错误={e}")
                raise LLMError(f"Embedding API request failed: {str(e)}")

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        批量获取文本向量表示

        Args:
            texts: 文本列表

        Returns:
            List[List[float]]: 向量列表
        """
        async with httpx.AsyncClient(
            base_url=EMBEDDING_API_BASE,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=httpx.Timeout(60.0)
        ) as client:
            payload = {
                "model": self.embedding_model,
                "input": texts,
            }

            try:
                response = await client.post("/embeddings", json=payload)
                response.raise_for_status()
                result = response.json()

                if "data" in result:
                    return [item["embedding"] for item in result["data"]]

                raise LLMError("No embeddings returned")
            except httpx.HTTPError as e:
                raise LLMError(f"Embeddings API request failed: {str(e)}")

    async def close(self):
        """关闭客户端"""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def rerank(
        self,
        query: str,
        documents: List[str],
        top_n: Optional[int] = None,
        model: Optional[str] = None,
        max_length: Optional[int] = None,
    ) -> List[Tuple[int, float]]:
        """
        对检索结果进行重排（Rerank）

        使用BAAI/bge-reranker-v2-m3模型对文档进行相关性排序。

        Args:
            query: 查询文本
            documents: 待重排的文档列表
            top_n: 返回前N个结果
            model: Rerank模型名称
            max_length: 最大长度

        Returns:
            List[Tuple[int, float]]: 包含原始索引和相关性分数的列表，按分数降序排列
        """
        async with httpx.AsyncClient(
            base_url=RERANK_API_BASE,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=httpx.Timeout(60.0)
        ) as client:
            payload = {
                "model": model or RERANK_MODEL,
                "query": query,
                "documents": documents,
                "top_n": top_n or RERANK_TOP_N,
                "max_length": max_length or RERANK_MAX_LENGTH,
            }

            try:
                logger.debug(f"Calling rerank API with {len(documents)} documents")
                response = await client.post("/rerank", json=payload)
                response.raise_for_status()
                result = response.json()

                if "results" in result:
                    rerank_results = [
                        (item["index"], item["relevance_score"])
                        for item in result["results"]
                    ]
                    logger.debug(f"Rerank returned {len(rerank_results)} results")
                    return rerank_results

                raise LLMError("No rerank results returned")
            except httpx.HTTPError as e:
                logger.error(f"Rerank API request failed: {e}")
                raise LLMError(f"Rerank API request failed: {str(e)}")

    async def chat_with_context(
        self,
        query: str,
        context_docs: List[str],
        system_prompt: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        """
        使用上下文文档进行对话

        Args:
            query: 用户查询
            context_docs: 上下文文档列表
            system_prompt: 系统提示
            history: 对话历史

        Returns:
            str: 生成的回复
        """
        if not system_prompt:
            system_prompt = """你是一个课程学习知识库问答系统的智能助手。
            请基于提供的参考文档回答用户问题，回答必须严格基于文档内容，不要编造信息。
            如果文档中没有相关信息，请明确告知用户。"""

        context_str = "\n\n".join([f"【参考文档{idx+1}】\n{doc}" for idx, doc in enumerate(context_docs)])
        
        messages = []
        messages.append({"role": "system", "content": system_prompt})

        if history:
            messages.extend(history)

        user_message = f"""参考文档：
{context_str}

用户问题：{query}

请基于上述参考文档回答问题。"""
        
        messages.append({"role": "user", "content": user_message})

        response = await self.chat(messages)
        
        if "choices" in response and len(response["choices"]) > 0:
            return response["choices"][0]["message"]["content"]

        return ""


class LLMError(Exception):
    """LLM调用异常"""
    pass


class MockLLMClient(LLMClient):
    """
    Mock LLM客户端

    用于测试，不调用真实API。
    """

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """返回模拟响应"""
        last_message = messages[-1]["content"] if messages else ""
        return {
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": f"【Mock回复】已收到您的问题：{last_message[:50]}..."
                    }
                }
            ]
        }

    async def get_embedding(self, text: str) -> List[float]:
        """返回模拟向量"""
        import hashlib
        hash_value = int(hashlib.md5(text.encode()).hexdigest(), 16)
        return [(hash_value % 1000) / 1000.0 for _ in range(1536)]
