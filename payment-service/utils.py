from dotenv import load_dotenv
import os
import requests
from fastapi import  HTTPException
import base64


CONFIG = {
    "SUBSCRIPTION_PRIMARY_KEY": os.getenv("SUBSCRIPTION_PRIMARY_KEY"),
    "API_USER_ID": os.getenv("API_USER_ID"),
    "API_KEY": os.getenv("API_KEY"),
    "TARGET_ENVIRONMENT": os.getenv("TARGET_ENVIRONMENT"),
    "MOMO_BASE_URL": os.getenv("MOMO_BASE_URL"),
}

def get_momo_token() -> str:
    """Get access token from MTN Momo API"""
    url = f"{CONFIG['MOMO_BASE_URL']}/collection/token/"
    
    # Create the base64 encoded string in format: API_USER_ID:API_KEY
    credentials = f"{CONFIG['API_USER_ID']}:{CONFIG['API_KEY']}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    
    print(f"🔧 Debug: Encoded credentials: {encoded_credentials}")
    
    headers = {
        "Authorization": f"Basic {encoded_credentials}",
        "Ocp-Apim-Subscription-Key": CONFIG["SUBSCRIPTION_PRIMARY_KEY"],
    }
    
    try:
        response = requests.post(url, headers=headers)
        print(f"🔧 Debug: Token response status: {response.status_code}")
        print(f"🔧 Debug: Token response text: {response.text}")
        
        response.raise_for_status()
        token_data = response.json()
        print(f"🔧 Debug: Token received: {token_data.get('access_token', '')[:20]}...")
        return token_data["access_token"]
    except requests.exceptions.RequestException as e:
        print(f"🔧 Debug: Token request failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get access token: {str(e)}"
        )