import argparse
import asyncio
import os
import time

from dotenv import load_dotenv

from langchain_gigachat.chat_models import GigaChat
from langchain_core.prompts import ChatPromptTemplate


load_dotenv()


DEFAULT_MODEL = "ai-sage/GigaChat3-10B-A1.8B"
DEFAULT_TEMPERATURE = 0.1


BASE_PROMPT = """
Ты помощник по решению логических задач.
Ты должен выдавать пошаговое решение задачи.
"""


TASK = """
Крестьянину нужно перевезти через реку волка, козу и капусту. В лодке, кроме него, помещается только один объект. Если оставить волка с козой, он съест козу, если оставить козу и капусту, коза съест капусту, когда крестьянин находится на берегу, никто никого не ест.
"""


def init_model(model=DEFAULT_MODEL, temperature=DEFAULT_TEMPERATURE):
    api_key = os.environ.get("API_KEY")
    url = os.environ.get("BASE_URL")

    llm = GigaChat(
        credentials=api_key,
        base_url=url,
        # model=model,
        scope="GIGACHAT_API_PERS",
        temperature=temperature,
        verify_ssl_certs=False,
    )

    return llm


async def main():
    models = [
        "Gigachat-2-Lite",
        "Gigachat-2-Pro",
        "Gigachat-2-Max",
    ]

    input_prices = {
        "Gigachat-2-Lite": 1_300 / 20_000_000,
        "Gigachat-2-Pro": 1_500 / 3_000_000,
        "Gigachat-2-Max": 1_950 / 3_000_000,
    }

    output_prices = {
        "Gigachat-2-Lite": 1_300 / 20_000_000,
        "Gigachat-2-Pro": 1_500 / 3_000_000,
        "Gigachat-2-Max": 1_950 / 3_000_000,
    }

    for model in models:
        print("model:", model)
        print("prompt:", BASE_PROMPT)
        print("query:", TASK)
        llm = init_model(model=model, temperature=0.1)

        start = time.perf_counter_ns()
        response = await run(llm, BASE_PROMPT, TASK)
        end = time.perf_counter_ns()
        elapsed = end - start

        print("resonse:", response.content)
        print("\n")
        md = response.usage_metadata
        print("Elapsed time:", elapsed / 1000000000.0)

        input_tokens = md.get("input_tokens")
        output_tokens = md.get("output_tokens")
        total_tokens = md.get("total_tokens")

        print("input tokens:", input_tokens)
        print("output tokens:", output_tokens)
        print("total tokens:", total_tokens)

        input_price = input_prices[model] * input_tokens
        output_price = output_prices[model] * output_tokens
        total_price = input_price + output_price

        print("input price:", input_price)
        print("output price:", output_price)
        print("total price:", total_price)

        time.sleep(10)
        print("*" * 50)


async def run(llm, prompt, query):
    prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
            ("human", "{user_input}"),
        ]
    )

    chain = prompt_template | llm

    response = await chain.ainvoke({"user_input": query})
    return response


if __name__ == "__main__":
    asyncio.run(main())
