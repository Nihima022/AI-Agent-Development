#Import Libraries
import os
import json
import asyncio

from dotenv import load_dotenv
from agents import Agent
from agents import Runner
from agents import OpenAIChatCompletionsModel
from agents import set_tracing_disabled
from openai import AsyncOpenAI
from pydantic import BaseModel
from pydantic import Field
from typing import List

from pywin.tools.TraceCollector import outputWindow

#Set API Key
load_dotenv()

llm_base_url=os.getenv("BASE_URL")
llm_model_name=os.getenv("MODEL_NAME")
llm_api_key= os.getenv("API_KEY")

if not llm_base_url:
    raise ValueError("No URL Provided")

if not llm_model_name:
    raise ValueError("No model found")

if not llm_api_key:
    raise ValueError("No API Key Found")

#Create a Structured Model
client=AsyncOpenAI(
    base_url=llm_base_url,
    api_key=llm_api_key
)

structured_model= OpenAIChatCompletionsModel(
    model=llm_model_name,
    openai_client= client
)

#disabled step by step tracing
set_tracing_disabled(True)

#Create a basemodel Class for agent
class TravelAgent(BaseModel):
    place: str
    Duration: int
    Flight: str
    Transport: str
    Budget: float
    activities: List[str]= Field(description="List of recommended activities")
    note: List[str]= Field(description="List of recommended notes")

#Build Agent
travel_planning_agent=Agent(
    name="Travel_Planning_Agent",
    instructions="""
     You are a comprehensive travel planning assistant that helps users plan their perfect trip.

    You can create personalized travel itineraries based on the user's interests and preferences.

    Always be helpful, informative, and enthusiastic about travel. Provide specific recommendations
    based on the user's interests and preferences.

    When creating travel plans, consider:
    - Local attractions and activities
    - Budget constraints
    - Travel duration
    - suitable flight name or transport must choose
    """,
    model=structured_model,
    output_type= TravelAgent
)

#Run The Agent
async def main():
    queries=["Plan a trip for me at Canada"]

    for query in queries:
        print("\n" + "="*100)
        print(f"Query: {query}")
        print("="*100)

        result= await Runner.run(travel_planning_agent,query)

        print("\n")
        print("Your Trip Planning Result:")
        print("-"*500)
        response=result.final_output
        print(response)
        print("-" * 500)

        json_format=response.model_dump_json()
        print(json_format)
        print("-" * 500)

        python_dict=json.loads(json_format)
        print(python_dict)
        print("-" * 500)

        json_string=json.dumps(python_dict, indent=2)
        print(json_string)
        print("-" * 500)

        print("\n Your Full Trip Planning:")
        print("-"*50+"\n")

        print(f"Destination: {response.place}")
        print(f"Duration: {response.Duration} Days")
        print(f"Flight: {response.Flight}")
        print(f"Budget: {response.Budget} BDT")
        print(f"Transport: {response.Transport}")

        print("Activities:")
        for i,activity in enumerate(response.activities,1):
            print(f"  {i}.{activity}")

        print("Always Remember in mind:")
        for i, notes in enumerate(response.note,1):
            print(f"  {i}.{notes}")

if __name__ == "__main__":
    asyncio.run(main())