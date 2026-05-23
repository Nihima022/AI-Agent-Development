import os
import json
import asyncio

from altair import Theta
from dotenv import load_dotenv
from agents import Agent
from agents import Runner
from agents import OpenAIChatCompletionsModel
from agents import set_tracing_disabled
from agents import function_tool

from agents import GuardrailFunctionOutput
from agents import InputGuardrailTripwireTriggered
from agents import RunContextWrapper
from agents import TResponseInputItem
from agents import input_guardrail

from dataclasses import dataclass

from openai import AsyncOpenAI

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
class MathHomeWorkOutput:
    is_math_homework : bool
    reasoning: str

guardrail_agent=Agent(
    name="Guardrail Agent",
    instructions="Check if the user is asking you to do their math homework.",
    output_type=MathHomeWorkOutput,
    model=structured_model
)

@input_guardrail
async def guardrail(
        ctx:RunContextWrapper[None],
        agent:Agent,
        input:str | list[TResponseInputItem]):

    response=await Runner.run(
        starting_agent=guardrail_agent,
        input=input,
        context=ctx.context)

    final_output=response.final_output

    print(final_output)

    print("Guardrail is working")
    print("Is_Math_HomeWork:", final_output.is_math_homework)
    print("Reasoning:", final_output.reasoning)

    return GuardrailFunctionOutput(
        output_info="Guardrail Function Output",
        tripwire_triggered=response.final_output.is_math_homework
    )

agent=Agent(
    name="Customer support agent",
    instructions="You are a customer support agent. You help customers with their questions.",
    input_guardrails=[guardrail],
    model=structured_model
)

query_text=["Hello, can you help me solve for x: 2x + 3 = 11?",
            "hello,can you tell me the capital of bangladesh"]

async def main():
    for query in query_text:
        print(f"QUERY:{query}")
        print("="*500)

        try:
            result = await Runner.run(agent, query)
            print("The final output is:",result.final_output)

        except InputGuardrailTripwireTriggered as e:
            print("Guardrail is triggered")
            print(e)


set_tracing_disabled(True)

if __name__=="__main__":
    asyncio.run(main())









