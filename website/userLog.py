from flask import Flask, request, render_template_string, redirect, url_for, session, Blueprint, render_template
import os
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
import matplotlib.pyplot as plt
from langchain import hub
import numpy as np
import pandas as pd
from langchain_experimental.agents.agent_toolkits.python.base import create_python_agent
from langchain_openai import OpenAI
from langchain_openai import ChatOpenAI
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import YoutubeLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
embeddings = OpenAIEmbeddings()
from dotenv import load_dotenv
load_dotenv()
os.environ['OPENAI_API_KEY']
os.environ["SERPER_API_KEY"] = "7150885e8711a9b49a52871eb4c912575d9a0631"
from .testing import create_db_from_pdf, get_response_from_query, create_db_from_youtube_video_url, provide_analysis
from .studyMaterialGen import format_questions
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
import csv
from langchain_core.tools import Tool
from langchain_experimental.utilities import PythonREPL
from langchain_experimental.tools import PythonREPLTool
import re
userLog = Blueprint('userLog', __name__)

@userLog.route('/userLog')

def home():
    print(session['total_scores'])
    print(session['mini_section_scores'])
    print(session['missed_topics'])
    def clean_input(input_list):
        cleaned_list = []
        for item in input_list:
            # Remove numbers followed by a period and any extra spaces, and remove newline characters
            cleaned_item = re.sub(r'\d+\.\s*', '', item).replace('\n', ', ')
            cleaned_list.append(cleaned_item.strip())
        return cleaned_list
        import csv

    def write_scores_to_csv(total_scores, mini_section_scores, missed_topics, filename='/Users/shreyastulsi/Desktop/LangchainProfessional/experiments/educationGPT/website/userLog.csv'):
        # Find the maximum length among the lists
        max_length = max(len(total_scores), len(mini_section_scores), len(missed_topics))
        
        # Extend each list to match the maximum length, filling missing values with 'N/A'
        total_scores.extend([''] * (max_length - len(total_scores)))
        mini_section_scores.extend([''] * (max_length - len(mini_section_scores)))
        missed_topics.extend([''] * (max_length - len(missed_topics)))
        
        # Define the header
        header = ['Main-Test', 'Side-Test', 'Missed-Topics']

        # Combine the data into rows
        rows = zip(total_scores, mini_section_scores, missed_topics)
        
        # Write to the CSV file
        with open(filename, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(header)  # Write the header
            writer.writerows(rows)   # Write the rows

    # Example inputs
    total_scores = session['total_scores']
    mini_section_scores = session['mini_section_scores']
    missed_topics = clean_input(session['missed_topics'])

    # Call the function to save the data to 'scores.csv'
    write_scores_to_csv(total_scores, mini_section_scores, missed_topics)




    return render_template("userLog.html", s=session['total_scores'],s2="3", s3="3", s4="4")
    
    
    
@userLog.route('/getRec', methods=['POST'])
def chatRec():

    df = pd.read_csv(
    "/Users/shreyastulsi/Desktop/LangchainProfessional/experiments/educationGPT/website/userLog.csv"
    )
    
    
    query = request.form.get("user_query")
    agent = create_pandas_dataframe_agent(OpenAI(temperature=0), df, verbose=True, allow_dangerous_code=True)
    response = (agent.invoke({"input": query}))['output']
    return render_template("userLog.html", queryResponse=response)