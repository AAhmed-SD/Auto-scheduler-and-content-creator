from twilio.rest import Client
import os
from dotenv import load_dotenv
import asyncio
from twilio_service import twilio_service

# Load environment variables
load_dotenv()

def test_twilio_credentials():
    try:
        # Initialize Twilio client
        client = Client(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )
        
        # Test credentials by fetching account info
        account = client.api.accounts(os.getenv('TWILIO_ACCOUNT_SID')).fetch()
        print(f"✅ Twilio credentials verified successfully!")
        print(f"Account Status: {account.status}")
        print(f"Account Type: {account.type}")
        
        return True
    except Exception as e:
        print(f"❌ Error verifying Twilio credentials: {str(e)}")
        return False

def send_test_message(to_number):
    try:
        client = Client(
            os.getenv('TWILIO_ACCOUNT_SID'),
            os.getenv('TWILIO_AUTH_TOKEN')
        )
        
        message = client.messages.create(
            body="This is a test message from your Auto-Scheduler app!",
            from_=os.getenv('TWILIO_PHONE_NUMBER'),
            to=to_number
        )
        
        print(f"✅ Test message sent successfully!")
        print(f"Message SID: {message.sid}")
        print(f"Status: {message.status}")
        
        return True
    except Exception as e:
        print(f"❌ Error sending test message: {str(e)}")
        return False

async def test_twilio_service():
    # Test phone number (replace with your number)
    test_number = "+1234567890"  # Replace with actual number
    
    try:
        # Test basic SMS
        print("\nTesting basic SMS...")
        result = await twilio_service.send_sms(
            test_number,
            "This is a test message from the Auto-Scheduler service."
        )
        print("SMS Result:", result)
        
        # Test verification code
        print("\nTesting verification code...")
        verification = await twilio_service.send_verification_code(test_number)
        print("Verification Result:", verification)
        
        # Test notifications
        print("\nTesting content scheduled notification...")
        notification = await twilio_service.send_notification(
            test_number,
            "content_scheduled",
            {"title": "Test Content", "scheduled_time": "2024-03-20 15:00:00"}
        )
        print("Notification Result:", notification)
        
    except Exception as e:
        print(f"Error during testing: {str(e)}")

if __name__ == "__main__":
    print("Testing Twilio Integration...")
    if test_twilio_credentials():
        # Replace with your test phone number
        test_number = input("Enter a phone number to send test message (format: +1234567890): ")
        send_test_message(test_number)
    else:
        asyncio.run(test_twilio_service()) 