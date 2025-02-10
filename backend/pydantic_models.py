from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import Optional


class ModelName(str, Enum):
    GPT4_O = "gpt-4o"
    GPT4_O_MINI = "gpt-4o-mini"


class QueryInput(BaseModel):
    question: str = Field(..., min_length=1, description="User's query")
    session_id: Optional[str] = Field(default=None, description="Session ID")
    model: ModelName = Field(default=ModelName.GPT4_O_MINI, description="OpenAI model to use for querying")
    user_id: Optional[str] = Field(default=None, description="Unique user identifier for analytics")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of the query")


class QueryResponse(BaseModel):
    answer: str
    session_id: str
    model: ModelName
    groq_metadata: dict = Field(default_factory=dict, description="Groq-specific metadata")
    error: Optional[str] = Field(default=None, description="Error message if the Groq API call fails")


class DocumentInfo(BaseModel):
    id: int = Field(..., description="Unique document identifier")
    filename: str = Field(..., min_length=1, description="Name of the uploaded document")
    upload_timestamp: datetime = Field(..., description="Timestamp when the document was uploaded")


class DeleteFileRequest(BaseModel):
    file_id: int = Field(..., description="ID of the file to be deleted")
    reason: Optional[str] = Field(default=None, description="Reason for deleting the document")
    user_id: Optional[int] = Field(default=None, description="ID of the user requesting the deletion")
    requested_at: datetime = Field(default_factory=datetime.utcnow, description="Time of deletion request")
