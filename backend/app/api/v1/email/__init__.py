from fastapi import APIRouter

router = APIRouter()

@router.get("/providers")
async def get_providers() -> dict:
    """Get list of supported email marketing providers"""
    return {
        "providers": [
            "mailchimp",
            "sendgrid",
            "constant_contact"
        ]
    } 