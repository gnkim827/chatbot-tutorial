from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    directory = '../vector_store'
    file_path = Path("../data")

    for file in file_path.glob("*.pdf"):
        loader = PyPDFLoader(str(file))
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=20,
            length_function=len,
            is_separator_regex=False
        )

        docs = loader.load_and_split(text_splitter)

        embeddings_model = OpenAIEmbeddings()
        
        vector_store = Chroma.from_documents(
            docs,
            embeddings_model,
            persist_directory=directory
        )

    docs = vector_store.similarity_search("소비자 물가 전망 알려줘")

    for idx, doc in enumerate(docs, 1):
        print(f"Document {idx}")
        print(doc.page_content)
        print()
