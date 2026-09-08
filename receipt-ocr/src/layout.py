"""Map native PDF page elements into a spatial Excel-grid representation.

PDF coordinates are measured in points from the top-left page origin. The
mapper first normalizes each bbox to the page width and height, then clusters
element anchors into logical rows and columns. Excel positions are one-based
logical indices, not claims that a PDF point equals an Excel cell.
"""

from __future__ import annotations

from statistics import median
from typing import TypedDict

from .pdf_structure import PDFPageStructure, PDFStructureElement


class LayoutElement(TypedDict):
    type: str
    text: str
    name: str
    value: object
    bbox: list[float]
    normalized_bbox: list[float]
    excel_row: int
    excel_col: int
    editable: bool
    field_type: str


class PDFLayout(TypedDict):
    page: int
    page_width: float
    page_height: float
    row_tolerance: float
    column_tolerance: float
    logical_rows: int
    logical_columns: int
    elements: list[LayoutElement]


def _normalized_bbox(bbox: list[float], width: float, height: float) -> list[float]:
    x0, y0, x1, y1 = bbox
    return [x0 / width, y0 / height, x1 / width, y1 / height]


def _cluster(values: list[float], tolerance: float) -> dict[float, int]:
    """Assign sorted anchor values to one-based clusters within tolerance."""
    if not values:
        return {}

    unique_values = sorted(set(values))
    clusters: list[list[float]] = [[unique_values[0]]]
    for value in unique_values[1:]:
        if value - clusters[-1][-1] <= tolerance:
            clusters[-1].append(value)
        else:
            clusters.append([value])

    return {
        value: cluster_index
        for cluster_index, cluster in enumerate(clusters, start=1)
        for value in cluster
    }


def _default_tolerance(
    elements: list[PDFStructureElement], axis: str, page_dimension: float
) -> float:
    """Derive a normalized tolerance from the median native element size."""
    sizes = [
        (element["bbox"][3] - element["bbox"][1])
        if axis == "y"
        else (element["bbox"][2] - element["bbox"][0])
        for element in elements
        if element["bbox"][3] > element["bbox"][1]
        and element["bbox"][2] > element["bbox"][0]
    ]
    if not sizes:
        return 0.01
    tolerance = median(sizes) / page_dimension
    if axis == "y":
        tolerance *= 0.5
    return max(min(tolerance, 0.03), 0.005)


def map_page_layout(
    page: PDFPageStructure,
    *,
    row_tolerance: float | None = None,
    column_tolerance: float | None = None,
) -> PDFLayout:
    """Map one native PDF page to inferred logical Excel rows and columns.

    Tolerances are fractions of the page dimension and can be supplied by a
    caller. When omitted, they are derived from the median native element
    height/width and clamped to a small normalized range.
    """
    elements = page["elements"]
    width = page["width"]
    height = page["height"]
    if width <= 0 or height <= 0:
        raise ValueError("PDF page dimensions must be positive")

    normalized = [
        _normalized_bbox(element["bbox"], width, height) for element in elements
    ]
    effective_row_tolerance = (
        _default_tolerance(elements, "y", height)
        if row_tolerance is None
        else row_tolerance
    )
    effective_column_tolerance = (
        _default_tolerance(elements, "x", width)
        if column_tolerance is None
        else column_tolerance
    )
    row_anchors = [(bbox[1] + bbox[3]) / 2 for bbox in normalized]
    column_anchors = [bbox[0] for bbox in normalized]
    row_clusters = _cluster(row_anchors, effective_row_tolerance)
    column_clusters = _cluster(column_anchors, effective_column_tolerance)

    mapped: list[LayoutElement] = []
    for element, bbox, row_anchor, column_anchor in zip(
        elements, normalized, row_anchors, column_anchors
    ):
        mapped.append(
            {
                "type": element["type"],
                "text": element["text"],
                "name": element["name"],
                "value": element["value"],
                "bbox": element["bbox"],
                "normalized_bbox": [round(value, 6) for value in bbox],
                "excel_row": row_clusters[row_anchor],
                "excel_col": column_clusters[column_anchor],
                "editable": element["editable"],
                "field_type": element["field_type"],
            }
        )

    mapped.sort(key=lambda element: (element["excel_row"], element["excel_col"], element["bbox"][1]))
    return {
        "page": page["page"],
        "page_width": width,
        "page_height": height,
        "row_tolerance": effective_row_tolerance,
        "column_tolerance": effective_column_tolerance,
        "logical_rows": len(set(element["excel_row"] for element in mapped)),
        "logical_columns": len(set(element["excel_col"] for element in mapped)),
        "elements": mapped,
    }