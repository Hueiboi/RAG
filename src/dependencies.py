# dependencies.py
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from src.auth import AuthenticatedUser, verify_token

# Depends là DI container của FastAPI
# Nếu truyền thẳng chỉ là referrence -> không thể chạy
# Dùng depends fastapi tự inject để lấy kết quả

rag_chain = None
security = HTTPBearer()


def get_chain():
    return rag_chain


async def get_current_user(token: str = Depends(security)) -> AuthenticatedUser:
    """Xác thực request. Fail-closed: không có user hợp lệ thì luôn 401."""
    user = verify_token(token.credentials)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user
