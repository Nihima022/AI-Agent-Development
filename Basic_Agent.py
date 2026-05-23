#Import Libraries
import os
from dotenv import load_dotenv
from agents import Agent
from agents import Runner
from agents import OpenAIChatCompletionsModel
from agents import set_tracing_disabled
from openai import AsyncOpenAI

#Set API Key
load_dotenv()

base_url=os.getenv("BASE_URL")
api_key=os.getenv("API_KEY")
model_name=os.getenv("MODEL_NAME")

if not base_url:
    raise ValueError("BASE_URL is not found")

if not api_key:
    raise ValueError("API_KEY is not found")

if not model_name:
    raise ValueError("MODEL_NAME is not found")

#Structured model to communicate with LLM
client=AsyncOpenAI(
    base_url=base_url,
    api_key=api_key
)

structured_model=OpenAIChatCompletionsModel(
    model=model_name,
    openai_client= client
)

#Build an agent without tool
agent=Agent(
    name="Assistent",
    instructions= "You are a helpful agent to find anything. You should always maintain 6 line",
    model=structured_model
)

set_tracing_disabled(True)

def main():
    response=Runner.run_sync(agent, "Write a bad joke about python")
    print(response.final_output)

if __name__=="__main__":
    main()