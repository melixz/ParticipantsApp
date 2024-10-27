import httpx
from typing import Optional, Tuple


async def get_coordinates_from_city(city: str) -> Optional[Tuple[float, float, str]]:
    """Получение координат и названия города по названию с использованием Nominatim API."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": city,
        "format": "json",
        "limit": 1,
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        if response.status_code == 200 and response.json():
            data = response.json()[0]
            latitude = float(data["lat"])
            longitude = float(data["lon"])
            display_name = data.get(
                "display_name", city
            )  # Название города из API или указанное значение
            return latitude, longitude, display_name
    return None
