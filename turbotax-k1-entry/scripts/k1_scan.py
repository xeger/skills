#!/usr/bin/env python3
"""
Triage a folder of Schedule K-1 PDFs before dispatching extraction subagents.

Answers the questions you always need first: which files are duplicates, which
entity is which, how big each package is, whether the K-1 is final or amended,
and whether an attached Schedule K-3 carries actual foreign activity. Running
this costs a second and saves every invocation from rediscovering the same facts.

    python k1_scan.py ~/Downloads
    python k1_scan.py ~/Downloads --json

Requires pdftotext and pdfinfo (poppler-utils).

A note on why this parses the way it does: K-1 PDFs come from many different
preparers, and some lay text out with erratic per-character spacing, so
"Schedule K-1" arrives as "Schedule      K - 1". Label-anchored regexes are
therefore unreliable. Everything here matches against a whitespace-normalized
copy and falls back to shape-based patterns (an EIN looks like NN-NNNNNNN; an
entity name is uppercase and ends in a corporate suffix). This is triage, not
extraction -- the Haiku extractor reads the form properly.
"""

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

CORP_SUFFIX = r"(?:L\.?L\.?C|L\.?P\.?|INC|CORP|COMPANY|PARTNERSHIP|HOLDINGS|FUND|TRUST)"
ENTITY_PAT = re.compile(
    rf"\b([A-Z][A-Z0-9&.,'\- ]{{4,60}}?\s{CORP_SUFFIX})\.?(?![A-Za-z])"
)
EIN_PAT = re.compile(r"\b(\d{2}-\d{7})\b")


def sh(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=120).stdout
    except (subprocess.SubprocessError, OSError):
        return ""


def normalize(text):
    return re.sub(r"\s+", " ", text)


def file_hash(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def page_count(path):
    m = re.search(r"Pages:\s+(\d+)", sh(["pdfinfo", str(path)]))
    return int(m.group(1)) if m else None


def looks_like_k1(norm):
    return "Schedule K-1" in norm or "651123" in norm


def form_type(norm):
    m = re.search(r"Schedule K-1 \(Form (1065|1120S|1041)\)", norm)
    return m.group(1) if m else None


def find_ein(norm):
    """
    Prefer the EIN that follows the Part I label; fall back to the first
    EIN-shaped token in the document, which on a K-1 is the partnership's.
    A partner SSN has a different shape (NNN-NN-NNNN) so it won't collide.
    """
    m = re.search(
        r"employer identification number.{0,120}?(\d{2}-\d{7})", norm, re.I
    )
    if m:
        return m.group(1)
    m = EIN_PAT.search(norm)
    return m.group(1) if m else None


def find_entity_name(norm):
    for m in ENTITY_PAT.finditer(norm):
        name = m.group(1).strip().rstrip(",")
        if len(name.split()) >= 2:
            return name
    return None


def k3_status(norm):
    """
    Whether a K-3 is attached and whether it plausibly reports foreign activity.

    On a purely domestic partnership every populated Part II line sits in the
    U.S.-source column and no country code is filled in. A country code is the
    cheapest reliable positive signal. This flags which packages deserve a
    closer look; the extractor makes the actual determination.
    """
    if "Schedule K-3" not in norm:
        return {"attached": False}

    section = re.search(r"Part II Foreign Tax Credit Limitation(.{0,8000})", norm)
    foreign = None
    if section:
        foreign = bool(re.search(r"\(country code\s*\)?\s*[A-Z]{2}\b", section.group(1)))

    return {"attached": True, "likely_has_foreign_activity": foreign}


def scan(path):
    text = sh(["pdftotext", "-layout", str(path), "-"])
    rec = {"file": path.name, "pages": page_count(path), "md5": file_hash(path)}

    if not text.strip():
        rec["warning"] = "no text layer -- likely a scan, needs OCR"
        return rec

    norm = normalize(text)
    if not looks_like_k1(norm):
        rec["warning"] = "does not look like a Schedule K-1"
        return rec

    rec.update(
        {
            "form": form_type(norm),
            "ein": find_ein(norm),
            "entity": find_entity_name(norm),
            "final_k1": bool(re.search(r"X Final K-1|Final K-1 X", norm)),
            "amended_k1": bool(re.search(r"X Amended K-1|Amended K-1 X", norm)),
            "k3": k3_status(norm),
        }
    )
    return rec


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("folder", help="folder containing K-1 PDFs")
    ap.add_argument("--json", action="store_true", help="emit JSON")
    args = ap.parse_args()

    folder = Path(args.folder).expanduser()
    if not folder.is_dir():
        sys.exit(f"not a directory: {folder}")

    pdfs = sorted(folder.glob("*.pdf"))
    if not pdfs:
        sys.exit(f"no PDFs in {folder}")

    records = [scan(p) for p in pdfs]

    by_hash = {}
    for r in records:
        by_hash.setdefault(r["md5"], []).append(r["file"])
    dupes = {h: g for h, g in by_hash.items() if len(g) > 1}
    for r in records:
        r["duplicate_of"] = next(
            (g[0] for g in dupes.values() if r["file"] in g and g[0] != r["file"]), None
        )

    if args.json:
        print(json.dumps(records, indent=2))
        return

    k1s = [r for r in records if r.get("ein")]
    others = [r for r in records if not r.get("ein")]

    print(f"\n{len(k1s)} K-1(s) in {folder}\n")
    for r in k1s:
        tag = "   [DUPLICATE]" if r["duplicate_of"] else ""
        print(f"  {r['entity'] or '?'}   ({r['ein']}){tag}")
        print(f"    {r['file']}  ({r['pages']}p, Form {r['form'] or '?'})")
        flags = []
        if r["final_k1"]:
            flags.append("FINAL K-1 -- interest ended, confirm disposition")
        if r["amended_k1"]:
            flags.append("AMENDED")
        if r["k3"]["attached"]:
            flags.append(
                "K-3 attached, "
                + (
                    "possible foreign activity -- check"
                    if r["k3"].get("likely_has_foreign_activity")
                    else "no foreign activity detected"
                )
            )
        if flags:
            print("    " + "\n    ".join(flags))
        print()

    if dupes:
        print("Duplicates (identical content -- enter once):")
        for g in dupes.values():
            print("  " + "  ==  ".join(g))
        print()

    if others:
        print("Not recognized as K-1s:")
        for r in others:
            print(f"  {r['file']} -- {r.get('warning', 'unrecognized')}")
        print()


if __name__ == "__main__":
    main()
