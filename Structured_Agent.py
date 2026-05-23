# Import Libraries
import os
import json
# It converts python list, dict, string to text format so that Internet API can read it easily.
import asyncio
# instead of running task one by one and wait for another, it starts running all task at a time efficiently.
from agents import Agent
from agents import Runner
from agents import OpenAIChatCompletionsModel
from agents import set_tracing_disabled
# turn off internal tracking of agent step
from typing import List
# creates list of string or list of int orr list of float
from pydantic import Field
# each attribute like [city days interests] are field.
from pydantic import BaseModel
# parent model which automatically correct if any input type is error
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Set API Key to access LLM
load_dotenv()

llm_base_url = os.getenv("BASE_URL")
llm_model_name = os.getenv("MODEL_NAME")
llm_api_key = os.getenv("API_KEY")

if not llm_base_url:
    raise ValueError("You need to set BASE_URL environment variable")

if not llm_model_name:
    raise ValueError("You need to set MODEL_NAME environment variable")

if not llm_api_key:
    raise ValueError("You need to set API_KEY environment variable")

# Create Structured Model
client = AsyncOpenAI(
    base_url=llm_base_url,
    api_key=llm_api_key
)

structured_model = OpenAIChatCompletionsModel(
    model=llm_model_name,
    openai_client=client
)


# Create a class so that output can be generated in that format
class TravelPlanner(BaseModel):
    destination: str
    duration: int
    budget: float
    flight: str
    activities: List[str]
    notes: List[str]


# Create an agent
agent = Agent(
    name="Assistant",
    instructions=""" You are a comprehensive travel planning assistant that helps users plan their perfect trip.

    You can create personalized travel itineraries based on the user's interests and preferences.

    Always be helpful, informative, and enthusiastic about travel. Provide specific recommendations
    based on the user's interests and preferences.

    When creating travel plans, consider:
    - Local attractions and activities
    - Budget constraints
    - Travel duration
    - suitable flight name must choose""",
    model=structured_model,
    output_type=TravelPlanner
)


def main():
    queries = ["I want to go Coxs'Bazar . Can you plan a trip for me?"]

    for query in queries:
        print("\n" + "=" * 50)
        print(f"Query: {query}")

        result = Runner.run_sync(agent, query)
        print("\n Final Response:\n")

        response = result.final_output
        print(response)

        print("\nJSON FORMAT\n")
        json_format=response.model_dump_json()
        print(json_format)

        print("\nPython object Format\n")
        python_obj=json.loads(json_format)
        print(python_obj)

        print("\nJSON String Format\n")
        json_string=json.dumps(python_obj, indent=2)
        print(json_string)

        print("\n\n\n\n"+"-"*100)

        print(f"Travel Destination:{response.destination.upper()}")
        print(f"Duration:{response.duration} days")
        print(f"Budget:{response.budget} BDT")
        print(f"Flight Name:{response.flight}")
        print(f"Activity Name:")
        for i, activity in enumerate(response.activities,2):
            print(f" {i}. {activity}")
        print(f"Notes:{response.notes}")





set_tracing_disabled(True)

if __name__ == "__main__":
    main()
