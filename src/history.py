"""Interface lịch sử hội thoại.

Hiện nó đi qua PostgREST của Supabase (`.table("chat_messages")`), KHÔNG qua
`DATABASE_URL`. Đây là chỗ dễ tưởng đã tách khỏi Supabase nhưng chưa: đổi
DATABASE_URL sang Postgres khác thì bảng chat_messages vẫn ở lại Supabase.

Gom vào đây để khi chuyển sang SQLAlchemy (cùng DB với vector) chỉ phải sửa
file này, route không đổi.
"""

from __future__ import annotations

from src.supabase_client import get_admin

TABLE = "chat_messages"


def save(user_id: str, role: str, content: str) -> None:
    get_admin().table(TABLE).insert(
        {"user_id": user_id, "role": role, "content": content}
    ).execute()


def list_for_user(user_id: str) -> list[dict]:
    """Toàn bộ lịch sử của user, cũ nhất trước."""
    response = (
        get_admin()
        .table(TABLE)
        .select("*")
        .eq("user_id", user_id)
        .order("created_at", desc=False)
        .execute()
    )
    return response.data or []
