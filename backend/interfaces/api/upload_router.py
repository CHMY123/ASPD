"""
文件上传API路由

提供用户头像、课程封面、电子书封面等文件的上传接口。
"""

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from typing import Optional
import logging

from infrastructure.storage_service import storage_service
from interfaces.api.auth_router import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/upload", tags=["上传"])


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    """
    上传用户头像

    Args:
        file: 头像文件
        user: 当前用户

    Returns:
        头像URL
    """
    try:
        file_data = await file.read()
        url = storage_service.upload_user_avatar(file_data, file.filename, user.get('id', 'anonymous'))
        
        if not url:
            raise HTTPException(status_code=500, detail="头像上传失败")
        
        return {"url": url}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"头像上传异常: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.post("/course-cover/{course_id}")
async def upload_course_cover(
    course_id: str,
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    """
    上传课程封面

    Args:
        course_id: 课程ID
        file: 封面文件
        user: 当前用户

    Returns:
        封面URL
    """
    try:
        file_data = await file.read()
        url = storage_service.upload_course_cover(file_data, file.filename, course_id)
        
        if not url:
            raise HTTPException(status_code=500, detail="课程封面上传失败")
        
        return {"url": url}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"课程封面上传异常: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.post("/ebook-cover/{ebook_id}")
async def upload_ebook_cover(
    ebook_id: str,
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user)
):
    """
    上传电子书封面

    Args:
        ebook_id: 电子书ID
        file: 封面文件
        user: 当前用户

    Returns:
        封面URL
    """
    try:
        file_data = await file.read()
        url = storage_service.upload_ebook_cover(file_data, file.filename, ebook_id)
        
        if not url:
            raise HTTPException(status_code=500, detail="电子书封面上传失败")
        
        return {"url": url}
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"电子书封面上传异常: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")


@router.delete("/file")
async def delete_file(
    url: str,
    user: dict = Depends(get_current_user)
):
    """
    删除文件

    Args:
        url: 文件URL
        user: 当前用户

    Returns:
        删除结果
    """
    try:
        success = storage_service.delete_file(url)
        
        if not success:
            raise HTTPException(status_code=500, detail="文件删除失败")
        
        return {"success": True}
    
    except Exception as e:
        logger.error(f"文件删除异常: {e}")
        raise HTTPException(status_code=500, detail="服务器内部错误")