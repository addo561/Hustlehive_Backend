from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
import uuid
import os
from dotenv import load_dotenv


#load environment variables
load_dotenv()

#Api attributes
app = FastAPI(
    title='Momo payment  Api',
    description="API for processing Mobile Money payments via MTN Momo",
    version='1.0.0'
)

#CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    alow_methods = ['*'],
    alow_headers = ['*']
)

#from momo api 
CONFIG = {
    "SUBSCRIPTION_PRIMARY_KEY": os.getenv("SUBSCRIPTION_PRIMARY_KEY"),
    "API_USER_ID": os.getenv("API_USER_ID"),
    "API_KEY": os.getenv("API_KEY"),
    "TARGET_ENVIRONMENT": os.getenv("TARGET_ENVIRONMENT"),
    "MOMO_BASE_URL": os.getenv("MOMO_BASE_URL"),
}

#validate  config

for key ,value in CONFIG.items():
    if not value and  key != 'TARGET_ENVIRONMENT':
        raise Exception(f'Missing env variable: {key}')
    
    


