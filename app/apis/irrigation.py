"""
Irrigation API endpoints for AgriSmart
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List
import logging

from ..models.schemas import UserResponse
from ..services.auth import get_current_user
from ..services.irrigation import get_irrigation_schedule, update_irrigation_schedule

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/schedule")
async def get_schedule(current_user: UserResponse = Depends(get_current_user)) -> Dict[str, Any]:
    """Get irrigation schedule for the current user"""
    try:
        schedule = await get_irrigation_schedule(current_user.id)
        return {
            "schedule": schedule
        }
    except Exception as e:
        logger.error(f"Error getting irrigation schedule: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching irrigation schedule"
        )

@router.post("/schedule")
async def update_schedule(
    schedule: List[Dict[str, Any]],
    current_user: UserResponse = Depends(get_current_user)
) -> Dict[str, Any]:
    """Update irrigation schedule for the current user"""
    try:
        updated_schedule = await update_irrigation_schedule(current_user.id, schedule)
        return {
            "schedule": updated_schedule,
            "message": "Schedule updated successfully"
        }
    except Exception as e:
        logger.error(f"Error updating irrigation schedule: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error updating irrigation schedule"
        )