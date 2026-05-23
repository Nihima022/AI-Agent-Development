#install Libraries
import os
import json
import asyncio

from dotenv import load_dotenv

from agents import Agent
from agents import set_tracing_disabled
from agents import Runner
from agents import Tool
from agents import OpenAIChatCompletionsModel
from agents import function_tool

from typing import Optional
from typing import List

from pydantic import BaseModel
from pydantic import Field

from openai import AsyncOpenAI

#API to access LLM
load_dotenv()

llm_base_url=os.getenv("BASE_URL")
llm_api_key=os.getenv("API_KEY")
llm_model_name=os.getenv("MODEL_NAME")

#Create a Structured Model
client=AsyncOpenAI(
    base_url=llm_base_url,
    api_key=llm_api_key
)

structured_model=OpenAIChatCompletionsModel(
    model=llm_model_name,
    openai_client=client
)

#Create a BaseModel for agents
class Flight_recommendation (BaseModel):
    airline: str
    departure_time:str
    arrival_time: str
    price: float
    direct_flight: str
    recommendation_reason: str

class Hotel_recommendation(BaseModel):
    name:str
    location: str
    price_per_night: float
    amenities: List[str]
    recommendation_reason: str

class Travel_recommendation(BaseModel):
    destination: str
    duration_days: int
    budget: float
    activities: List[str]
    note: str

#Create Tools for agent
@function_tool()
def flight_tool(origin:str,destination:str,date:str) -> str:
    """Search for flight between two cities on a specific date"""
    flight_name=[
        {
            "airline":"sky-ways",
            "departure_time":"08:00",
            "arrival_time":"14:00",
            "price":2500,
            "direct_flight":True,
            "recommendation_reason": "Fastest direct flight available."
        },
        {
            "airline": "OceanAirline",
            "departure_time": "07:00",
            "arrival_time": "12:15",
            "price": 17000,
            "direct_flight": True,
            "recommendation_reason": "Fastest direct flight available."
        },
        {
            "airline": "MountainJet",
            "departure_time": "08:30",
            "arrival_time": "17:30",
            "price": 9570,
            "direct_flight": False,
            "recommendation_reason": "Fastest direct flight available."
        },
        {
            "airline": "US-Bangla",
            "departure_time": "11:45",
            "arrival_time": "20:08",
            "price": 10349,
            "direct_flight": False,
            "recommendation_reason": "Fastest direct flight available."
        }
    ]
    return json.dumps(flight_name)

@function_tool()
def hotel_tool(city:str, check_in_date:str, check_out_date:str, max_price:Optional[float]=None):
    """Search a hotel in that city for the specific date with maximum price"""
    hotel_name=[
        {
            "name":"City center Hotel",
            "location":"DownTown",
            "price_per_night":2500,
            "amenities":["pool","WIFI","GYM"],
            "recommendation_reason": "Great central location with premium facilities."
        },
        {
            "name": "RiverSide Inn",
            "location": "Riverside District",
            "price_per_night": 149,
            "amenities": ["pool","breakfast","boat"],
            "recommendation_reason": "Great central location with premium facilities."
        },
        {
            "name": "Lux Palace",
            "location": "Historic District",
            "price_per_night": 1790,
            "amenities": ["car","pool","Spa","Parking"],
            "recommendation_reason": "Great central location with premium facilities."
        },
        {
            "name": "Bay Watch",
            "location": "Mountain District",
            "price_per_night": 4500,
            "amenities": ["breafast","transport","spa","pool","gym","restaurant"],
            "recommendation_reason": "Great central location with premium facilities."
        }
    ]

    if max_price is not None:
        filtered_hotel=[]

        for hotel in hotel_name:
            hotel_price=hotel["price_per_night"]
            if hotel_price <= max_price:
                filtered_hotel.append(hotel)

    else:
        filtered_hotel=hotel_name

    return json.dumps(filtered_hotel)

@function_tool()
def weather_tool(city:str, date:str)->str:
    """Provide Weather condition on selected date for that selected city"""
    weather_condition={
        "New York":{
            "Sunny":0.3,
            "Cloudy":0.2,
            "Rain":0.5,
        },
        "Downtown": {
            "Sunny": 0.3,
            "Cloudy": 0.2,
            "Rain": 0.5,
        },
        "Mountain View": {
            "Sunny": 0.3,
            "Cloudy": 0.2,
            "Rain": 0.5,
        },
        "Hill District": {
            "Sunny": 0.3,
            "Cloudy": 0.2,
            "Rain": 0.5,
        }
    }
    if city in weather_condition:
        city_weather_condition=weather_condition[city]
        highest_probability= max(city_weather_condition,key=city_weather_condition.get)
        temperature_range={
            "New York": "15-20C",
            "Downtown": "16-17C",
            "Mountain View": "18-19C",
            "Hill District": "20-21C"
        }
        temperature=temperature_range.get(city,"10-12C")
        return f"The weather condition of {city} will be {highest_probability} on that day and temperature will be {temperature}"
    else:
        return f"the weather data is not available for that {city}"


#Build Agent
flight_agent=Agent(
    name="Flight Agent",
    instructions=
    """You are a flight specialist who helps users find the best flights for their trips.
    
    Use the search_flights tool to find flight options, and then provide personalized recommendations
    based on the user's preferences (price, time, direct vs. connecting).
    
    Always explain the reasoning behind your recommendations.
    
    Format your response in a clear, organized way with flight details and prices.
    """,
    model=structured_model,
    tools=[flight_tool],
    output_type= Flight_recommendation,
    handoff_description="Specialist agent for finding and recommending flights"
)

hotel_agent=Agent(
    name="Hotel Advisior",
    instructions=
    """You are a hotel specialist who helps users find the best accommodations for their trips.
    
    Use the search_hotels tool to find hotel options, and then provide personalized recommendations
    based on the user's preferences (location, price, amenities).
    
    Always explain the reasoning behind your recommendations.
    
    Format your response in a clear, organized way with hotel details, amenities, and prices.
    """,
    model=structured_model,
    tools=[hotel_tool],
    output_type= Hotel_recommendation,
    handoff_description="Specialist Agent for finding and recommending hotels"
)

travel_agent=Agent(
    name="Travel Planner",
    instructions="""
    You are a comprehensive travel planning assistant that helps users plan their perfect trip.
    
    You can:
    1. Provide weather information for destinations
    2. Create personalized travel itineraries
    3. Hand off to specialists for flights and hotels when needed
    
    Always be helpful, informative, and enthusiastic about travel. Provide specific recommendations
    based on the user's interests and preferences.
    
    When creating travel plans, consider:
    - The weather at the destination
    - Local attractions and activities
    - Budget constraints
    - Travel duration
    
    If the user asks specifically about flights or hotels, hand off to the appropriate specialist agent.
    """,
    model=structured_model,
    tools=[weather_tool],
    handoffs=[hotel_agent,flight_agent],
    output_type=Travel_recommendation
)

async def main():
    queries=["I need a flight from New York to Chicago tomorrow",
             "Find me a hotel in Paris with a pool for under $300 per night",
             "I want to go downtown tomorrow in downtown find a hotel for me under $4000 per night",
             "I want to go Cox's Bazar, Book a flight for me on 7 am",
             "I want to go cox's Bazar Book a Hotel for me",
             "plan a trip for me to Cox's Bazar"]

    for query in queries:
        print("="*100)
        print(f"QUERY: {query}")
        print("="*100)

        result=await Runner.run(travel_agent, query)
        response=result.final_output
        print(response)

        if hasattr(response,"airline"):
            print(f"AIRLINE: {response.airline}")
            print(f"Departure Time: {response.departure_time}")
            print("Arrival Time: {response.arrival_time}")
            print(f"Price: {response.price}")
            print(f"Direct_Flight: {response.direct_flight}")
            print(f"Recommended_Reason: {response.recommendation_reason}")

        elif hasattr(response,"name"):
            print(f"NAME: {response.name}")
            print(f"Location: {response.location}")
            print(f"Price_per_Night: {response.price_per_night}")
            print(f"Amenities: {response.amenities}")
            print(f"Recommended_Reason: {response.recommendation_reason}")

        elif hasattr(response,"destination"):
            print(f"DESTINATION: {response.destination}")
            print(f"Duration_Days: {response.duration_days}")
            print(f"Budget: {response.budget}")
            print(f"Activities: {response.activities}")
            print(f"Note: {response.note}")

        else:
            print(response)

set_tracing_disabled(True)

if __name__=="__main__":
    asyncio.run(main())





