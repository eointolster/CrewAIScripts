from crewai import Agent, Task, Crew, Process
import os

from langchain.tools import DuckDuckGoSearchRun
search_tool = DuckDuckGoSearchRun()
from langchain.llms import Ollama
ollama_openhermes = Ollama(model="openhermes")



openai_api_key = os.environ.get("OPENAI_API_KEY")

researcher = Agent(
    role='Researcher',
    goal='Research methods to grow this channel http://www.youtube.com/@Engomonster on youtube and get more subscribers',
    backstory='You are an AI research assistant',
    tools=[search_tool],
    verbose=True,
    llm=ollama_openhermes, # Ollama model passed here
    allow_delegation=False
)

writer = Agent(
    role='Writer',
    goal='Write compelling and engaging reasons as to why someone should join Engomonsters youtube channel',
    backstory='You are an AI master mind capable of growing any youtube channel',
    verbose=True,
    llm=ollama_openhermes, # Ollama model passed here
    allow_delegation=False
)


task1 = Task(description='Investigate Engomonsters channel', agent=researcher)
task2 = Task(description='Investigate sure fire ways to grow a channel', agent=researcher)

task3 = Task(description='Write a list of tasks Engomonster must do to grow his channel', agent=writer)

crew = Crew(
    agents=[researcher, writer],
    tasks = [task1,task2,task3],
    verbose=2,
    process=Process.sequential
)

result = crew.kickoff()

print("######################")
print(result)

