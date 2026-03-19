import argparse
import asyncio
import os
import time

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()


BASE_PROMPT = """
Ты ассистент для обучения программированию
"""

STEP_BY_STEP_PROMPT = (
    BASE_PROMPT
    + """
Нужно решить задачу пошагово.
"""
)

EXPERT_PROMPT = """
1. Составь пошаговый алгоритм решения задачи
2. Составь решение на основе полученного алгоритма
3. Проанализируй полученный код на проблемы с производительностью
4. Исправь код на основе полученных замечаний
"""


TASK = """
Дана шахматная доска 5 на 5
Нужно обойти всю шахматную доску, поситив каждую клетку только один раз.
Нужно посчитать суммарное количество всех маршрутов коня из каждой клетки шахматной доски.
"""


GENERATE_PROMPT = (
    TASK
    + """
Составь план, в котором будет постановка задачи и пошаговое описание алгоритма на естественном языке.
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

    print("решение без подсказок")
    print("query:", TASK)
    response = await run(llm, BASE_PROMPT, TASK)
    time.sleep(10)
    print("\n" * 10)

    print("пошаговое решение")
    print("prompt:", STEP_BY_STEP_PROMPT)
    print("query:", TASK)
    response = await run(llm, STEP_BY_STEP_PROMPT, TASK)
    time.sleep(10)
    print("\n" * 10)

    print("решение с генерацией промпта")
    print("prompt:", BASE_PROMPT)
    print("query:", GENERATE_PROMPT)
    generated_prompt = await run(llm, BASE_PROMPT, GENERATE_PROMPT)
    print("generated_prompt:", generated_prompt)
    response = await run(llm, generated_prompt, TASK)
    time.sleep(10)
    print("\n" * 10)

    print("решение от совета экспертов")
    print("prompt:", EXPERT_PROMPT)
    print("query:", TASK)
    response = await run(llm, EXPERT_PROMPT, TASK)


async def run(llm, prompt, query):
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
            ("human", "{user_input}"),
        ]
    )

    chain = prompt_template | llm

    response = ""
    print("response:")
    stream = chain.astream({"user_input": query})
    async for chunk in stream:
        print(chunk.content, end="", flush=True)
        response += chunk.content
    return response


if __name__ == "__main__":
    asyncio.run(main())
