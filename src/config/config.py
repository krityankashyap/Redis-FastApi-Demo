import os
from dotenv import load_dotenv
from fastapi import Request
from redis.asyncio import Redis, ConnectionPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

load_dotenv()

# configuration URLs

Database_URL= os.getenv("DATABASE_URL")

Redis_URL = os.getenv("REDIS_URL")

# Mysql engine and session
engine= create_async_engine(Database_URL, pool_pre_ping=True, echo=True) 
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


# Redis connection pool
redis_pool = ConnectionPool.from_url(Redis_URL, decode_responses=True)

# Dependencies
async def get_db():
  async with AsyncSessionLocal() as session:
    yield session

async def get_redis(request: Request) -> Redis:
    return request.app.state.redis
  




