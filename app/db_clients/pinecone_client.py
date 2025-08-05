"""Pinecone client for vector-based semantic memory storage."""

from typing import Dict, List, Any, Optional, Tuple
import logging
import uuid
from datetime import datetime

from pinecone import Pinecone, PodSpec
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document

from app.config import settings

logger = logging.getLogger(__name__)

class PineconeClient:
    """Pinecone client for semantic vector storage."""
    
    def __init__(self, index_name: Optional[str] = settings.PINECONE_MEMORY_INDEX):
        """Initialize Pinecone client."""
        self.index_name = index_name
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        
        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY,
            dimensions=512
            #spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )

        # Check if index exists, if not create it
        self._initialize_index()
        
        # Initialize vector store
        self.vector_store = PineconeVectorStore(
            index=self.pc.Index(self.index_name),
            embedding=self.embeddings,
            text_key="text"
        )
        
        logger.info("Pinecone client initialized")
    
    def _initialize_index(self):
        """Initialize Pinecone index if it doesn't exist."""
        # Check if index exists
        if not self.pc.list_indexes().get("indexes") or self.index_name not in [idx["name"] for idx in self.pc.list_indexes().get("indexes", [])]:
            logger.info(f"Creating Pinecone index: {self.index_name}")
            
            # Create index with dimensions for text-embedding-3-small
            self.pc.create_index(
                name=self.index_name,
                vector_type="dense",
                dimension=512,  # Dimension for text-embedding-3-small
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            logger.info(f"Created Pinecone index: {self.index_name}")
        else:
            logger.info(f"Pinecone index {self.index_name} already exists")
    
    def store_memory(
        self,
        user_id: str,
        text: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store text in semantic memory.
        
        Args:
            user_id: User ID
            text: Text content to store
            metadata: Optional metadata
            
        Returns:
            ID of the stored memory
        """
        if metadata is None:
            metadata = {}
            
        # Add user_id and timestamp to metadata
        metadata.update({
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "type": "semantic_memory"
        })
        
        # Create document
        document = Document(
            page_content=text,
            metadata=metadata
        )
        
        # Generate ID
        memory_id = str(uuid.uuid4())
        
        # Add document to vector store
        self.vector_store.add_documents(
            documents=[document],
            ids=[memory_id]
        )
        
        logger.debug(f"Stored semantic memory {memory_id} for user {user_id}")
        return memory_id
    
    def retrieve_similar(
        self,
        user_id: str,
        query: str,
        k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[Document, float]]:
        """
        Retrieve semantically similar memories.
        
        Args:
            user_id: User ID to filter by
            query: Query text
            k: Number of results to return
            filter_metadata: Additional metadata filters
            
        Returns:
            List of (document, score) tuples
        """
        filter_dict = {"user_id": user_id}
        
        if filter_metadata:
            filter_dict.update(filter_metadata)
            
        results = self.vector_store.similarity_search_with_score(
            query=query,
            k=k,
            filter=filter_dict
        )
        
        logger.debug(f"Retrieved {len(results)} similar memories for user {user_id}")
        return results

    def query_knowledge(
        self,
        query: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    )->  List[Tuple[Document, float]]:
        """
        Query the knowledge base.

        Args:
            query: The search query
            top_k: Number of results to return
            filter_metadata: Optional metadata filters 
        Returns:
            List of matching documents with metadata
        """
        
        result_docs = self.vector_store.similarity_search_with_score(
            query=query,
            k=top_k,
            filter=filter_metadata
        )

        return result_docs

    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory by ID."""
        try:
            self.vector_store.delete(ids=[memory_id])
            logger.debug(f"Deleted semantic memory {memory_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting memory {memory_id}: {e}")
            return False
    
    def text_insert(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """
        Insert a batch of texts into semantic memory.
        
        Args:
            #user_id: User ID
            texts: List of text contents
            metadatas: Optional list of metadata dictionaries including doc type, topic and more
            
        Returns:
            List of memory IDs
        """
        # Generate IDs
        memory_ids = [str(uuid.uuid4()) for _ in range(len(texts))]
        
        # Create documents
        documents = []
        
        for i, text in enumerate(texts):
            metadata = metadatas[i] if metadatas and i < len(metadatas) else {}
            
            # Add user_id and timestamp to metadata
            metadata.update({
                "timestamp": datetime.utcnow().isoformat(),
                #"type": "semantic_memory"
            })
            
            documents.append(Document(
                page_content=text,
                metadata=metadata
            ))
        
        # Add documents to vector store
        self.vector_store.add_documents(
            documents=documents,
            ids=memory_ids
        )
        
        logger.debug(f"Batch inserted {len(memory_ids)} semantic memories for user {user_id}")
        return memory_ids
