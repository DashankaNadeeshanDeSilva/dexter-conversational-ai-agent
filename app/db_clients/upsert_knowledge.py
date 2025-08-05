import os
from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader, DirectoryLoader
from typing import List
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.db_clients.pinecone_client import PineconeClient
import logging
from langchain_core.documents import Document  # Updated import

logger = logging.getLogger(__name__)
PINECONE_KNOWLEDGE_INDEX= "dexter-v1-knowledge-base"

def load_documents(file_path: str) -> List[Document]:

    # get file extention
    file_extension = os.path.splitext(file_path)[-1].lower()

    if file_extension == ".pdf":
        doc_loader = PyPDFLoader(file_path)
    elif file_extension == ".docx":
        doc_loader = Docx2txtLoader(file_path)
    elif file_extension == ".txt":
        doc_loader = TextLoader(file_path)
    else:
        logger.warning(f"Unsupported file type: {file_extension}")
        return None

    documents = doc_loader.load()

    return documents


def upsert_documents(documents: List[Document]):
        """
        Insert a documnets (text) into semantic memory.
        """
  
        ## Chunk document
        splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
        document_chunks = splitter.split_documents(documents)

        if not document_chunks:
            logger.warning("No chunks to upsert. Exiting.")
            return

        index_name = PINECONE_KNOWLEDGE_INDEX
        logger.info(f"Initializing Pinecone client for index: {index_name}")

        pinecone_client = PineconeClient(index_name=index_name)

        pinecone_client.vector_store.add_documents(document_chunks)
        print("==== Upsert complete ! ====")



def main(file_path: str):
    documents = load_documents(file_path)

    if documents:
        upsert_documents(documents)
    else:
        logger.warning("No documents to upsert. Exiting.")
        return



if __name__ == "__main__":
    main("app/db_clients/upsert_data/company_data.txt")