"""
管理员API路由 (Admin API Router)

提供管理员专用的系统管理功能。
"""

from fastapi import APIRouter, HTTPException, Depends, Query, status, Body
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from interfaces.api.auth_router import get_current_user
from infrastructure.database import fetch_sql, execute_sql, fetchrow_sql

router = APIRouter(prefix="/api/admin", tags=["管理员"])


async def require_admin(current_user: dict = Depends(get_current_user)):
    """要求管理员权限"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限"
        )
    return current_user


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    real_name: Optional[str]
    role: str
    is_active: bool
    created_at: str
    updated_at: str


class UserCreateRequest(BaseModel):
    username: str
    email: str
    password: str
    real_name: Optional[str] = None
    role: str = "student"
    is_active: bool = True


class UserUpdateRequest(BaseModel):
    email: Optional[str] = None
    real_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class StatisticsResponse(BaseModel):
    total_users: int
    total_students: int
    total_teachers: int
    total_courses: int
    total_books: int
    total_conversations: int


class CourseCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    instructor: str
    credits: int
    semester: Optional[str] = None
    category: Optional[str] = None


class CourseUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    instructor: Optional[str] = None
    credits: Optional[int] = None
    semester: Optional[str] = None
    category: Optional[str] = None


class BookCreateRequest(BaseModel):
    title: str
    author: str
    translator: Optional[str] = None
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    publish_date: Optional[str] = None
    cover_url: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None
    table_of_contents: Optional[str] = None


class BookUpdateRequest(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    translator: Optional[str] = None
    isbn: Optional[str] = None
    publisher: Optional[str] = None
    publish_date: Optional[str] = None
    cover_url: Optional[str] = None
    summary: Optional[str] = None
    category: Optional[str] = None
    table_of_contents: Optional[str] = None


# 用户管理接口
@router.get("/users", response_model=List[UserResponse])
async def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    role: Optional[str] = None,
    search: Optional[str] = None,
    current_user: dict = Depends(require_admin)
):
    """获取用户列表"""
    try:
        query = "SELECT * FROM users WHERE 1=1"
        params = []
        
        if role:
            query += " AND role = %s"
            params.append(role)
        
        if search:
            query += " AND (username LIKE %s OR email LIKE %s OR real_name LIKE %s)"
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern, search_pattern])
        
        query += " ORDER BY created_at DESC"
        
        offset = (page - 1) * page_size
        query += " LIMIT %s OFFSET %s"
        params.extend([page_size, offset])
        
        users = await fetch_sql(query, *params)
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/users", response_model=UserResponse)
async def create_user(
    request: UserCreateRequest,
    current_user: dict = Depends(require_admin)
):
    """创建新用户"""
    try:
        existing_user = await fetchrow_sql(
            "SELECT id FROM users WHERE username = %s OR email = %s",
            request.username, request.email
        )
        
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名或邮箱已存在")
        
        from domain.user.service import hash_password
        hashed_password = hash_password(request.password)
        
        user_id = await execute_sql(
            """
            INSERT INTO users (username, email, password_hash, real_name, role, is_active, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            request.username,
            request.email,
            hashed_password,
            request.real_name,
            request.role,
            request.is_active,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        )
        
        new_user = await fetchrow_sql("SELECT * FROM users WHERE id = %s", user_id)
        return new_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    request: UserUpdateRequest,
    current_user: dict = Depends(require_admin)
):
    """更新用户信息"""
    try:
        user = await fetchrow_sql("SELECT * FROM users WHERE id = %s", user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        update_fields = []
        params = []
        
        if request.email is not None:
            update_fields.append("email = %s")
            params.append(request.email)
        
        if request.real_name is not None:
            update_fields.append("real_name = %s")
            params.append(request.real_name)
        
        if request.role is not None:
            update_fields.append("role = %s")
            params.append(request.role)
        
        if request.is_active is not None:
            update_fields.append("is_active = %s")
            params.append(request.is_active)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="没有提供需要更新的字段")
        
        params.append(user_id)
        
        query = "UPDATE users SET " + ", ".join(update_fields) + ", updated_at = %s WHERE id = %s"
        params.append(datetime.now().isoformat())
        
        await execute_sql(query, *params)
        
        updated_user = await fetchrow_sql("SELECT * FROM users WHERE id = %s", user_id)
        return updated_user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: dict = Depends(require_admin)
):
    """删除用户"""
    try:
        user = await fetchrow_sql("SELECT * FROM users WHERE id = %s", user_id)
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        
        if user["role"] == "admin":
            admin_count = await fetchrow_sql("SELECT COUNT(*) as count FROM users WHERE role = 'admin'")
            if admin_count["count"] <= 1:
                raise HTTPException(status_code=400, detail="不能删除最后一个管理员")
        
        await execute_sql("DELETE FROM users WHERE id = %s", user_id)
        
        return {"success": True, "message": "用户删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 课程管理接口
@router.get("/courses")
async def get_courses(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    current_user: dict = Depends(require_admin)
):
    """获取课程列表"""
    try:
        query = "SELECT * FROM courses WHERE 1=1"
        params = []
        
        if search:
            query += " AND (course_name LIKE %s OR description LIKE %s OR teacher_name LIKE %s)"
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern, search_pattern])
        
        query += " ORDER BY created_at DESC"
        
        count_query = "SELECT COUNT(*) as total FROM courses WHERE 1=1"
        count_params = []
        if search:
            count_query += " AND (course_name LIKE %s OR description LIKE %s OR teacher_name LIKE %s)"
            count_params.extend([search_pattern, search_pattern, search_pattern])
        
        count_result = await fetchrow_sql(count_query, *count_params)
        total = count_result["total"] if count_result else 0
        
        offset = (page - 1) * page_size
        query += " LIMIT %s OFFSET %s"
        params.extend([page_size, offset])
        
        courses = await fetch_sql(query, *params)
        
        return {"data": courses, "total": total, "page": page, "page_size": page_size}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/courses")
async def create_course(
    request: CourseCreateRequest,
    current_user: dict = Depends(require_admin)
):
    """创建课程"""
    try:
        course_id = await execute_sql(
            """
            INSERT INTO courses (name, description, instructor, credits, semester, category, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            request.name,
            request.description,
            request.instructor,
            request.credits,
            request.semester,
            request.category,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        )
        
        new_course = await fetchrow_sql("SELECT * FROM courses WHERE id = %s", course_id)
        return {"success": True, "message": "课程创建成功", "course": new_course}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/courses/{course_id}")
async def update_course(
    course_id: str,
    request: CourseUpdateRequest,
    current_user: dict = Depends(require_admin)
):
    """更新课程"""
    try:
        course = await fetchrow_sql("SELECT * FROM courses WHERE id = %s", course_id)
        if not course:
            raise HTTPException(status_code=404, detail="课程不存在")
        
        update_fields = []
        params = []
        
        if request.name is not None:
            update_fields.append("name = %s")
            params.append(request.name)
        
        if request.description is not None:
            update_fields.append("description = %s")
            params.append(request.description)
        
        if request.instructor is not None:
            update_fields.append("instructor = %s")
            params.append(request.instructor)
        
        if request.credits is not None:
            update_fields.append("credits = %s")
            params.append(request.credits)
        
        if request.semester is not None:
            update_fields.append("semester = %s")
            params.append(request.semester)
        
        if request.category is not None:
            update_fields.append("category = %s")
            params.append(request.category)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="没有提供需要更新的字段")
        
        query = "UPDATE courses SET " + ", ".join(update_fields) + ", updated_at = %s WHERE id = %s"
        params.append(datetime.now().isoformat())
        params.append(course_id)
        
        await execute_sql(query, *params)
        
        updated_course = await fetchrow_sql("SELECT * FROM courses WHERE id = %s", course_id)
        return {"success": True, "message": "课程更新成功", "course": updated_course}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/courses/{course_id}")
async def delete_course(
    course_id: str,
    current_user: dict = Depends(require_admin)
):
    """删除课程"""
    try:
        course = await fetchrow_sql("SELECT * FROM courses WHERE id = %s", course_id)
        if not course:
            raise HTTPException(status_code=404, detail="课程不存在")
        
        await execute_sql("DELETE FROM courses WHERE id = %s", course_id)
        
        return {"success": True, "message": "课程删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 书籍管理接口
@router.get("/books")
async def get_books(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[str] = None,
    current_user: dict = Depends(require_admin)
):
    """获取书籍列表"""
    try:
        query = "SELECT * FROM books WHERE 1=1"
        params = []
        
        if search:
            query += " AND (title LIKE %s OR author LIKE %s OR summary LIKE %s)"
            search_pattern = f"%{search}%"
            params.extend([search_pattern, search_pattern, search_pattern])
        
        if category:
            query += " AND category = %s"
            params.append(category)
        
        query += " ORDER BY created_at DESC"
        
        count_query = "SELECT COUNT(*) as total FROM books WHERE 1=1"
        count_params = []
        if search:
            count_query += " AND (title LIKE %s OR author LIKE %s OR summary LIKE %s)"
            count_params.extend([search_pattern, search_pattern, search_pattern])
        if category:
            count_query += " AND category = %s"
            count_params.append(category)
        
        count_result = await fetchrow_sql(count_query, *count_params)
        total = count_result["total"] if count_result else 0
        
        offset = (page - 1) * page_size
        query += " LIMIT %s OFFSET %s"
        params.extend([page_size, offset])
        
        books = await fetch_sql(query, *params)
        
        return {"data": books, "total": total, "page": page, "page_size": page_size}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/books/{book_id}")
async def update_book(
    book_id: str,
    request: BookUpdateRequest,
    current_user: dict = Depends(require_admin)
):
    """更新书籍"""
    try:
        book = await fetchrow_sql("SELECT * FROM books WHERE id = %s", book_id)
        if not book:
            raise HTTPException(status_code=404, detail="书籍不存在")
        
        update_fields = []
        params = []
        
        if request.title is not None:
            update_fields.append("title = %s")
            params.append(request.title)
        
        if request.author is not None:
            update_fields.append("author = %s")
            params.append(request.author)
        
        if request.translator is not None:
            update_fields.append("translator = %s")
            params.append(request.translator)
        
        if request.isbn is not None:
            update_fields.append("isbn = %s")
            params.append(request.isbn)
        
        if request.publisher is not None:
            update_fields.append("publisher = %s")
            params.append(request.publisher)
        
        if request.publish_date is not None:
            update_fields.append("publish_date = %s")
            params.append(request.publish_date)
        
        if request.cover_url is not None:
            update_fields.append("cover = %s")
            params.append(request.cover_url)
        
        if request.summary is not None:
            update_fields.append("summary = %s")
            params.append(request.summary)
        
        if request.category is not None:
            update_fields.append("category = %s")
            params.append(request.category)
        
        if request.table_of_contents is not None:
            update_fields.append("table_of_contents = %s")
            params.append(request.table_of_contents)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="没有提供需要更新的字段")
        
        query = "UPDATE books SET " + ", ".join(update_fields) + ", updated_at = %s WHERE id = %s"
        params.append(datetime.now().isoformat())
        params.append(book_id)
        
        await execute_sql(query, *params)
        
        updated_book = await fetchrow_sql("SELECT * FROM books WHERE id = %s", book_id)
        return {"success": True, "message": "书籍更新成功", "book": updated_book}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/books/{book_id}")
async def delete_book(
    book_id: str,
    current_user: dict = Depends(require_admin)
):
    """删除书籍"""
    try:
        book = await fetchrow_sql("SELECT * FROM books WHERE id = %s", book_id)
        if not book:
            raise HTTPException(status_code=404, detail="书籍不存在")
        
        await execute_sql("DELETE FROM books WHERE id = %s", book_id)
        
        return {"success": True, "message": "书籍删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 系统统计接口
@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(
    current_user: dict = Depends(require_admin)
):
    """获取系统统计数据"""
    try:
        total_users = await fetchrow_sql("SELECT COUNT(*) as count FROM users")
        total_students = await fetchrow_sql("SELECT COUNT(*) as count FROM users WHERE role = 'student'")
        total_teachers = await fetchrow_sql("SELECT COUNT(*) as count FROM users WHERE role = 'teacher'")
        total_courses = await fetchrow_sql("SELECT COUNT(*) as count FROM courses")
        total_books = await fetchrow_sql("SELECT COUNT(*) as count FROM books")
        total_conversations = await fetchrow_sql("SELECT COUNT(*) as count FROM conversations")
        
        return {
            "total_users": total_users["count"] if total_users else 0,
            "total_students": total_students["count"] if total_students else 0,
            "total_teachers": total_teachers["count"] if total_teachers else 0,
            "total_courses": total_courses["count"] if total_courses else 0,
            "total_books": total_books["count"] if total_books else 0,
            "total_conversations": total_conversations["count"] if total_conversations else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
