"""Nơi duy nhất tạo Supabase client.

Tách riêng để auth/storage không phải tự biết cách khởi tạo client, và để
đổi provider sau này chỉ cần sửa file này (hoặc thay client bằng thứ khác
cùng interface). Client được tạo lazy + cache, không tạo lúc import, nên
import module không cần .env hợp lệ.
"""

from __future__ import annotations

from functools import lru_cache

from supabase import Client, create_client

from src.config import settings


@lru_cache(maxsize=1)
def get_anon() -> Client:
    """Client quyền thấp. Dùng để xác thực token của user."""
    return create_client(settings.supabase_url, settings.supabase_anon_key)


@lru_cache(maxsize=1)
def get_admin() -> Client:
    """Client service_role: bỏ qua RLS. Chỉ dùng server-side, luôn scope theo user."""
    return create_client(settings.supabase_url, settings.supabase_service_role_key)
