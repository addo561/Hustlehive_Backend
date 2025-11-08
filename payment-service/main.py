from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import requests
import uuid
import os
from dotenv import load_dotenv