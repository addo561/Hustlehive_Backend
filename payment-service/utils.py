from dotenv import load_dotenv
import os
import requests
from fastapi import  HTTPException


CONFIG = {
    "SUBSCRIPTION_PRIMARY_KEY": os.getenv("SUBSCRIPTION_PRIMARY_KEY"),
    "API_USER_ID": os.getenv("API_USER_ID"),
    "API_KEY": os.getenv("API_KEY"),
    "TARGET_ENVIRONMENT": os.getenv("TARGET_ENVIRONMENT"),
    "MOMO_BASE_URL": os.getenv("MOMO_BASE_URL"),
}

# Utility func
def get_momo_token() -> str:
    """Get access token from MTN Momo API"""
    url = f"{CONFIG['MOMO_BASE_URL']}/collection/token/"
    headers = {
        "Authorization": f"Basic {CONFIG['API_KEY']}",
        "Ocp-Apim-Subscription-Key": CONFIG["SUBSCRIPTION_PRIMARY_KEY"],
    }
    
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        return response.json()["access_token"]
    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get access token: {str(e)}"
        )