"""Generate a newcomer guide PDF using only the Python standard library."""

from pathlib import Path
import re
import textwrap

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "system_guide.md"
OUTPUT = ROOT / "docs" / "financial_analytics_system_guide.pdf"
PAGE_WIDTH = 595
PAGE_HEIGHT = 842
LEFT = 48
TOP = 790
BOTTOM = 48


def clean_text(value: str) -> str:
    replacements = {"→": "->", "×": "x", "–": "-", "—": "-", "’": "'", "“": '"', "”": '"'}
    for old, new in replacements.items():
        value = value.replace(old, new)
    return value.encode("latin-1", "replace").decode("latin-1")


def strip_markup(value: str) -> str:
    value = re.sub(r"\*\*([^*]+)\*\*", r"\1", value)
    return re.sub(r"`([^`]+)`", r"\1", value)


def pdf_escape(value: str) -> str:
    return clean_text(value).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def wrap_line(text: str, width: int) -> list[str]:
    if not text:
        return [""]
    return textwrap.wrap(text, width=width, break_long_words=False, break_on_hyphens=False) or [""]


def parse_lines(markdown: str) -> list[tuple[str, str]]:
    result = []
    in_code = False
    for raw in markdown.splitlines():
        line = raw.rstrip()
        if line.startswith("```"):
            in_code = not in_code
            continue
        if not line:
            result.append(("space", ""))
        elif in_code:
            result.append(("code", line))
        elif line.startswith("# "):
            result.append(("title", strip_markup(line[2:])))
        elif line.startswith("## "):
            result.append(("h1", strip_markup(line[3:])))
        elif line.startswith("### "):
            result.append(("h2", strip_markup(line[4:])))
        elif line == "---":
            result.append(("rule", ""))
        elif line.startswith("- "):
            result.append(("bullet", "- " + strip_markup(line[2:])))
        else:
            result.append(("body", strip_markup(line)))
    return result


def build_page(lines: list[tuple[str, str]], page_number: int) -> bytes:
    commands = ["q", "1 1 1 rg", "0 0 595 842 re", "f", "Q"]
    y = TOP
    for kind, raw_text in lines:
        if kind == "space":
            y -= 7
            continue
        if kind == "rule":
            commands.extend(["0.75 0.80 0.85 RG", f"{LEFT} {y + 3} m 547 {y + 3} l S"])
            y -= 12
            continue
        if kind == "title":
            font, size, color, width, leading = "/F2", 21, "0.09 0.21 0.36", 52, 28
        elif kind == "h1":
            font, size, color, width, leading = "/F2", 14, "0.09 0.21 0.36", 76, 20
        elif kind == "h2":
            font, size, color, width, leading = "/F2", 11, "0.18 0.33 0.60", 92, 15
        elif kind == "code":
            font, size, color, width, leading = "/F3", 7.4, "0.12 0.16 0.20", 105, 10
        elif kind == "bullet":
            font, size, color, width, leading = "/F1", 8.5, "0.12 0.16 0.20", 100, 12
        else:
            font, size, color, width, leading = "/F1", 8.5, "0.12 0.16 0.20", 105, 12
        for text in wrap_line(raw_text, width):
            if y < BOTTOM + leading:
                break
            if kind == "code":
                commands.extend(["0.95 0.96 0.97 rg", f"{LEFT - 3} {y - 2} 499 {leading + 3} re", "f"])
            commands.extend(["BT", f"{color} rg", f"{font} {size} Tf", f"{LEFT} {y} Td", f"({pdf_escape(text)}) Tj", "ET"])
            y -= leading
        if kind in {"title", "h1", "h2"}:
            y -= 3
    commands.extend([
        "0.48 0.53 0.58 rg", "/F1 7 Tf", "BT", f"{LEFT} 27 Td",
        "(Financial Analytics and Risk Reporting System) Tj", "ET",
        "BT", f"/F1 7 Tf 475 27 Td", f"(Page {page_number}) Tj", "ET",
    ])
    return ("\n".join(commands) + "\n").encode("latin-1")


def write_pdf(page_contents: list[bytes]) -> None:
    objects: list[bytes] = []
    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    page_ids = []
    next_id = 6
    for _ in page_contents:
        page_ids.append(next_id)
        next_id += 2
    objects.append(f"<< /Type /Pages /Kids [{' '.join(f'{pid} 0 R' for pid in page_ids)}] /Count {len(page_contents)} >>".encode())
    objects.extend([
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Courier >>",
    ])
    for page_id, content in zip(page_ids, page_contents):
        objects.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_WIDTH} {PAGE_HEIGHT}] /Resources << /Font << /F1 3 0 R /F2 4 0 R /F3 5 0 R >> >> /Contents {page_id + 1} 0 R >>".encode())
        objects.append(f"<< /Length {len(content)} >>\nstream\n".encode() + content + b"endstream")
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for object_number, obj in enumerate(objects, 1):
        offsets.append(len(pdf))
        pdf.extend(f"{object_number} 0 obj\n".encode() + obj + b"\nendobj\n")
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode())
    pdf.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode())
    OUTPUT.write_bytes(pdf)


def main() -> None:
    parsed = parse_lines(SOURCE.read_text(encoding="utf-8"))
    pages = []
    current = []
    y = TOP
    for item in parsed:
        kind = item[0]
        height = {"title": 31, "h1": 23, "h2": 18, "code": 10, "bullet": 12, "body": 12, "space": 7, "rule": 12}[kind]
        if y - height < BOTTOM + 18:
            pages.append(build_page(current, len(pages) + 1))
            current = []
            y = TOP
        current.append(item)
        y -= height
    if current:
        pages.append(build_page(current, len(pages) + 1))
    write_pdf(pages)
    print(f"Generated {OUTPUT} ({len(pages)} pages)")


if __name__ == "__main__":
    main()
