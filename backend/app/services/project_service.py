# backend/app/services/project_service.py
"""Project management service"""

from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from app.db import get_database
from app.models import ProjectCreate, Project
from app.utils import serialize_mongo_doc

# UUID for dev user (a valid ObjectId pattern)
DEV_USER_OBJECT_ID = ObjectId("000000000000000000000001")

def _get_user_oid(user_id: str) -> ObjectId:
    """Safely convert user_id to ObjectId, handling dev mode bypass"""
    if user_id == "dev_user_id":
        return DEV_USER_OBJECT_ID
    return ObjectId(user_id)


class ProjectService:
    """Service for project management"""
    
    def __init__(self):
        self.db = get_database()
        self.projects_collection = self.db.projects
        self.videos_collection = self.db.videos
    
    async def create_project(self, user_id: str, project_data: ProjectCreate, tenant_id: Optional[str] = None) -> Project:
        """Create a new project for a user and tenant"""
        user_oid = _get_user_oid(user_id)
        active_tenant = tenant_id or user_id
        project_dict = {
            "user_id": user_oid,  # Store as ObjectId in DB
            "tenant_id": active_tenant,
            "name": project_data.name,
            "description": project_data.description,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        
        result = await self.projects_collection.insert_one(project_dict)
        
        # Convert ObjectIds to strings for Pydantic model
        project_dict["_id"] = str(result.inserted_id)
        project_dict["user_id"] = str(user_oid)
        project_dict["tenant_id"] = active_tenant
        
        return Project(**project_dict)
    
    async def get_user_projects(
        self, user_id: str, skip: int = 0, limit: int = 20, tenant_id: Optional[str] = None
    ) -> List[Project]:
        """Get all projects for a user/tenant with pagination"""
        user_oid = _get_user_oid(user_id)
        if tenant_id:
            query = {
                "$or": [
                    {"tenant_id": tenant_id},
                    {"tenant_id": {"$exists": False}, "user_id": user_oid}
                ]
            }
        else:
            query = {"user_id": user_oid}

        cursor = self.projects_collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        
        projects = []
        async for project_dict in cursor:
            # Convert ObjectIds to strings for Pydantic
            project_dict["_id"] = str(project_dict["_id"])
            project_dict["user_id"] = str(project_dict["user_id"])
            project_dict["tenant_id"] = project_dict.get("tenant_id") or str(project_dict["user_id"])
            projects.append(Project(**project_dict))
        
        return projects
    
    async def get_project(self, project_id: str, user_id: str, tenant_id: Optional[str] = None) -> Optional[Project]:
        """Get a specific project with tenant ownership verification"""
        if not ObjectId.is_valid(project_id):
            return None
        
        user_oid = _get_user_oid(user_id)
        if tenant_id:
            query = {
                "_id": ObjectId(project_id),
                "$or": [
                    {"tenant_id": tenant_id},
                    {"tenant_id": {"$exists": False}, "user_id": user_oid}
                ]
            }
        else:
            query = {"_id": ObjectId(project_id), "user_id": user_oid}

        project_dict = await self.projects_collection.find_one(query)
        
        if not project_dict:
            return None
        
        # Convert ObjectIds to strings for Pydantic
        project_dict["_id"] = str(project_dict["_id"])
        project_dict["user_id"] = str(project_dict["user_id"])
        project_dict["tenant_id"] = project_dict.get("tenant_id") or str(project_dict["user_id"])
        
        return Project(**project_dict)
    
    async def delete_project(self, project_id: str, user_id: str, tenant_id: Optional[str] = None) -> bool:
        """Delete a project and all associated videos with tenant verification"""
        if not ObjectId.is_valid(project_id):
            return False
        
        project = await self.get_project(project_id, user_id, tenant_id)
        if not project:
            return False
        
        # Delete associated videos
        await self.videos_collection.delete_many({"project_id": ObjectId(project_id)})
        
        # Delete project
        result = await self.projects_collection.delete_one({
            "_id": ObjectId(project_id)
        })
        
        return result.deleted_count > 0
    
    async def get_project_history(self, project_id: str, user_id: str, tenant_id: Optional[str] = None) -> List[dict]:
        """Get video generation history for a project with tenant verification"""
        project = await self.get_project(project_id, user_id, tenant_id)
        if not project:
            return []
        
        cursor = self.videos_collection.find(
            {"project_id": ObjectId(project_id)}
        ).sort("created_at", -1)
        
        videos = []
        async for video_dict in cursor:
            videos.append(serialize_mongo_doc(video_dict))
        
        return videos
