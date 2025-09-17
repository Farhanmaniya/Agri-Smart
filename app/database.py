"""
Database configuration and utilities for AgriSmart Backend.
Uses Supabase for data storage with Row Level Security.
"""

import os
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from dotenv import load_dotenv
import logging
from datetime import datetime

load_dotenv()
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_ANON_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set")
        
        self.client = create_client(url, key)
        
    async def execute_query(self, table: str, query_type: str, **kwargs) -> Dict[str, Any]:
        """Execute a query on Supabase."""
        try:
            query = self.client.table(table)
            
            if query_type == "select":
                result = query.select("*")
            elif query_type == "insert":
                result = query.insert(kwargs.get("data", {}))
            elif query_type == "update":
                result = query.update(kwargs.get("data", {})).eq("id", kwargs.get("id"))
            elif query_type == "delete":
                result = query.delete().eq("id", kwargs.get("id"))
            else:
                raise ValueError(f"Unknown query type: {query_type}")
                
            response = result.execute()
            return response.data
            
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            raise

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        try:
            response = await self.execute_query(
                "users",
                "select",
                data={"email": email}
            )
            return response[0] if response else None
        except Exception as e:
            logger.error(f"Error getting user by email: {str(e)}")
            return None

    async def create_user(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create a new user."""
        try:
            response = await self.execute_query(
                "users",
                "insert",
                data=user_data
            )
            return response[0] if response else None
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return None

    async def save_prediction(self, prediction_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Save a prediction result."""
        try:
            prediction_data["created_at"] = datetime.utcnow().isoformat()
            response = await self.execute_query(
                "predictions",
                "insert",
                data=prediction_data
            )
            return response[0] if response else None
        except Exception as e:
            logger.error(f"Error saving prediction: {str(e)}")
            return None

    async def get_user_predictions(self, user_id: str) -> List[Dict[str, Any]]:
        """Get predictions for a specific user."""
        try:
            response = await self.execute_query(
                "predictions",
                "select",
                data={"user_id": user_id}
            )
            return response if response else []
        except Exception as e:
            logger.error(f"Error getting user predictions: {str(e)}")
            return []

# Global database instance
db = DatabaseManager()