"""Parsers for HKDSE examination timetable PDFs."""

from __future__ import annotations

import re
from datetime import date
from typing import Any

from .pdf_extract import RawDocument, RawPage, RawTable
from .text_utils import (
    CJK_RE,
    cell_str,
    chinese_numeral,
    is_blank,
    split_bilingual,
)

WEEKDAYS = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)
MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}

EN_DATE_RE = re.compile(
    rf"(?:{'|'.join(WEEKDAYS)})[,]?\s+(\d{{1,2}})(?:st|nd|rd|th)?\s+"
    rf"({'|'.join(MONTHS)})",
    re.I,
)
CN_DATE_RE = re.compile(
    r"((?:\d+)|(?:[一二三四五六七八九十]+))\s*月\s*"
    r"((?:\d+)|(?:[一二三四五六七八九十]+))\s*日"
)
TIME_RE = re.compile(
    r"([#*]*)\s*(\d{1,2}:\d{2})\s*[-–—]\s*(\d{1,2}:\d{2})\s*([*]*)"
)
PAPER_RE = re.compile(
    r"(?P<name>.*?)(?:\s+(?P<paper>"
    r"1A|1B|Modules?\s+1(?:\s*[,&]\s*2)?|1,\s*2|1,2|1\s*&\s*2|[1-4]"
    r"))(?:\s|\(|$)",
    re.I,
)


def _lines(value: Any) -> list[str]:
    return [ln.strip() for ln in cell_str(value).splitlines() if ln.strip()]


def _split_en_zh_inline(text: str) -> tuple[str, str]:
    text = cell_str(text)
    match = CJK_RE.search(text)
    if not match:
        return text.strip(), ""
    return text[: match.start()].strip(), text[match.start() :].strip()


def _parse_en_date(text: str, year: int | None) -> date | None:
    match = EN_DATE_RE.search(text)
    if not match or year is None:
        return None
    day = int(match.group(1))
    month = MONTHS[match.group(2).lower()]
    try:
        return date(year, month, day)
    except ValueError:
        return None


def _parse_cn_date(text: str, year: int | None) -> date | None:
    match = CN_DATE_RE.search(text)
    if not match or year is None:
        return None
    month = chinese_numeral(match.group(1))
    day = chinese_numeral(match.group(2))
    if month is None or day is None:
        return None
    try:
        return date(year, month, day)
    except ValueError:
        return None


def _parse_time(text: str) -> dict[str, Any]:
    raw = cell_str(text)
    match = TIME_RE.search(raw)
    if not match:
        return {
            "time_raw": raw or None,
            "time_start": None,
            "time_end": None,
            "has_listening_reporting_mark": "#" in raw,
            "has_approx_end_mark": "*" in raw,
        }
    prefix, start, end, suffix = match.groups()
    return {
        "time_raw": raw,
        "time_start": start,
        "time_end": end,
        "has_listening_reporting_mark": "#" in (prefix or "") or "#" in raw,
        "has_approx_end_mark": "*" in (suffix or "") or "*" in raw,
    }


def _parse_paper(subject_en: str) -> tuple[str, str | None]:
    text = subject_en.strip()
    match = PAPER_RE.match(text)
    if not match:
        return text, None
    name = match.group("name").strip(" -–")
    paper = re.sub(r"\s+", "", match.group("paper"))
    paper = paper.replace("Modules", "Modules ").replace("Module", "Module ")
    paper = re.sub(r"\s+", " ", paper).strip()
    return name or text, paper


def _is_header_row(row: list[Any]) -> bool:
    blob = " ".join(cell_str(c) for c in row).lower()
    return "date" in blob and ("time" in blob or "時間" in blob)


def _is_empty_row(row: list[Any]) -> bool:
    return all(is_blank(c) for c in row)


def parse_written_table(
    doc: RawDocument, page: RawPage, table: RawTable
) -> list[dict[str, Any]]:
    date_zh = ""
    date_en = ""
    records: list[dict[str, Any]] = []
    for row in table.rows:
        if _is_header_row(row) or _is_empty_row(row):
            continue
        padded = list(row) + [""] * (4 - len(row))
        date_cell, time_cell, en_cell, zh_cell = padded[:4]
        if not is_blank(date_cell):
            zh_part, en_part = split_bilingual(date_cell)
            if not zh_part and not en_part:
                zh_part, en_part = _split_en_zh_inline(cell_str(date_cell))
            if not zh_part and CJK_RE.search(cell_str(date_cell)):
                zh_part = cell_str(date_cell).split("\n")[0]
            if not en_part and any(day in cell_str(date_cell) for day in WEEKDAYS):
                en_part = cell_str(date_cell)
            # A new Chinese date starts a new day; do not keep yesterday's English.
            if zh_part:
                date_zh = zh_part
                date_en = en_part
            elif en_part:
                date_en = en_part

        times = _lines(time_cell)
        ens = _lines(en_cell)
        zhs = _lines(zh_cell)
        # English and Chinese sometimes share one cell.
        if ens and not zhs:
            split_ens: list[str] = []
            split_zhs: list[str] = []
            for item in ens:
                en, zh = _split_en_zh_inline(item)
                split_ens.append(en)
                split_zhs.append(zh)
            ens, zhs = split_ens, split_zhs
        n = max(len(times), len(ens), len(zhs), 1)
        for i in range(n):
            time_text = times[i] if i < len(times) else (times[-1] if times else "")
            en = ens[i] if i < len(ens) else (ens[-1] if ens else "")
            zh = zhs[i] if i < len(zhs) else (zhs[-1] if zhs else "")
            if not en and not zh and not time_text:
                continue
            subject_en, paper = _parse_paper(en)
            exam_date = _parse_en_date(date_en, doc.year) or _parse_cn_date(date_zh, doc.year)
            is_reserve = "reserve" in en.lower() or "後備" in zh
            if not en and not zh and not is_reserve:
                continue
            rec = {
                "year": doc.year,
                "exam_date": exam_date.isoformat() if exam_date else None,
                "date_text_en": date_en or None,
                "date_text_zh": date_zh or None,
                "subject_en": subject_en or None,
                "subject_zh": zh or None,
                "paper": paper,
                "is_reserve": is_reserve,
                "source_file": doc.path.name,
                "source_page": page.page_number,
            }
            rec.update(_parse_time(time_text))
            records.append(rec)
            if date_en:
                for prev in reversed(records[:-1]):
                    if prev["date_text_zh"] == rec["date_text_zh"] and not prev["date_text_en"]:
                        prev["date_text_en"] = date_en
                        if not prev["exam_date"]:
                            parsed = _parse_en_date(date_en, doc.year)
                            if parsed:
                                prev["exam_date"] = parsed.isoformat()
                    else:
                        break
    return records


def parse_practical_table(
    doc: RawDocument, page: RawPage, table: RawTable
) -> list[dict[str, Any]]:
    date_zh = ""
    date_en = ""
    records: list[dict[str, Any]] = []
    pending: dict[str, Any] | None = None
    for row in table.rows:
        if _is_header_row(row) or _is_empty_row(row):
            continue
        padded = list(row) + [""] * (4 - len(row))
        date_cell, time_cell, c2, c3 = padded[:4]
        if not is_blank(date_cell):
            zh_part, en_part = split_bilingual(date_cell)
            if zh_part:
                date_zh = zh_part
                date_en = en_part
            elif en_part:
                date_en = en_part
        subject_blob = " ".join(x for x in (cell_str(c2), cell_str(c3)) if x)
        en, zh = _split_en_zh_inline(subject_blob.replace("\n", " "))
        is_sen = "SEN" in subject_blob or "特殊需要" in subject_blob
        if not en and not zh and is_blank(time_cell) and not is_sen:
            if pending and date_en:
                pending["date_text_en"] = date_en
            continue
        is_tentative = (
            "tentative" in (date_en or "").lower()
            or "tentative" in subject_blob.lower()
            or "暫定" in (date_zh or "")
            or "暫定" in (date_en or "")
        )
        component = None
        lowered = f"{en} {zh}".lower()
        if "speaking" in lowered or "口試" in zh:
            component = "speaking"
        elif "practical" in lowered or "實習" in zh:
            component = "practical"
        rec = {
            "year": doc.year,
            "date_text_en": date_en or None,
            "date_text_zh": date_zh or None,
            "subject_en": re.sub(r"\s+", " ", en).strip(" -") or None,
            "subject_zh": zh or None,
            "component": component,
            "is_sen": is_sen,
            "is_tentative": is_tentative,
            "source_file": doc.path.name,
            "source_page": page.page_number,
        }
        rec.update(_parse_time(time_cell))
        # Merge SEN continuation rows that only add the SEN label.
        if pending and not rec["time_start"] and is_sen:
            pending["is_sen"] = True
            if date_en:
                pending["date_text_en"] = date_en
            continue
        if pending:
            records.append(pending)
        pending = rec
    if pending:
        records.append(pending)
    return records


def extract_timetable_notes(doc: RawDocument) -> list[dict[str, Any]]:
    notes: list[dict[str, Any]] = []
    for page in doc.pages:
        lines = [ln.strip() for ln in page.text.splitlines() if ln.strip()]
        keep: list[str] = []
        for line in lines:
            if line.startswith("日期") or line.startswith("Date"):
                continue
            if re.match(r"20\d{2}", line) and "EXAMINATION" in line.upper():
                continue
            if "TIMETABLE" in line.upper() or line.startswith("考試時間表"):
                continue
            keep.append(line)
        # Keep footnote-like lines
        text = "\n".join(keep)
        for pattern in (
            r"(#.+)",
            r"(\*.+)",
            r"(Note:.+)",
            r"(註：.+)",
            r"(注意.+)",
            r"(Candidates should.+)",
            r"(考生必須.+)",
        ):
            pass
        notes.append(
            {
                "year": doc.year,
                "source_file": doc.path.name,
                "notes_text": text,
            }
        )
    return notes
