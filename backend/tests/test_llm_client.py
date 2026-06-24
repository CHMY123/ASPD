"""
单元测试 - LLM客户端

测试多模型回退、重试机制、向量化、流式输出等功能。
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from infrastructure.llm_client import LLMClient, FALLBACK_MODELS, retry_on_failure


class TestLLMClient:
    @pytest.fixture
    def client(self):
        return LLMClient(
            api_key="test-key",
            api_base="https://api.test.com/v1",
            model="test-model",
            fallback_models=["fallback-1", "fallback-2"]
        )

    def test_init_defaults(self):
        """验证默认初始化使用env配置"""
        client = LLMClient()
        assert client.api_key is not None
        assert client.api_base is not None
        assert client.model is not None

    def test_fallback_models_list(self):
        """验证多模型回退列表不为空"""
        assert len(FALLBACK_MODELS) > 0
        assert "Qwen/Qwen3-8B" in FALLBACK_MODELS

    def test_custom_fallback_models(self):
        """验证可自定义回退模型列表"""
        custom = ["model-a", "model-b"]
        client = LLMClient(
            api_key="test-key",
            fallback_models=custom
        )
        assert client.fallback_models == custom

    @pytest.mark.asyncio
    async def test_chat_fallback_primary_succeeds(self, client):
        """验证主模型成功时直接返回，不尝试回退模型"""
        with patch.object(client, '_chat_single', new_callable=AsyncMock) as mock_chat:
            mock_chat.return_value = {"choices": [{"message": {"content": "ok"}}]}
            
            result = await client.chat(
                messages=[{"role": "user", "content": "hello"}],
                use_fallback=True
            )
            
            assert result["choices"][0]["message"]["content"] == "ok"
            mock_chat.assert_called_once()

    @pytest.mark.asyncio
    async def test_chat_fallback_on_failure(self, client):
        """验证主模型失败后自动切换到回退模型"""
        call_count = [0]
        
        async def mock_chat_single(*args, **kwargs):
            call_count[0] += 1
            model = kwargs.get("model") or args[1] if len(args) > 1 else "unknown"
            if call_count[0] == 1:
                raise Exception("Primary model failed")
            return {"choices": [{"message": {"content": f"response from {model}"}}]}
        
        with patch.object(client, '_chat_single', side_effect=mock_chat_single):
            result = await client.chat(
                messages=[{"role": "user", "content": "hello"}],
                use_fallback=True
            )
            
            assert result["choices"][0]["message"]["content"] == "response from fallback-1"
            assert call_count[0] == 2

    @pytest.mark.asyncio
    async def test_chat_all_models_fail(self, client):
        """验证所有模型都失败时抛出异常"""
        with patch.object(client, '_chat_single', new_callable=AsyncMock) as mock_chat:
            mock_chat.side_effect = Exception("API Error")
            
            with pytest.raises(Exception) as exc_info:
                await client.chat(
                    messages=[{"role": "user", "content": "hello"}],
                    use_fallback=True
                )
            
            assert "所有模型" in str(exc_info.value) or "fallback" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_chat_without_fallback(self, client):
        """验证禁用回退时不尝试其他模型"""
        call_count = [0]
        
        async def mock_chat_single(*args, **kwargs):
            call_count[0] += 1
            raise Exception("Failed")
        
        with patch.object(client, '_chat_single', side_effect=mock_chat_single):
            with pytest.raises(Exception):
                await client.chat(
                    messages=[{"role": "user", "content": "hello"}],
                    use_fallback=False
                )
            
            assert call_count[0] == 1  # 应重试2次（由_chat_single内部控制）

    @pytest.mark.asyncio
    async def test_embedding(self, client):
        """验证向量化请求"""
        response_data = {
            "data": [
                {"embedding": [0.1, 0.2, 0.3], "index": 0}
            ],
            "model": "test-embedding-model",
            "usage": {"total_tokens": 5}
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value=response_data)
        
        with patch.object(client, '_get_client') as mock_get_client:
            mock_http = AsyncMock()
            mock_http.post = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_http

            embedding = await client.get_embedding("test text")

            assert embedding == [0.1, 0.2, 0.3]
            mock_http.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_rerank(self, client):
        """验证Rerank重排请求"""
        response_data = {
            "results": [
                {"index": 1, "relevance_score": 0.9},
                {"index": 0, "relevance_score": 0.7}
            ]
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value=response_data)
        
        with patch.object(client, '_get_client') as mock_get_client:
            mock_http = AsyncMock()
            mock_http.post = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_http

            results = await client.rerank(
                query="test query",
                documents=["doc a", "doc b"]
            )

            assert len(results) == 2
            assert results[0] == (1, 0.9)
            assert results[1] == (0, 0.7)

    @pytest.mark.asyncio
    async def test_embedding_passage_prefix(self, client):
        """验证embedding可接收带passage前缀的文本"""
        response_data = {
            "data": [
                {"embedding": [0.5, 0.6], "index": 0}
            ],
            "model": "test-embedding-model",
            "usage": {"total_tokens": 5}
        }

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json = MagicMock(return_value=response_data)
        
        with patch.object(client, '_get_client') as mock_get_client:
            mock_http = AsyncMock()
            mock_http.post = AsyncMock(return_value=mock_response)
            mock_get_client.return_value = mock_http

            passage_text = "passage: 什么是数组？数组是一种数据结构。"
            embedding = await client.get_embedding(passage_text)

            assert embedding == [0.5, 0.6]

            # 验证请求体包含正确的input
            call_args = mock_http.post.call_args
            assert call_args is not None
            json_payload = call_args[1].get("json", {})
            assert "input" in json_payload


class TestRetryDecorator:
    """重试装饰器测试"""

    @pytest.mark.asyncio
    async def test_retry_success_on_first_attempt(self):
        """验证第一次尝试即成功时无需重试"""
        mock_fn = AsyncMock(return_value="success")
        decorated = retry_on_failure(max_retries=3, delay=0.1)(mock_fn)
        
        result = await decorated()
        assert result == "success"
        mock_fn.assert_called_once()

    @pytest.mark.asyncio
    async def test_retry_eventually_succeeds(self):
        """验证失败重试后最终成功"""
        call_count = [0]
        
        async def flaky_fn():
            call_count[0] += 1
            if call_count[0] < 2:
                raise Exception("Transient error")
            return "success"
        
        decorated = retry_on_failure(max_retries=3, delay=0.1)(flaky_fn)
        
        result = await decorated()
        assert result == "success"
        assert call_count[0] == 2

    @pytest.mark.asyncio
    async def test_retry_all_attempts_fail(self):
        """验证所有重试次数用尽后抛出异常"""
        mock_fn = AsyncMock(side_effect=Exception("Persistent error"))
        decorated = retry_on_failure(max_retries=2, delay=0.1)(mock_fn)
        
        with pytest.raises(Exception, match="Persistent error"):
            await decorated()
        
        assert mock_fn.call_count == 2  # 1初始 + 1重试 = 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
