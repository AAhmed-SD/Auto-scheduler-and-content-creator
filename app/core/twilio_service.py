from twilio.rest import Client
import os
from dotenv import load_dotenv
from typing import Optional
from fastapi import HTTPException

# Load environment variables
load_dotenv()

class TwilioService:
    def __init__(self):
        self.client = Client(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )
        self.phone_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        if not all([self.client, self.phone_number]):
            raise HTTPException(
                status_code=500,
                detail="Twilio configuration is incomplete. Please check environment variables."
            )
    
    async def send_sms(self, to_number: str, message: str) -> dict:
        """
        Send an SMS message using Twilio
        
        Args:
            to_number (str): Recipient's phone number in E.164 format (e.g., +1234567890)
            message (str): Message content
            
        Returns:
            dict: Message details including SID and status
        """
        try:
            message = self.client.messages.create(
                body=message,
                from_=self.phone_number,
                to=to_number
            )
            
            return {
                "success": True,
                "message_sid": message.sid,
                "status": message.status,
                "to": message.to,
                "from": message.from_
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send SMS: {str(e)}"
            )
    
    async def send_verification_code(self, to_number: str) -> dict:
        """
        Send a verification code via SMS
        
        Args:
            to_number (str): Recipient's phone number in E.164 format
            
        Returns:
            dict: Verification details including code and status
        """
        try:
            # Generate a 6-digit verification code
            import random
            verification_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            
            message = f"Your verification code is: {verification_code}"
            
            result = await self.send_sms(to_number, message)
            
            return {
                "success": True,
                "verification_code": verification_code,
                "message_sid": result["message_sid"],
                "status": result["status"]
            }
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send verification code: {str(e)}"
            )
    
    async def send_notification(self, to_number: str, notification_type: str, data: dict) -> dict:
        """
        Send a formatted notification based on type
        
        Args:
            to_number (str): Recipient's phone number
            notification_type (str): Type of notification (e.g., 'content_scheduled', 'content_published')
            data (dict): Additional data for the notification
            
        Returns:
            dict: Notification details
        """
        try:
            message_templates = {
                "content_scheduled": "Your content '{title}' has been scheduled for {scheduled_time}",
                "content_published": "Your content '{title}' has been published successfully!",
                "team_invite": "You've been invited to join the team '{team_name}'",
                "content_approval": "New content '{title}' requires your approval"
            }
            
            if notification_type not in message_templates:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid notification type: {notification_type}"
                )
            
            message = message_templates[notification_type].format(**data)
            return await self.send_sms(to_number, message)
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send notification: {str(e)}"
            )

# Create a singleton instance
twilio_service = TwilioService() 