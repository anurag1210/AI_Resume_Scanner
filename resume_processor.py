import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY

embedding = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
llm = ChatGoogleGenerativeAI(model="models/gemini-2.5-flash", temperature=0.3)  # ✅ models/

def load_resume(file_path):
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith('.docx'):
        loader = Docx2txtLoader(file_path)
    elif file_path.endswith('.txt'):
        loader = TextLoader(file_path)
    else:
        raise ValueError('Unsupported file format. Please upload a PDF, DOCX or TXT file')
    
    documents = loader.load()    # ✅ no arguments, one line!
    return documents

def analyze_resume(docs, job_description):
    full_resume = " ".join([doc.page_content for doc in docs])
    prompt = f"""
    Compare the resume with the job description. Give below details:
    1. Suitability score between 0 to 100.
    2. Skills Match: List key skills that match.
    3. Experience Match: Summarize experience alignment.
    4. Education Match: Summarize education alignment.
    5. Strength: Highlight candidate strengths.
    6. Weakness: Highlight gaps in profile.
    7. Overall Assessment: Two line summary.

    Job Description: {job_description}
    Resume: {full_resume}
    """
    result = llm.invoke(prompt)
    return result.content.strip()

def store_to_vectorstore(docs, persistant_directory="chroma_store"):
    text_splitter = RecursiveCharacterTextSplitter(    # ✅ correct name
        chunk_size=1000, 
        chunk_overlap=200                              # ✅ no double p
    )
    chunks = text_splitter.split_documents(docs)       # ✅ text_splitter not splitter
    texts = [chunk.page_content for chunk in chunks]
    metadatas = [{"source": f"chunk_{i}"} for i in range(len(texts))]

    vectorstore = Chroma.from_texts(                   # ✅ correct method
        texts=texts, 
        embedding=embedding,                           # ✅ singular
        metadatas=metadatas, 
        persist_directory=persistant_directory
    )
    vectorstore.persist()                              # ✅ correct spelling
    return vectorstore

def run_self_query(query, persist_directory="chroma_store"):
    vectorstore = Chroma(
        persist_directory=persist_directory, 
        embedding_function=embedding
    )
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 3}
    )
    docs = retriever.invoke(query)                     # ✅ invoke not retrieve

    combined_docs = "\n\n".join([                      # ✅ \n\n not \n]n
        doc.page_content if hasattr(doc, 'page_content') 
        else str(doc) for doc in docs
    ])
    
    prompt = f"""Based on the following retrieved information from the resume, 
    answer the query in brief:
    Query: {query}
    Retrieved Content: {combined_docs}
    """
    result = llm.invoke(prompt)
    return result.content.strip()