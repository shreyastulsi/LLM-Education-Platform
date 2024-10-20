from flask import Blueprint, render_template, request, session
import os
from .testing import create_db_from_pdf, create_db_from_youtube_video_url, get_response_from_query
import re






def format_questions(text, q_type):
    parts = text.split("ANSWERS")
    question_segment = parts[0].strip()
    
    answer_segment = parts[1].strip() if len(parts) > 1 else ""

    formatted_answer_segment=""
    formatted_question_segment=""
    old_char =""
    if q_type==1 or q_type==2 or q_type==3:
        for char in question_segment:

            if old_char.isdigit() and char==':':
                formatted_question_segment+=char
                formatted_question_segment = formatted_question_segment[:(len(formatted_question_segment)-2)] +  '\n'  +'\n' + formatted_question_segment[len(formatted_question_segment)-2:len(formatted_question_segment)] + formatted_question_segment[(len(formatted_question_segment)+1):]
            elif char == ')' and (old_char == 'A' or old_char == 'B' or old_char == 'C' or old_char == 'D'):
                formatted_question_segment += char
                formatted_question_segment = formatted_question_segment[:(len(formatted_question_segment)-3)] + '\n' + formatted_question_segment[len(formatted_question_segment)-2:len(formatted_question_segment)] + formatted_question_segment[(len(formatted_question_segment)+1):]
            else:
                formatted_question_segment += char
                
            old_char = char
            
        for char in answer_segment:
            if (char  == ':' or char == ')') and old_char.isdigit():
             
             
                formatted_answer_segment+=char
                if q_type==3:
                     formatted_answer_segment = (formatted_answer_segment[:(len(formatted_answer_segment)-2)] ) +'\n' +'\n' + formatted_answer_segment[len(formatted_answer_segment)-2:len(formatted_answer_segment)] + formatted_answer_segment[(len(formatted_answer_segment)+1):]        
                formatted_answer_segment = (formatted_answer_segment[:(len(formatted_answer_segment)-2)] ) +'\n' + formatted_answer_segment[len(formatted_answer_segment)-2:len(formatted_answer_segment)] + formatted_answer_segment[(len(formatted_answer_segment)+1):]
        
                
            else:
                formatted_answer_segment += char
                
            old_char = char
                
    
    else:
        formatted_question_segment, formatted_answer_segment = question_segment, answer_segment
    
   
        

       
        
    return formatted_question_segment, formatted_answer_segment

    



studyMaterialGen = Blueprint('studyMaterialGen', __name__)

@studyMaterialGen.route('/studyMaterialGen', methods=['GET','POST'])
def home():

    if request.method == 'POST':
        gen_type = int(request.form.get('gen_type'))
        num_q = int(request.form.get('num_q'))
        query = ""
        yt_url=""
        pdf_url=""
        uploadMethod = 0
      


        if os.path.exists("/Users/shreyastulsi/Desktop/LangchainProfessional/experiments/educationGPT/website/ytlink.txt"):
            with open("/Users/shreyastulsi/Desktop/LangchainProfessional/experiments/educationGPT/website/ytlink.txt", "r") as file:
                yt_url = file.readline()
                uploadMethod=1
        elif os.path.exists("/Users/shreyastulsi/Desktop/LangchainProfessional/experiments/educationGPT/website/currfile.pdf"):
            pdf_url = "/Users/shreyastulsi/Desktop/LangchainProfessional/experiments/educationGPT/website/currfile.pdf"
            uploadMethod=2
        

        

        if gen_type == 1:
            query = f"""Contruct {num_q} MCQ Questions & Answers on this topic, using this exact template, with the exact labels for Questions and Answers
            QUESTIONS
            1: (insert question here)
                A)
                B)
                C)
                D)
            repeat this for {num_q}
           
            ANSWERS
            1) A
            repeat this for {num_q}

            """
        elif gen_type==2:
            query = f"""Generate {num_q} Vocab questions on this topic, using this exact template, with the exact labels for Questions and Answers

            QUESTIONS
            1:  (insert question here)
            repeat this for {num_q}
            
            
            ANSWERS
            1: Couple word answer
            repeat this for {num_q}
            """
     
        elif gen_type == 3:
            query = f"""Generate {num_q} Free response questions & answers on this topic, answers should be 4-5 sentences, using this exact template, with the exact labels for Questions and Answers
            QUESTIONS
            1: (insert question here)
            repeat this for {num_q}
            
            
            ANSWERS
            1: 2-3 Sentence Answer
            repeat this for {num_q}
           
            """
  
        if uploadMethod==1:
            db = create_db_from_youtube_video_url(yt_url)
           
        else:
            db = create_db_from_pdf(pdf_url)
           
        
        response = get_response_from_query(db, query, "")
        print(response)
        formatted_response, formatted_answers = format_questions(response, gen_type)

       
        return render_template('studyMaterialGen.html', questions=formatted_response, answers=formatted_answers)

    return render_template('studyMaterialGen.html')                                                      