import streamlit as st
import asyncio

from datetime import datetime

from travel_agent_with_guardrail import travel_agent
from travel_agent_with_guardrail import Runner
from travel_agent_with_guardrail import InputGuardrailTripwireTriggered
from travel_agent_with_guardrail import OutputGuardrailTripwireTriggered

#Page Design
st.set_page_config(
    page_title="Travel Planner",
    page_icon="<UNK>",
    layout="wide",
    initial_sidebar_state="expanded",
)

#Load  CSS
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True )
load_css("style.css")
#Heading
st.markdown(
    '<div class="main-title"> ✈️ Travel Planner </div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">Flights • Hotels • Weather • Trip plan</div> ',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title"><br>Give your travel plan with appropriate destination and get suitable trip</div>',
    unsafe_allow_html=True
)

#Sidebar
with st.sidebar:
    st.title("🌍 Travel Control Panel")

    st.markdown("### Current Date")
    st.info(f"Today: {datetime.now().strftime('%d %B %Y')}")

    st.markdown("### Flight Booking")

    flight_option= st.selectbox(
        "Choose Flight", ["sky-ways",
                          "OceanAirline",
                          "MountainJet",
                          "US-Bangla"])

    st.markdown("### Travel Date")

    date_option= st.date_input("Select Travel Date")

    st.markdown("Pick Budget")

    budget_slider=st.slider(
        "Amount(USD)",
        min_value=100,
        max_value=5000,
        value=1000,
        step
        =100
    )

    trip_type=st.selectbox(
        "Trip Type",
        ["One Way", "Round Trip"]
    )

    st.markdown("### ✨ Features")
    st.markdown("""
        - Flight Booking
        - Hotel Recommendation
        - AI Travel Planning
        - Weather Forecast
        - Guardrail Security
        - Any Command without destination will be rejected
        """)

#Weather Data
st.markdown("## Weather Overview")

col11,col12,col13= st.columns(3)

with col11:
    st.markdown("""
    <div class="weather-box">
    <h2>☀️ Cox's Bazar</h2>
    <h1>29°C</h1>
    <p>Sunny</p>
    </div>""",
    unsafe_allow_html=True)

with col12:
    st.markdown("""
    <div class="weather-box">
    <h2>🌧️ Paris</h2>
    <h1>18°C</h1>
    <p>Rainy</p>
    </div>""",
    unsafe_allow_html=True)

with col13:
    st.markdown("""
    <div class="weather-box">
        <h2>☁️ New York</h2>
        <h1>21°C</h1>
        <p>Cloudy</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

#state checking
if "messages" not in st.session_state:
    st.session_state.messages = []

for role,content in st.session_state.messages:
    with st.chat_message(role):
        st.markdown(content, unsafe_allow_html=True)

#Input Taking
prompt=st.chat_input("Ask your travel assistant anything...")

#Bridge between UI and Agent
async def run_agent(query):
    result= await Runner.run(travel_agent,query)
    return result.final_output

#This block will run when user type something
if prompt:
    # Store user message
    st.session_state.messages.append(("user", prompt))
    # Show user bubble
    with st.chat_message("user"):
        st.markdown(prompt)
    # Assistant response bubble
    with st.chat_message("assistant"):
        with st.spinner("✈️ Planning your perfect journey..."):
            try:
                response = asyncio.run(run_agent(prompt))
                if hasattr(response, "airline"):
                    flight_html = f"""
                    <div class="glass-card">
                      <h2>✈️ Flight Recommendation</h2>
                      <div class="flight-card">
                        <h3>{response.airline}</h3>
                        <hr>
                        <div style="display:flex;justify-content:space-between;">
                          <div>
                            <h4>Departure</h4>
                            <p>{response.departure_time}</p>
                          </div>
                          <div>
                            <h4>Arrival</h4>
                            <p>{response.arrival_time}</p>
                          </div>
                          <div>
                            <h4>Price</h4>
                            <p>${response.price}</p>
                          </div>
                        </div>
                        <p><b>Direct Flight:</b>{response.direct_flight}</p>
                        <p><b>Recommendation:</b>{response.recommendation_reason}</p>
                      </div>
                    </div>"""
                    st.markdown(flight_html,unsafe_allow_html=True)
                    st.session_state.messages.append(("assistant", flight_html))
                elif hasattr(response, "name"):
                    amenities = ", ".join(response.amenities)
                    hotel_html = f"""
                    <div class="glass-card">
                      <h2>🏨 Hotel Recommendation</h2>
                      <div class="hotel-card">
                        <h3>{response.name}</h3>
                        <hr>
                        <p><b>📍 Location:</b>{response.location}</p>
                        <p><b>💰 Price/Night:</b>${response.price_per_night}</p>
                        <p><b>✨ Amenities:</b>{amenities}</p>
                        <p><b>Recommendation:</b>{response.recommendation_reason}</p>
                      </div>
                    </div>
                    """
                    st.markdown(hotel_html,unsafe_allow_html=True)
                    st.session_state.messages.append(("assistant", hotel_html))

                elif hasattr(response, "destination"):
                    activities = ", ".join(response.activities)
                    travel_html = f"""
                    <div class="glass-card">
                      <h2>🌍Travel Plan</h2>
                      <p><b>Destination:</b>{response.destination}</p>
                      <p><b>Duration:</b>{response.duration_days} Days</p>
                      <p><b>Budget:</b>${response.budget}</p>
                      <p><b>Activities:</b>{activities}</p>
                      <p><b>Travel Notes:</b>{response.note}</p>
                    </div>"""
                    st.markdown(travel_html,unsafe_allow_html=True)
                    st.session_state.messages.append(("assistant", travel_html))

                else:
                    st.write(response)
                    st.session_state.messages.append(("assistant", str(response)))

            except InputGuardrailTripwireTriggered:
                st.error("🚫 Your request was blocked because it is not travel-related.")

            except OutputGuardrailTripwireTriggered:
                st.error("⚠️ Unsafe response blocked by output guardrail.")

            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
