"""
pytest 配置文件

启用异步测试支持（pytest-asyncio auto mode）
"""

import pytest


def pytest_configure(config):
    """配置 pytest-asyncio 为 auto 模式"""
    config.option.asyncio_mode = "auto"
    config.addinivalue_line("markers", "asyncio: mark test as async")
