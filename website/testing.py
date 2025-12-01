from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import YoutubeLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOpenAI
from dotenv import find_dotenv, load_dotenv
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate

import textwrap

load_dotenv(find_dotenv())
embeddings = OpenAIEmbeddings()

def create_db_from_pdf(pdf_url):
    loader = PyPDFLoader(pdf_url)
    content = loader.load_and_split()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=300)
    docs = text_splitter.split_documents(content)

    db = FAISS.from_documents(docs, embeddings)
    return db
def create_db_from_youtube_video_url(video_url):
    loader = YoutubeLoader.from_youtube_url(video_url)
    transcript = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=200)
    docs = text_splitter.split_documents(transcript)

    db = FAISS.from_documents(docs, embeddings)
    return db

def get_response_from_query(db, query, focus, k=4):
    docs = db.similarity_search(query, k=k)
    docs_page_content = " ".join([d.page_content for d in docs])

    chat = ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=0.2)

    # Template to use for the system message prompt
    
    if(focus==""):
        template = """
        You are an educational assistance tool and your goal is to take the most vital information provided here {docs}
        to contruct the most effective study material in the format that is desired by the user.{foc}
        
        """
        print("first")
    else:
       template = """
        You are an personalized educational tool generator, you are generating study material for a student who answered these questions incorrectly {foc}, 
        use this information set {docs} to create study material relating to those missed concepts.
        """ 
       print("second")
        
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)

    # Human question prompt
    human_template = "Answer the following question: {question}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )

    chain = chat_prompt | chat

    response_msg = chain.invoke({"question": query, "docs": docs_page_content, "foc": focus})
    response = getattr(response_msg, "content", str(response_msg))

    response = response.replace("\n", "")

    return response


def provide_analysis(db, incorrect_answers, k=4):
    docs = db.similarity_search(incorrect_answers, k=k)
    docs_page_content = " ".join([d.page_content for d in docs])
    chat = ChatOpenAI(model_name="gpt-3.5-turbo-16k", temperature=0.2)

    # Template to use for the system message prompt
    template = """
        You are a Educational Feedback tool, You will be provided questions the user got wrong{ans1}, List these questions and then use the {document} to help provide explanations. Format accordingly:
        
        List Question
            -> Explanation
            
        Repeat for all question
        
        """
    system_message_prompt = SystemMessagePromptTemplate.from_template(template)

    # Human question prompt
    human_template = "Perform task: {question}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )

    runnable = chat_prompt | chat

    response = runnable.invoke({"question":"Give feedback to user", "document":docs_page_content, "ans1": incorrect_answers})
    
    return response.content


    
