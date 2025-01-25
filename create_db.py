
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
import os 
import shutil
from pathlib import Path

CHROMA_PATH = "chroma"
DATA_PATH = "dataset/"

# Path to the directory containing your Markdown files
directory_path = "dataset/"

#Initialize list to hold documents
md_documents = []

AZURE_OPENAI_ENDPOINT='https://samip-m42jr2pq-eastus2.cognitiveservices.azure.com/openai/deployments/text-embedding-3-small-2/embeddings?api-version=2023-05-15'

# Configure Chroma as a retriever with top_k=3
embeddings= AzureOpenAIEmbeddings(model="text-embedding-3-small"
                                  ,api_key=os.getenv("AZURE_OPENAI_EMBEDDING_KEY"),
                                  azure_endpoint=AZURE_OPENAI_ENDPOINT,
                                  openai_api_version="2023-05-15")

# Load all Markdown files from the directory
def load_documents():
    data_folder = Path(directory_path)
    for file_path in data_folder.iterdir():
        print(file_path)
        if file_path.suffix == '.md':
            loader = UnstructuredMarkdownLoader(str(file_path))
            md_documents.extend(loader.load())
            # print(md_documents)

    return md_documents

def split_text(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=200,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    return chunks

def save_to_chroma(chunks: list[Document]):
    # Clear out the database first.
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # emb_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    # Create a new DB from the documents.
    db = Chroma.from_documents(
        chunks, embeddings, persist_directory=CHROMA_PATH
    )
    db.persist()
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")
# Split the documents into chunks
# docs = text_splitter.split_documents(documents)


def main():
    print("Start")
    documents = load_documents()
    print(f"Loaded {len(documents)} documents")
    chunks = split_text(documents)
    print("Chunks generated")
    save_to_chroma(chunks)

main()