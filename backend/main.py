from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from src.utils import format_docs
from src.prompt import prompt
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# LLM
llm = OpenAI(
    model_name="gpt-3.5-turbo-instruct",
    temperature=0.2,
    max_tokens=512,
    streaming=True
)

# Vector Store
db = Chroma(persist_directory="./vector_store", embedding_function=OpenAIEmbeddings())
retriever = db.as_retriever(search_type="similarity")

# Chain
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserQuery(BaseModel):
    """user question input model"""
    question: str


@app.post("/chat/")
async def chat(query: UserQuery):
    """chat endpoint"""
    answer = rag_chain.invoke(query.question).strip()
    return {"answer": answer}
    