import re


def extract_batch_letter(batch: str | None) -> str | None:
    """
    Extracts single uppercase batch letter ('A', 'B', 'C') from strings like
    'Batch A', 'Batch B', 'Batch C', 'A', 'B', 'C', 'batch-a', '(A)', etc.
    Avoids accidentally matching 'B' from the word 'Batch'.
    """
    if not batch:
        return None
    s = str(batch).strip()
    if s.upper() in ("A", "B", "C"):
        return s.upper()
    # Match specific pattern: word boundary or 'batch' prefix followed by letter A, B, or C
    m = re.search(r"(?:batch|division|div|sec)?[\s\-_:\(]*([A-C])(?:\)|$|\s)", s, re.IGNORECASE)
    if m:
        return m.group(1).upper()
    m = re.search(r"\b([A-C])\b", s, re.IGNORECASE)
    if m:
        return m.group(1).upper()
    m = re.search(r"([A-C])$", s, re.IGNORECASE)
    if m:
        return m.group(1).upper()
    return s


def normalize_batch(batch: str | None) -> str | None:
    """Normalizes batch value to standard 'Batch X' format, or None if empty."""
    if not batch or str(batch).strip().lower() in ("none", "null", ""):
        return None
    letter = extract_batch_letter(batch)
    if letter and letter in ("A", "B", "C"):
        return f"Batch {letter}"
    return str(batch).strip()


def format_display_class(
    class_name: str | None,
    batch: str | None = None,
    is_lab: bool = False,
    session_type: str = "Theory"
) -> str:
    """
    Formats class division and practical batch according to EduNova standard:
    - Practical sessions: 'SY AD1 (A)', 'SY AD1 (B)', 'TY AD1 (B)', 'BE AD2 (C)'
    - Theory lectures: 'SY AD1', 'TY AD1', 'BE AD2' (unless explicitly assigned a batch)
    - Practical without batch: 'SY AD1 (Batch Required)'
    """
    if not class_name:
        return ""

    raw_class = str(class_name).replace("-", " ").strip()
    # Strip any trailing parenthesized batch (e.g. 'SY AD1 (A)' -> 'SY AD1') to avoid duplicate '(A) (A)'
    clean_class = re.sub(r"\s*\([A-Za-z0-9\s]+\)$", "", raw_class).strip()

    is_practical = is_lab or (session_type and session_type.lower() in ("practical", "lab", "lab practical"))

    batch_letter = extract_batch_letter(batch)

    if is_practical:
        if batch_letter:
            return f"{clean_class} ({batch_letter})"
        else:
            return f"{clean_class} (Batch Required)"

    # Theory lecture: only show batch if explicitly assigned
    if batch_letter:
        return f"{clean_class} ({batch_letter})"

    return clean_class
