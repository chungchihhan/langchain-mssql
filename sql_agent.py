import pyodbc
import gradio as gr
from dotenv import load_dotenv
import os

from langchain.sql_database import SQLDatabase
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import create_sql_agent, AgentType
from langchain_openai import OpenAI

# Load environment variables from .env file
load_dotenv()
# Access variables
server = os.getenv('SERVER')
database = os.getenv('DATABASE')
username = os.getenv('DB_USERNAME')
password = os.getenv('PASSWORD')

openai_api_key=os.getenv("OPENAI_API_KEY")
connection_string = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"

db = SQLDatabase.from_uri(connection_string)
print(db)

# Create the SQLDatabaseToolkit using the initialized SQLDatabase object and an OpenAI instance
toolkit = SQLDatabaseToolkit(db=db, llm=OpenAI(temperature=0,openai_api_key=openai_api_key))

agent_executor = create_sql_agent(
    llm=OpenAI(temperature=0, openai_api_key=openai_api_key),
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,  # You can choose the appropriate agent type here
)


def sql_chat(question):
    return agent_executor.run(question)

demo = gr.Interface(
    fn=sql_chat, 
    inputs="textbox",
    outputs="textbox"
)

# demo.launch(share=True, auth=("username", "password"))
demo.launch()