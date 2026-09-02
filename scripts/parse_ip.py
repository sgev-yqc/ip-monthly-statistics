#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""parse_ip.py — 解析知识产权证书文本 → 结构化字段（受理/授权/软著/PCT）

用法:
  python parse_ip.py <extract_ip_pdf.py 输出的 JSON> --out <结构化JSON>

说明:
  - 受理通知书: 申请号/申请日/申请人/发明人/名称/卷号（块提取, 处理跨行名单）
  - 授权证书: 证书号/专利号/申请日/授权公告日/名称/申请人/发明人（处理竖排文本）
  - 软著证书: 软件名称+V1.0/证书编号/登记号/著作权人/日期/取得方式/权利范围
  - PCT 通知书: 国际申请号/国际申请日/优先权日/申请人/名称/档案号
  - 无文本层记录标记 SCAN，需 OCR 后手动补充

输出字段用中文顿号分隔；日期统一 yyyy-mm-dd。
"""
import json, re, os, argparse


def norm_date(s):
    if not s:
        return ""
    m = re.search(r"(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日", s)
    if m:
        return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
    return s.strip()


def clean_multi(v):
    return re.sub(r"\s+", "", v) if v else ""


def sep_to_dun(v):
    if not v:
        return ""
    v = v.replace(",", "、").replace(";", "、").replace("；", "、").replace("，", "、")
    return re.sub(r"、+", "、", v).strip("、")


def parse_one(r):
    fn = os.path.basename(r["file"])
    t = r["text"]
    rec = {"file": fn, "chars": r["len"], "type": None}
    if r["len"] == 0:
        rec["type"] = "SCAN"
        return rec
    if "专利申请受理通知书" in t:
        rec["type"] = "受理"
        m = re.search(r"申请号：([\d.]+X?)", t)
        rec["申请号"] = m.group(1).strip() if m else ""
        m = re.search(r"申请日：\s*([^\n]+)", t)
        rec["申请日"] = norm_date(m.group(1)) if m else ""
        m1 = re.search(r"申请人：\s*(.*?)(?:发明人|发明创造名称)", t, re.S)
        rec["申请人"] = sep_to_dun(clean_multi(m1.group(1))) if m1 else ""
        m2 = re.search(r"发明人：\s*(.*?)(?:发明创造名称)", t, re.S)
        rec["发明人"] = sep_to_dun(clean_multi(m2.group(1))) if m2 else ""
        m3 = re.search(r"发明创造名称：\s*(.*?)(?:经核实|提示)", t, re.S)
        rec["名称"] = clean_multi(m3.group(1)) if m3 else ""
        m4 = re.search(r"申请方案卷号：\s*([^\n]+)", t)
        rec["卷号"] = m4.group(1).strip() if m4 else ""
        m5 = re.search(r"发文日：\s*([^\n]+)", t)
        rec["发文日"] = norm_date(m5.group(1)) if m5 else ""
    elif "发明专利证书" in t or "实用新型专利证书" in t or "专利证书" in t:
        rec["type"] = "授权"
        m = re.search(r"证书号第(\d+)号", t)
        rec["证书号"] = m.group(1) if m else ""
        m = re.search(r"专利号[：:]\s*([^\n]+)", t) or re.search(r"ZL\s*([\d\s.]+)", t)
        rec["专利号"] = clean_multi(m.group(1)) if m else ""
        m = re.search(r"专利申请日[：:]\s*([^\n]+)", t)
        rec["申请日"] = norm_date(m.group(1)) if m else ""
        m = re.search(r"授权公告日[：:]\s*([^\n]+)", t)
        rec["授权公告日"] = norm_date(m.group(1)) if m else ""
        m = re.search(r"(?:发明|实用新型)名称[：:]\s*([^\n]+)", t)
        rec["名称"] = clean_multi(m.group(1)) if m else ""
        m3 = re.search(r"申请日时申请人[：:]\s*(.*?)(?:申请日时发明人)", t, re.S)
        if m3:
            rec["申请日时申请人"] = sep_to_dun(clean_multi(m3.group(1)))
        m4 = re.search(r"申请日时发明人[：:]\s*(.*?)(?:国家知识产权局)", t, re.S)
        if m4:
            rec["申请日时发明人"] = sep_to_dun(clean_multi(m4.group(1)))
    elif "计算机软件著作权" in t or "软著登字" in t or "软件名称" in t:
        rec["type"] = "软著"
        m = re.search(r"软件名称[：:]\s*([^\n]+)", t)
        rec["软件名称"] = clean_multi(m.group(1)) if m else ""
        m = re.search(r"V([0-9.]+)", t)
        rec["版本"] = ("V" + m.group(1)) if m else ""
        m = re.search(r"著作权人[：:]\s*([^\n]+)", t)
        rec["著作权人"] = sep_to_dun(clean_multi(m.group(1))) if m else ""
        m = re.search(r"20\d{2}SR\d+", t)
        rec["登记号"] = m.group(0) if m else ""
        m = re.search(r"软著登字第(\d+)号", t)
        rec["证书编号"] = ("软著登字第" + m.group(1) + "号") if m else ""
        m = re.search(r"权利取得方式[：:]\s*([^\n]+)", t)
        rec["权利取得方式"] = clean_multi(m.group(1)) if m else ""
        m = re.search(r"权利范围[：:]\s*([^\n]+)", t)
        rec["权利范围"] = clean_multi(m.group(1)) if m else ""
        m = re.search(r"(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日", t)
        rec["登记日期"] = norm_date(m.group(0)) if m else ""
    elif "PCT" in t or "国际申请" in t or "专利合作条约" in t:
        rec["type"] = "PCT"
        m = re.search(r"国际申请号\s*([^\n]*PCT/CN\d{4}/\d+)", t)
        rec["国际申请号"] = m.group(1).strip() if m else ""
        m = re.search(r"国际申请日\s*\(年/月/日\)\s*(\d{4}年\d{1,2}月\d{1,2}日)", t)
        rec["国际申请日"] = norm_date(m.group(1)) if m else ""
        m = re.search(r"优先权日\s*\(年/月/日\)\s*(\d{4}年\d{1,2}月\d{1,2}日)", t)
        rec["优先权日"] = norm_date(m.group(1)) if m else ""
        m = re.search(r"发明名称\s*([^\n]+)", t)
        rec["名称"] = clean_multi(m.group(1)) if m else ""
        m = re.search(r"申请人或代理人的档案号\s*([^\n]+)", t)
        rec["档案号"] = m.group(1).strip() if m else ""
    else:
        rec["type"] = "未知"
        rec["head"] = t[:150]
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="extract_ip_pdf.py 输出的提取文本 JSON")
    ap.add_argument("--out", required=True, help="输出结构化 JSON")
    args = ap.parse_args()

    data = json.load(open(args.input, encoding="utf-8"))
    records = [parse_one(r) for r in data]
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(records, fh, ensure_ascii=False, indent=1)
    for rec in records:
        if rec["type"] != "SCAN":
            print(json.dumps(rec, ensure_ascii=False))
    scans = [r for r in records if r["type"] == "SCAN"]
    if scans:
        print(f"\nSCAN 需 OCR: {len(scans)} 份")
        for s in scans:
            print("  ", s["file"])


if __name__ == "__main__":
    main()
