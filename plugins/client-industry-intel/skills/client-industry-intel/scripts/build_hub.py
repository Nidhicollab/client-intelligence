#!/usr/bin/env python3
"""Validate a hub.json file and render it into the client hub HTML template.

Usage: python3 build_hub.py <hub.json> <out.html> [--template PATH]
Exits 1 and prints every problem if the data is invalid; nothing is written.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROLES = {
    "product-manager": "Product manager",
    "engineering-lead": "Engineering lead or architect",
    "ux-designer": "UX or product designer",
    "engagement-lead": "Engagement lead or partner",
    "data-analyst": "Business or data analyst",
}
EVIDENCE_TYPES = {
    "filing", "earnings", "regulator", "company", "research",
    "news", "sentiment", "website", "client_document",
}
CONFIDENCE = {"high", "medium", "low"}
LEVELS = {"high", "medium", "low"}
VISUAL_KINDS = {"mermaid", "chart", "cards", "table"}
RESERVED_IDS = {"podcast", "signals", "sources"}
PLACEHOLDER = "__HUB_DATA__"
DEFAULT_TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "hub.html"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
URL_RE = re.compile(r"^https?://", re.IGNORECASE)
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _visual_errors(where, visual):
    if not isinstance(visual, dict) or visual.get("kind") not in VISUAL_KINDS:
        return [f"{where}: visual.kind must be one of {sorted(VISUAL_KINDS)}"]
    kind = visual["kind"]
    if kind == "mermaid":
        if not isinstance(visual.get("code"), str) or not visual["code"].strip():
            return [f"{where}: mermaid visual needs non-empty 'code'"]
    elif kind == "chart":
        if not isinstance(visual.get("config"), dict):
            return [f"{where}: chart visual needs a 'config' object"]
    elif kind == "cards":
        cards = visual.get("cards")
        if not isinstance(cards, list) or not cards:
            return [f"{where}: cards visual needs a non-empty 'cards' list"]
        return [
            f"{where}: card {i} needs a 'title'"
            for i, card in enumerate(cards)
            if not isinstance(card, dict) or not card.get("title")
        ]
    elif kind == "table":
        columns, rows = visual.get("columns"), visual.get("rows")
        if not isinstance(columns, list) or not columns or not isinstance(rows, list):
            return [f"{where}: table visual needs 'columns' and 'rows' lists"]
        errors = []
        for i, row in enumerate(rows):
            if not isinstance(row, list) or len(row) != len(columns):
                errors.append(f"{where}: table row {i} must have {len(columns)} cells")
                continue
            for cell in row:
                if isinstance(cell, dict) and cell.get("level") not in (None, *LEVELS):
                    errors.append(f"{where}: table row {i} has invalid level {cell.get('level')!r}")
        return errors
    return []


def _record_errors(data, records):
    errors, ids = [], set()
    for i, rec in enumerate(records):
        where = f"record {i}"
        if not isinstance(rec, dict):
            errors.append(f"{where}: must be an object")
            continue
        rid = rec.get("id")
        if not isinstance(rid, str) or not rid:
            errors.append(f"{where}: needs an 'id'")
        elif rid in ids:
            errors.append(f"{where}: duplicate id {rid!r}")
        else:
            ids.add(rid)
        if not rec.get("claim"):
            errors.append(f"{where}: needs a 'claim'")
        etype = rec.get("evidence_type")
        if etype not in EVIDENCE_TYPES:
            errors.append(f"{where}: invalid evidence_type {etype!r}")
        if rec.get("confidence") not in CONFIDENCE:
            errors.append(f"{where}: confidence must be high, medium or low")
        if etype == "client_document":
            if rec.get("confidential") is not True:
                errors.append(f"{where}: client_document records must be confidential")
        elif not URL_RE.match(str(rec.get("source_url") or "")):
            errors.append(f"{where}: source_url must start with http:// or https://")
        if rec.get("confidential") is True and data.get("confidential") is False:
            errors.append(f"{where}: is confidential, so the hub's confidential flag must be true")
    return errors, ids


def _output_errors(outputs, record_ids):
    errors, seen = [], set()
    for i, out in enumerate(outputs):
        where = f"output {i + 2}"
        if not isinstance(out, dict):
            errors.append(f"{where}: must be an object")
            continue
        oid = out.get("id")
        if not isinstance(oid, str) or not ID_RE.match(oid):
            errors.append(f"{where}: id must be a lowercase-hyphenated slug")
        elif oid in RESERVED_IDS:
            errors.append(f"{where}: id {oid!r} is reserved")
        elif oid in seen:
            errors.append(f"{where}: duplicate id {oid!r}")
        else:
            seen.add(oid)
        if not out.get("title"):
            errors.append(f"{where}: needs a 'title'")
        status = out.get("status")
        if status == "incomplete":
            if not out.get("reason"):
                errors.append(f"{where}: incomplete outputs need a 'reason'")
        elif status == "complete":
            if not out.get("so_what"):
                errors.append(f"{where}: needs a 'so_what'")
            errors.extend(_visual_errors(where, out.get("visual")))
            evidence = out.get("evidence")
            if not isinstance(evidence, list) or not evidence:
                errors.append(f"{where}: needs at least one evidence record id")
            else:
                errors.extend(
                    f"{where}: unknown record id {rid!r}" for rid in evidence if rid not in record_ids
                )
        else:
            errors.append(f"{where}: status must be 'complete' or 'incomplete'")
    return errors


def validate(data):
    """Return a list of problems with the hub data. An empty list means it is valid."""
    if not isinstance(data, dict):
        return ["hub data must be a JSON object"]
    errors = []
    if not isinstance(data.get("company"), str) or not data["company"].strip():
        errors.append("company must be a non-empty string")
    if not isinstance(data.get("as_of"), str) or not DATE_RE.match(data["as_of"]):
        errors.append("as_of must be a YYYY-MM-DD date")
    if data.get("role") not in ROLES:
        errors.append(f"role must be one of {sorted(ROLES)}")
    if not isinstance(data.get("confidential"), bool):
        errors.append("confidential must be true or false")
    miro = data.get("miro_url")
    if miro is not None and not URL_RE.match(str(miro)):
        errors.append("miro_url must start with http:// or https://, or be null")
    podcast = data.get("podcast")
    if not isinstance(podcast, dict):
        errors.append("podcast must be an object")
    else:
        audio = podcast.get("audio")
        if audio is not None and (not isinstance(audio, str) or ":" in audio or "/" in audio or "\\" in audio):
            errors.append("podcast.audio must be a file name next to hub.html, or null")
    if not isinstance(data.get("signals"), dict):
        errors.append("signals must be an object")

    records = data.get("records")
    if not isinstance(records, list):
        errors.append("records must be a list")
        records = []
    record_errors, record_ids = _record_errors(data, records)
    errors.extend(record_errors)

    outputs = data.get("outputs")
    if not isinstance(outputs, list) or len(outputs) != 4:
        errors.append("outputs must be a list of exactly 4 items")
    if isinstance(outputs, list):
        errors.extend(_output_errors(outputs, record_ids))
    return errors


def build(data, template):
    """Return the template with the hub data embedded as safe JSON."""
    if PLACEHOLDER not in template:
        raise ValueError(f"template is missing {PLACEHOLDER}")
    data = dict(data)
    data.setdefault("role_label", ROLES.get(data.get("role"), ""))
    payload = json.dumps(data, ensure_ascii=False)
    # Stop text inside the data from closing the <script> block it lives in.
    payload = payload.replace("</", "<\\/").replace("<!--", "<\\u0021--")
    return template.replace(PLACEHOLDER, payload)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate hub.json and render the client hub.")
    parser.add_argument("data", help="path to hub.json")
    parser.add_argument("out", help="path to write hub.html")
    parser.add_argument("--template", default=str(DEFAULT_TEMPLATE))
    args = parser.parse_args(argv)
    try:
        data = json.loads(Path(args.data).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: cannot read {args.data}: {exc}", file=sys.stderr)
        return 1
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"error: {error}", file=sys.stderr)
        return 1
    template = Path(args.template).read_text(encoding="utf-8")
    Path(args.out).write_text(build(data, template), encoding="utf-8")
    print(args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
