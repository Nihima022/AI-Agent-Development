#Import Libraries
import os
import json
import asyncio
from http.client import responses
from turtledemo.sorting_animate import instructions1

from dotenv import load_dotenv

from agents import Agent
from agents import Tool
from agents import Runner
from agents import OpenAIChatCompletionsModel
from agents import set_tracing_disabled
from agents import function_tool

from openai import AsyncOpenAI

from pydantic import BaseModel
from pydantic import Field

from typing import List

#API to access LLM
load_dotenv()

llm_base_url=os.getenv("BASE_URL")
llm_api_key=os.getenv("API_KEY")
llm_model_name=os.getenv("MODEL_NAME")

#disabled step by step tracing
set_tracing_disabled(True)

#Create a structured model
client=AsyncOpenAI(
    base_url=llm_base_url,
    api_key=llm_api_key
)

structured_model=OpenAIChatCompletionsModel(
    model=llm_model_name,
    openai_client=client
)

#Build Tools for agent

#1.Cost Tool
@function_tool
def get_predicted_travel_cost( city:str, activities:List[str]):
    """Predict the travel cost based on given city and activities"""
    travel_cost={
        "New York": 1500,
        "Chicago": 2000,
        "Los Angels": 2300,
        "Paris":3000
    }
    cost= travel_cost.get(city,1000)
    return f"To visit {city} and to enjoy {activities} , you need {cost} for each person"
    print("Cost Tool is called")

#2.Weather Tool
@function_tool
def get_weather_forcast(city:str,date:str)->str:
    """Predict the correct weather for given city in that particular date"""
    weather_forcast={
        "New York":{
            "sunny":0.3,
            "cloudy":0.2,
            "rainy":0.5
        },
        "Chicago":{
            "sunny":0.4,
            "cloudy":0.2,
            "rainy":0.4
        },
        "Los Angels":{
            "sunny":0.6,
            "cloudy":0.3,
            "rainy":0.1
        },
        "Paris":{
            "sunny":0.7,
            "cloudy":0.3,
            "rainy":0.1
        }
    }
    if city in weather_forcast:
        selected_city=weather_forcast[city]
        highest_probability= max(selected_city, key=selected_city.get)
        temperature_range={
            "New York": "15-25C",
            "Los Angels": "30-35C",
            "Paris": "40-45C",
            "Chicago": "50-60C",
            "France": "70-80C"
        }
        temperature=temperature_range.get(city,"25-35C")
        return f"When you visit {city} the approximate temperature is between {temperature}"

    else:
        return f"You can't find {city} in my weather database"

    print("weather tool is called")

#Create a BaseModel which automatically correct input
class Planning(BaseModel):
    Destination: str
    Duration: int
    Flight: str
    Budget: float
    Weather: str
    Estimated_Cost: str
    Activities: List[str]=Field(description="Should be described in one word")
    Note: List[str]=Field(description="Should be explained in small sentences")

#Create an agent
agents= Agent(
    name="Planning and Advicing Agent",
    instructions=
    """
        You are a comprehensive travel planning assistant that helps users plan their perfect trip.
    
        You can create personalized travel itineraries based on the user's interests and preferences.
    
        Always be helpful, informative, and enthusiastic about travel. Provide specific recommendations
        based on the user's interests and preferences.
        You can 2 tools to help you with your task:
    
        1. get_weather_forecast to get the weather forecast for a city
        2. get_predicted_travel_cost to get the predicted travel cost for a city and activity
    
        When creating travel plans, consider:
        - The weather at the destination
        - Local attractions and activities
        - Budget constraints
        - Travel duration
        - get_weather_forcast for weather information
        - get_predicted_travel_cost for cost estimation

        Do not estimate weather or cost yourself.

        Always use tool outputs in final response.

        Return response strictly following the Planning schema.
        """,
    model= structured_model,
    tools=[get_predicted_travel_cost,get_weather_forcast],
    output_type= Planning

)

async def main():
    queries=input("Enter Your Choice:")
    print("="*100)
    print(f"Query: {queries}")

    print("=" * 100)

    result = await Runner.run(agents, queries)
    response = result.final_output
    print(response)

    print("=" * 100)

    json_format = response.model_dump_json()
    python_dict = json.loads(json_format)
    json_string = json.dumps(python_dict,indent=2)
    print(json_string)

    print("=" * 100)

    print("Trip Planning")
    print("-" * 50)

    print(f"Destination:{response.Destination.upper()}")
    print(f"Duration:{response.Duration} days")
    print(f"Flight:{response.Flight}")
    print(f"Budget:{response.Budget}")
    print(f"Temperature: {response.Weather.upper()}")
    print(f"Estimated Cost: {response.Estimated_Cost}")

    print("Activities:")
    for i, activity in enumerate(response.Activities, 1):
        print(f"  {i}. {activity}")

    print("Advices:")
    for i,advices in enumerate(response.Note,1):
        print(f"  {i}. {advices}")

if __name__ == "__main__":
    asyncio.run(main())






