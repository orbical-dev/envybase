from pydantic import BaseModel, Field
from typing import Dict, Any


class Document(BaseModel):
    """Document model for creating new documents. The actual document content goes into the 'json' field."""

    json: Dict[str, Any] = Field(
        {},
        description="The actual document content as a JSON object."
    )
    
class Query(BaseModel):
    """Query model for querying documents."""

    query: Dict[str, Any] = Field(
        {},
        description="The query to filter documents."
    )
    limit: int = Field(
        0,
        description="The maximum number of documents to return. Default is 0 (No limit).",
    )
    
class Update(BaseModel):
    """Update model for updating documents."""

    query: Dict[str, Any] = Field(
        {},
        description="The query to filter documents."
    )
    update: Dict[str, Any] = Field(
        {},
        description="The update to apply to the documents."
    )
    
class Delete(BaseModel):
    """Query model for querying documents."""

    query: Dict[str, Any] = Field(
        {},
        description="The query to filter documents."
    )