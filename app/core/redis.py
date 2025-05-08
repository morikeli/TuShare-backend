from app.core.config import Config
import redis.asyncio as aioredis


JTI_EXPIRY =  Config.JTI_EXPIRY
token_blacklist = aioredis.StrictRedis(
    host=Config.REDIS_HOST,
    port=Config.REDIS_PORT,
    password=Config.REDIS_PASSWORD,
    db=0,
    decode_responses=True,
)


async def add_token_to_blacklist(token_jti: str) -> None:
    await token_blacklist.set(
        name=token_jti,
        value="",
        ex=JTI_EXPIRY
    )

async def token_in_blacklist(token_jti: str) -> bool:
    token = await token_blacklist.get(token_jti)

    return token is not None   # return True if token is in blacklist else False
