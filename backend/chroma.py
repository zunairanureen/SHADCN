from typing import List
import os
import logging

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredHTMLLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,  
    chunk_overlap=50,  
    length_function=len,
    separators=["\n\n", "\n", " ", ""]  
)

embedding_function = OpenAIEmbeddings(api_key='') # Ensure API key is passed


vectorstore = Chroma(
    persist_directory="./chroma_db",
    embedding_function=embedding_function,
    collection_name="documents",
)

def load_and_split_document(file_path: str) -> List[Document]:
    """Loads and splits a document into smaller text chunks."""
    logger.info(f"Loading document: {file_path}")
    
    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith('.docx'):
        loader = Docx2txtLoader(file_path)
    elif file_path.endswith('.html'):
        loader = UnstructuredHTMLLoader(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_path}")
    
    documents = loader.load()
    splits = text_splitter.split_documents(documents)
    logger.info(f"Document split into {len(splits)} chunks")
    return splits

def reset_chroma_collection():
    """Reset the entire Chroma collection."""
    try:
        logger.info("Resetting Chroma collection")
        vectorstore._collection.delete(where={})
        logger.info("Chroma collection reset successful")
        return True
    except Exception as e:
        logger.error(f"Error resetting Chroma collection: {e}")
        return False

def index_document_to_chroma(file_path: str, file_id: int) -> bool:
    """Indexes a document into ChromaDB after splitting it into chunks."""
    try:
        logger.info(f"Starting indexing for document {file_path} with file_id {file_id}")
        
        
        delete_doc_from_chroma(file_id)
        
        
        splits = load_and_split_document(file_path)
        
        
        for split in splits:
            split.metadata.update({
                'file_id': str(file_id),
                'source': file_path,
                'chunk_size': len(split.page_content)
            })
        
       
        vectorstore.add_documents(splits)
        logger.info(f"Successfully indexed {len(splits)} chunks for file_id {file_id}")
        
        return True
    except Exception as e:
        logger.error(f"Error indexing document: {e}")
        return False

def delete_doc_from_chroma(file_id: int) -> bool:
    """Deletes all document chunks related to the given file_id from ChromaDB."""
    try:
        file_id_str = str(file_id)
        logger.info(f"Deleting document chunks for file_id {file_id}")
        
        
        docs_before = vectorstore._collection.get(where={"file_id": file_id_str})
        count_before = len(docs_before['ids']) if docs_before and 'ids' in docs_before else 0
        
        vectorstore._collection.delete(where={"file_id": file_id_str})
        
        logger.info(f"Deleted {count_before} chunks for file_id {file_id}")
        return True
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        return False

def query_document(query: str, file_id: int = None, k: int = 4):
    """
    Query the vectorstore for relevant document chunks.
    If file_id is provided, only search within that document.
    """
    try:
        logger.info(f"Querying with: '{query}' {'for file_id: ' + str(file_id) if file_id else 'across all documents'}")
        
        search_kwargs = {}
        if file_id is not None:
            search_kwargs['filter'] = {"file_id": str(file_id)}
        
        results = vectorstore.similarity_search(
            query,
            k=k,
            **search_kwargs
        )
        
        for idx, doc in enumerate(results):
            logger.info(f"Result {idx + 1} metadata: {doc.metadata}")
        
        return results
    except Exception as e:
        logger.error(f"Error during query: {e}")
        return []

def get_collection_stats():
    """Get statistics about the current collection."""
    try:
        all_docs = vectorstore._collection.get()
        return {
            'total_documents': len(all_docs['ids']) if 'ids' in all_docs else 0,
            'unique_file_ids': len(set(all_docs['metadatas'][i]['file_id'] 
                                     for i in range(len(all_docs['ids']))))
            if 'metadatas' in all_docs else 0
        }
    except Exception as e:
        logger.error(f"Error getting collection stats: {e}")
        return {'error': str(e)}
