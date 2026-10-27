"""Đưa toàn bộ tài liệu trong data/ lên Supabase Storage và ingest vào pgvector.

Vì sao cần script này: app không đọc data/. Ingestion lấy bytes từ Storage,
nên file nằm trong data/ chưa chắc đã có trong index. Script đi đúng đường của
route /api/upload (storage.upload -> load_or_build), chỉ bỏ tầng HTTP.

Chạy lại nhiều lần vẫn an toàn: load_or_build xoá vector cũ của đúng cặp
(user_id, file_name) trước khi thêm, nên không sinh chunk trùng.

    python -m eval.seed_corpus --user-id <uuid>
    python -m eval.seed_corpus --user-id <uuid> --dry-run
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from sqlalchemy import text

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SUFFIXES = {".txt", ".pdf", ".docx"}


def count_chunks(engine, user_id: str, file_name: str) -> int:
    with engine.connect() as conn:
        return conn.execute(
            text(
                "SELECT count(*) FROM langchain_pg_embedding "
                "WHERE cmetadata->>'user_id' = :uid "
                "AND cmetadata->>'file_name' = :fname"
            ),
            {"uid": user_id, "fname": file_name},
        ).scalar_one()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--user-id", required=True, help="UUID user sở hữu tài liệu")
    ap.add_argument("--dry-run", action="store_true",
                    help="chỉ liệt kê file sẽ xử lý, không upload/ingest")
    args = ap.parse_args()

    logging.basicConfig(level=logging.WARNING, format="%(levelname)s | %(message)s")

    files = [p for p in sorted(DATA_DIR.iterdir())
             if p.is_file() and p.suffix.lower() in SUFFIXES]
    if not files:
        print(f"Không có file {sorted(SUFFIXES)} nào trong {DATA_DIR}")
        return 1

    print(f"Sẽ xử lý {len(files)} file cho user {args.user_id}\n")
    if args.dry_run:
        for p in files:
            print(f"  {p.name:45} {p.stat().st_size:>8} bytes")
        return 0

    # Import trễ để --dry-run không phải load embedding model.
    from src import storage
    from src.ingestion import connect_to_pgvector, load_or_build

    vectorstore = connect_to_pgvector()
    engine = vectorstore._engine

    failed: list[tuple[str, str]] = []
    for p in files:
        try:
            storage.upload(args.user_id, p.name, p.read_bytes())
            load_or_build(user_id=args.user_id, files_to_rebuild=[p.name])
            n = count_chunks(engine, args.user_id, p.name)
            if n == 0:
                raise RuntimeError("0 chunk sau khi ingest")
            print(f"  [ok]   {p.name:45} {n:4} chunk")
        except Exception as e:  # giữ lại lỗi của từng file, không dừng cả batch
            failed.append((p.name, f"{type(e).__name__}: {e}"))
            print(f"  [FAIL] {p.name:45} {type(e).__name__}: {e}")

    with engine.connect() as conn:
        total = conn.execute(
            text(
                "SELECT count(*) FROM langchain_pg_embedding "
                "WHERE cmetadata->>'user_id' = :uid"
            ),
            {"uid": args.user_id},
        ).scalar_one()
        n_files = conn.execute(
            text(
                "SELECT count(DISTINCT cmetadata->>'file_name') "
                "FROM langchain_pg_embedding WHERE cmetadata->>'user_id' = :uid"
            ),
            {"uid": args.user_id},
        ).scalar_one()

    print(f"\nTổng: {total} chunk / {n_files} file trong DB cho user này")
    if failed:
        print(f"\n{len(failed)} file lỗi:")
        for name, err in failed:
            print(f"  - {name}: {err}")
        return 1

    print("Không có file lỗi.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
