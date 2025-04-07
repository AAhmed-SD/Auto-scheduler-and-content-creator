import firebase_admin
from firebase_admin import credentials, firestore, auth
from app.core.config import get_settings
from google.cloud import firestore as cloud_firestore
from typing import Optional, Dict, Any
import json
from fastapi import HTTPException, status

settings = get_settings()


def initialize_firebase() -> None:
    """Initialize Firebase Admin SDK"""
    try:
        # Get credentials from settings
        cred_dict = settings.get_firebase_credentials()

        # Initialize Firebase
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
    except ValueError as e:
        if "already exists" not in str(e):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Firebase initialization error: {str(e)}",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize Firebase: {str(e)}",
        )


def get_firestore() -> cloud_firestore.Client:
    """Get Firestore client instance"""
    try:
        return firestore.client()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Firestore client: {str(e)}",
        )


def get_auth() -> auth.Client:
    """Get Firebase Auth client instance"""
    try:
        return auth
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get Auth client: {str(e)}",
        )
