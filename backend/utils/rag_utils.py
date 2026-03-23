from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.schema import Document

class RAGHelper:
    """Helper class for Retrieval Augmented Generation"""
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
    
    def create_vector_store(self, documents: List[str], metadata: List[Dict] = None) -> FAISS:
        """Create vector store from documents"""
        
        # Create Document objects
        docs = []
        for i, doc in enumerate(documents):
            meta = metadata[i] if metadata and i < len(metadata) else {}
            docs.append(Document(page_content=doc, metadata=meta))
        
        # Split documents
        split_docs = self.text_splitter.split_documents(docs)
        
        # Create vector store
        vector_store = FAISS.from_documents(split_docs, self.embeddings)
        
        return vector_store
    
    def similarity_search(self, vector_store: FAISS, query: str, k: int = 5) -> List[Document]:
        """Perform similarity search"""
        return vector_store.similarity_search(query, k=k)
    
    def get_relevant_context(self, documents: List[str], query: str, k: int = 3) -> str:
        """Get relevant context for a query"""
        
        if not documents:
            return ""
        
        # Create temporary vector store
        vector_store = self.create_vector_store(documents)
        
        # Search for relevant chunks
        relevant_docs = self.similarity_search(vector_store, query, k=k)
        
        # Combine relevant content
        context = "\n\n".join([doc.page_content for doc in relevant_docs])
        
        return context