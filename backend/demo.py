import requests
import numpy as np
import chromadb
from chromadb.config import Settings
from openai import OpenAI
import json
import time
from pathlib import Path
import re

# 全局配置
API_KEY = "sk-nkjhcdndlmaojcocructrqxctaorinahxclchoszspjbpbun"
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
embed_url = "https://api.siliconflow.cn/v1/embeddings"
rerank_url = "https://api.siliconflow.cn/v1/rerank"
chat_url = "https://api.siliconflow.cn/v1"

# 初始化OpenAI兼容客户端
llm_client = OpenAI(
    api_key=API_KEY,
    base_url=chat_url,
    timeout=60.0
)

# 初始化本地Chroma持久化向量库
client = chromadb.PersistentClient(
    path="./cs_know_db",
    settings=Settings(
        anonymized_telemetry=False,
        allow_reset=True
    )
)
client.reset()
collection = client.get_or_create_collection(name="cs_collection")

# ==================== 工具函数 ====================
def load_knowledge_files(knowledge_dir):
    """加载知识目录下的所有md文件并分割为知识块"""
    knowledge_path = Path(knowledge_dir)
    if not knowledge_path.exists():
        print(f"  ❌ 知识库目录不存在: {knowledge_dir}")
        return []
    
    all_chunks = []
    
    for md_file in sorted(knowledge_path.glob("*.md")):
        print(f"  📄 读取文件: {md_file.name}")
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 按标题分割文档
            chunks = _split_markdown_sections(content, md_file.stem)
            all_chunks.extend(chunks)
            print(f"    ✅ 提取 {len(chunks)} 个知识块")
            
        except Exception as e:
            print(f"    ❌ 读取文件失败: {e}")
    
    return all_chunks

def _split_markdown_sections(content, filename):
    """将Markdown内容分割为知识块，处理各级标题"""
    chunks = []
    
    # 使用正则匹配标题，支持 # 到 ####
    # 匹配所有标题级别
    pattern = r'(#{2,4})\s+(.+?)\n'
    sections = re.split(pattern, content)
    
    if len(sections) > 1:
        # 有标题的情况，按标题分割
        current_title = ""
        current_content = ""
        
        for i in range(1, len(sections), 3):
            if i + 2 <= len(sections):
                level = sections[i]
                title = sections[i + 1].strip()
                content_part = sections[i + 2] if i + 2 < len(sections) else ""
                
                # 如果有前一个区块，先保存
                if current_title and current_content.strip():
                    chunks.append(f"【{filename}】{current_title}\n{current_content.strip()}")
                
                current_title = f"{level} {title}"
                current_content = content_part
        
        # 保存最后一个区块
        if current_title and current_content.strip():
            chunks.append(f"【{filename}】{current_title}\n{current_content.strip()}")
    else:
        # 没有标题的情况，按段落分割
        paragraphs = content.split("\n\n")
        for para in paragraphs:
            para = para.strip()
            if para and len(para) > 10:  # 过滤短内容
                chunks.append(f"【{filename}】{para}")
    
    return chunks

def get_embedding(text_list, label=""):
    """向量化函数，增加标签用于调试"""
    payload = {
        "model": "BAAI/bge-m3",
        "input": text_list,
        "encoding_format": "float"
    }
    try:
        print(f"  📤 调用 Embedding API ({label})...")
        res = requests.post(embed_url, json=payload, headers=headers, timeout=30)
        res.raise_for_status()
        result = res.json()
        print(f"  ✅ 向量化成功，维度: {len(result['data'][0]['embedding'])}")
        return result
    except Exception as e:
        print(f"  ❌ Embedding API错误: {e}")
        raise

def rerank(query, docs):
    """重排序函数"""
    payload = {
        "model": "BAAI/bge-reranker-v2-m3",
        "query": query,
        "documents": docs
    }
    try:
        print("  📤 调用 Rerank API...")
        res = requests.post(rerank_url, json=payload, headers=headers, timeout=30)
        res.raise_for_status()
        result = res.json()
        print("  ✅ 重排序成功")
        return result
    except Exception as e:
        print(f"  ❌ Rerank API错误: {e}")
        raise

def llm_answer(user_question, reference_docs, debug=False):
    """LLM生成回答"""
    doc_context = "\n".join([f"- {doc}" for doc in reference_docs])
    
    system_prompt = """你是计算机技术助手。使用参考文档回答问题，保持简洁专业。"""
    user_message = f"""【参考文档】
{doc_context}

【用户问题】
{user_question}

请基于上述参考文档直接回答问题。"""
    
    if debug:
        print(f"\n  📝 发送给模型的 Prompt:")
        print(f"  {'='*60}")
        print(f"  System: {system_prompt}")
        print(f"  User: {user_message}")
        print(f"  {'='*60}")
    
    try:
        models_to_try = ["Qwen/Qwen3-8B"]
        
        for model in models_to_try:
            try:
                print(f"  🤖 尝试模型: {model}")
                
                response = llm_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.7,
                    max_tokens=512,
                    top_p=0.9,
                    frequency_penalty=0.1,
                    presence_penalty=0.1,
                    stream=False
                )
                
                content = response.choices[0].message.content
                
                if content and content.strip():
                    print(f"  ✅ 模型 {model} 返回成功")
                    return content.strip()
                else:
                    print(f"  [WARNING] 模型 {model} 返回空内容，尝试下一个...")
                    continue
                    
            except Exception as e:
                print(f"  ❌ 模型 {model} 调用失败: {e}")
                continue
        
        return "所有模型调用失败，请检查API配置或网络连接。"
        
    except Exception as e:
        return f"调用大模型失败：{str(e)}"

# ==================== 主流程 ====================
print("\n" + "="*80)
print("🚀 RAG 检索增强生成系统 - 完整流程演示")
print("="*80)

# -------------------- 步骤1: 准备知识库 --------------------
print("\n📚 步骤1: 准备知识库数据")
print("-" * 60)
# 从 docs/knowledge 目录加载所有知识库文件
knowledge_dir = Path(__file__).parent.parent / "docs" / "knowledge"
print(f"  知识库目录: {knowledge_dir}")
raw_chunks = load_knowledge_files(knowledge_dir)

if not raw_chunks:
    print("  ❌ 未找到任何知识库文件，使用示例数据")
    raw_chunks = [
        "【已知缺陷】multilingual-e5-base向量模型在处理中英混合计算机专业文档时，存在中文语义区分度不足的缺陷，检索时文档区分模糊。",
        "【推荐替代方案】BAAI/bge-m3专门优化中英混合技术文本，支持8192上下文，能够解决multilingual-e5-base区分度不足的检索缺陷。"
    ]

print(f"\n  共加载 {len(raw_chunks)} 个知识块")
print("  部分知识块预览:")
for i, chunk in enumerate(raw_chunks[:3], 1):
    preview = chunk[:100] + "..." if len(chunk) > 100 else chunk
    print(f"    [{i}] {preview}")

# -------------------- 步骤2: 向量化入库 --------------------
print("\n🔢 步骤2: 文档向量化并存入 ChromaDB")
print("-" * 60)
print("  2.1 对文档进行向量化 (Embedding)")
passage_inputs = [f"passage: {text}" for text in raw_chunks]
embed_resp = get_embedding(passage_inputs, "文档入库")
vec_list = [item["embedding"] for item in embed_resp["data"]]
doc_ids = [f"doc_{i}" for i in range(len(raw_chunks))]

print("  2.2 存入 ChromaDB 向量数据库")
collection.add(
    ids=doc_ids,
    documents=raw_chunks,
    embeddings=vec_list
)
print(f"  ✅ 已存入 {len(raw_chunks)} 条文档到向量库")

# -------------------- 步骤3: 用户提问 --------------------
print("\n❓ 步骤3: 用户提出问题")
print("-" * 60)
user_query_raw = "二叉树的定义是什么？"
print(f"  👤 用户提问: {user_query_raw}")

# -------------------- 步骤4: 向量检索(粗召回) --------------------
print("\n🔍 步骤4: 向量检索 - 粗召回 (Retrieval)")
print("-" * 60)
print("  4.1 对用户问题向量化")
query_input = [f"query: {user_query_raw}"]
query_resp = get_embedding(query_input, "用户查询")
query_vec = query_resp["data"][0]["embedding"]

print("  4.2 在向量库中检索最相关的文档")
retrieve_result = collection.query(
    query_embeddings=[query_vec],
    n_results=2,
    include=["documents", "distances"]
)
recall_docs = retrieve_result["documents"][0]
distances = retrieve_result["distances"][0]

print("  📋 粗召回结果 (按相似度排序):")
for i, (doc, dist) in enumerate(zip(recall_docs, distances), 1):
    print(f"    [{i}] 相似度距离: {dist:.4f}")
    print(f"        内容: {doc}")

# -------------------- 步骤5: 重排序(精排) --------------------
print("\n🎯 步骤5: 重排序 - 精排 (Rerank)")
print("-" * 60)
print("  5.1 调用 Rerank API 对召回结果重新排序")
rerank_res = rerank(user_query_raw, recall_docs)
rerank_result = sorted(rerank_res["results"], key=lambda x: x["relevance_score"], reverse=True)
sorted_ref_docs = [recall_docs[item["index"]] for item in rerank_result]

print("  📋 精排结果 (按相关度评分):")
for item in rerank_result:
    idx = item["index"]
    score = item["relevance_score"]
    print(f"    [文档{idx+1}] 相关度评分: {score:.4f}")
    print(f"        内容: {recall_docs[idx]}")

# -------------------- 步骤6: 生成最终回答 --------------------
print("\n💬 步骤6: 大模型生成回答 (Generation)")
print("-" * 60)
print("  6.1 将精排后的文档作为上下文")
print("  6.2 调用 Qwen 模型生成回答")
final_ans = llm_answer(user_query_raw, sorted_ref_docs, debug=True)

# -------------------- 步骤7: 输出最终结果 --------------------
print("\n" + "="*80)
print("📊 最终输出结果")
print("="*80)

print(f"\n👤 用户提问：{user_query_raw}\n")

print("📖 参考文档 (按相关度排序):")
for idx, doc in enumerate(sorted_ref_docs, 1):
    print(f"  [{idx}] {doc}")

print("\n🤖 最终回答:")
print("-" * 60)
print(final_ans)
print("-" * 60)

# -------------------- 调试: API测试 --------------------
if "失败" in final_ans or "错误" in final_ans:
    print("\n[WARNING] API 调用出现问题，执行连通性测试...")
    print("-" * 60)
    test_payload = {
        "model": "Qwen/Qwen3-8B",
        "messages": [
            {"role": "system", "content": "你是技术助手"},
            {"role": "user", "content": "请回答：1+1等于几？"}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }
    try:
        print("  📤 发送测试请求到 SiliconFlow...")
        test_res = requests.post(
            "https://api.siliconflow.cn/v1/chat/completions",
            json=test_payload,
            headers=headers,
            timeout=30
        )
        print(f"  📊 API状态码: {test_res.status_code}")
        if test_res.status_code == 200:
            test_data = test_res.json()
            result = test_data.get('choices', [{}])[0].get('message', {}).get('content', '无内容')
            print(f"  ✅ API测试成功，返回: {result}")
        else:
            print(f"  ❌ API测试失败: {test_res.text}")
    except Exception as e:
        print(f"  ❌ API测试异常: {e}")

print("\n" + "="*80)
print("✅ RAG 流程演示完成")
print("="*80)