import logging

logger = logging.getLogger(__name__)

def send_alert(user_id: str, message: str):
    # Mock notification: In real, integrate with email/SMS service like Twilio
    logger.info(f"Alert sent to user {user_id}: {message}")
    # For competition edge: Could add push notifications via Firebase