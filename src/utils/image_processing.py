from PIL import Image
from io import BytesIO
import asyncio

WATERMARK_PATH = "src/utils/watermark.png"


async def add_watermark(avatar_content: BytesIO) -> BytesIO:
    """Асинхронное добавление водяного знака к изображению."""
    await asyncio.sleep(0)  # Помощь в освобождении текущего потока выполнения
    avatar = Image.open(avatar_content).convert("RGBA")
    watermark = Image.open(WATERMARK_PATH).convert("RGBA")

    # Изменение размера водяного знака под изображение
    watermark = watermark.resize((avatar.width // 4, avatar.height // 4))
    avatar.paste(
        watermark,
        (avatar.width - watermark.width, avatar.height - watermark.height),
        watermark,
    )

    result = BytesIO()
    avatar.save(result, format="PNG")
    result.seek(0)
    return result
