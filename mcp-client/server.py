import json
import httpx
import os
from dotenv import load_dotenv
from typing import Any
from mcp.server.fastmcp import FastMCP

# 初始化 MCP 服务器
mcp = FastMCP("WeatherServer")


# 加载 .env 文件，确保 API Key 受到保护
load_dotenv()

# OpenWeather API 配置
OPENWEATHER_API_BASE = "https://api.weatherapi.com/v1/current.json"
API_KEY = ""  # 请替换为你自己的 OpenWeather API Key
USER_AGENT = "weather-app/1.0"

async def fetch_weather(city: str) -> dict[str, Any] | None:
    """
    从 Weather API 获取天气信息。
    :param city: 城市名称（需使用英文，如 Beijing）
    :return: 天气数据字典；若出错返回包含 error 信息的字典
    """
    params = {
        "q": city,
        "key": os.getenv("WEATHER_API_KEY"),
        "lang": "zh"
    }
    headers = {"User-Agent": USER_AGENT,
               "accept": "application/json"
               }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(OPENWEATHER_API_BASE, params=params, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()  # 返回字典类型
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP 错误: {e.response.status_code}"}
        except Exception as e:
            return {"error": f"请求失败: {str(e)}"}

def format_weather(data: dict[str, Any] | str) -> str:
    """
    将天气数据格式化为易读文本。
    :param data: 天气数据（可以是字典或 JSON 字符串）
    :return: 格式化后的天气信息字符串
    """
    # 如果传入的是字符串，则先转换为字典
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception as e:
            return f"无法解析天气数据: {e}"

    # 如果数据中包含错误信息，直接返回错误提示
    if "error" in data:
        return f"⚠️ {data['error']}"

    # 提取数据时做容错处理
    location = data.get("location", {}) if isinstance(data, dict) else {}
    current = data.get("current", {}) if isinstance(data, dict) else {}

    city = location.get("name", "未知")
    country = location.get("country", "未知")
    temp_c = current.get("temp_c", "N/A")
    humidity = current.get("humidity", "N/A")
    wind_kph = current.get("wind_kph", "N/A")
    condition = current.get("condition", {}) if isinstance(current.get("condition", {}), dict) else {}
    description = condition.get("text", "未知")

    return (
        f"🌍 {city}, {country}\n"
        f"🌡 温度: {temp_c}°C\n"
        f"💧 湿度: {humidity}%\n"
        f"🌬 风速: {wind_kph} km/h\n"
        f"🌤 天气: {description}\n"
    )

@mcp.tool()
async def query_weather(city: str) -> str:
    """
    输入指定城市的英文名称，返回今日天气查询结果。
    :param city: 城市名称（需使用英文）
    :return: 格式化后的天气信息
    """
    data = await fetch_weather(city)
    return format_weather(data)

if __name__ == "__main__":
    # 以标准 I/O 方式运行 MCP 服务器
    mcp.run(transport='stdio')
