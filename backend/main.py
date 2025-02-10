from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # Import CORS middleware
from pydantic_models import QueryInput, QueryResponse, DocumentInfo, DeleteFileRequest
from langchain_utils import get_rag_chain
from sql_lite import initialize_database, insert_application_logs, get_chat_history, get_all_documents, insert_document_record, delete_document_record
import os
import uvicorn
import uuid
import logging
from datetime import datetime
import shutil

# Import Chroma functions
from chroma import index_document_to_chroma, delete_doc_from_chroma

# Configure logging
logging.basicConfig(filename='app.log', level=logging.INFO)

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:3333",  # Add your frontend URL here
    "https://shadcn-chatbot-kit.vercel.app",  # Add your production frontend URL here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the database at app startup
initialize_database()

# /chat endpoint - Get chat response from RAG system
@app.post("/chat", response_model=QueryResponse)
def chat(query_input: QueryInput):
    session_id = query_input.session_id
    logging.info(f"Session ID: {session_id}, User Query: {query_input.question}, Model: {query_input.model.value}, Timestamp: {datetime.utcnow()}")

    if not session_id:
        session_id = str(uuid.uuid4())

    # Retrieve chat history
    chat_history = get_chat_history(session_id)

    # Get RAG chain and invoke it for response
    rag_chain = get_rag_chain(query_input.model.value)
    response = rag_chain.invoke({
        "input": query_input.question,
        "chat_history": chat_history
    })

    answer = response['answer']

    # Log application
    insert_application_logs(session_id, query_input.question, answer, query_input.model.value)
    logging.info(f"Session ID: {session_id}, AI Response: {answer}, Timestamp: {datetime.utcnow()}")

    return QueryResponse(answer=answer, session_id=session_id, model=query_input.model)

# /upload-doc endpoint - Upload and index document
@app.post("/upload-doc")
def upload_and_index_document(file: UploadFile = File(...)):
    allowed_extensions = ['.pdf', '.docx', '.html']
    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed types are: {', '.join(allowed_extensions)}")

    temp_file_path = f"temp_{file.filename}"

    try:
        # Save the uploaded file to a temporary file
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_id = insert_document_record(file.filename)
        success = index_document_to_chroma(temp_file_path, file_id)

        if success:
            return {"message": f"File {file.filename} has been successfully uploaded and indexed.", "file_id": file_id}
        else:
            delete_document_record(file_id)
            raise HTTPException(status_code=500, detail=f"Failed to index {file.filename}.")
    except Exception as e:
        logging.error(f"Error uploading and indexing document {file.filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred while uploading the file.")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

# /list-docs endpoint - List all documents
@app.get("/list-docs", response_model=list[DocumentInfo])
def list_documents(skip: int = 0, limit: int = 10):
    all_docs = get_all_documents()
    return all_docs[skip:skip+limit]

# /delete-doc endpoint - Delete a document from the system
@app.post("/delete-doc")
def delete_document(request: DeleteFileRequest):
    try:
        chroma_delete_success = delete_doc_from_chroma(request.file_id)
        if chroma_delete_success:
            db_delete_success = delete_document_record(request.file_id)
            if db_delete_success:
                return {"message": f"Successfully deleted document with file_id {request.file_id} from the system."}
            else:
                raise HTTPException(status_code=500, detail="Failed to delete from database.")
        else:
            raise HTTPException(status_code=500, detail="Failed to delete document from Chroma.")
    except Exception as e:
        logging.error(f"Error deleting document with file_id {request.file_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
