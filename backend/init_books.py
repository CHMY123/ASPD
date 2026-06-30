"""
书籍数据初始化脚本

将D:\Mine\Other\Practice\images下的书籍添加到数据库中
"""

import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from infrastructure.database import execute_sql, fetch_sql
from datetime import datetime


BOOKS_DATA = [
    {
        "isbn": "9787111611943",
        "title": "人工智能",
        "subtitle": "一种现代的方法（第4版）",
        "author": "Stuart Russell, Peter Norvig",
        "translator": "姜哲",
        "publisher": "人民邮电出版社",
        "publish_date": "2020-12-01",
        "category": "ai",
        "cover": "/assets/books/artificial_intelligence.jpg",
        "summary": "本书是人工智能领域的经典教材，全面介绍了人工智能的理论和实践。全书分为八大部分：第一部分介绍人工智能的基本概念和问题；第二部分讨论搜索问题求解；第三部分阐述知识表示和推理；第四部分介绍规划和行动；第五部分讨论不确定知识和推理；第六部分介绍机器学习；第七部分阐述通信、感知和行动；第八部分讨论人工智能的哲学、伦理和未来发展。本书适合作为高等院校计算机相关专业的人工智能课程教材，也可供对人工智能感兴趣的读者自学参考。",
        "table_of_contents": {
            "chapters": [
                "第1章 人工智能",
                "第2章 智能 Agent",
                "第3章 用搜索对问题求解",
                "第4章 超越经典搜索",
                "第5章 对抗搜索",
                "第6章 约束满足问题",
                "第7章 逻辑 Agent",
                "第8章 一阶逻辑",
                "第9章 推理",
                "第10章 知识表示",
                "第11章 规划",
                "第12章 不确定性",
                "第13章 概率推理",
                "第14章 概率规划",
                "第15章 学习",
                "第16章 强化学习",
                "第17章 通信",
                "第18章 感知",
                "第19章 机器人学",
                "第20章 结论"
            ]
        }
    },
    {
        "isbn": "9787111544937",
        "title": "深入理解计算机系统",
        "subtitle": "（第3版）",
        "author": "Randal E. Bryant, David R. O'Hallaron",
        "translator": "龚奕利, 雷迎春",
        "publisher": "机械工业出版社",
        "publish_date": "2016-12-01",
        "category": "os",
        "cover": "/assets/books/computer_systems_a_programmers_perspective.jpg",
        "summary": "从程序员的角度详细阐述计算机系统的本质概念，包括程序如何映射到系统上、程序如何执行以及程序如何与系统交互。全书共12章，涵盖了计算机系统的多个方面：从最底层的内存寻址、数据表示，到处理器架构、指令级并行，再到操作系统、网络编程等。本书的特色在于帮助读者理解程序运行时的行为，从而能够编写出更高效、更可靠的程序。书中包含大量的代码示例和练习，适合作为计算机专业本科生的系统课程教材，也适合有一定编程经验的程序员深入学习。",
        "table_of_contents": {
            "chapters": [
                "第1章 计算机系统漫游",
                "第2章 信息的表示和处理",
                "第3章 程序的机器级表示",
                "第4章 处理器体系结构",
                "第5章 优化程序性能",
                "第6章 存储器层次结构",
                "第7章 链接",
                "第8章 异常控制流",
                "第9章 虚拟内存",
                "第10章 系统级I/O",
                "第11章 网络编程",
                "第12章 并发编程"
            ]
        }
    },
    {
        "isbn": "9787111621949",
        "title": "数据结构与算法分析",
        "subtitle": "C语言描述（第2版）",
        "author": "Mark Allen Weiss",
        "translator": "冯舜玺",
        "publisher": "机械工业出版社",
        "publish_date": "2020-01-01",
        "category": "data-structure",
        "cover": "/assets/books/data_structures_and_algorithm_analysis.jpg",
        "summary": "本书是数据结构与算法领域的经典教材，采用C语言描述，全面介绍了数据结构的基本概念和算法分析方法。全书分为10章，涵盖了线性表、栈、队列、树、图等基本数据结构，以及排序、查找等常用算法。书中不仅介绍了数据结构的实现方法，还深入讨论了算法的时间复杂度和空间复杂度分析。每章都包含大量的示例和练习，帮助读者巩固所学知识。本书适合作为计算机专业本科生的数据结构课程教材，也可供对数据结构和算法感兴趣的读者自学。",
        "table_of_contents": {
            "chapters": [
                "第1章 引论",
                "第2章 算法分析",
                "第3章 表、栈和队列",
                "第4章 树",
                "第5章 散列",
                "第6章 优先队列",
                "第7章 排序",
                "第8章 不相交集",
                "第9章 图论算法",
                "第10章 算法设计技巧"
            ]
        }
    },
    {
        "isbn": "9787111634382",
        "title": "数据库系统概念",
        "subtitle": "（第7版）",
        "author": "Abraham Silberschatz, Henry F. Korth, S. Sudarshan",
        "translator": "杨冬青, 李红燕, 王腾蛟",
        "publisher": "机械工业出版社",
        "publish_date": "2020-10-01",
        "category": "database",
        "cover": "/assets/books/database_system_concepts.jpg",
        "summary": "本书是数据库系统领域的经典教材，全面介绍了数据库系统的基本概念、原理和技术。全书分为六个部分：第一部分介绍数据库系统概述和关系模型；第二部分讨论SQL语言和关系代数；第三部分阐述数据库设计和ER模型；第四部分介绍查询处理和优化；第五部分讨论事务管理和并发控制；第六部分介绍数据库安全和分布式数据库。本书内容丰富，涵盖了数据库系统的各个方面，包括最新的技术发展。书中包含大量的示例和练习，适合作为计算机专业本科生的数据库课程教材。",
        "table_of_contents": {
            "chapters": [
                "第1章 引言",
                "第2章 关系模型",
                "第3章 SQL",
                "第4章 高级SQL",
                "第5章 关系代数",
                "第6章 数据库设计",
                "第7章 实体-联系模型",
                "第8章 关系数据库设计",
                "第9章 查询处理",
                "第10章 查询优化",
                "第11章 事务",
                "第12章 并发控制",
                "第13章 恢复系统",
                "第14章 数据库安全",
                "第15章 分布式数据库"
            ]
        }
    },
    {
        "isbn": "9787115355769",
        "title": "算法图解",
        "subtitle": "",
        "author": "Aditya Bhargava",
        "translator": "袁国忠",
        "publisher": "人民邮电出版社",
        "publish_date": "2017-03-01",
        "category": "algorithm",
        "cover": "/assets/books/grokking_algorithms.jpg",
        "summary": "本书采用大量的图解和示例，以通俗易懂的方式介绍了各种算法的原理和应用。全书共10章，涵盖了二分查找、快速排序、递归、动态规划、图算法等常用算法。书中的图解生动形象，帮助读者直观理解算法的工作过程。每章都包含练习和示例，适合作为算法入门读物。本书的特色在于将复杂的算法概念简单化，让读者能够轻松理解和掌握。无论是计算机专业的学生还是编程爱好者，都可以从本书中受益。",
        "table_of_contents": {
            "chapters": [
                "第1章 算法简介",
                "第2章 选择排序",
                "第3章 递归",
                "第4章 快速排序",
                "第5章 哈希表",
                "第6章 广度优先搜索",
                "第7章 狄克斯特拉算法",
                "第8章 贪婪算法",
                "第9章 动态规划",
                "第10章 K最近邻算法"
            ]
        }
    },
    {
        "isbn": "9787111407010",
        "title": "算法导论",
        "subtitle": "（第3版）",
        "author": "Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein",
        "translator": "殷建平, 徐云, 王刚",
        "publisher": "机械工业出版社",
        "publish_date": "2012-12-01",
        "category": "algorithm",
        "cover": "/assets/books/introduction_to_algorithms.jpg",
        "summary": "本书是算法领域的经典教材，全面介绍了算法的设计和分析方法。全书分为八大部分：第一部分介绍算法的基本概念和数学基础；第二部分讨论排序和顺序统计量；第三部分阐述数据结构；第四部分介绍高级设计和分析技术；第五部分讨论高级数据结构；第六部分介绍图算法；第七部分阐述算法研究问题选编；第八部分讨论计算几何和NP完全性。本书内容严谨，涵盖了算法领域的各个方面，是学习算法的权威参考书。书中包含大量的伪代码和练习，适合作为计算机专业本科生和研究生的算法课程教材。",
        "table_of_contents": {
            "chapters": [
                "第1章 算法在计算中的作用",
                "第2章 算法基础",
                "第3章 函数的增长",
                "第4章 分治策略",
                "第5章 概率分析和随机算法",
                "第6章 堆排序",
                "第7章 快速排序",
                "第8章 线性时间排序",
                "第9章 中位数和顺序统计量",
                "第10章 基本数据结构",
                "第11章 散列表",
                "第12章 二叉搜索树",
                "第13章 红黑树",
                "第14章 数据结构的扩张",
                "第15章 动态规划",
                "第16章 贪心算法",
                "第17章 摊还分析",
                "第18章 B树",
                "第19章 斐波那契堆",
                "第20章 van Emde Boas树"
            ]
        }
    },
    {
        "isbn": "9787115279470",
        "title": "机器学习实战",
        "subtitle": "",
        "author": "Peter Harrington",
        "translator": "李锐, 李鹏, 曲亚东",
        "publisher": "人民邮电出版社",
        "publish_date": "2013-06-01",
        "category": "ai",
        "cover": "/assets/books/machine_learning_in_action.jpg",
        "summary": "本书通过大量的实际案例，介绍了机器学习的核心算法和应用方法。全书共12章，涵盖了K近邻算法、决策树、朴素贝叶斯、Logistic回归、支持向量机、AdaBoost集成方法、线性回归、树回归、K均值聚类、Apriori算法、FP-growth算法和PCA降维等常用机器学习算法。每章都包含完整的Python代码实现，帮助读者理解算法的工作原理并能够实际应用。本书适合作为机器学习的入门读物，无论是计算机专业的学生还是从事数据科学工作的人员，都可以从本书中受益。",
        "table_of_contents": {
            "chapters": [
                "第1章 机器学习基础",
                "第2章 K近邻算法",
                "第3章 决策树",
                "第4章 朴素贝叶斯",
                "第5章 Logistic回归",
                "第6章 支持向量机",
                "第7章 AdaBoost集成方法",
                "第8章 线性回归",
                "第9章 树回归",
                "第10章 K均值聚类",
                "第11章 Apriori关联分析",
                "第12章 FP-growth算法",
                "第13章 PCA降维"
            ]
        }
    },
    {
        "isbn": "9787111544937",
        "title": "操作系统导论",
        "subtitle": "",
        "author": "Remzi H. Arpaci-Dusseau, Andrea C. Arpaci-Dusseau",
        "translator": "王海鹏",
        "publisher": "机械工业出版社",
        "publish_date": "2019-01-01",
        "category": "os",
        "cover": "/assets/books/operating_system_introduction.jpg",
        "summary": "本书从原理和实践两个角度介绍了操作系统的核心概念。全书分为三个部分：第一部分介绍虚拟化，包括CPU虚拟化和内存虚拟化；第二部分讨论并发，包括线程、锁、条件变量和信号量等；第三部分阐述持久性，包括文件系统和磁盘管理。本书的特色在于通过大量的代码示例和实验，帮助读者理解操作系统的工作原理。书中包含多个可运行的项目，让读者能够亲自动手实现操作系统的核心功能。本书适合作为计算机专业本科生的操作系统课程教材，也适合对操作系统感兴趣的读者深入学习。",
        "table_of_contents": {
            "chapters": [
                "第1章 虚拟化：CPU",
                "第2章 虚拟化：内存",
                "第3章 并发：线程",
                "第4章 并发：锁",
                "第5章 并发：条件变量",
                "第6章 并发：信号量",
                "第7章 并发：调度",
                "第8章 持久性：文件系统",
                "第9章 持久性：磁盘",
                "第10章 持久性：RAID",
                "第11章 分布式系统",
                "第12章 安全性"
            ]
        }
    }
]


async def init_books():
    """初始化书籍数据"""
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    try:
        for book_data in BOOKS_DATA:
            # 检查ISBN是否已存在
            existing = await fetch_sql(
                "SELECT id FROM books WHERE isbn = %s LIMIT 1",
                book_data["isbn"]
            )
            
            if existing:
                logger.info(f"书籍 {book_data['title']} 已存在，跳过")
                continue

            # 生成唯一ID
            book_id = str(int(datetime.now().timestamp() * 1000)) + str(hash(book_data["isbn"]) % 1000)
            
            # 插入数据
            await execute_sql(
                """
                INSERT INTO books (
                    id, isbn, title, subtitle, author, translator, 
                    publisher, publish_date, category, summary, 
                    table_of_contents, cover, file_url, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                book_id,
                book_data["isbn"],
                book_data["title"],
                book_data["subtitle"],
                book_data["author"],
                book_data["translator"],
                book_data["publisher"],
                book_data["publish_date"],
                book_data["category"],
                book_data["summary"],
                str(book_data["table_of_contents"]),
                book_data["cover"],
                "",
                datetime.now().isoformat()
            )
            
            logger.info(f"书籍 {book_data['title']} 添加成功")

        logger.info("所有书籍数据初始化完成")
        
    except Exception as e:
        logger.error(f"初始化书籍数据失败: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(init_books())
