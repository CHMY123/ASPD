"""
数据库初始化模块单元测试

测试DatabaseInitializer的功能。
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from infrastructure.database_init import (
    DatabaseInitializer,
    TableSchema,
    InitOrder,
    initialize_database,
    verify_database
)


class TestDatabaseInitializer:
    """测试DatabaseInitializer类"""

    @pytest.fixture
    def initializer(self):
        """创建初始化器实例"""
        return DatabaseInitializer()

    def test_initializer_initial_state(self, initializer):
        """测试初始化器初始状态"""
        assert initializer._initialized_tables == set()
        assert initializer._errors == []

    def test_get_all_schemas_returns_all_tables(self, initializer):
        """测试获取所有表结构"""
        schemas = initializer._get_all_schemas()
        
        assert InitOrder.USERS in schemas
        assert InitOrder.CONVERSATIONS in schemas
        assert InitOrder.MESSAGES in schemas
        assert InitOrder.LEARNING_RECORDS in schemas
        assert InitOrder.KNOWLEDGE_COLLECTIONS in schemas
        
        assert schemas[InitOrder.USERS]["name"] == "users"
        assert schemas[InitOrder.CONVERSATIONS]["name"] == "conversations"
        assert schemas[InitOrder.MESSAGES]["name"] == "messages"

    def test_table_schemas_have_required_fields(self, initializer):
        """测试表结构包含必需字段"""
        schemas = initializer._get_all_schemas()
        
        for order, schema in schemas.items():
            assert "name" in schema
            assert "create_sql" in schema
            assert "indexes" in schema
            assert isinstance(schema["indexes"], list)

    def test_users_schema_has_correct_columns(self, initializer):
        """测试users表结构定义"""
        schemas = initializer._get_all_schemas()
        users_schema = schemas[InitOrder.USERS]["create_sql"]
        
        assert "id" in users_schema
        assert "username" in users_schema
        assert "email" in users_schema
        assert "password_hash" in users_schema
        assert "role" in users_schema
        assert "status" in users_schema

    def test_conversations_schema_has_correct_columns(self, initializer):
        """测试conversations表结构定义"""
        schemas = initializer._get_all_schemas()
        conv_schema = schemas[InitOrder.CONVERSATIONS]["create_sql"]
        
        assert "id" in conv_schema
        assert "user_id" in conv_schema
        assert "title" in conv_schema
        assert "message_count" in conv_schema

    def test_messages_schema_has_correct_columns(self, initializer):
        """测试messages表结构定义"""
        schemas = initializer._get_all_schemas()
        msg_schema = schemas[InitOrder.MESSAGES]["create_sql"]
        
        assert "id" in msg_schema
        assert "conversation_id" in msg_schema
        assert "role" in msg_schema
        assert "content" in msg_schema
        assert "references" in msg_schema.lower().replace("`", "")

    def test_learning_records_schema_has_correct_columns(self, initializer):
        """测试learning_records表结构定义"""
        schemas = initializer._get_all_schemas()
        records_schema = schemas[InitOrder.LEARNING_RECORDS]["create_sql"]
        
        assert "id" in records_schema
        assert "user_id" in records_schema
        assert "knowledge_point_id" in records_schema
        assert "action" in records_schema
        assert "duration" in records_schema

    def test_knowledge_collections_schema_has_correct_columns(self, initializer):
        """测试knowledge_collections表结构定义"""
        schemas = initializer._get_all_schemas()
        coll_schema = schemas[InitOrder.KNOWLEDGE_COLLECTIONS]["create_sql"]
        
        assert "id" in coll_schema
        assert "user_id" in coll_schema
        assert "knowledge_point_id" in coll_schema
        assert "folder" in coll_schema
        assert "note" in coll_schema


class TestDatabaseInitializerAsync:
    """测试DatabaseInitializer异步方法"""

    @pytest.fixture
    def initializer(self):
        return DatabaseInitializer()

    @pytest.mark.asyncio
    async def test_initialize_all_handles_exceptions(self, initializer):
        """测试初始化异常处理"""
        with patch("infrastructure.database_init.get_pool") as mock_pool:
            mock_conn = AsyncMock()
            mock_cursor = AsyncMock()
            mock_cursor.fetchone.return_value = {"version": "8.0.11"}
            mock_cursor.fetchone.side_effect = Exception("Database error")
            mock_conn.cursor.return_value.__aenter__.return_value = mock_cursor
            mock_pool.return_value.acquire.return_value.__aenter__.return_value = mock_conn
            
            result = await initializer.initialize_all()
            
            assert result["success"] == False
            assert len(result["errors"]) > 0

    @pytest.mark.asyncio
    async def test_verify_tables_returns_dict(self, initializer):
        """测试表验证返回字典"""
        with patch("infrastructure.database_init.fetchrow_sql") as mock_fetch:
            mock_fetch.return_value = {"count": 1}
            
            result = await initializer.verify_tables()
            
            assert isinstance(result, dict)
            assert "users" in result


class TestTableSchema:
    """测试TableSchema数据类"""

    def test_table_schema_creation(self):
        """测试TableSchema创建"""
        schema = TableSchema(
            name="test_table",
            create_sql="CREATE TABLE test_table (id INT);",
            indexes=[{"name": "idx_test", "sql": "CREATE INDEX idx_test ON test_table (id);"}],
            seed_data=[(1, "test")]
        )
        
        assert schema.name == "test_table"
        assert schema.create_sql.startswith("CREATE TABLE")
        assert len(schema.indexes) == 1
        assert len(schema.seed_data) == 1

    def test_table_schema_optional_seed_data(self):
        """测试TableSchema可选种子数据"""
        schema = TableSchema(
            name="test_table",
            create_sql="CREATE TABLE test_table (id INT);",
            indexes=[]
        )
        
        assert schema.seed_data is None


class TestInitOrder:
    """测试InitOrder枚举"""

    def test_init_order_values(self):
        """测试初始化顺序值"""
        assert InitOrder.USERS.value == 1
        assert InitOrder.CONVERSATIONS.value == 2
        assert InitOrder.MESSAGES.value == 3
        assert InitOrder.LEARNING_RECORDS.value == 4
        assert InitOrder.KNOWLEDGE_COLLECTIONS.value == 5

    def test_init_order_sorting(self):
        """测试初始化顺序排序"""
        orders = [InitOrder.KNOWLEDGE_COLLECTIONS, InitOrder.USERS, InitOrder.MESSAGES]
        sorted_orders = sorted(orders, key=lambda x: x.value)
        
        assert sorted_orders[0] == InitOrder.USERS
        assert sorted_orders[1] == InitOrder.MESSAGES
        assert sorted_orders[2] == InitOrder.KNOWLEDGE_COLLECTIONS


class TestDatabaseInitFunctions:
    """测试数据库初始化函数"""

    @pytest.mark.asyncio
    async def test_initialize_database_returns_dict(self):
        """测试initialize_database返回字典"""
        with patch("infrastructure.database_init.get_initializer") as mock_get:
            mock_initializer = Mock()
            mock_initializer.initialize_all = AsyncMock(return_value={
                "success": True,
                "tables_created": ["users"],
                "indexes_created": ["idx_users_username"],
                "errors": []
            })
            mock_get.return_value = mock_initializer
            
            result = await initialize_database()
            
            assert isinstance(result, dict)
            assert "success" in result
            assert "tables_created" in result

    @pytest.mark.asyncio
    async def test_verify_database_returns_dict(self):
        """测试verify_database返回字典"""
        with patch("infrastructure.database_init.get_initializer") as mock_get:
            mock_initializer = Mock()
            mock_initializer.verify_tables = AsyncMock(return_value={
                "users": True,
                "conversations": True
            })
            mock_get.return_value = mock_initializer
            
            result = await verify_database()
            
            assert isinstance(result, dict)
            assert "users" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
