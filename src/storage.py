"""Interface lưu trữ file.

App chỉ biết user_id + file_name; không biết file nằm ở Supabase Storage,
S3, hay thư mục local. Đổi provider = sửa đúng file này.

Mọi hàm đều nhận user_id và tự ghép thành prefix `{user_id}/`, nên không có
đường nào đọc/ghi chéo user nếu tầng gọi truyền đúng user_id từ token.
"""

from __future__ import annotations

import logging as log
from pathlib import Path

from src.supabase_client import get_admin

BUCKET = "documents"


def _object_path(user_id: str, file_name: str) -> str:
    """Ghép object path, chỉ giữ tên file cuối để chặn `../` và tên có dấu /."""
    name = Path(file_name).name
    if not name or name in {".", ".."}:
        raise ValueError(f"Invalid file name: {file_name!r}")
    return f"{user_id}/{name}"


def download(user_id: str, file_name: str) -> bytes:
    """Tải nội dung file. Raise nếu file không tồn tại."""
    path = _object_path(user_id, file_name)
    log.info("Downloading %s", path)
    return get_admin().storage.from_(BUCKET).download(path)


def list_files(user_id: str) -> list[dict]:
    """Danh sách file của user, đã bỏ thư mục con và chuẩn hoá shape.

    Trả về shape cố định của app, không phải shape của provider, để route
    không phải biết Supabase trả field gì.
    """
    items = get_admin().storage.from_(BUCKET).list(path=f"{user_id}")

    files = []
    for item in items:
        name = item.get("name")
        if not name or name.endswith("/"):
            continue
        files.append(
            {
                "name": name,
                "size": item.get("metadata", {}).get("size"),
                "created_at": item.get("created_at"),
            }
        )
    return files


def upload(user_id: str, file_name: str, content: bytes) -> None:
    """Ghi đè file nếu đã tồn tại (upsert)."""
    path = _object_path(user_id, file_name)
    get_admin().storage.from_(BUCKET).upload(
        path=path,
        file=content,
        file_options={"upsert": "true"},
    )
    log.info("Uploaded %s (%d bytes)", path, len(content))


def remove(user_id: str, file_name: str) -> None:
    path = _object_path(user_id, file_name)
    get_admin().storage.from_(BUCKET).remove(paths=[path])
    log.info("Removed %s", path)
