# backend/tests/conftest.py
"""Pytest configuration and shared fixtures"""

import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from faker import Faker

from app.core.config import settings
from app.db import MongoDB
from app.models import UserCreate
from app.services.auth_service import AuthService

fake = Faker()

_MONGO_ALIVE = None

async def check_mongo_alive():
    global _MONGO_ALIVE
    if _MONGO_ALIVE is not None:
        return _MONGO_ALIVE
    try:
        check_client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=800)
        await check_client.admin.command('ping')
        check_client.close()
        _MONGO_ALIVE = True
    except Exception:
        _MONGO_ALIVE = False
    return _MONGO_ALIVE


# Test database name
TEST_DB_NAME = "video_generator_test"


@pytest_asyncio.fixture
async def test_db():
    """
    Create a test database connection
    Automatically cleans up after tests, or skips gracefully if MongoDB is offline.
    """
    if not await check_mongo_alive():
        pytest.skip(f"MongoDB not running locally on {settings.MONGODB_URL}; skipping database integration test.")

    # Override database name for tests
    original_db_name = settings.MONGODB_DB_NAME
    settings.MONGODB_DB_NAME = TEST_DB_NAME
    
    # Connect to test database
    await MongoDB.connect_db()
    db = MongoDB.get_db()
    
    yield db
    
    # Cleanup: drop all collections
    try:
        for collection_name in await db.list_collection_names():
            await db.drop_collection(collection_name)
        await MongoDB.close_db()
    except Exception:
        pass
    
    settings.MONGODB_DB_NAME = original_db_name


@pytest_asyncio.fixture
async def auth_service(test_db):
    """Auth service fixture"""
    return AuthService()


@pytest_asyncio.fixture
async def test_user(auth_service):
    """
    Create a test user
    """
    user_data = UserCreate(
        email=fake.email(),
        username=fake.user_name(),
        password="testpassword123"
    )
    
    user = await auth_service.create_user(user_data)
    return user, "testpassword123"  # Return user and password


@pytest_asyncio.fixture
async def test_user_tokens(auth_service, test_user):
    """
    Create a test user with authentication tokens
    """
    user, password = test_user
    tokens = auth_service.create_tokens(user)
    return user, tokens


@pytest.fixture
def valid_user_data():
    """Generate valid user registration data"""
    return {
        "email": fake.email(),
        "username": fake.user_name(),
        "password": "securepassword123"
    }


@pytest.fixture
def valid_project_data():
    """Generate valid project data"""
    return {
        "name": fake.company(),
        "description": fake.text(max_nb_chars=200)
    }
