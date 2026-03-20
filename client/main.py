import argparse
import asyncio
import os
import time

from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()


DEFAULT_MODEL = "ai-sage/GigaChat3-10B-A1.8B"
DEFAULT_TEMPERATURE = 0.1


BASE_PROMPT = """
Ты дизайнер одежды для животных
"""


TASK = """
Придумай три вида зимней одежды для котов
"""


def init_model(model=DEFAULT_MODEL, temperature=DEFAULT_TEMPERATURE):
    api_key = os.environ.get("API_KEY")
    url = os.environ.get("BASE_URL")
    llm = ChatOpenAI(
        api_key=api_key,
        base_url=url,
        model=model,
        temperature=temperature,
    )
    return llm


async def main():
    print("temperature: 0")
    print("prompt:", BASE_PROMPT)
    print("query:", TASK)
    llm = init_model(temperature=0)
    response = await run(llm, BASE_PROMPT, TASK)
    time.sleep(10)
    print("\n" * 10)

    print("temperature: 0.05")
    print("prompt:", BASE_PROMPT)
    print("query:", TASK)
    llm = init_model(temperature=0.5)
    response = await run(llm, BASE_PROMPT, TASK)
    time.sleep(10)
    print("\n" * 10)

    print("temperature: 1")
    print("prompt:", BASE_PROMPT)
    print("query:", TASK)
    llm = init_model(temperature=1)
    response = await run(llm, BASE_PROMPT, TASK)
    time.sleep(10)
    print("\n" * 10)


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
