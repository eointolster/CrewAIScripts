#https://github.com/joaomdmoura/crewAI
#pip install websocket-client
#requests
#duckduck-go
#crewsai
#pip install playsound
#pip install websocket-client
#pip install pypub
from crewai import Agent, Task, Crew, Process
import requests
import os
import websocket
import threading
import json
import base64
from playsound import playsound
import time
from pydub import AudioSegment
from pydub.playback import play
from pydub.playback import _play_with_simpleaudio
import threading

from langchain.tools import DuckDuckGoSearchRun
search_tool = DuckDuckGoSearchRun()
from langchain.llms import Ollama
ollama_openhermes = Ollama(model="openhermes")
ollama_openchat = Ollama(model="openchat:7b-v3.5-1210")
ollama_mistral = Ollama(model="mistral:7b")
ollama_codellma = Ollama(model="codellama:7b")

openai_api_key = os.environ.get("OPENAI_API_KEY")

def download_and_play_audio(audio_url):
    # Use requests to download the audio file
    response = requests.get(audio_url)
    if response.status_code == 200:
        with open("output.mp3", "wb") as f:
            f.write(response.content)
        # Play the audio
        playsound('output.mp3')

def play_audio(file_path):
    audio_segment = AudioSegment.from_file(file_path)
    _play_with_simpleaudio(audio_segment)

# WebSocket Function for ElevenLabs TTS
def elevenlabs_speech(text, voice_id, model_id, api_key):
    audio_data = bytearray()
    audio_ready = threading.Event()

    def on_message(ws, message):
        nonlocal audio_data
        response = json.loads(message)
        if 'audio' in response:
            audio_chunk = base64.b64decode(response['audio'])
            audio_data.extend(audio_chunk)
        if response.get('isFinal', False):
            audio_ready.set()  # Set the event when audio data is complete

    def on_close(ws, close_status_code, close_msg):
        audio_ready.set()  # Set the event in case of WebSocket closing

    def on_open(ws):
        def run(*args):
            bos_message = {
                "text": " ",
                "voice_settings": {"stability": 0.5, "similarity_boost": 0.8},
                "xi_api_key": api_key,
            }
            ws.send(json.dumps(bos_message))

            text_message = {"text": text, "try_trigger_generation": True}
            ws.send(json.dumps(text_message))

            eos_message = {"text": ""}
            ws.send(json.dumps(eos_message))

        threading.Thread(target=run).start()

    ws_url = f"wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input?model_id={model_id}"
    ws = websocket.WebSocketApp(ws_url, on_open=on_open, on_message=on_message, on_close=on_close)
    ws_thread = threading.Thread(target=ws.run_forever)
    ws_thread.start()

    audio_ready.wait()  # Wait for the audio data to be ready
    ws.close()  # Close the WebSocket connection
    #with open('output.mp3', 'wb') as audio_file:
    #    audio_file.write(audio_data)
    #audio_segment = AudioSegment.from_mp3('output.mp3')
    #play(audio_segment)  # Play the audio
    with open('output.mp3', 'wb') as audio_file:
        audio_file.write(audio_data)
    
    play_audio('output.mp3')  # Directly play the audio from the file
    #ws_thread.join()  # Ensure the WebSocket thread is finished before moving on


researcher = Agent(
    role='Researcher',
    goal='Research as well as possible any topic given',
    backstory='You are an AI research assistant with the love or being accurate',
    tools=[search_tool],
    verbose=True,
    llm=ollama_openhermes, # Ollama model passed here
    allow_delegation=False
)

writer = Agent(
    role='Writer',
    goal='Write concise summaries given any data',
    backstory='You are an AI master mind when it comes to finding the most valuable information',
    verbose=True,
    llm=ollama_mistral, # Ollama model passed here
    allow_delegation=False
)


voice_id = "2EiwWnXFnvU5JabPnv8n"
model_id = "eleven_multilingual_v1"
api_key = "YourownAPIKEY"######################################### add your key here ################################################
# List of topics to research
topics = [
    "Toyota vs Tesla", "Nvidia vs AMD", "Alphabet Inc vs Apple",
    "Microsoft vs Oracle", "Facebook vs Twitter", "Netflix vs Hulu",
    "Amazon vs eBay", "McDonald's vs Burger King", "Coca-Cola vs Pepsi",
    "BMW vs Mercedes", "Uber vs Lyft", "Airbnb vs Booking.com",
    "Samsung vs LG", "Intel vs Qualcomm", "Spotify vs Apple Music",
    "Adobe vs Corel", "Zoom vs Skype", "Slack vs Microsoft Teams",
    "Canon vs Nikon", "Dell vs HP", "PlayStation vs Xbox",
    "Marvel vs DC", "Starbucks vs Dunkin' Donuts", "Visa vs Mastercard",
    "FedEx vs UPS", "Boeing vs Airbus", "Goldman Sachs vs Morgan Stanley",
    "Nike vs Adidas", "Gucci vs Louis Vuitton", "Walmart vs Target",
    "IKEA vs Home Depot", "Sony vs Panasonic", "Fox News vs CNN",
    "BBC vs Al Jazeera", "Pfizer vs Moderna", "Johnson & Johnson vs AstraZeneca",
    "Google Maps vs Waze", "Instagram vs Snapchat", "WhatsApp vs Telegram",
    "Reddit vs Quora", "Yelp vs TripAdvisor", "TikTok vs YouTube",
    "WeWork vs Regus", "PayPal vs Square", "Venmo vs Zelle",
    "Salesforce vs SAP", "Roku vs Chromecast", "Fitbit vs Garmin",
    "Peloton vs NordicTrack", "Tesla Model S vs Lucid Air",
    "Ford F-150 vs Chevrolet Silverado", "Honda vs Yamaha (Motorcycles)",
    "Ducati vs Kawasaki", "Audi vs Jaguar", "Land Rover vs Jeep",
    "Subaru vs Mazda", "Hyundai vs Kia", "GMC vs Ram Trucks",
    "Porsche vs Ferrari", "Lamborghini vs McLaren", "Aston Martin vs Bentley",
    "Harley-Davidson vs Indian Motorcycles", "Bombardier vs Cessna (Private Jets)",
    "Carnival Cruise Line vs Royal Caribbean", "Norwegian Cruise Line vs Disney Cruise Line",
    "Expedia vs Priceline", "T-Mobile vs Verizon", "AT&T vs Sprint",
    "Dropbox vs Google Drive", "OneDrive vs iCloud", "GoPro vs DJI (Action Cameras)",
    "HBO Max vs Disney+", "Paramount+ vs Peacock", "Epic Games vs Steam",
    "Unity vs Unreal Engine", "Python vs Java", "C++ vs C#",
    "Ruby vs PHP", "Angular vs React", "Vue.js vs Ember.js",
    "Docker vs Kubernetes", "MongoDB vs MySQL", "PostgreSQL vs SQLite",
    "AWS vs Azure", "DigitalOcean vs Linode", "VMware vs Hyper-V",
    "Norton vs McAfee", "Avast vs Kaspersky", "Bitdefender vs ESET"
]

for topic in topics:
    # Define Tasks based on the topic
    task1 = Task(description=f'Investigate {topic}', agent=researcher)
    #task2 = Task(description=f'Investigate uses for {topic}', agent=researcher)
    task2 = Task(description=f'Write a list of values attributed to {topic}', agent=writer)

    crew = Crew(
        agents=[researcher, writer],
        tasks = [task1,task2],
        verbose=2,
        process=Process.sequential
    )

    result = crew.kickoff()

    print("######################")
    print(result)

    # Convert the result to speech using ElevenLabs
    # Call the ElevenLabs WebSocket TTS function
    elevenlabs_speech(result, voice_id, model_id, api_key)
    