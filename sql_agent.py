import pyodbc
import gradio as gr
import pandas as pd
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
print(openai_api_key)
connection_string = f"mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server"

db = SQLDatabase.from_uri(connection_string)

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

#Print out the original data using the language in SQL
def fetch_data():
    connection_string_fetch_data = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    cnxn = pyodbc.connect(connection_string_fetch_data)
    cursor = cnxn.cursor()

    query = "SELECT * FROM ERPobjects"
    cursor.execute(query)

    # Fetch data and column names
    data = cursor.fetchall()

    # Convert to pandas DataFrame
    df = pd.DataFrame.from_records(data, columns=[column[0] for column in cursor.description])

    # Close cursor and connection
    cursor.close()
    cnxn.close()

    return df


# use gradio to create an interface for sql agent
# demo = gr.Interface(
#     fn=sql_chat, 
#     inputs="textbox",
#     outputs="textbox"
# )

# Create a Gradio interface with Blocks
with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column():
            # Button for fetching data
            fetch_button = gr.Button("Fetch Origin Data")
            # Output textbox for fetch data
            fetch_output = gr.Dataframe()
        with gr.Column():
            with gr.Row():
                # Textbox for entering SQL query
                query_input = gr.Textbox(label="Enter your SQL query")
                # Button for SQL chat
                chat_button = gr.Button("Ask SQL Agent")
            # Output textbox for SQL chat
            chat_output = gr.Textbox(label="SQL Agent Response")
        
    # Define actions
    fetch_button.click(fn=fetch_data, outputs=fetch_output)
    chat_button.click(fn=sql_chat, inputs=query_input, outputs=chat_output)


# demo.launch(share=True, auth=("username", "password"))
demo.launch()