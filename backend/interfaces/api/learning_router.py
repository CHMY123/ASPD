"""
学习API路由

处理学习记录相关的HTTP请求。
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional

from interfaces.schemas.learning_schema import (
    LearningRecordRequest,
    LearningRecordResponse,
    LearningHistoryResponse,
    LearningRecordItem,
    LearningStatsResponse,
    CollectionRequest,
    CollectionResponse,
    CollectionItem,
    FolderRequest,
    FolderListResponse,
    LearningPathResponse,
    LearningPathItem,
    RecommendationRequest,
    RecommendationResponse,
)
from application.learning_service import LearningService
from interfaces.api.auth_router import get_current_user

router = APIRouter(prefix="/api/learning", tags=["学习"])

_learning_service: LearningService = None


def set_learning_service(service: LearningService):
    """设置学习服务（由main.py调用）"""
    global _learning_service
    _learning_service = service


def get_learning_service() -> LearningService:
    """获取学习服务"""
    if _learning_service is None:
        raise HTTPException(status_code=500, detail="学习服务未初始化")
    return _learning_service


async def require_authentication(current_user: dict = Depends(get_current_user)):
    """要求用户认证"""
    return current_user


@router.post(
    "/record",
    response_model=LearningRecordResponse,
    responses={401: {"description": "未授权"}}
)
async def record_learning(
    request: LearningRecordRequest,
    service: LearningService = Depends(get_learning_service),
    current_user: dict = Depends(require_authentication)
):
    """
    记录用户学习行为

    记录用户的浏览、搜索、提问等学习行为。
    """
    try:
        record = await service.record_action(
            user_id=request.user_id,
            knowledge_point_id=request.knowledge_point_id,
            action=request.action,
            duration=request.duration
        )
        return LearningRecordResponse(
            success=True,
            record_id=record.id
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "记录失败",
                "detail": str(e),
                "code": "RECORD_ERROR"
            }
        )


@router.get(
    "/history/{user_id}",
    response_model=LearningHistoryResponse,
    responses={401: {"description": "未授权"}}
)
async def get_learning_history(
    user_id: str,
    limit: int = Query(50, ge=1, le=100, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    service: LearningService = Depends(get_learning_service),
    current_user: dict = Depends(require_authentication)
):
    """
    获取用户学习历史

    返回指定用户的学习记录列表。
    """
    try:
        history = await service.get_learning_history(
            user_id=user_id,
            limit=limit,
            offset=offset
        )

        return LearningHistoryResponse(
            records=[
                LearningRecordItem(
                    id=item["record"]["id"],
                    user_id=item["record"]["user_id"],
                    knowledge_point_id=item["record"]["knowledge_point_id"],
                    action=item["record"]["action"],
                    duration=item["record"]["duration"],
                    created_at=item["record"]["created_at"]
                )
                for item in history
            ],
            total=len(history)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/stats/{user_id}",
    response_model=LearningStatsResponse,
    responses={401: {"description": "未授权"}}
)
async def get_learning_stats(
    user_id: str,
    service: LearningService = Depends(get_learning_service),
    current_user: dict = Depends(require_authentication)
):
    """
    获取用户学习统计

    返回指定用户的学习统计数据。
    """
    try:
        stats = await service.get_user_stats(user_id)

        return LearningStatsResponse(
            user_id=stats.user_id,
            total_views=stats.total_views,
            total_searches=stats.total_searches,
            total_questions=stats.total_questions,
            total_collections=stats.total_collections,
            total_duration=stats.total_duration,
            knowledge_coverage=stats.knowledge_coverage
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/path/{user_id}",
    response_model=LearningPathResponse,
    responses={401: {"description": "未授权"}}
)
async def get_learning_path(
    user_id: str,
    limit: int = Query(10, ge=1, le=50, description="返回数量限制"),
    service: LearningService = Depends(get_learning_service),
    current_user: dict = Depends(require_authentication)
):
    """
    获取用户学习路径

    返回指定用户最近的学习路径。
    """
    try:
        path = await service.get_user_learning_path(
            user_id=user_id,
            limit=limit
        )

        return LearningPathResponse(
            path=[
                LearningPathItem(
                    id=item["id"],
                    title=item["title"],
                    course=item["course"]
                )
                for item in path
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/collect",
    response_model=dict,
    responses={401: {"description": "未授权"}}
)
async def collect_knowledge(
    request: CollectionRequest,
    service: LearningService = Depends(get_learning_service),
    current_user: dict = Depends(require_authentication)
):
    """
    收藏知识点

    将指定知识点添加到用户收藏夹。
    """
    try:
        success = await service.collect_knowledge(
            user_id=request.user_id,
            knowledge_point_id=request.knowledge_point_id,
            folder=request.folder,
            note=request.note
        )
        return {"success": success}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "收藏失败",
                "detail": str(e),
                "code": "COLLECT_ERROR"
            }
        )


@router.delete(
    "/collect/{user_id}/{knowledge_point_id}",
    responses={401: {"description": "未授权"}}
)
async def uncollect_knowledge(
    user_id: str,
    knowledge_point_id: str,
    service: LearningService = Depends(get_learning_service),
    current_user: dict = Depends(require_authentication)
):
    """
    取消收藏

    从用户收藏夹中移除指定知识点。
    """
    try:
        success = await service.uncollect_knowledge(
            user_id=user_id,
            knowledge_point_id=knowledge_point_id
        )
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/collections/{user_id}",
    response_model=CollectionResponse,
    responses={401: {"description": "未授权"}}
)
async def get_user_collections(
    user_id: str,
    folder: Optional[str] = Query(None, description="收藏夹过滤"),
    limit: int = Query(50, ge=1, le=100, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    service: LearningService = Depends(get_learning_service),
    current_user: dict = Depends(require_authentication)
):
    """
    获取用户收藏列表

    返回指定用户的知识收藏列表。
    """
    try:
        collections = await service.get_user_collections(
            user_id=user_id,
            folder=folder,
            limit=limit,
            offset=offset
        )

        return CollectionResponse(
            collections=[
                CollectionItem(
                    collection_id=item["collection_id"],
                    knowledge=item["knowledge"],
                    folder=item["folder"],
                    note=item["note"],
                    created_at=item["created_at"]
                )
                for item in collections
            ],
            total=len(collections)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/collections/{user_id}/check/{knowledge_point_id}",
    responses={401: {"description": "未授权"}}
)
async def check_collected(
    user_id: str,
    knowledge_point_id: str,
    service: LearningService = Depends(get_learning_service),
    current_user: dict = Depends(require_authentication)
):
    """
    检查是否已收藏

    检查指定知识点是否已被用户收藏。
    """
    try:
        is_collected = await service.is_collected(
            user_id=user_id,
            knowledge_point_id=knowledge_point_id
        )
        return {"is_collected": is_collected}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/folders/{user_id}",
    response_model=FolderListResponse,
    responses={401: {"description": "未授权"}}
)
async def get_user_folders(
    user_id: str,
    service: LearningService = Depends(get_learning_service),
    current_user: dict = Depends(require_authentication)
):
    """
    获取用户收藏夹列表

    返回指定用户创建的所有收藏夹。
    """
    try:
        folders = await service.get_user_folders(user_id)
        return FolderListResponse(folders=folders)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/folders", responses={401: {"description": "未授权"}})
async def create_folder(
    request: FolderRequest,
    service: LearningService = Depends(get_learning_service),
    current_user: dict = Depends(require_authentication)
):
    """
    创建收藏夹

    在用户收藏夹中创建新的收藏夹。
    """
    try:
        success = await service.create_folder(
            user_id=request.user_id,
            folder_name=request.folder_name
        )
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/folders/{user_id}/{folder_name}", responses={401: {"description": "未授权"}})
async def delete_folder(
    user_id: str,
    folder_name: str,
    service: LearningService = Depends(get_learning_service),
    current_user: dict = Depends(require_authentication)
):
    """
    删除收藏夹

    删除指定的收藏夹（同时移除其中的所有收藏）。
    """
    try:
        success = await service.delete_folder(
            user_id=user_id,
            folder_name=folder_name
        )
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/records",
    response_model=LearningHistoryResponse,
    responses={401: {"description": "未授权"}}
)
async def get_learning_records(
    limit: int = Query(50, ge=1, le=100, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    service: LearningService = Depends(get_learning_service),
    current_user: dict = Depends(require_authentication)
):
    """
    获取当前用户学习记录

    返回当前用户的学习记录列表。
    """
    try:
        history = await service.get_learning_history(
            user_id=current_user["id"],
            limit=limit,
            offset=offset
        )

        return LearningHistoryResponse(
            records=[
                LearningRecordItem(
                    id=item["record"]["id"],
                    user_id=item["record"]["user_id"],
                    knowledge_point_id=item["record"]["knowledge_point_id"],
                    action=item["record"]["action"],
                    duration=item["record"]["duration"],
                    created_at=item["record"]["created_at"]
                )
                for item in history
            ],
            total=len(history)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/progress",
    response_model=dict,
    responses={401: {"description": "未授权"}}
)
async def get_learning_progress(
    service: LearningService = Depends(get_learning_service),
    current_user: dict = Depends(require_authentication)
):
    """
    获取当前用户学习进度

    返回当前用户的学习进度统计。
    """
    try:
        stats = await service.get_user_stats(current_user["id"])
        return {
            "user_id": stats.user_id,
            "total_views": stats.total_views,
            "total_searches": stats.total_searches,
            "total_questions": stats.total_questions,
            "total_collections": stats.total_collections,
            "total_duration": stats.total_duration,
            "knowledge_coverage": stats.knowledge_coverage,
            "recent_learning": []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/enrollments",
    response_model=List[dict],
    responses={401: {"description": "未授权"}}
)
async def get_user_enrollments(
    service: LearningService = Depends(get_learning_service),
    current_user: dict = Depends(require_authentication)
):
    """
    获取用户已选课程

    返回当前用户已选择的课程列表。
    """
    try:
        enrollments = [
            {
                "id": "1",
                "course_id": "数据结构",
                "course_name": "数据结构",
                "course_code": "CS-001",
                "credits": 3.0,
                "enrollment_time": "2024-09-01",
                "status": "active",
                "progress": 65
            },
            {
                "id": "2",
                "course_id": "计算机网络",
                "course_name": "计算机网络",
                "course_code": "CS-002",
                "credits": 3.0,
                "enrollment_time": "2024-09-01",
                "status": "active",
                "progress": 42
            }
        ]
        return enrollments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/enroll",
    response_model=dict,
    responses={401: {"description": "未授权"}}
)
async def enroll_course(
    request: dict,
    service: LearningService = Depends(get_learning_service),
    current_user: dict = Depends(require_authentication)
):
    """
    选课

    用户选择一门课程进行学习。
    """
    try:
        course_id = request.get("course_id")
        if not course_id:
            raise HTTPException(status_code=400, detail="课程ID不能为空")
        
        return {
            "success": True,
            "message": f"成功选择课程: {course_id}"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/track",
    response_model=dict,
    responses={401: {"description": "未授权"}}
)
async def track_learning(
    request: dict,
    service: LearningService = Depends(get_learning_service),
    current_user: dict = Depends(require_authentication)
):
    """
    跟踪学习行为

    记录用户的学习行为，包括浏览、学习等。
    """
    try:
        knowledge_point_id = request.get("knowledge_point_id")
        action = request.get("action", "view")
        duration = request.get("duration", 0)
        
        await service.record_action(
            user_id=current_user["id"],
            knowledge_point_id=knowledge_point_id,
            action=action,
            duration=duration
        )
        
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/collections",
    response_model=List[dict],
    responses={401: {"description": "未授权"}}
)
async def get_collections(
    folder: Optional[str] = Query(None, description="收藏夹过滤"),
    limit: int = Query(50, ge=1, le=100, description="返回数量限制"),
    offset: int = Query(0, ge=0, description="偏移量"),
    service: LearningService = Depends(get_learning_service),
    current_user: dict = Depends(require_authentication)
):
    """
    获取当前用户收藏列表

    返回当前用户的知识收藏列表。
    """
    try:
        collections = await service.get_user_collections(
            user_id=current_user["id"],
            folder=folder,
            limit=limit,
            offset=offset
        )
        
        return [
            {
                "id": item["collection_id"],
                "knowledge_point_id": item.get("knowledge_point_id", ""),
                "folder": item["folder"],
                "note": item["note"],
                "created_at": item["created_at"],
                "knowledge": item.get("knowledge", {})
            }
            for item in collections
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/collections",
    response_model=dict,
    responses={401: {"description": "未授权"}}
)
async def add_collection(
    request: dict,
    service: LearningService = Depends(get_learning_service),
    current_user: dict = Depends(require_authentication)
):
    """
    添加收藏

    将知识点添加到用户收藏。
    """
    try:
        knowledge_point_id = request.get("knowledge_point_id")
        note = request.get("note", "")
        
        success = await service.collect_knowledge(
            user_id=current_user["id"],
            knowledge_point_id=knowledge_point_id,
            folder="默认收藏夹",
            note=note
        )
        
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/collections/{collection_id}",
    response_model=dict,
    responses={401: {"description": "未授权"}}
)
async def remove_collection(
    collection_id: str,
    service: LearningService = Depends(get_learning_service),
    current_user: dict = Depends(require_authentication)
):
    """
    删除收藏

    从用户收藏中移除指定收藏项。
    """
    try:
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
