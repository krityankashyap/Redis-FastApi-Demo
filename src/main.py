import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

# Import connections and dependencies from your config module
from config import engine, redis_pool, get_db, get_redis

@asynccontextmanager
async def lifespan(app: FastAPI):
  # Attach redis client to app state on startup
  app.state.redis= Redis(connection_pool= redis_pool)
  yield 
  
  # Gracefully close the redis connection on shutdown
  await app.state.redis.close()
  await app.state.redis.dispose()

app= FastAPI(lifespan=lifespan)


@app.get("/users/{user_id}")
async def get_user(
  user_id: int,
  db: AsyncSession= Depends(get_db),
  redis: Redis= Depends(get_redis)
):
  cache_key= f"user:{user_id}"

  # 1. check if user data is in Redis cache
  cached_user= await redis.get(cache_key)
  if cached_user:
    return json.loads(cached_user)
  
  # 2. Cache Miss -> Query MySQL
    # result = await db.execute(select(User).where(User.id == user_id))
    # user = result.scalar_one_or_none()
  user = {"id": user_id, "name": "MySQL User", "role": "developer"}
    
  if not user:
      raise HTTPException(status_code=404, detail="User not found")
        
  # 3. Write to Redis
  await redis.setex(cache_key, 300, json.dumps(user))
    
  return user