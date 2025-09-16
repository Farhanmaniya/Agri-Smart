"""Test imports to ensure everything is working correctly."""

try:
    from app.main import app
    print("✅ Main app imports successful")
except Exception as e:
    print(f"❌ Error importing main app: {str(e)}")

try:
    from app.models.schemas import UserCreate, UserLogin
    print("✅ Schema imports successful")
except Exception as e:
    print(f"❌ Error importing schemas: {str(e)}")

try:
    from app.services.auth import auth_service
    print("✅ Services imports successful")
except Exception as e:
    print(f"❌ Error importing services: {str(e)}")

try:
    from app.utils.security import create_access_token
    print("✅ Utils imports successful")
except Exception as e:
    print(f"❌ Error importing utils: {str(e)}")