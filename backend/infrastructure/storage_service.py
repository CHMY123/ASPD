"""
缤纷云存储服务 (Storage Service)

提供基于S3协议的文件上传、下载和管理功能。
"""

import boto3
from botocore.exceptions import ClientError
from typing import Optional, Tuple
import uuid
import logging

from config import (
    S3_ACCESS_KEY_ID,
    S3_SECRET_ACCESS_KEY,
    S3_ENDPOINT_URL,
    S3_BUCKET_NAME,
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE
)

logger = logging.getLogger(__name__)


class StorageService:
    """
    缤纷云存储服务

    提供文件上传、下载、删除等操作。
    """

    def __init__(self):
        """初始化存储服务（延迟初始化）"""
        self._s3_client = None
        self.bucket_name = S3_BUCKET_NAME
        self._initialized = False

    def _ensure_initialized(self):
        """确保客户端已初始化（延迟初始化）"""
        if self._initialized:
            return
        
        try:
            self._s3_client = boto3.client(
                's3',
                aws_access_key_id=S3_ACCESS_KEY_ID,
                aws_secret_access_key=S3_SECRET_ACCESS_KEY,
                endpoint_url=S3_ENDPOINT_URL,
                region_name='ap-southeast-1'
            )
            self._ensure_bucket_exists()
            self._initialized = True
        except Exception as e:
            logger.warning(f"存储服务初始化失败: {e}")
            self._initialized = True  # 标记已尝试初始化，避免重复尝试

    def _ensure_bucket_exists(self):
        """确保存储桶存在"""
        if not self._s3_client:
            return
            
        try:
            self._s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                logger.info(f"存储桶 {self.bucket_name} 不存在，正在创建...")
                try:
                    self._s3_client.create_bucket(Bucket=self.bucket_name)
                    logger.info(f"存储桶 {self.bucket_name} 创建成功")
                except ClientError as create_error:
                    logger.warning(f"创建存储桶失败: {create_error}")
            else:
                logger.warning(f"检查存储桶失败: {e}")

    def _generate_file_key(self, original_filename: str, folder: str = 'uploads') -> str:
        """
        生成文件存储键

        Args:
            original_filename: 原始文件名
            folder: 存储文件夹

        Returns:
            文件存储键
        """
        ext = original_filename.split('.')[-1].lower() if '.' in original_filename else 'jpg'
        file_id = str(uuid.uuid4())
        return f"{folder}/{file_id}.{ext}"

    def _validate_file(self, filename: str, file_size: int) -> Tuple[bool, str]:
        """
        验证文件是否符合要求

        Args:
            filename: 文件名
            file_size: 文件大小（字节）

        Returns:
            (是否有效, 错误信息)
        """
        # 检查文件大小
        if file_size > MAX_FILE_SIZE:
            return False, f"文件大小超过限制（最大 {MAX_FILE_SIZE // 1024 // 1024}MB）"

        # 检查文件扩展名
        ext = filename.split('.')[-1].lower() if '.' in filename else ''
        if ext not in ALLOWED_EXTENSIONS:
            return False, f"不支持的文件格式，支持的格式: {', '.join(ALLOWED_EXTENSIONS)}"

        return True, ""

    def upload_file(self, file_data: bytes, filename: str, folder: str = 'uploads') -> Optional[str]:
        """
        上传文件到缤纷云存储

        Args:
            file_data: 文件二进制数据
            filename: 原始文件名
            folder: 存储文件夹

        Returns:
            文件访问URL，如果上传失败返回None
        """
        # 确保客户端已初始化
        self._ensure_initialized()
        
        if not self._s3_client:
            logger.error("存储服务未初始化，无法上传文件")
            return None
        
        # 验证文件
        is_valid, error_msg = self._validate_file(filename, len(file_data))
        if not is_valid:
            logger.error(f"文件验证失败: {error_msg}")
            raise ValueError(error_msg)

        # 生成存储键
        file_key = self._generate_file_key(filename, folder)

        try:
            # 上传文件
            self._s3_client.put_object(
                Bucket=self.bucket_name,
                Key=file_key,
                Body=file_data,
                ContentType=self._get_content_type(filename)
            )

            # 生成访问URL
            url = f"{S3_ENDPOINT_URL}/{self.bucket_name}/{file_key}"
            logger.info(f"文件上传成功: {url}")
            return url

        except ClientError as e:
            logger.error(f"文件上传失败: {e}")
            return None

    def upload_user_avatar(self, file_data: bytes, filename: str, user_id: str) -> Optional[str]:
        """
        上传用户头像

        Args:
            file_data: 文件二进制数据
            filename: 原始文件名
            user_id: 用户ID

        Returns:
            文件访问URL，如果上传失败返回None
        """
        folder = f"avatars/{user_id}"
        return self.upload_file(file_data, filename, folder)

    def upload_course_cover(self, file_data: bytes, filename: str, course_id: str) -> Optional[str]:
        """
        上传课程封面

        Args:
            file_data: 文件二进制数据
            filename: 原始文件名
            course_id: 课程ID

        Returns:
            文件访问URL，如果上传失败返回None
        """
        folder = f"courses/{course_id}"
        return self.upload_file(file_data, filename, folder)

    def upload_ebook_cover(self, file_data: bytes, filename: str, ebook_id: str) -> Optional[str]:
        """
        上传电子书封面

        Args:
            file_data: 文件二进制数据
            filename: 原始文件名
            ebook_id: 电子书ID

        Returns:
            文件访问URL，如果上传失败返回None
        """
        folder = f"ebooks/{ebook_id}"
        return self.upload_file(file_data, filename, folder)

    def delete_file(self, file_url: str) -> bool:
        """
        删除文件

        Args:
            file_url: 文件URL

        Returns:
            是否删除成功
        """
        # 确保客户端已初始化
        self._ensure_initialized()
        
        if not self._s3_client:
            logger.error("存储服务未初始化，无法删除文件")
            return False
            
        try:
            # 从URL中提取文件键
            if f"{S3_ENDPOINT_URL}/{self.bucket_name}/" in file_url:
                file_key = file_url.replace(f"{S3_ENDPOINT_URL}/{self.bucket_name}/", "")
            else:
                file_key = file_url

            self._s3_client.delete_object(Bucket=self.bucket_name, Key=file_key)
            logger.info(f"文件删除成功: {file_url}")
            return True
        except ClientError as e:
            logger.error(f"文件删除失败: {e}")
            return False

    def _get_content_type(self, filename: str) -> str:
        """
        获取文件的Content-Type

        Args:
            filename: 文件名

        Returns:
            Content-Type
        """
        ext = filename.split('.')[-1].lower() if '.' in filename else ''
        content_types = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'webp': 'image/webp'
        }
        return content_types.get(ext, 'application/octet-stream')

    def get_file_url(self, file_key: str) -> str:
        """
        根据文件键生成访问URL

        Args:
            file_key: 文件存储键

        Returns:
            文件访问URL
        """
        return f"{S3_ENDPOINT_URL}/{self.bucket_name}/{file_key}"


# 创建全局存储服务实例（延迟初始化）
def _get_storage_service():
    """延迟创建存储服务实例"""
    return StorageService()

class _LazyStorageService:
    """延迟初始化的存储服务包装器"""
    def __getattr__(self, name):
        # 使用object.__getattribute__避免触发__getattr__导致无限递归
        try:
            service = object.__getattribute__(self, '_service')
        except AttributeError:
            service = StorageService()
            object.__setattr__(self, '_service', service)
        return getattr(service, name)

storage_service = _LazyStorageService()