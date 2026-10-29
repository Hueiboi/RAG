"""Kiểm tra chất lượng corpus trong data/ trước khi ingest.

Bắt các kiểu hỏng đã từng xảy ra:
  - công cụ crawl chèn marker "content has been truncated..." vào text
  - file bị cắt giữa câu (không kết thúc bằng dấu câu)
  - nhiều file dừng cùng một độ dài ~3000 -> dấu hiệu cap cứng
  - còn sót HTML
  - anchor trong eval_set không khớp hoặc khớp nhiều chunk

    python -m eval.check_corpus
    python -m eval.check_corpus --strict   # coi cảnh báo là lỗi
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SUFFIXES = {".txt", ".pdf"}

TRUNCATION_MARKERS = [
    "content has been truncated",
    "truncated to stay below",
    "[...]",
]
HTML_TAG = re.compile(r"<(p|div|span|br|table|a)\b[^>]*>", re.IGNORECASE)
# Ký tự kết thúc câu hợp lệ. ":" và ";" bị loại có chủ ý: file kết thúc bằng
# "trong đó:" là dấu hiệu bị cắt ngay trước một danh sách, không phải kết thúc.
SENTENCE_END = tuple(".!?…。") + ('"', "'", ")", "”", "’")


def read_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        from pypdf import PdfReader
        return "\n".join(p.extract_text() or "" for p in PdfReader(path).pages)
    return path.read_text(encoding="utf-8")


def check_files() -> list[dict]:
    rows = []
    for path in sorted(DATA_DIR.iterdir()):
        if not path.is_file() or path.suffix.lower() not in SUFFIXES:
            continue
        text = read_text(path).strip()
        flags = []
        low = text.lower()
        for marker in TRUNCATION_MARKERS:
            if marker in low:
                flags.append(f"MARKER[{marker}]")
        if text and not text.endswith(SENTENCE_END):
            flags.append("MID-SENTENCE")
        if HTML_TAG.search(text):
            flags.append("HTML")
        if not text:
            flags.append("EMPTY")
        rows.append({"name": path.name, "chars": len(text), "flags": flags})
    return rows


def check_suspicious_caps(rows: list[dict]) -> None:
    """Nhiều file cùng dừng ở một độ dài -> gần như chắc chắn là cap cứng."""
    items = sorted((r["chars"], r["name"]) for r in rows if not r["name"].endswith(".pdf"))
    clusters: list[list[tuple[int, str]]] = []
    for chars, name in items:
        if clusters and chars - clusters[-1][0][0] <= clusters[-1][0][0] * 0.10:
            clusters[-1].append((chars, name))
        else:
            clusters.append([(chars, name)])
    for cluster in clusters:
        if len(cluster) < 3:
            continue
        lo, hi = cluster[0][0], cluster[-1][0]
        print(f"  [cap?] {len(cluster)} file dừng trong khoảng {lo}-{hi} ký tự "
              f"({hi - lo} ký tự chênh lệch):")
        for chars, name in cluster:
            print(f"           {chars:6}  {name}")


def check_anchors() -> tuple[int, int]:
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    from src.config import settings

    from eval.run_eval import load_eval_set, normalize

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap
    )
    chunks: list[tuple[str, str]] = []
    for path in sorted(DATA_DIR.iterdir()):
        if not path.is_file() or path.suffix.lower() not in SUFFIXES:
            continue
        for piece in splitter.split_text(read_text(path)):
            chunks.append((path.name, normalize(piece)))

    items = load_eval_set()
    bad = 0
    print(f"\nAnchor: {len(items)} câu hỏi trên {len(chunks)} chunk")
    for item in items:
        needle = normalize(item["context_anchor"])
        hits = [(name, i) for i, (name, c) in enumerate(chunks) if needle in c]
        if len(hits) == 1:
            continue
        if hits and len({name for name, _ in hits}) == 1:
            # Nhiều chunk cùng file = chunk_overlap lặp lại cùng đoạn văn,
            # không phải anchor mơ hồ. Chấp nhận.
            print(f"  [ok  ] #{item['id']:<2} x{len(hits)} chunk cùng file "
                  f"({hits[0][0]}) - overlap")
            continue
        bad += 1
        label = "MISS " if not hits else f"x{len(hits)}  "
        files = ", ".join(sorted({name for name, _ in hits})) or "-"
        print(f"  [{label}] #{item['id']:<2} {files}")
    if not bad:
        print("  tất cả anchor khớp đúng 1 chunk")
    return len(items) - bad, len(items)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--strict", action="store_true", help="cảnh báo cũng tính là lỗi")
    args = ap.parse_args()

    rows = check_files()
    if not rows:
        print("Không có file nào trong data/")
        return 1

    print(f"Kiểm tra {len(rows)} file\n")
    print(f"{'file':42} {'ký tự':>7} {'trạng thái'}")
    print("-" * 80)
    broken = 0
    for r in rows:
        status = "ok" if not r["flags"] else " ".join(r["flags"])
        if r["flags"]:
            broken += 1
        print(f"{r['name']:42} {r['chars']:7} {status}")

    print("\nNghi ngờ cap cứng (≥3 file cùng độ dài):")
    check_suspicious_caps(rows)

    ok_items, total_items = check_anchors()

    print(f"\nTổng kết: {len(rows) - broken}/{len(rows)} file sạch | "
          f"anchor {ok_items}/{total_items}")
    failed = broken or ok_items != total_items
    if args.strict and failed:
        return 1
    return 0 if not broken else 1


if __name__ == "__main__":
    sys.exit(main())
