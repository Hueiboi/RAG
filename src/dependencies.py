# dependencies.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from supabase import create_client
from src.config import settings

# Depends là DI container của FastAPI
# Nếu truyền thẳng chỉ là referrence -> không thể chạy
# Dùng depends fastapi tự inject để lấy kết quả

rag_chain = None
security = HTTPBearer()
supabase = create_client(settings.supabase_url, settings.supabase_anon_key)
supabase_admin = create_client(settings.supabase_url, settings.supabase_service_role_key)

def get_chain():
    return rag_chain

async def get_current_user(token: str = Depends(security)): 
    try: 
        response = supabase.auth.get_user(token.credentials)
        return response.user
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")