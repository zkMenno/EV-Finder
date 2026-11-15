"""Minimal OpenDocument spreadsheet (.ods) reader, standard library only.

DfT publishes the EVCI tables as ODS only. They are a few kB each, so reading content.xml
with ElementTree is enough and saves a dependency (odfpy / pandas). Returns each sheet as a
list of rows of plain Python values: float for numbers, ISO strings for dates, str for text,
None for empty cells. Repeated empty rows and columns are capped so a sheet padded to
1,048,576 rows doesn't blow up memory.
"""

from __future__ import annotations

import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

TABLE = "urn:oasis:names:tc:opendocument:xmlns:table:1.0"
OFFICE = "urn:oasis:names:tc:opendocument:xmlns:office:1.0"
TEXT = "urn:oasis:names:tc:opendocument:xmlns:text:1.0"
T, OF, X = f"{{{TABLE}}}", f"{{{OFFICE}}}", f"{{{TEXT}}}"
MAX_REPEAT = 256
MAX_CONTENT_BYTES = 64 * 1024 * 1024

Cell = float | str | None


def _value(cell: ET.Element) -> Cell:
    vt = cell.get(OF + "value-type")
    if vt in ("float", "percentage", "currency"):
        return float(cell.get(OF + "value", "nan"))
    if vt == "date":
        return cell.get(OF + "date-value")
    if vt == "boolean":
        return cell.get(OF + "boolean-value")
    parts = ["".join(p.itertext()) for p in cell.findall(X + "p")]
    return "\n".join(parts) if parts else None


def read_sheets(path: Path) -> dict[str, list[list[Cell]]]:
    with zipfile.ZipFile(path) as zf:
        info = zf.getinfo("content.xml")
        if info.file_size > MAX_CONTENT_BYTES:
            raise ValueError(f"{path.name}: content.xml is {info.file_size} bytes; refused")
        root = ET.fromstring(zf.read("content.xml"))
    sheets: dict[str, list[list[Cell]]] = {}
    for table in root.iter(T + "table"):
        rows: list[list[Cell]] = []
        for row in table.iter(T + "table-row"):
            cells: list[Cell] = []
            for cell in row:
                if cell.tag not in (T + "table-cell", T + "covered-table-cell"):
                    continue
                n = min(int(cell.get(T + "number-columns-repeated", "1")), MAX_REPEAT)
                cells.extend([_value(cell)] * n)
            while cells and cells[-1] is None:
                cells.pop()
            n_rows = min(int(row.get(T + "number-rows-repeated", "1")), MAX_REPEAT)
            rows.extend([list(cells) for _ in range(n_rows if cells else min(n_rows, 1))])
        while rows and not rows[-1]:
            rows.pop()
        sheets[table.get(T + "name", f"sheet{len(sheets)}")] = rows
    return sheets


def write_sheets(path: Path, sheets: dict[str, list[list[Cell]]]) -> None:
    """Write a tiny ODS (for test fixtures): numbers as float cells, everything else as text."""
    from xml.sax.saxutils import escape, quoteattr

    body = []
    for name, rows in sheets.items():
        body.append(f"<table:table table:name={quoteattr(name)}>")
        for row in rows:
            body.append("<table:table-row>")
            for v in row:
                if isinstance(v, int | float) and not isinstance(v, bool):
                    body.append(
                        f'<table:table-cell office:value-type="float" office:value="{v!r}">'
                        f"<text:p>{v!r}</text:p></table:table-cell>"
                    )
                elif v is None:
                    body.append("<table:table-cell/>")
                else:
                    body.append(
                        '<table:table-cell office:value-type="string">'
                        f"<text:p>{escape(str(v))}</text:p></table:table-cell>"
                    )
            body.append("</table:table-row>")
        body.append("</table:table>")
    content = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f'<office:document-content xmlns:office="{OFFICE}" xmlns:table="{TABLE}" '
        f'xmlns:text="{TEXT}" office:version="1.2"><office:body><office:spreadsheet>'
        + "".join(body)
        + "</office:spreadsheet></office:body></office:document-content>"
    )
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr(zipfile.ZipInfo("mimetype"), "application/vnd.oasis.opendocument.spreadsheet")
        zf.writestr("content.xml", content, compress_type=zipfile.ZIP_DEFLATED)
