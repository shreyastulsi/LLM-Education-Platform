from flask import Flask, request, render_template_string, redirect, url_for, session, Blueprint, render_template
import os
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from langchain_openai import OpenAI
import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import YoutubeLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
embeddings = OpenAIEmbeddings()
from dotenv import load_dotenv
load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    raise EnvironmentError("OPENAI_API_KEY not set. Add it to your .env file.")
if not os.getenv("SERPER_API_KEY"):
    raise EnvironmentError("SERPER_API_KEY not set. Add it to your .env file.")
from .testing import create_db_from_pdf, get_response_from_query, create_db_from_youtube_video_url, provide_analysis
from .studyMaterialGen import format_questions
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
import csv
import re
from .supabase_client import save_test_result, fetch_test_results
userLog = Blueprint('userLog', __name__)

@userLog.route('/userLog')

def home():
    print(session['total_scores'])
    print(session['mini_section_scores'])
    print(session['missed_topics'])
    user_id = session.get("user_id", "anon")
    def clean_input(input_list):
        cleaned_list = []
        for item in input_list:
            # Remove numbers followed by a period and any extra spaces, and remove newline characters
            cleaned_item = re.sub(r'\d+\.\s*', '', item).replace('\n', ', ')
            cleaned_list.append(cleaned_item.strip())
        return cleaned_list
        import csv

    # Example inputs
    total_scores = session.get('total_scores', [])
    mini_section_scores = session.get('mini_section_scores', [])
    missed_topics = clean_input(session.get('missed_topics', []))

    # Persist latest snapshot to Supabase
    main_score = total_scores[-1] if total_scores else None
    side_score = mini_section_scores[-1] if mini_section_scores else None
    topics_str = missed_topics[-1] if missed_topics else ""
    if main_score is not None:
        try:
            save_test_result(user_id, main_score, side_score, topics_str)
        except Exception as exc:
            print("Failed to save test result:", exc)

    rows = fetch_test_results(user_id)
    scores = [r.get("main_score") for r in rows if r.get("main_score") is not None]
    high = max(scores) if scores else 0
    mean = float(np.mean(scores)) if scores else 0
    median = float(np.median(scores)) if scores else 0
    std = float(np.std(scores)) if scores else 0

    return render_template("userLog.html", s=scores, s1=high, s2=round(mean, 2), s3=round(median, 2), s4=round(std, 2))
    
    
    
@userLog.route('/getRec', methods=['POST'])
def chatRec():

    user_id = session.get("user_id", "anon")
    rows = fetch_test_results(user_id)
    df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=["main_score", "side_score", "missed_topics"])
        
    query = request.form.get("user_query")
    agent = create_pandas_dataframe_agent(OpenAI(temperature=0), df, verbose=True, allow_dangerous_code=True)
    response = (agent.invoke({"input": query}))['output']
    return render_template("userLog.html", queryResponse=response)
