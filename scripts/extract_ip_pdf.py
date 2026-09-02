#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""extract_ip_pdf.py — 批量提取知识产权证书 PDF 文本（受理通知书/授权证书/软著证书/PCT 通知书）

用法:
  python extract_ip_pdf.py <输入目录或PDF文件> [更多目录/文件...] --out <输出JSON>

说明:
  - 递归扫描目录下所有 .pdf
  - 文本型 PDF 直接提取；无文本层(chars<50)标记 SCAN，需另行 OCR
  - 输出 JSON: [{file, len, head, text}, ...]

依赖: pymupdf (pip install pymupdf)
"""
import os, sys, json, argparse
import pymupdf


def extract_one(fp: str) -> dict:
    try:
        doc = pymupdf.open(fp)
        text = "\n".join(pg.get_text() for pg in doc)
        doc.close()
    except Exception as e:
        text = f"__ERROR__ {e}"
    return {"file": fp, "len": len(text.strip()), "head": text.strip()[:260], "text": text}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+", help="PDF 文件或目录（目录递归扫描）")
    ap.add_argument("--out", required=True, help="输出 JSON 路径")
    args = ap.parse_args()

    files = []
    for inp in args.inputs:
        if os.path.isdir(inp):
            for root, _, fns in os.walk(inp):
                for fn in sorted(fns):
                    if fn.lower().endswith(".pdf"):
                        files.append(os.path.join(root, fn))
        elif os.path.isfile(inp):
            files.append(inp)

    results = [extract_one(f) for f in files]
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(results, fh, ensure_ascii=False, indent=1)

    for r in results:
        tag = "SCAN?" if r["len"] < 50 else ""
        print(f"{os.path.basename(r['file'])} | chars={r['len']} | {tag}")
    print(f"\nTOTAL: {len(results)} -> {args.out}")


if __name__ == "__main__":
    main()
