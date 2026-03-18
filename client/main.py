import argparse
import asyncio
import os

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()


BASE_PROMPT = """
Ты ассистент для обучения программированию
"""

ADVANCED_PROMPT = (
    BASE_PROMPT
    + """
Ответ должен состоять из трёх предложений
Заверши ответ словом КОНЕЦ
"""
)


async def main():
    api_key = os.environ.get("API_KEY")
    url = os.environ.get("BASE_URL")
    llm = ChatOpenAI(
        api_key=api_key,
        base_url=url,
        model="ai-sage/GigaChat3-10B-A1.8B",
        temperature=0.1,
    )

    query = "расскажи о языке программирования Go"

    await run(llm, BASE_PROMPT, query)

    await run(llm, ADVANCED_PROMPT, query)


async def run(llm, prompt, query):
    print("-" * 80)
    print("prompt:", prompt)
    print("query:", query)

    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
            ("human", "{user_input}"),
        ]
    )

    chain = prompt_template | llm

    response = await chain.ainvoke({"user_input": query})
    print("response:", response.content)


if __name__ == "__main__":
    asyncio.run(main())
