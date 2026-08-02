# dependencies.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from supabase import create_client
from src.config import settings

rag_chain = None
security = HTTPBearer()
supabase = create_client(settings.supabase_url, settings.supabase_anon_key)

def get_chain():
    return rag_chain

async def get_current_user(token: str = Depends(security)): 
    try: 
        response = supabase.auth.get_user(token.credentials)
        return response.user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")