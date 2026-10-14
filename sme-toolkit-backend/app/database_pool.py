"""
Database connection pooling and read replica routing for production scale
"""

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import QueuePool
from sqlalchemy import select
from contextlib import asynccontextmanager
from typing import Optional, AsyncGenerator
import logging
import os

logger = logging.getLogger(__name__)

DATABASE_CONFIG = {
    "pool_size": int(os.getenv("DB_POOL_SIZE", "20")),
    "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "10")),
    "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
    "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "3600")),
    "pool_pre_ping": True,
    "echo_pool": False,
}

PRIMARY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://smeuser:password@localhost:5432/sme_toolkit"
)

REPLICA_DATABASE_URLS = [
    url.strip() 
    for url in os.getenv("REPLICA_DATABASE_URLS", "").split(",") 
    if url.strip()
]


def create_production_engine(database_url: str, is_replica: bool = False):
    return create_async_engine(
        database_url,
        poolclass=QueuePool,
        **DATABASE_CONFIG,
        connect_args={
            "server_settings": {
                "application_name": "sme-toolkit-api",
                "jit": "on" if not is_replica else "off",
            },
            "command_timeout": 60,
        }
    )


primary_engine = create_production_engine(PRIMARY_DATABASE_URL, is_replica=False)

replica_engines = [
    create_production_engine(url, is_replica=True) 
    for url in REPLICA_DATABASE_URLS
]

primary_session_maker = async_sessionmaker(
    primary_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

replica_session_makers = [
    async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    for engine in replica_engines
]


class ReadWriteRouter:
    """Route queries to primary or replica based on operation type"""
    
    _instance: Optional["ReadWriteRouter"] = None
    
    def __init__(self):
        self.replica_index = 0
    
    @classmethod
    def get_instance(cls) -> "ReadWriteRouter":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def get_replica_session_maker(self) -> async_sessionmaker:
        if not replica_session_makers:
            return primary_session_maker
        
        replica = replica_session_makers[self.replica_index]
        self.replica_index = (self.replica_index + 1) % len(replica_session_makers)
        return replica
    
    @asynccontextmanager
    async def get_read_session(self) -> AsyncGenerator[AsyncSession, None]:
        session_maker = self.get_replica_session_maker()
        async with session_maker() as session:
            try:
                yield session
            finally:
                await session.close()
    
    @asynccontextmanager
    async def get_write_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with primary_session_maker() as session:
            try:
                yield session
            finally:
                await session.close()


router = ReadWriteRouter.get_instance()


async def get_db() -> AsyncSession:
    """Default dependency - uses replica for reads, primary for writes"""
    async with router.get_write_session() as session:
        yield session


async def get_read_db() -> AsyncSession:
    """Read-only dependency - routes to replicas"""
    async with router.get_read_session() as session:
        yield session


async def get_write_db() -> AsyncSession:
    """Write-only dependency - always uses primary"""
    async with router.get_write_session() as session:
        yield session


async def health_check() -> dict:
    """Check database connection health"""
    result = {
        "primary": False,
        "replicas": [],
        "pool_stats": {}
    }
    
    try:
        async with primary_session_maker() as session:
            await session.execute(select(1))
        result["primary"] = True
    except Exception as e:
        logger.error(f"Primary database health check failed: {e}")
    
    for i, session_maker in enumerate(replica_session_makers):
        try:
            async with session_maker() as session:
                await session.execute(select(1))
            result["replicas"].append({"index": i, "healthy": True})
        except Exception as e:
            logger.error(f"Replica {i} health check failed: {e}")
            result["replicas"].append({"index": i, "healthy": False, "error": str(e)})
    
    pool = primary_engine.pool
    result["pool_stats"] = {
        "size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "invalid": pool.invalidatedcount(),
    }
    
    return result


async def close_connections():
    """Close all database connections"""
    await primary_engine.dispose()
    for engine in replica_engines:
        await engine.dispose()
    logger.info("All database connections closed")
