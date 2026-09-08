"""Generate an editable Excel prototype from a mapped PDF page."""

from __future__ import annotations

import os
from collections import defaultdict
from pathlib import Path
from typing import TypedDict

from openpyxl import Workbook
from openpyxl.comments import Comment
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

from .layout import LayoutElement, PDFLayout


class ExcelGenerationResult(TypedDict):
    output_path: str
    text_elements: int
    form_fields: int
    editable_cells: int
    collisions_resolved: int
    field_cells: dict[str, str]


def _resolve_positions(layout: PDFLayout) -> tuple[dict[int, tuple[int, int]], int]:
    """Allocate unique cells while preserving each element's spatial order."""
    by_row: dict[int, list[tuple[int, LayoutElement]]] = defaultdict(list)
    for index, element in enumerate(layout["elements"]):
        by_row[element["excel_row"]].append((index, element))

    positions: dict[int, tuple[int, int]] = {}
    collisions = 0
    for row, row_elements in by_row.items():
        occupied: set[int] = set()
        for index, element in sorted(
            row_elements,
            key=lambda item: (item[1]["bbox"][0], item[1]["bbox"][2], item[0]),
        ):
            column = element["excel_col"]
            while column in occupied:
                column += 1
                collisions += 1
            occupied.add(column)
            positions[index] = (row, column)
    return positions, collisions


def _element_label(element: LayoutElement) -> str:
    return element["text"] if element["type"] == "text" else element["name"]


def _set_dimensions(
    worksheet, elements: list[LayoutElement], positions: dict[int, tuple[int, int]]
) -> None:
    column_metrics: dict[int, dict[str, float]] = defaultdict(
        lambda: {"source_width": 0.0, "text_width": 0.0}
    )
    row_heights: dict[int, float] = defaultdict(float)
    for index, element in enumerate(elements):
        row, column = positions[index]
        metric = column_metrics[column]
        metric["source_width"] = max(
            metric["source_width"], element["bbox"][2] - element["bbox"][0]
        )
        metric["text_width"] = max(metric["text_width"], len(_element_label(element)) * 0.8)
        line_count = max(1, element["text"].count("\n") + 1)
        row_heights[row] = max(
            row_heights[row],
            min(120.0, max(15.0, (element["bbox"][3] - element["bbox"][1]) * 1.15, line_count * 15.0)),
        )

    for column, metric in column_metrics.items():
        width = max(8.0, min(60.0, metric["source_width"] / 7.0, metric["text_width"]))
        worksheet.column_dimensions[get_column_letter(column)].width = width
    for row, height in row_heights.items():
        worksheet.row_dimensions[row].height = height


def _write_text_cell(cell, element: LayoutElement) -> None:
    cell.value = element["text"]
    cell.alignment = Alignment(wrap_text=True, vertical="top")
    cell.font = Font(name="Calibri", size=10)


def _write_field_cell(cell, element: LayoutElement, page: int) -> None:
    cell.value = element["value"] if element["value"] not in (None, "") else None
    cell.alignment = Alignment(horizontal="right", vertical="center")
    cell.fill = PatternFill(fill_type="solid", fgColor="EAF3F8")
    cell.border = Border(
        left=Side(style="thin", color="7F9DB9"),
        right=Side(style="thin", color="7F9DB9"),
        top=Side(style="thin", color="7F9DB9"),
        bottom=Side(style="thin", color="7F9DB9"),
    )
    cell.comment = Comment(
        "Source PDF field:\n"
        f"{element['name']}\n"
        f"PDF page: {page}\n"
        f"PDF bbox: {element['bbox']}",
        "PDF layout mapper",
    )


def generate_page_workbook(layout: PDFLayout, output_path: str | os.PathLike[str]) -> ExcelGenerationResult:
    """Generate one editable worksheet from a generic mapped PDF layout."""
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = f"Page {layout['page']}"
    positions, collisions = _resolve_positions(layout)

    text_count = 0
    field_count = 0
    field_cells: dict[str, str] = {}
    for index, element in enumerate(layout["elements"]):
        row, column = positions[index]
        cell = worksheet.cell(row=row, column=column)
        if element["type"] == "field":
            _write_field_cell(cell, element, layout["page"])
            field_count += 1
            field_cells[element["name"]] = cell.coordinate
        else:
            _write_text_cell(cell, element)
            text_count += 1

    _set_dimensions(worksheet, layout["elements"], positions)
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(output)
    return {
        "output_path": str(output),
        "text_elements": text_count,
        "form_fields": field_count,
        "editable_cells": field_count,
        "collisions_resolved": collisions,
        "field_cells": field_cells,
    }