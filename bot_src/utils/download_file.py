import uuid
from aiogram.client.session import aiohttp
from aiogram.types import FSInputFile


async def download_file(url: str, suffix: str) -> FSInputFile | None:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    tmp_path = f"/tmp/{uuid.uuid4()}_{suffix}"
                    with open(tmp_path, "wb") as f:
                        f.write(await response.read())
                    return FSInputFile(tmp_path)
    except Exception:
        return None
