import os
import json
import asyncio

from dataclasses import dataclass

from openai import AsyncOpenAI

from dotenv import load_dotenv
from agents import Agent
from agents import Runner
from agents import OpenAIChatCompletionsModel
from agents import set_tracing_disabled
from agents import function_tool

from agents import GuardrailFunctionOutput
from agents import InputGuardrailTripwireTriggered
from agents import TResponseInputItem
from agents import input_guardrail
from agents import RunContextWrapper

load_dotenv()

llm_base_url= os.getenv("BASE_URL")
llm_api_key= os.getenv("API_KEY")
llm_model_name= os.getenv("MODEL_NAME")

if not llm_api_key or not llm_model_name or not llm_base_url:
    raise ValueError("You need to set environment variables BASE_URL, API_KEY and MODEL_NAME")

client= AsyncOpenAI(
    api_key=llm_api_key,
    base_url=llm_base_url,
)

structured_model=OpenAIChatCompletionsModel(
    model=llm_model_name,
    openai_client=client
)

@dataclass
class user_info:
    name: str
    subscription:str

@input_guardrail
async def guardrail(ctx:RunContextWrapper[user_info],
                    agent: Agent,
                    input:str|list[TResponseInputItem]):
    print("====================================Guardrail Running=======================================================")
    print("Name:",ctx.context.name)
    print("Subscription:",ctx.context.subscription)
    print("Input:",input)

    user_input=str(input).lower()
    bad_words=["hack","attack","virus"]

    for word in bad_words:
        if word in user_input:
            return GuardrailFunctionOutput(
                output_info=f"The {word} is against our concerns",
                tripwire_triggered=True,
            )

    return GuardrailFunctionOutput(
        output_info="The word is ok",
        tripwire_triggered=False,
        )

agent=Agent(
    name="Guardrail Agent",
    instructions="You are a safety agent",
    input_guardrails=[guardrail],
    model=structured_model
)

async def main():
    user=user_info(
        name="Nihima",
        subscription="premium",
    )

    print("\n================ SAFE INPUT TEST ================\n")

    try:
        result = await Runner.run(
            starting_agent=agent,
            context=user,
            input="Teach me python")

        print(result.final_output)

    except InputGuardrailTripwireTriggered as e:
        print("Guardrail block the request")
        print(e)

    print("\n================ UNSAFE INPUT TEST ================\n")
    try:
        response = await Runner.run(
            starting_agent=agent,
            input="attack this world",
            context=user
        )
        print(response.final_output)

    except InputGuardrailTripwireTriggered as e:
        print("Guardrail block the request")
        print(e)

if __name__ == "__main__":
    asyncio.run(main())


