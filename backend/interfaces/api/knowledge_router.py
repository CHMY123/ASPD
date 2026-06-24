"""
知识库API路由

处理知识库管理相关的HTTP请求。
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional

from interfaces.schemas.knowledge_schema import (
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
    KnowledgeSearchResult,
    KnowledgeImportRequest,
    KnowledgeImportResponse,
    ImportError,
    KnowledgeDetailResponse,
    KnowledgePointBase,
    KnowledgeUpdateRequest,
    CourseListResponse,
    KnowledgeCountResponse,
)
from application.knowledge_service import KnowledgeService
from interfaces.api.auth_router import get_current_user
from infrastructure.database import fetch_sql

router = APIRouter(prefix="/api/knowledge", tags=["知识库"])

_knowledge_service: KnowledgeService = None


def set_knowledge_service(service: KnowledgeService):
    """设置知识库服务（由main.py调用）"""
    global _knowledge_service
    _knowledge_service = service


def get_knowledge_service() -> KnowledgeService:
    """获取知识库服务"""
    if _knowledge_service is None:
        raise HTTPException(status_code=500, detail="知识库服务未初始化")
    return _knowledge_service


async def require_authentication(current_user: dict = Depends(get_current_user)):
    """要求用户认证"""
    return current_user


@router.post(
    "/import",
    response_model=KnowledgeImportResponse,
    responses={401: {"description": "未授权"}}
)
async def import_knowledge(
    request: KnowledgeImportRequest,
    service: KnowledgeService = Depends(get_knowledge_service),
    current_user: dict = Depends(require_authentication)
):
    """
    批量导入Markdown格式的知识库文件

    从指定文件夹导入知识库文件到向量数据库。
    """
    try:
        result = await service.import_from_folder(
            folder_path=request.folder_path,
            course_filter=request.course_filter
        )

        return KnowledgeImportResponse(
            success=result.failed == 0,
            total=result.total,
            imported=result.imported,
            failed=result.failed,
            errors=[ImportError(**e) for e in result.errors]
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "导入失败，请检查文件格式和路径",
                "detail": str(e),
                "code": "IMPORT_ERROR"
            }
        )


@router.get(
    "",
    response_model=KnowledgeSearchResponse,
    responses={401: {"description": "未授权"}}
)
async def search_knowledge(
    query: str = Query(..., description="检索关键词"),
    course: Optional[str] = Query(None, description="课程过滤"),
    limit: int = Query(5, ge=1, le=20, description="返回数量限制"),
    service: KnowledgeService = Depends(get_knowledge_service),
    current_user: dict = Depends(require_authentication)
):
    """
    语义检索知识库

    基于向量相似度检索相关知识点。
    """
    try:
        results = await service.search_knowledge(
            query=query,
            course=course,
            limit=limit
        )

        return KnowledgeSearchResponse(
            results=[
                KnowledgeSearchResult(
                    id=r.knowledge_point.id,
                    title=r.knowledge_point.title,
                    content=r.knowledge_point.content[:200] + "..." if len(r.knowledge_point.content) > 200 else r.knowledge_point.content,
                    course=r.knowledge_point.course,
                    chapter=r.knowledge_point.chapter,
                    score=round(r.score, 4)
                )
                for r in results
            ],
            total=len(results)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "检索失败，请稍后重试",
                "detail": str(e),
                "code": "SEARCH_ERROR"
            }
        )


@router.post(
    "/search",
    response_model=KnowledgeSearchResponse,
    responses={401: {"description": "未授权"}}
)
async def search_knowledge_post(
    request: KnowledgeSearchRequest,
    service: KnowledgeService = Depends(get_knowledge_service),
    current_user: dict = Depends(require_authentication)
):
    """
    语义检索知识库（POST方法）

    基于向量相似度检索相关知识点。
    """
    return await search_knowledge(
        query=request.query,
        course=request.course,
        limit=request.limit,
        service=service
    )


@router.get(
    "/courses/list",
    response_model=CourseListResponse
)
async def get_course_list(
    service: KnowledgeService = Depends(get_knowledge_service)
):
    """
    获取课程列表（简单列表）

    返回知识库中所有课程名称。
    """
    try:
        courses = await service.get_all_courses()
        return CourseListResponse(
            courses=courses,
            total=len(courses)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/courses",
    response_model=List[dict],
    responses={401: {"description": "未授权"}}
)
async def get_courses(
    service: KnowledgeService = Depends(get_knowledge_service),
    current_user: dict = Depends(require_authentication)
):
    """
    获取完整课程列表（包含详情）

    返回所有课程的详细信息。
    """
    import logging
    logger = logging.getLogger(__name__)
    try:
        # 从数据库查询课程列表
        try:
            rows = await fetch_sql(
                "SELECT * FROM courses ORDER BY created_at DESC"
            )
        except Exception as db_err:
            logger.warning(f"数据库查询courses表失败: {db_err}")
            rows = []

        if rows:
            courses = []
            for row in rows:
                course = {
                    "id": str(row.get("id", "")),
                    "course_code": row.get("course_code", ""),
                    "course_name": row.get("course_name", ""),
                    "credits": float(row.get("credits", 3.0)),
                    "hours": int(row.get("hours", 48)),
                    "semester": row.get("semester", "2024-2025-1"),
                    "course_type": row.get("course_type", "elective"),
                    "description": row.get("description", ""),
                    "teacher_name": row.get("teacher_name", "未知"),
                    "teacher_title": row.get("teacher_title", "讲师"),
                    "schedule": row.get("schedule", ""),
                    "location": row.get("location", ""),
                    "class_location": row.get("class_location", ""),
                    "class_time": row.get("class_time", ""),
                    "cover": row.get("cover", ""),
                    "created_at": str(row.get("created_at", "")) if row.get("created_at") else ""
                }
                courses.append(course)
            return courses

        # 数据库无数据时返回空列表
        logger.info("数据库courses表为空，返回空列表")
        return []

    except Exception as e:
        logger.error(f"获取课程列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/courses/{course_id}",
    response_model=dict,
    responses={401: {"description": "未授权"}, 404: {"description": "课程不存在"}}
)
async def get_course_detail(
    course_id: str,
    service: KnowledgeService = Depends(get_knowledge_service),
    current_user: dict = Depends(require_authentication)
):
    """
    获取课程详情

    返回指定课程的详细信息和知识点列表。
    """
    try:
        knowledge_list = await service.get_knowledge_by_course(course_id)
        if not knowledge_list:
            raise HTTPException(status_code=404, detail="课程不存在")
        
        chapters = {}
        for k in knowledge_list:
            chapter = k.chapter or "未分类"
            if chapter not in chapters:
                chapters[chapter] = []
            chapters[chapter].append({
                "id": k.id,
                "title": k.title,
                "content": k.content[:100] + "..." if len(k.content) > 100 else k.content,
                "tags": k.tags
            })
        
        return {
            "id": course_id,
            "course_code": f"CS-{hash(course_id) % 1000:03d}",
            "course_name": course_id,
            "credits": 3.0,
            "hours": 48,
            "semester": "2024-2025-1",
            "course_type": "required" if course_id in ["数据结构", "计算机网络", "操作系统", "数据库系统"] else "elective",
            "description": f"{course_id}课程介绍",
            "teacher_name": "未知",
            "teacher_title": "讲师",
            "knowledge_count": len(knowledge_list),
            "chapters": chapters
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/courses",
    response_model=dict,
    responses={401: {"description": "未授权"}, 400: {"description": "参数错误"}}
)
async def add_course(
    course_data: dict,
    current_user: dict = Depends(require_authentication)
):
    """
    添加新课程

    将新课程信息保存到数据库。
    """
    import logging
    from infrastructure.database import execute_sql
    from datetime import datetime
    
    logger = logging.getLogger(__name__)
    try:
        # 验证必填字段
        required_fields = ['course_code', 'course_name', 'credits', 'hours', 'semester', 'teacher_name']
        for field in required_fields:
            if not course_data.get(field):
                raise HTTPException(status_code=400, detail=f"缺少必填字段: {field}")
        
        # 生成唯一ID
        course_id = str(int(datetime.now().timestamp() * 1000))
        
        # 插入数据库
        await execute_sql(
            """
            INSERT INTO courses (
                id, course_code, course_name, credits, hours, semester, 
                course_type, description, teacher_name, teacher_title, 
                schedule, location, class_location, class_time, cover, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            course_id,
            course_data.get('course_code', ''),
            course_data.get('course_name', ''),
            course_data.get('credits', 3.0),
            course_data.get('hours', 48),
            course_data.get('semester', '2024-2025-1'),
            course_data.get('course_type', 'required'),
            course_data.get('description', ''),
            course_data.get('teacher_name', ''),
            course_data.get('teacher_title', ''),
            course_data.get('schedule', ''),
            course_data.get('location', ''),
            course_data.get('class_location', ''),
            course_data.get('class_time', ''),
            course_data.get('cover', ''),
            datetime.now().isoformat()
        )
        
        logger.info(f"课程添加成功: {course_data.get('course_name')}")
        
        return {
            "success": True,
            "message": "课程添加成功",
            "course_id": course_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加课程失败: {e}")
        raise HTTPException(status_code=500, detail=f"添加课程失败: {str(e)}")


@router.get(
    "/books",
    response_model=List[dict],
    responses={401: {"description": "未授权"}}
)
async def get_books(
    service: KnowledgeService = Depends(get_knowledge_service),
    category: Optional[str] = Query(None, description="按分类筛选"),
    current_user: dict = Depends(require_authentication)
):
    """
    获取书籍列表

    从数据库电子书表中查询，若表为空则返回默认数据。
    """
    import logging
    logger = logging.getLogger(__name__)
    try:
        # 先从数据库查询
        try:
            if category:
                rows = await fetch_sql(
                    "SELECT * FROM books WHERE category = %s ORDER BY created_at DESC",
                    category
                )
            else:
                rows = await fetch_sql(
                    "SELECT * FROM books ORDER BY created_at DESC"
                )
        except Exception as db_err:
            logger.warning(f"数据库查询books表失败: {db_err}")
            rows = []

        if rows:
            books = []
            for row in rows:
                book = {
                    "id": str(row.get("id", "")),
                    "isbn": row.get("isbn", ""),
                    "title": row.get("title", ""),
                    "subtitle": row.get("subtitle", ""),
                    "author": row.get("author", ""),
                    "translator": row.get("translator", ""),
                    "publisher": row.get("publisher", ""),
                    "publish_date": row.get("publish_date", ""),
                    "cover_url": row.get("cover", ""),
                    "summary": row.get("summary", ""),
                    "category": row.get("category", ""),
                    "toc": row.get("table_of_contents", ""),
                    "created_at": str(row.get("created_at", "")) if row.get("created_at") else ""
                }
                books.append(book)
            return books

        # 数据库无数据时返回空列表
        logger.info("数据库books表为空，返回空列表")
        return []

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/books/{book_id}",
    response_model=dict,
    responses={401: {"description": "未授权"}, 404: {"description": "书籍不存在"}}
)
async def get_book_detail(
    book_id: str,
    service: KnowledgeService = Depends(get_knowledge_service),
    current_user: dict = Depends(require_authentication)
):
    """
    获取书籍详情

    返回指定书籍的详细信息。
    """
    import logging
    logger = logging.getLogger(__name__)
    try:
        # 先从数据库查询
        try:
            rows = await fetch_sql(
                "SELECT * FROM books WHERE id = %s LIMIT 1",
                book_id
            )
            if rows:
                row = rows[0]
                return {
                    "id": str(row.get("id", "")),
                    "isbn": row.get("isbn", ""),
                    "title": row.get("title", ""),
                    "subtitle": row.get("subtitle", ""),
                    "author": row.get("author", ""),
                    "translator": row.get("translator", ""),
                    "publisher": row.get("publisher", ""),
                    "publish_date": row.get("publish_date", ""),
                    "cover_url": row.get("cover", ""),
                    "summary": row.get("summary", ""),
                    "category": row.get("category", ""),
                    "toc": row.get("table_of_contents", ""),
                    "created_at": str(row.get("created_at", "")) if row.get("created_at") else ""
                }
        except Exception as db_err:
            logger.warning(f"数据库查询book详情失败: {db_err}")

        # 数据库无数据时报错
        raise HTTPException(status_code=404, detail="书籍不存在")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/books",
    response_model=dict,
    responses={401: {"description": "未授权"}, 400: {"description": "参数错误"}}
)
async def add_book(
    book_data: dict,
    current_user: dict = Depends(require_authentication)
):
    """
    添加新书籍

    将新书籍信息保存到数据库。
    """
    import logging
    from infrastructure.database import execute_sql
    from datetime import datetime
    
    logger = logging.getLogger(__name__)
    try:
        # 验证必填字段
        required_fields = ['title', 'author', 'publisher', 'category']
        for field in required_fields:
            if not book_data.get(field):
                raise HTTPException(status_code=400, detail=f"缺少必填字段: {field}")
        
        # 生成唯一ID
        book_id = str(int(datetime.now().timestamp() * 1000))
        
        # 插入数据库
        await execute_sql(
            """
            INSERT INTO books (
                id, isbn, title, subtitle, author, translator, 
                publisher, publish_date, cover, summary, category, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            book_id,
            book_data.get('isbn', ''),
            book_data.get('title', ''),
            book_data.get('subtitle', ''),
            book_data.get('author', ''),
            book_data.get('translator', ''),
            book_data.get('publisher', ''),
            book_data.get('publish_date', ''),
            book_data.get('cover_url', ''),
            book_data.get('summary', ''),
            book_data.get('category', ''),
            datetime.now().isoformat()
        )
        
        logger.info(f"书籍添加成功: {book_data.get('title')}")
        
        return {
            "success": True,
            "message": "书籍添加成功",
            "book_id": book_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"添加书籍失败: {e}")
        raise HTTPException(status_code=500, detail=f"添加书籍失败: {str(e)}")


@router.post(
    "/books/batch-delete",
    response_model=dict,
    responses={401: {"description": "未授权"}}
)
async def batch_delete_books(
    request: dict,
    current_user: dict = Depends(require_authentication)
):
    """
    批量删除书籍

    根据提供的ID列表批量删除电子书。
    """
    import logging
    from infrastructure.database import execute_sql
    logger = logging.getLogger(__name__)
    try:
        book_ids = request.get("ids", [])
        if not book_ids:
            raise HTTPException(status_code=400, detail="未提供要删除的书籍ID列表")
        
        # 逐条删除
        deleted_count = 0
        for book_id in book_ids:
            try:
                await execute_sql("DELETE FROM books WHERE id = %s", book_id)
                deleted_count += 1
            except Exception as e:
                logger.warning(f"删除书籍 {book_id} 失败: {e}")
        
        logger.info(f"批量删除书籍完成: 成功删除 {deleted_count}/{len(book_ids)} 条")
        return {
            "success": True,
            "message": f"成功删除 {deleted_count} 本电子书",
            "deleted_count": deleted_count
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量删除书籍失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量删除书籍失败: {str(e)}")


@router.post(
    "/courses/batch-delete",
    response_model=dict,
    responses={401: {"description": "未授权"}}
)
async def batch_delete_courses(
    request: dict,
    current_user: dict = Depends(require_authentication)
):
    """
    批量删除课程

    根据提供的ID列表批量删除课程。
    """
    import logging
    from infrastructure.database import execute_sql
    logger = logging.getLogger(__name__)
    try:
        course_ids = request.get("ids", [])
        if not course_ids:
            raise HTTPException(status_code=400, detail="未提供要删除的课程ID列表")
        
        deleted_count = 0
        for course_id in course_ids:
            try:
                await execute_sql("DELETE FROM courses WHERE id = %s", course_id)
                deleted_count += 1
            except Exception as e:
                logger.warning(f"删除课程 {course_id} 失败: {e}")
        
        logger.info(f"批量删除课程完成: 成功删除 {deleted_count}/{len(course_ids)} 条")
        return {
            "success": True,
            "message": f"成功删除 {deleted_count} 门课程",
            "deleted_count": deleted_count
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量删除课程失败: {e}")
        raise HTTPException(status_code=500, detail=f"批量删除课程失败: {str(e)}")


@router.get(
    "/{knowledge_id}",
    response_model=KnowledgeDetailResponse,
    responses={401: {"description": "未授权"}}
)
async def get_knowledge_detail(
    knowledge_id: str,
    service: KnowledgeService = Depends(get_knowledge_service),
    current_user: dict = Depends(require_authentication)
):
    """
    获取知识点详情

    返回指定知识点的完整信息，包括关联的知识点。
    """
    try:
        result = await service.get_knowledge_with_relations(knowledge_id)

        if not result or not result.get("knowledge"):
            raise HTTPException(status_code=404, detail="知识点不存在")

        kp = result["knowledge"]

        return KnowledgeDetailResponse(
            id=kp.id,
            title=kp.title,
            content=kp.content,
            course=kp.course,
            chapter=kp.chapter,
            tags=kp.tags,
            source_file=kp.source_file,
            prerequisites=[
                KnowledgePointBase(
                    id=p.id,
                    title=p.title,
                    content=p.content,
                    course=p.course,
                    chapter=p.chapter,
                    tags=p.tags,
                    source_file=p.source_file
                )
                for p in result.get("prerequisites", [])
            ],
            successors=[
                KnowledgePointBase(
                    id=s.id,
                    title=s.title,
                    content=s.content,
                    course=s.course,
                    chapter=s.chapter,
                    tags=s.tags,
                    source_file=s.source_file
                )
                for s in result.get("successors", [])
            ],
            related=[
                KnowledgePointBase(
                    id=r.id,
                    title=r.title,
                    content=r.content,
                    course=r.course,
                    chapter=r.chapter,
                    tags=r.tags,
                    source_file=r.source_file
                )
                for r in result.get("related", [])
            ]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{knowledge_id}", responses={401: {"description": "未授权"}})
async def update_knowledge(
    knowledge_id: str,
    request: KnowledgeUpdateRequest,
    service: KnowledgeService = Depends(get_knowledge_service),
    current_user: dict = Depends(require_authentication)
):
    """
    更新知识点

    更新指定知识点的内容、标签等信息。
    """
    try:
        knowledge = await service.get_knowledge_by_id(knowledge_id)
        if not knowledge:
            raise HTTPException(status_code=404, detail="知识点不存在")

        if request.title is not None:
            knowledge.title = request.title
        if request.content is not None:
            knowledge.content = request.content
        if request.chapter is not None:
            knowledge.chapter = request.chapter
        if request.tags is not None:
            knowledge.tags = request.tags
        if request.prerequisites is not None:
            knowledge.prerequisites = request.prerequisites
        if request.successors is not None:
            knowledge.successors = request.successors
        if request.related_ids is not None:
            knowledge.related_ids = request.related_ids

        success = await service.update_knowledge(knowledge)
        if not success:
            raise HTTPException(status_code=500, detail="更新失败")

        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{knowledge_id}", responses={401: {"description": "未授权"}})
async def delete_knowledge(
    knowledge_id: str,
    service: KnowledgeService = Depends(get_knowledge_service),
    current_user: dict = Depends(require_authentication)
):
    """
    删除知识点

    从知识库中删除指定的知识点。
    """
    try:
        success = await service.delete_knowledge(knowledge_id)
        if not success:
            raise HTTPException(status_code=404, detail="知识点不存在")
        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/course/{course}",
    response_model=List[KnowledgePointBase]
)
async def get_course_knowledge(
    course: str,
    service: KnowledgeService = Depends(get_knowledge_service)
):
    """
    获取课程的所有知识点

    返回指定课程下的所有知识点列表。
    """
    try:
        knowledge_list = await service.get_knowledge_by_course(course)
        return [
            KnowledgePointBase(
                id=k.id,
                title=k.title,
                content=k.content,
                course=k.course,
                chapter=k.chapter,
                tags=k.tags,
                source_file=k.source_file
            )
            for k in knowledge_list
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/stats/count",
    response_model=KnowledgeCountResponse
)
async def get_knowledge_count(
    service: KnowledgeService = Depends(get_knowledge_service)
):
    """
    获取知识点统计

    返回知识库的统计信息。
    """
    try:
        count = await service.get_knowledge_count()
        courses = await service.get_all_courses()

        return KnowledgeCountResponse(
            count=count,
            courses=courses
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
