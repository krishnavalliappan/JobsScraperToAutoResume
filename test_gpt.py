# import asyncio
# from typing import Optional
# from weakref import proxy
# from pydantic import BaseModel
# from g4f.client import AsyncClient
# from langchain.llms.base import LLM
# from Utilities.proxies import ProxyRotator

# proxy_rotator = ProxyRotator()

# class WeatherLLM(LLM):
#     @property
#     def _llm_type(self) -> str:
#         return "custom"

#     async def _call(self, prompt: str) -> str:
#         try:
#             proxy = proxy_rotator.get_proxy()["http"]
#             client = AsyncClient(proxies=proxy)
#             print(f"Using proxy: {client.get_proxy()}")
#             response = await client.chat.completions.create(
#                     model="gpt-3.5-turbo",
#                     messages=[{"role": "user", "content": prompt}],
#                     timeout=10
#                 )
#             return response.choices[0].message.content
#         except Exception as e:
#             print(f"Error with proxy {e}")
#             proxy_rotator.remove_current_proxy()
#             if not proxy_rotator.proxies:
#                 print("All proxies exhausted")
#                 raise

# class WeatherOutput(BaseModel):
#     weather: str

# class WeatherAnalyzer:
#     def __init__(self):
#         self.llm = WeatherLLM()

#     async def get_weather(self) -> Optional[WeatherOutput]:
#         prompt = "What's the weather today?"
#         try:
#             result = await self.llm._call(prompt)
#             return WeatherOutput(weather=result)
#         except Exception as e:
#             print(f"Error in get_weather: {e}")
#             return None

# async def main():
#     analyzer = WeatherAnalyzer()
#     weather = await analyzer.get_weather()
#     if weather:
#         print(f"Today's weather: {weather.weather}")
#     else:
#         print("Unable to get weather information.")

# if __name__ == "__main__":
#     asyncio.run(main())

import asyncio
import g4f
from g4f.client import Client
from g4f.cookies import set_cookies_dir, read_cookie_files
# from g4f.Provider import 
import os

from Utilities import proxies

g4f.debug.logging = True
cookies_dir = os.path.join(os.path.dirname(__file__), "har_and_cookies")
set_cookies_dir(cookies_dir)
read_cookie_files(cookies_dir)

def main():
    client = Client()

    task1 = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Say this is a test"}],
    )

    print(task1.choices[0].message.content)

if __name__ == "__main__":
    main()