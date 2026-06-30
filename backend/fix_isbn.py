import asyncio
import sys
sys.path.insert(0, '.')

async def fix():
    from infrastructure.database import execute_sql
    count = await execute_sql("UPDATE books SET isbn = NULL WHERE isbn = %s", '')
    print(f'Updated {count} rows')

asyncio.run(fix())
