"""Shared text, number, and bilingual-cell helpers."""

from __future__ import annotations

import re
from typing import Any

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
LATIN_RE = re.compile(r"[A-Za-z]")

GENDER_MALE = re.compile(r"男生|\bMale\b")
GENDER_FEMALE = re.compile(r"女生|\bFemale\b")
GENDER_TOTAL = re.compile(r"總數|\bTotal\b")

CN_DIGIT = {
    "零": 0,
    "一": 1,
    "二": 2,
    "三": 3,
    "四": 4,
    "五": 5,
    "六": 6,
    "七": 7,
    "八": 8,
    "九": 9,
}

KNOWN_GROUPS: dict[str, tuple[str, str]] = {
    "business accounting and financial studies": (
        "Business, Accounting and Financial Studies",
        "企業、會計與財務概論",
    ),
    "mathematics": ("Mathematics", "數學"),
    "science": ("Science", "科學"),
    "technology and living": ("Technology and Living", "科技與生活"),
    "applied science": ("Applied Science", "應用科學"),
    "business management and law": ("Business, Management and Law", "商業、管理及法律"),
    "creative studies": ("Creative Studies", "創意學習"),
    "engineering and production": ("Engineering and Production", "工程及生產"),
    "media and communication": ("Media and Communication", "媒體及傳意"),
    "services": ("Services", "服務"),
    "applied learning chinese for non chinese speaking students": (
        "Applied Learning Chinese (for non-Chinese speaking students)",
        "應用學習中文（非華語學生適用）",
    ),
    "applied learning vocational english": (
        "Applied Learning (Vocational English)",
        "應用學習（職業英語）",
    ),
}


def cell_str(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("\xa0", " ").strip()


def is_blank(value: Any) -> bool:
    text = cell_str(value)
    return text == "" or text in {"None"}


def looks_missing(value: Any) -> bool:
    text = cell_str(value).replace("\n", "").strip()
    return text in {"", "-", "–", "—", "-%", "–%"}


def parse_int(value: Any) -> int | None:
    if looks_missing(value):
        return None
    for part in cell_str(value).split("\n"):
        part = part.replace(",", "").replace(" ", "").replace("%", "").strip()
        if re.fullmatch(r"-?\d+", part):
            return int(part)
    return None


def parse_pct(value: Any) -> float | None:
    if looks_missing(value):
        return None
    text = cell_str(value).replace("%", "").replace(" ", "").replace("\n", "")
    if not re.fullmatch(r"-?\d+(?:\.\d+)?", text):
        return None
    return float(text)


def split_count_pct(value: Any) -> tuple[int | None, float | None]:
    """Split a cell that stacks an absolute count over a percentage."""
    if looks_missing(value):
        return None, None
    count: int | None = None
    pct: float | None = None
    for part in re.split(r"[\n/]", cell_str(value)):
        part = part.strip()
        if looks_missing(part):
            continue
        if "%" in part:
            parsed = parse_pct(part)
            if parsed is not None:
                pct = parsed
        else:
            parsed = parse_int(part)
            if parsed is not None:
                count = parsed
            else:
                parsed = parse_pct(part)
                if parsed is not None:
                    pct = parsed
    return count, pct


def detect_gender(value: Any) -> str | None:
    text = cell_str(value)
    if not text:
        return None
    if GENDER_MALE.search(text):
        return "male"
    if GENDER_FEMALE.search(text):
        return "female"
    if GENDER_TOTAL.search(text) and "Subtotal" not in text and "小計" not in text:
        return "total"
    return None


def _is_reversed_latin(line: str) -> bool:
    letters = re.sub(r"[^A-Za-z]", "", line)
    return len(letters) >= 3 and letters[0].islower() and letters[-1].isupper()


def unrotate_vertical(text: str) -> str:
    """Undo 90°-rotated labels that pdfplumber reads top-to-bottom."""
    lines = [ln.strip() for ln in cell_str(text).splitlines() if ln.strip()]
    if not lines:
        return ""
    if not any(_is_reversed_latin(ln) for ln in lines):
        return "\n".join(lines)

    flipped: list[str] = []
    for line in lines:
        if LATIN_RE.search(line) and not CJK_RE.search(line):
            flipped.append(line[::-1])
        elif CJK_RE.search(line):
            flipped.append(line[::-1])
        else:
            flipped.append(line)

    zh = "".join(ln for ln in flipped if CJK_RE.search(ln))
    en_parts = [ln for ln in flipped if not CJK_RE.search(ln)]
    en_parts.reverse()
    en = re.sub(r"\s+", " ", " ".join(en_parts))
    en = re.sub(r"\s+,", ",", en).strip(" ,")
    if zh and en:
        return f"{zh}\n{en}"
    return zh or en


def _norm_key(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def split_bilingual(text: str) -> tuple[str, str]:
    """Split mixed Chinese/English cell text into (zh, en)."""
    raw = unrotate_vertical(text)
    zh_parts: list[str] = []
    en_parts: list[str] = []
    for line in [ln.strip() for ln in raw.splitlines() if ln.strip()]:
        if CJK_RE.search(line):
            zh_parts.append(line)
        else:
            en_parts.append(line)
    zh = "".join(zh_parts)
    en = re.sub(r"\s+", " ", " ".join(en_parts))
    en = re.sub(r"\s+([,.;:])", r"\1", en)
    en = re.sub(r"\(\s+", "(", en)
    en = re.sub(r"\s+\)", ")", en)
    en = en.strip(" ,")
    return zh, en


def match_subject_group(text: str) -> tuple[str | None, str | None]:
    zh, en = split_bilingual(text)
    key = _norm_key(en + " " + zh)
    for needle, (en_name, zh_name) in sorted(
        KNOWN_GROUPS.items(), key=lambda item: len(item[0]), reverse=True
    ):
        if needle in key:
            return en_name, zh_name
    if en or zh:
        return (en or None), (zh or None)
    return None, None


def is_summary_name(en: str, zh: str) -> bool:
    blob = f"{en} {zh}"
    return blob.startswith("All ") or zh.startswith("所有") or "All Category" in en


def merge_block_rows(rows: list[list[Any]]) -> list[str]:
    """Column-wise merge of sparse rows that belong to one gender block."""
    if not rows:
        return []
    width = max(len(row) for row in rows)
    columns: list[list[str]] = [[] for _ in range(width)]
    for row in rows:
        for i, cell in enumerate(row):
            text = cell_str(cell)
            if text and text not in columns[i]:
                columns[i].append(text)
    return ["\n".join(col) if col else "" for col in columns]


def find_gender_col(rows: list[list[Any]]) -> int | None:
    for row in rows:
        for i, cell in enumerate(row):
            if detect_gender(cell) == "male" and "男生" in cell_str(cell):
                return i
    return None


def chinese_numeral(text: str) -> int | None:
    text = text.strip()
    if text.isdigit():
        return int(text)
    if text in CN_DIGIT:
        return CN_DIGIT[text]
    if text == "十":
        return 10
    if text.startswith("十") and len(text) == 2 and text[1] in CN_DIGIT:
        return 10 + CN_DIGIT[text[1]]
    if text.endswith("十") and len(text) == 2 and text[0] in CN_DIGIT:
        return CN_DIGIT[text[0]] * 10
    if "十" in text:
        left, right = text.split("十", 1)
        if left in CN_DIGIT and (right == "" or right in CN_DIGIT):
            return CN_DIGIT[left] * 10 + (CN_DIGIT[right] if right else 0)
    return None
