"""Interface xác thực.

Toàn bộ phần còn lại của app chỉ biết `verify_token()` và `AuthenticatedUser`,
không biết token đến từ Supabase hay từ đâu. Muốn đổi sang JWT tự phát, Cognito,
Auth0... thì sửa đúng file này.

Token vẫn được Supabase phát hành ở phía frontend (@supabase/ssr) - đây là
phần phụ thuộc còn lại duy nhất, và nó chỉ nằm ở 1 hàm.
"""

from __future__ import annotations

import logging as log
from dataclasses import dataclass

from src.supabase_client import get_anon


@dataclass(frozen=True)
class AuthenticatedUser:
    """User đã xác thực trong phạm vi một request.

    Chỉ giữ những gì app thật sự dùng. Object user của Supabase rất nặng
    (metadata, app_metadata, identities...) và từng bị đẩy vào LangSmith trace.
    """

    id: str
    email: str | None = None


def verify_token(token: str) -> AuthenticatedUser | None:
    """Đổi access token thành user. Trả None nếu token không hợp lệ.

    Trả None thay vì raise để tầng gọi tự quyết định HTTP status, và để không
    có đường nào lọt qua khi provider trả về response rỗng (user=None).
    """
    if not token:
        return None

    try:
        response = get_anon().auth.get_user(token)
    except Exception as e:  # token hết hạn, sai chữ ký, mất mạng...
        log.info("Token verification failed: %s", e)
        return None

    user = getattr(response, "user", None)
    if user is None:
        # Provider có thể trả response không lỗi nhưng không có user.
        # Đây chính là cái bẫy fail-open cần chặn.
        return None

    return AuthenticatedUser(id=user.id, email=getattr(user, "email", None))
