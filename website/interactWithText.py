from flask import Blueprint, render_template, request
import os

from .testing import create_db_from_pdf, get_response_from_query, create_db_from_youtube_video_url
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()
os.environ['OPENAI_API_KEY']
os.environ["SERPER_API_KEY"] = "7150885e8711a9b49a52871eb4c912575d9a0631"
chat = ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=0.2)



from langchain.memory import ConversationBufferMemory
memory = ConversationBufferMemory(
    memory_key='chat_history',
)

from langchain.agents.agent_toolkits import create_retriever_tool
from langchain.agents.agent_toolkits import create_conversational_retrieval_agent
uploadMethod=0
yt_url=""
pdf_url=""

if os.path.exists("/Users/shreyastulsi/Desktop/LangchainProfessional/experiments/educationGPT/website/ytlink.txt"):
    with open("/Users/shreyastulsi/Desktop/LangchainProfessional/experiments/educationGPT/website/ytlink.txt", "r") as file:
        yt_url = file.readline()
        uploadMethod=1
elif os.path.exists("/Users/shreyastulsi/Desktop/LangchainProfessional/experiments/educationGPT/website/currfile.pdf"):
    pdf_url = "/Users/shreyastulsi/Desktop/LangchainProfessional/experiments/educationGPT/website/currfile.pdf"
    uploadMethod=2
 
if uploadMethod==1:
    db = create_db_from_youtube_video_url(yt_url)
    
else:
    db = create_db_from_pdf(pdf_url)
    

print(db)
        
tool = create_retriever_tool(
    db.as_retriever(search_kwargs={"top_k": 5}),  # Limits the number of retrieved results
    name="doc-searcher",
    description="Answer all questions on Shreyas through this document",
)

tools=[tool]
a1= create_conversational_retrieval_agent(chat, tools, memory_key='chat_history',handle_parsing_errors=True, verbose=True)
interactWithText = Blueprint('interactWithText', __name__)

@interactWithText.route('/interactWithText', methods=['GET','POST'])
def home():
    global a1
    if request.method == 'POST':
       

        query = request.form.get('user_query', "").strip()
        

                    
        response = ( a1.invoke({'input': query}) )['output']
             
            
        return render_template('interactWithText.html', response=response)
    

    return render_template('interactWithText.html')                                                      