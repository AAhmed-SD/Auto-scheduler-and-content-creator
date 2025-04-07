from fastapi import APIRouter

router = APIRouter()

@router.get("/platforms")
async def get_platforms() -> dict:
    """Get list of supported social media platforms"""
    return {
        "platforms": [
            "facebook",
            "twitter",
            "instagram",
            "linkedin"
        ]
    } 