"""
多Agent智能问答系统 - 示例使用
"""

import asyncio
import sys
import os
from typing import Dict, Any
import json

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents import CoordinationAgent
from base import MessageBus


# 示例知识库
SAMPLE_KNOWLEDGE_BASE = {
    "knowledge_block_1": {
        "content": """数组是一组相同类型元素的有序集合，在内存中连续存储。

**关键特性**
- **随机访问**：通过下标直接访问元素，时间复杂度O(1)
- **内存连续**：元素在内存中连续存储，利用局部性原理
- **固定大小**：创建时确定大小，动态调整需要复制

**时间复杂度**
- 访问：O(1)
- 插入：O(n) - 需要移动后续元素
- 删除：O(n) - 需要移动后续元素""",
        "metadata": {
            "章节": "1.1.1",
            "难度": "基础",
            "标签": ["线性表", "数组", "随机访问"],
            "预计阅读时间": "3分钟"
        }
    },
    "knowledge_block_2": {
        "content": """链表通过节点间的指针连接，每个节点包含数据域和指针域。

**链表类型**
- **单链表**：每个节点包含数据和指向下一节点的指针
- **双链表**：每个节点包含前驱和后继指针，支持双向遍历
- **循环链表**：尾节点的next指针指向头节点

**时间复杂度**
- 访问：O(n) - 需要从头遍历
- 插入：O(1) - 已知位置时
- 删除：O(1) - 已知位置时""",
        "metadata": {
            "章节": "1.1.2",
            "难度": "基础",
            "标签": ["线性表", "链表", "动态分配"],
            "预计阅读时间": "5分钟"
        }
    },
    "knowledge_block_3": {
        "content": """栈是一种后进先出（LIFO）的线性数据结构，只允许在一端（栈顶）进行操作。

**基本操作**
- **push**：压栈，向栈顶添加元素
- **pop**：出栈，删除并返回栈顶元素
- **peek/top**：查看栈顶元素但不删除
- **isEmpty**：判断栈是否为空

**应用场景**
- 函数调用栈（递归）
- 表达式求值（中缀转后缀）
- 括号匹配
- 浏览器前进后退
- 撤销操作""",
        "metadata": {
            "章节": "1.1.3",
            "难度": "基础",
            "标签": ["线性表", "栈", "LIFO"],
            "预计阅读时间": "3分钟"
        }
    },
    "knowledge_block_4": {
        "content": """队列是一种先进先出（FIFO）的线性数据结构，在一端入队，另一端出队。

**基本操作**
- **enqueue**：入队，向队尾添加元素
- **dequeue**：出队，删除并返回队首元素
- **front**：查看队首元素
- **isEmpty**：判断队列是否为空

**队列变体**
- **双端队列**：两端都可插入删除
- **优先队列**：按优先级出队，通常用堆实现
- **循环队列**：避免假溢出，空间利用率高""",
        "metadata": {
            "章节": "1.1.4",
            "难度": "基础",
            "标签": ["线性表", "队列", "FIFO"],
            "预计阅读时间": "4分钟"
        }
    },
    "knowledge_block_5": {
        "content": """二叉树是每个节点最多有两个子树（左子树和右子树）的树结构。

**基本性质**
- 第k层最多有2^(k-1)个节点
- 深度为h的二叉树最多有2^h - 1个节点
- 叶子节点数 = 度为2的节点数 + 1

**遍历方式**
- **前序遍历**：根 → 左 → 右
- **中序遍历**：左 → 根 → 右
- **后序遍历**：左 → 右 → 根
- **层序遍历**：按层从左到右""",
        "metadata": {
            "章节": "1.2.1",
            "难度": "中等",
            "标签": ["树", "二叉树", "递归"],
            "预计阅读时间": "5分钟"
        }
    },
    "knowledge_block_6": {
        "content": """二叉搜索树（BST）是一种特殊的二叉树，满足左子树所有节点 < 根节点 < 右子树所有节点。

**BST性质**
- 左子树上所有节点的值均小于根节点的值
- 右子树上所有节点的值均大于根节点的值
- 左右子树也分别为二叉搜索树
- 中序遍历得到有序序列

**基本操作**

**查找**
- 从根节点开始比较
- 小于当前节点则向左查找
- 大于当前节点则向右查找
- 时间复杂度：O(h)，h为树的高度

**插入**
- 类似查找操作
- 找到合适的空位置插入新节点
- 时间复杂度：O(h)

**删除**
- 删除叶子节点：直接删除
- 删除只有一个孩子的节点：用孩子节点替代
- 删除有两个孩子的节点：用后继节点（右子树最小）或前驱节点（左子树最大）替代

**性能分析**
- 平均情况：O(log n) - 树平衡时
- 最坏情况：O(n) - 退化为链表""",
        "metadata": {
            "章节": "1.2.2",
            "难度": "中等",
            "标签": ["树", "二叉搜索树", "BST"],
            "预计阅读时间": "6分钟"
        }
    },
    "knowledge_block_7": {
        "content": """AVL树是最早提出的自平衡二叉搜索树，要求任意节点的左右子树高度差（平衡因子）绝对值不超过1。

**平衡因子**
- 平衡因子 = 左子树高度 - 右子树高度
- AVL树要求 |平衡因子| ≤ 1

**旋转操作**
当插入或删除导致平衡被破坏时，通过旋转恢复平衡：

- **LL旋转（右单旋）**：左孩子的左子树过高
- **RR旋转（左单旋）**：右孩子的右子树过高
- **LR旋转（左右双旋）**：左孩子的右子树过高
- **RL旋转（右左双旋）**：右孩子的左子树过高

**时间复杂度**
- 查找：O(log n)
- 插入：O(log n) - 最多旋转两次
- 删除：O(log n) - 最多旋转O(log n)次""",
        "metadata": {
            "章节": "1.2.3",
            "难度": "较难",
            "标签": ["树", "平衡树", "AVL"],
            "预计阅读时间": "8分钟"
        }
    },
    "knowledge_block_8": {
        "content": """红黑树是一种自平衡二叉搜索树，通过颜色标记和旋转操作维持平衡。

**红黑树性质**
1. 每个节点要么红色要么黑色
2. 根节点是黑色
3. 叶子节点（NIL）是黑色
4. 红色节点的两个子节点都是黑色（不能有连续红色节点）
5. 从任一节点到其每个叶子的所有路径都包含相同数目的黑色节点（黑高相同）

**插入操作**
1. 按BST方式插入新节点（红色）
2. 根据父节点和叔节点的颜色进行调整
3. 通过变色和旋转恢复红黑性质

**删除操作**
1. 按BST方式删除节点
2. 处理被删除节点的孩子（可能是双重黑色）
3. 通过变色和旋转恢复红黑性质

**时间复杂度**
- 查找：O(log n)
- 插入：O(log n)
- 删除：O(log n)

**应用场景**
- C++ STL的map、set
- Java的TreeMap、TreeSet
- Linux内核的完全公平调度器（CFS）
- epoll的实现""",
        "metadata": {
            "章节": "1.2.4",
            "难度": "较难",
            "标签": ["树", "平衡树", "红黑树"],
            "预计阅读时间": "10分钟"
        }
    }
}


async def main():
    """主函数"""
    print("=" * 80)
    print("多Agent智能问答系统 - 示例演示")
    print("=" * 80)
    
    # 1. 初始化协调Agent
    print("\n[1] 初始化系统...")
    coordination_agent = CoordinationAgent(
        knowledge_base=SAMPLE_KNOWLEDGE_BASE
    )
    print("✓ 系统初始化完成")
    
    # 2. 显示系统状态
    print("\n[2] 系统状态:")
    status = coordination_agent.get_system_status()
    print(f"  - 注册的Agent: {list(status['agents'].keys())}")
    print(f"  - 可用工作流: {status['workflows']}")
    
    # 3. 示例查询
    queries = [
        "什么是二叉搜索树？如何进行查找操作？",
        "数组和链表有什么区别？",
        "栈和队列的应用场景有哪些？",
        "AVL树和红黑树有什么区别？"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n[3.{i}] 处理查询: {query}")
        print("-" * 80)
        
        # 设置上下文
        context = {
            'user_level': 'intermediate',
            'previous_topics': [],
            'conversation_history': []
        }
        
        # 处理查询
        result = await coordination_agent.process_query(query, context)
        
        # 显示结果
        if result.get('status') == 'success':
            print(f"\n【答案】")
            print(result.get('answer', ''))
            
            print(f"\n【置信度】: {result.get('confidence', 0):.2f}")
            print(f"【验证分数】: {result.get('validation_score', 0):.2f}")
            print(f"【验证反馈】: {result.get('validation_feedback', '')}")
            
            citations = result.get('citations', [])
            if citations:
                print(f"\n【引用来源】({len(citations)}个)")
                for citation in citations:
                    print(f"  {citation['id']}. {citation['section']} - {citation['title']}")
            
            related = result.get('related_knowledge', [])
            if related:
                print(f"\n【相关知识推荐】({len(related)}个)")
                for item in related:
                    print(f"  - {item['section']} (相关度: {item['relevance']:.2f})")
            
            learning_path = result.get('learning_path', [])
            if learning_path:
                print(f"\n【学习路径】")
                for step in learning_path:
                    print(f"  {step['step']}. {step['level']} - {step['description']} ({step['estimated_time']})")
        else:
            print(f"\n【错误】: {result.get('error', 'Unknown error')}")
        
        print("-" * 80)
    
    # 4. 显示最终系统状态
    print("\n[4] 最终系统状态:")
    final_status = coordination_agent.get_system_status()
    tasks = final_status.get('tasks', {})
    print(f"  - 已完成任务: {len(tasks.get('completed', []))}")
    print(f"  - 失败任务: {len(tasks.get('failed', []))}")
    
    print("\n" + "=" * 80)
    print("演示完成")
    print("=" * 80)


async def interactive_mode():
    """交互式模式"""
    print("=" * 80)
    print("多Agent智能问答系统 - 交互式模式")
    print("=" * 80)
    print("输入 'quit' 或 'exit' 退出")
    
    # 初始化系统
    coordination_agent = CoordinationAgent(
        knowledge_base=SAMPLE_KNOWLEDGE_BASE
    )
    
    context = {
        'user_level': 'intermediate',
        'previous_topics': [],
        'conversation_history': []
    }
    
    while True:
        print("\n" + "-" * 80)
        query = input("请输入您的问题: ").strip()
        
        if query.lower() in ['quit', 'exit', '退出']:
            print("再见！")
            break
        
        if not query:
            continue
        
        # 处理查询
        result = await coordination_agent.process_query(query, context)
        
        # 显示结果
        if result.get('status') == 'success':
            print(f"\n【答案】")
            print(result.get('answer', ''))
            
            print(f"\n【置信度】: {result.get('confidence', 0):.2f}")
            
            citations = result.get('citations', [])
            if citations:
                print(f"\n【引用来源】")
                for citation in citations:
                    print(f"  - {citation['section']}")
            
            # 更新上下文
            context['previous_topics'].append(query)
            context['conversation_history'].append({
                'query': query,
                'answer': result.get('answer', ''),
                'timestamp': result.get('timestamp', '')
            })
        else:
            print(f"\n【错误】: {result.get('error', 'Unknown error')}")


def run_example():
    """运行示例"""
    print("选择运行模式:")
    print("1. 演示模式 (预设查询)")
    print("2. 交互式模式 (手动输入)")
    
    choice = input("请选择 (1/2): ").strip()
    
    if choice == '1':
        asyncio.run(main())
    elif choice == '2':
        asyncio.run(interactive_mode())
    else:
        print("无效选择，运行演示模式")
        asyncio.run(main())


if __name__ == "__main__":
    run_example()