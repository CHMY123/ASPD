﻿# 华南师范大学计算机专业课程管理系统 - 数据库设计文档

## 一、概述

本文档详细描述了课程管理系统的数据库设计，包括实体关系、表结构设计、索引设计等内容。系统采用TiDB Cloud作为业务数据库，Chroma作为向量数据库。

## 二、数据库架构

### 2.1 整体架构

应用层连接TiDB Cloud和Chroma向量数据库，TiDB存储用户、课程、对话、学习数据，Chroma存储知识点向量和文档嵌入。

### 2.2 数据库选择说明

| 数据库类型 | 技术选型 | 用途 |
|-----------|---------|------|
| 关系型数据库 | TiDB Cloud | 存储用户、课程、对话等业务数据 |
| 向量数据库 | Chroma | 存储知识点向量，支持语义检索 |

## 三、核心表结构

### 3.1 用户表（users）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | VARCHAR(36) | PRIMARY KEY | 用户UUID |
| student_id | VARCHAR(20) | UNIQUE | 学号 |
| username | VARCHAR(100) | NOT NULL | 用户名 |
| email | VARCHAR(255) | UNIQUE | 邮箱 |
| password_hash | VARCHAR(255) | NOT NULL | 密码哈希 |
| real_name | VARCHAR(50) | NOT NULL | 真实姓名 |
| major | VARCHAR(100) | | 专业 |
| grade | VARCHAR(20) | | 年级 |
| role | VARCHAR(20) | DEFAULT 'student' | 用户角色 |
| is_active | BOOLEAN | DEFAULT true | 是否激活 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| updated_at | DATETIME | ON UPDATE CURRENT_TIMESTAMP | 更新时间 |

### 3.2 课程表（courses）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | VARCHAR(36) | PRIMARY KEY | 课程UUID |
| course_code | VARCHAR(50) | UNIQUE | 课程编号 |
| course_name | VARCHAR(200) | NOT NULL | 课程名称 |
| credits | DECIMAL(3,1) | NOT NULL | 学分 |
| hours | INT | NOT NULL | 学时 |
| semester | VARCHAR(20) | NOT NULL | 开课学期 |
| course_type | VARCHAR(20) | DEFAULT 'required' | 课程类型 |
| description | TEXT | | 课程简介 |
| teacher_name | VARCHAR(100) | | 教师姓名 |
| teacher_title | VARCHAR(50) | | 教师职称 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

### 3.3 选课表（enrollments）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | VARCHAR(36) | PRIMARY KEY | 记录UUID |
| user_id | VARCHAR(36) | FOREIGN KEY | 用户ID |
| course_id | VARCHAR(36) | FOREIGN KEY | 课程ID |
| enrollment_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 选课时间 |
| status | VARCHAR(20) | DEFAULT 'active' | 选课状态 |

### 3.4 电子书表（books）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | VARCHAR(36) | PRIMARY KEY | 书籍UUID |
| isbn | VARCHAR(20) | UNIQUE | ISBN编号 |
| title | VARCHAR(200) | NOT NULL | 书名 |
| author | VARCHAR(200) | NOT NULL | 作者 |
| publisher | VARCHAR(100) | | 出版社 |
| cover_url | VARCHAR(500) | | 封面URL |
| summary | TEXT | | 内容简介 |
| category | VARCHAR(50) | | 分类 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

### 3.5 对话表（conversations）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | VARCHAR(36) | PRIMARY KEY | 会话UUID |
| user_id | VARCHAR(36) | FOREIGN KEY | 用户ID |
| title | VARCHAR(200) | | 会话标题 |
| current_mode | VARCHAR(20) | DEFAULT 'knowledge' | 当前模式 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

### 3.6 消息表（messages）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | VARCHAR(36) | PRIMARY KEY | 消息UUID |
| conversation_id | VARCHAR(36) | FOREIGN KEY | 会话ID |
| role | VARCHAR(20) | NOT NULL | 角色 |
| content | TEXT | NOT NULL | 消息内容 |
| agent_used | VARCHAR(50) | | 使用的Agent |
| reasoning_steps | TEXT | | 推理步骤 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

### 3.7 学习记录表（learning_records）

| 字段名 | 类型 | 约束 | 说明 |
|--------|------|------|------|
| id | VARCHAR(36) | PRIMARY KEY | 记录UUID |
| user_id | VARCHAR(36) | FOREIGN KEY | 用户ID |
| knowledge_point_id | VARCHAR(64) | | 知识点ID |
| action | VARCHAR(20) | NOT NULL | 操作类型 |
| duration | INT | DEFAULT 0 | 停留时长 |
| created_at | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

## 四、向量数据库设计

### 4.1 Chroma集合结构

- 集合名称：cs_collection
- 向量维度：1024
- 距离度量：cosine

### 4.2 元数据字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| course_name | STRING | 所属课程名称 |
| chapter | STRING | 章节名称 |
| knowledge_type | STRING | 知识点类型 |
| keywords | LIST(STRING) | 关键词列表 |

## 五、数据库连接配置

### 5.1 TiDB Cloud

连接字符串从环境变量 `DATABASE_URL` 读取，配置格式：

```env
DATABASE_URL=mysql+pymysql://username:password@host:port/database
```

**注意**：TiDB Cloud连接需要SSL配置，后端已自动处理SSL连接。

### 5.2 Chroma

- 存储路径: `./cs_know_db`（从环境变量 `CHROMA_DB_PATH` 读取）
- 集合名称: `cs_collection`（从环境变量 `CHROMA_COLLECTION_NAME` 读取）
- Embedding模型: BAAI/bge-m3（1024维）
- 距离度量: cosine

### 5.3 环境变量配置

所有数据库连接配置通过 `backend/.env` 文件管理：

```env
# TiDB配置
DATABASE_URL=mysql+pymysql://user:password@host:port/database

# Chroma配置
CHROMA_DB_PATH=./cs_know_db
CHROMA_COLLECTION_NAME=cs_collection

# Embedding配置
EMBEDDING_MODEL=BAAI/bge-m3
EMBEDDING_DIMENSION=1024
```

---

文档版本: v1.1
创建日期: 2026年7月
