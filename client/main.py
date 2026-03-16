import asyncio
import os

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI

load_dotenv()


async def main():
    api_key = os.environ.get("API_KEY")
    url = os.environ.get("BASE_URL")
    llm = ChatOpenAI(
        api_key=api_key,
        base_url=url,
        model="ai-sage/GigaChat3-10B-A1.8B",
        temperature=0.1,
        max_tokens=1000,
    )

    await run(llm)


async def run(llm):
    response = await llm.ainvoke("Hello, world!")
    print(response.content)


if __name__ == "__main__":
    asyncio.run(main())
