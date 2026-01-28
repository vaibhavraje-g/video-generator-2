# backend/app/utils/serializers.py
"""Shared MongoDB serialization utilities"""

from datetime import datetime
from typing import Any, Dict, List, Union
from bson import ObjectId
from enum import Enum


def serialize_value(value: Any) -> Any:
    """
    Recursively serialize a value to JSON-compatible format.
    
    Handles:
    - ObjectId -> str
    - datetime -> ISO format string
    - Enum -> value
    - dict -> recursive serialization
    - list -> recursive serialization
    """
    if value is None:
        return None
    
    if isinstance(value, ObjectId):
        return str(value)
    
    if isinstance(value, datetime):
        return value.isoformat()
    
    if isinstance(value, Enum):
        return value.value
    
    if isinstance(value, dict):
        return serialize_mongo_doc(value)
    
    if isinstance(value, list):
        return [serialize_value(item) for item in value]
    
    # Return primitive types as-is
    return value


def serialize_mongo_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a MongoDB document to a JSON-serializable dictionary.
    
    This handles all common BSON types that FastAPI's jsonable_encoder
    doesn't handle natively:
    - ObjectId -> string
    - datetime -> ISO format string  
    - Enum -> value
    - Nested documents and arrays
    
    Args:
        doc: MongoDB document (dict)
        
    Returns:
        JSON-serializable dictionary
        
    Example:
        >>> doc = {"_id": ObjectId("..."), "created_at": datetime.now()}
        >>> serialize_mongo_doc(doc)
        {"_id": "...", "created_at": "2024-01-01T00:00:00"}
    """
    if not doc:
        return doc
    
    result = {}
    for key, value in doc.items():
        result[key] = serialize_value(value)
    
    return result


def serialize_mongo_docs(docs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Serialize a list of MongoDB documents.
    
    Args:
        docs: List of MongoDB documents
        
    Returns:
        List of JSON-serializable dictionaries
    """
    return [serialize_mongo_doc(doc) for doc in docs]
