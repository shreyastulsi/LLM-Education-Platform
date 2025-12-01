from flask import Flask, request, render_template_string, redirect, url_for, session, Blueprint, render_template
import os
import json
import statistics
import re
from dotenv import load_dotenv
from langchain_openai import OpenAI

from .supabase_client import save_test_result, fetch_test_results

load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    raise EnvironmentError("OPENAI_API_KEY not set. Add it to your .env file.")
if not os.getenv("SERPER_API_KEY"):
    raise EnvironmentError("SERPER_API_KEY not set. Add it to your .env file.")
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
    mean = float(statistics.mean(scores)) if scores else 0
    median = float(statistics.median(scores)) if scores else 0
    std = float(statistics.pstdev(scores)) if len(scores) > 1 else 0

    return render_template("userLog.html", s=scores, s1=high, s2=round(mean, 2), s3=round(median, 2), s4=round(std, 2))
    
    
    
@userLog.route('/getRec', methods=['POST'])
def chatRec():

    user_id = session.get("user_id", "anon")
    rows = fetch_test_results(user_id)
    query = request.form.get("user_query")
    llm = OpenAI(temperature=0)

    if not rows:
        response = "No test results found yet. Take a test first."
    else:
        formatted_rows = json.dumps(rows)
        prompt = f"You are assisting with user test history.\nData: {formatted_rows}\nUser question: {query}\nAnswer concisely using only the provided data."
        response = llm.invoke(prompt)

    return render_template("userLog.html", queryResponse=response)
