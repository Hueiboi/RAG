"""Đo chất lượng retrieval trên bộ eval cố định (data/eval_set.json).

Mục đích: có một con số trước/sau mỗi thay đổi retrieval (threshold, hybrid, chunking...).
Không gọi LLM, chỉ đo bước truy hồi -> chạy nhanh và không tốn token.

Cách dùng:

    # Kiểm tra bộ eval có hợp lệ không (không cần DB)
    python -m eval.run_eval --validate-only

    # Chạy đo thật, ghi thêm một mục vào data/eval_log.md
    python -m eval.run_eval --label baseline --user-id <uuid>

Mỗi lần chạy ghi APPEND vào data/eval_log.md, không sửa mục cũ -> giữ được
lịch sử theo thời điểm để viết báo cáo sau này.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
EVAL_SET = DATA_DIR / "eval_set.json"
LOG_FILE = DATA_DIR / "eval_log.md"


# --------------------------------------------------------------------------
# Chuẩn hoá văn bản
# --------------------------------------------------------------------------

def normalize(text: str) -> str:
    """Chuẩn hoá để so khớp anchor.

    Chỉ xử lý khoảng trắng và hoa/thường: PDF extract hay chèn newline giữa
    các dòng nên phải gộp lại, còn dấu tiếng Việt thì giữ nguyên (anchor là
    tiếng Anh nên không cần bỏ dấu).
    """
    return re.sub(r"\s+", " ", text).strip().lower()


def find_rank(anchor: str, docs: list) -> int | None:
    """Trả về rank (1-based) của chunk chứa anchor, None nếu không có."""
    needle = normalize(anchor)
    for i, doc in enumerate(docs, start=1):
        if needle in normalize(doc.page_content):
            return i
    return None


# --------------------------------------------------------------------------
# Nạp dữ liệu
# --------------------------------------------------------------------------

def load_eval_set() -> list[dict]:
    with EVAL_SET.open(encoding="utf-8") as f:
        items = json.load(f)

    required = {"id", "query", "ground_truth", "context_anchor"}
    for item in items:
        missing = required - item.keys()
        if missing:
            raise SystemExit(f"Câu {item.get('id', '?')} thiếu field: {sorted(missing)}")
    return items


def corpus_texts() -> list[tuple[str, str]]:
    """Đọc toàn bộ file trong data/ thành (tên file, text). Dùng cho --validate-only."""
    texts = []
    for path in sorted(DATA_DIR.iterdir()):
        if path.suffix.lower() == ".pdf":
            from pypdf import PdfReader

            text = "\n".join(p.extract_text() or "" for p in PdfReader(path).pages)
            texts.append((path.name, text))
        elif path.suffix.lower() == ".txt":
            texts.append((path.name, path.read_text(encoding="utf-8")))
    return texts


# --------------------------------------------------------------------------
# Chế độ 1: validate bộ eval (không cần DB)
# --------------------------------------------------------------------------

def validate(items: list[dict]) -> int:
    texts = corpus_texts()
    if not texts:
        print("Không tìm thấy file .pdf/.txt nào trong data/")
        return 1

    print(f"Kiểm tra {len(items)} câu hỏi với {len(texts)} file nguồn\n")
    bad = 0
    for item in items:
        needle = normalize(item["context_anchor"])
        found_in = [name for name, text in texts if needle in normalize(text)]
        if found_in:
            print(f"  [ok]   #{item['id']:<2} anchor có trong {', '.join(found_in)}")
        else:
            bad += 1
            print(f"  [MISS] #{item['id']:<2} anchor KHÔNG khớp file nào")
            print(f"         anchor: {item['context_anchor'][:90]}...")

    print()
    if bad:
        print(f"{bad}/{len(items)} anchor không khớp -> sửa eval_set.json trước khi đo.")
        return 1
    print("Tất cả anchor đều khớp. Bộ eval dùng được.")
    return 0


# --------------------------------------------------------------------------
# Chế độ 2: đo thật
# --------------------------------------------------------------------------

def git_rev() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return "unknown"


def corpus_stats(engine, user_id: str) -> dict:
    from sqlalchemy import text

    with engine.connect() as conn:
        total = conn.execute(
            text("SELECT count(*) FROM langchain_pg_embedding")
        ).scalar_one()
        mine = conn.execute(
            text(
                "SELECT count(*) FROM langchain_pg_embedding "
                "WHERE cmetadata->>'user_id' = :uid"
            ),
            {"uid": user_id},
        ).scalar_one()
        files = conn.execute(
            text(
                "SELECT DISTINCT cmetadata->>'file_name' FROM langchain_pg_embedding "
                "WHERE cmetadata->>'user_id' = :uid"
            ),
            {"uid": user_id},
        ).scalars().all()
    return {"total": total, "user_chunks": mine, "files": list(files)}


def run(items: list[dict], user_id: str, k: int, label: str) -> int:
    from src.config import settings
    from src.ingestion import connect_to_pgvector
    from src.retriever import get_retriever

    vectorstore = connect_to_pgvector()
    stats = corpus_stats(vectorstore._engine, user_id)

    print(f"Corpus: {stats['user_chunks']} chunk của user này "
          f"({stats['total']} chunk toàn bộ), file: {stats['files']}")
    if stats["user_chunks"] == 0:
        print("Không có chunk nào -> không đo được. Ingest tài liệu trước.")
        return 1
    if stats["user_chunks"] <= k:
        print(f"\nCẢNH BÁO: corpus chỉ có {stats['user_chunks']} chunk <= k={k}.")
        print("Mọi query đều trả về gần như toàn bộ corpus, nên recall@k sẽ = 1.0")
        print("một cách tầm thường. Con số này KHÔNG nói lên chất lượng retrieval.")
        print("Cần corpus lớn hơn (nhiều tài liệu hoặc chunk nhỏ hơn) mới đo có nghĩa.\n")

    # Retriever dùng đúng cấu hình đang chạy trong app.
    retriever = get_retriever(vectorstore, user_id)

    rows = []
    for item in items:
        docs = retriever.invoke(item["query"])
        rank = find_rank(item["context_anchor"], docs)
        rows.append(
            {
                "id": item["id"],
                "query": item["query"],
                "rank": rank,
                "n_returned": len(docs),
                "preview": docs[0].page_content[:70].replace("\n", " ") if docs else "",
            }
        )
        mark = f"rank {rank}" if rank else "MISS"
        print(f"  #{item['id']:<2} {mark:<8} (trả về {len(docs)} chunk)")

    n = len(rows)
    hits = [r for r in rows if r["rank"]]
    recall = len(hits) / n
    mrr = sum(1 / r["rank"] for r in hits) / n
    top1 = sum(1 for r in hits if r["rank"] == 1) / n

    print(f"\nrecall@{k} = {recall:.3f}   MRR@{k} = {mrr:.3f}   top1 = {top1:.3f}")

    append_log(
        label=label,
        k=k,
        rows=rows,
        recall=recall,
        mrr=mrr,
        top1=top1,
        stats=stats,
        user_id=user_id,
        settings=settings,
    )
    print(f"Đã ghi vào {LOG_FILE.relative_to(ROOT)}")
    return 0


def append_log(*, label, k, rows, recall, mrr, top1, stats, user_id, settings):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now().astimezone()

    lines = []
    if not LOG_FILE.exists():
        lines += [
            "# Eval log — retrieval",
            "",
            "Append-only. Mỗi mục là một lần đo, ghi rõ thời điểm và cấu hình,",
            "để so sánh trước/sau và dùng lại khi viết báo cáo.",
            "",
            "Metric: `recall@k` = tỉ lệ câu có chunk đúng trong top-k ·",
            "`MRR@k` = trung bình 1/rank · `top1` = tỉ lệ chunk đúng đứng đầu.",
            "",
        ]

    meaningful = stats["user_chunks"] > k
    lines += [
        "---",
        "",
        f"## {now.strftime('%Y-%m-%d %H:%M %Z')} — {label}",
        "",
        f"- commit: `{git_rev()}`",
        f"- embedding: `{settings.embedding_model}`",
        f"- chunk_size/overlap: `{settings.chunk_size}` / `{settings.chunk_overlap}` "
        f"(đơn vị: ký tự)",
        f"- retriever: dense `similarity_score_threshold`, k=`{k}`, "
        f"score_threshold=`{settings.score_threshold}`",
        f"- corpus: **{stats['user_chunks']} chunk** / {len(stats['files'])} file "
        f"({', '.join(stats['files']) or '—'}); toàn DB {stats['total']} chunk",
        "",
        f"| metric | value |",
        f"| --- | --- |",
        f"| recall@{k} | {recall:.3f} |",
        f"| MRR@{k} | {mrr:.3f} |",
        f"| top1 | {top1:.3f} |",
        "",
    ]

    if not meaningful:
        lines += [
            f"> **Không có giá trị đối chiếu.** Corpus chỉ có {stats['user_chunks']} chunk "
            f"với k={k}, nên gần như mọi query đều trả về toàn bộ corpus. Con số 1.000 ở "
            "trên là hệ quả của kích thước corpus, không phải chất lượng retrieval.",
            "",
        ]

    lines += [
        f"| # | query | rank | chunks trả về |",
        f"| --- | --- | --- | --- |",
    ]
    for r in rows:
        q = r["query"].replace("|", "\\|")
        rank = r["rank"] if r["rank"] else "MISS"
        lines.append(f"| {r['id']} | {q} | {rank} | {r['n_returned']} |")

    lines.append("")

    mode = "a" if LOG_FILE.exists() else "w"
    with LOG_FILE.open(mode, encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--validate-only", action="store_true",
                    help="chỉ kiểm tra anchor khớp file nguồn, không cần DB")
    ap.add_argument("--label", default="run", help="nhãn cho mục trong eval_log.md")
    ap.add_argument("--user-id", help="UUID user cần đo (bắt buộc khi đo thật)")
    ap.add_argument("--k", type=int, default=None, help="mặc định lấy settings.top_k")
    args = ap.parse_args()

    items = load_eval_set()
    if not items:
        print("eval_set.json rỗng")
        return 1

    if args.validate_only:
        return validate(items)

    if not args.user_id:
        print("Thiếu --user-id. Lấy UUID của user đã upload tài liệu.")
        return 2

    from src.config import settings

    k = args.k or settings.top_k
    return run(items, args.user_id, k, args.label)


if __name__ == "__main__":
    sys.exit(main())
