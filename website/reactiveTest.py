from flask import Flask, request, render_template_string, redirect, url_for, session, Blueprint, render_template, flash
import os
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from langchain_openai import OpenAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

from .testing import create_db_from_pdf, get_response_from_query, create_db_from_youtube_video_url, provide_analysis
from .studyMaterialGen import format_questions
from .source_utils import load_db_for_user

load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    raise EnvironmentError("OPENAI_API_KEY not set. Add it to your .env file.")
if not os.getenv("SERPER_API_KEY"):
    raise EnvironmentError("SERPER_API_KEY not set. Add it to your .env file.")



reactiveTest = Blueprint('reactiveTest', __name__)



query= """Contruct 5 MCQ Questions & Answers on this specific topic, using this exact template, with the exact labels for Questions and Answers
            QUESTIONS
            1: (insert question here)
                A)
                B)
                C)
                D)
            repeat this for 5
           
            ANSWERS
            1) A(just put the letter of the answer, not the answer itself)
            repeat this for 5
     """
     



db = None

def _load_db():
    """Lazy-load vector store from Supabase-backed source."""
    global db
    if db is None:
        user_id = session.get("user_id", "anon")
        db = load_db_for_user(user_id)
    return db
@reactiveTest.route('/initialTest')
def index():
    db_instance = _load_db()
    
    if 'total_scores' not in session:
        session['total_scores'] = []
    if 'mini_section_scores' not in session:
        session['mini_section_scores'] = []
    if 'missed_topics' not in session:
        session['missed_topics'] = []
    
    if 'feedback' not in session:
        session['feedback'] = ""
        
    if 'main' in session:
        if session['main']!="mini":
            session['feedback'] = ""
            
    if 'main' not in session:
        session['main']= ""
    initial_test_q, initial_test_a = format_questions(get_response_from_query(db_instance, query,session['feedback']), 1)
    session['questions']= initial_test_q
    
    
    ans_modified = initial_test_a.split('\n')
    ans_modified.remove('')
    session['actual_answers'] = [ans_modified.split(') ')[1] for ans_modified in ans_modified]
    
    
    print(session['actual_answers'])

    # return render_template("initialTest.html", questions="33333333333333333333\n33333333333333333333\n33333333333333333333\n33333333333333333333\n33333333333333333333\n33333333333333333333\n33333333333333333333\n33333333333333333333\n33333333333333333333\n")
    if session['main']=='mini':
        sideTest='side-test'
    else:
        sideTest='main-test'
    return render_template("initialTest.html", sideTest = sideTest, form_submitted=False, questions=initial_test_q, mf=False)

@reactiveTest.route('/submitTest', methods=['POST'])
def submit_test():

    submitted_answers=[]
    for i in range(0, len(request.form)):
        submitted_answers.append(request.form.get( ("Q")+str(i+1)))

    session['user_answers'] = submitted_answers
    
    wrong_questions = []
    for i in range(0, len(session['user_answers'])):
        if session['user_answers'][i]!=session['actual_answers'][i]:
            wrong_questions.append(str(i+1))
    
    print(wrong_questions)
    
    template = "Take the question numbers given to you, Out of these questions: {total_q}, output back the questions corresponiding to the question number"
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    
    human_template = "Here are the question numbers: {question_num}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )
    runnable = chat_prompt | ChatOpenAI()
    content = ( (runnable.invoke({"question_num": ' '.join(wrong_questions), "total_q": session['questions']})).content)
    
    session['current_score'] = int(  (( len(session['user_answers'])- len(wrong_questions)  ) / (len(session['user_answers'])))*100  )
    
    if 'main' not in session:
        session['total_scores'].append(session['current_score'])
    else:
        if (session['main']!="mini"):
            session['total_scores'].append(session['current_score'])
        else:
            session['mini_section_scores'].append(session['current_score'])
   
       
    
   

    if session['current_score'] < 90:
        session['feedback'] = provide_analysis(db, content)
        session['main'] = 'mini'
        template = "You are provided the feedback that was given to a user, For each question identify the central concept in two words, and list them"
        system_message_prompt = SystemMessagePromptTemplate.from_template(template)
    
        human_template = "Here is the feedback: {feed}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

        chat_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, human_message_prompt]
        )
        runnable2 = chat_prompt | ChatOpenAI()
        
        topics = (runnable2.invoke({"feed": session['feedback']})).content
        session['missed_topics'].append(topics)
        return render_template("initialTest.html", form_submitted=True, answers= session['actual_answers'], feedback = session['feedback'],focusTopics=topics, mf=True)
    else:
        if ('main' not in session):
            flash('First try!', 'success') 
            return render_template('congratulations.html', score=session['current_score'])

        else:
            
            if(session['main']!="mini"):
                flash('Test Completed!', 'success')
                return render_template('congratulations.html', score=session['current_score'])
            
            session['main']=''
            print("Returning to main")
            flash('Returning to Main Test', 'success')
            return redirect(url_for('reactiveTest.index'))

@reactiveTest.route('/adjustedTest', methods=['POST'])
def adjusted_test():
    session['main'] = "mini"
    return redirect(url_for('reactiveTest.index'))
# def home():
   
      

    
#     # if request.method == 'POST':
#     #     answer1 = request.form.get('Q1')
#     #     answer2 = request.form.get('Q2')
#     #     answer3 = request.form.get('Q3')
        
        
        
        
#     #     #     feedBack = (provide_analysis(db, initial_test_q, answer1+ '\n' + answer2+ '\n' + answer3, initial_test_a).content)
#     #     # initial_test_q, initial_test_a = format_questions(get_response_from_query(db, query,feedBack), 1)
    
        




#     #     return render_template('reactiveTest.html', questions=initial_test_q, answers=initial_test_a, feedback=feedBack)
       
#     # else:
#     #     initial_test_q, initial_test_a = format_questions(get_response_from_query(db, query, ""), 1)  
#     # return render_template('reactiveTest.html', questions=initial_test_q, answers=initial_test_a)       
#     session['notes']="True"                                     
#     return render_template('reactiveTest.html', questions="", answers="")    
    
    
    
    
#     """
#     Structure
#         Generate a sample test
#             Get responses
#                 Return score give feedback
#                     Based on that feedback generate test focusing on that
#                     Keep that test running until score is hit
                    
#         Come back to a new test
#     """
