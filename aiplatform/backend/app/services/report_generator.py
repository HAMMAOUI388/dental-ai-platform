from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import cv2
import numpy as np
from fpdf import FPDF
from ultralytics import YOLO


#(Optional) Config
# If I use these functions only as helpers from ai_service.py, it's fine to keep
# the model loading here – but ONLY if I actually call the functions that need them.
# Otherwise nothing will run at import time besides the helpers below.

try:
    from app.core.config import settings
    DETECTION_MODEL_PATH = getattr(settings, "DETECTION_MODEL_PATH", None)
    NUMBERING_MODEL_PATH = getattr(settings, "NUMBERING_MODEL_PATH", None)
except Exception:
    DETECTION_MODEL_PATH = None
    NUMBERING_MODEL_PATH = None

detection_model = YOLO(DETECTION_MODEL_PATH) if DETECTION_MODEL_PATH else None
tooth_model = YOLO(NUMBERING_MODEL_PATH) if NUMBERING_MODEL_PATH else None

#Utilities

def build_table_rows(findings: Dict[str, List[Tuple[str, float]]]) -> List[List[str]]:
    """Convert findings into table rows for the PDF."""
    rows: List[List[str]] = []
    for tooth, items in findings.items():
        for issue, conf in items:
            rows.append([str(tooth), str(issue), f"{float(conf):.2f}"])
    return rows


def compute_iou(boxA: Tuple[int, int, int, int], boxB: Tuple[int, int, int, int]) -> float:
    """Compute intersection over union for two boxes [x1,y1,x2,y2]."""
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])

    interW = max(0, xB - xA)
    interH = max(0, yB - yA)
    interArea = interW * interH
    boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
    boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

    denom = (boxAArea + boxBArea - interArea + 1e-6)
    return float(interArea / denom)


def number_teeth(image_path: str) -> Dict[str, List[Tuple[int, int, int, int]]]:
    """Return a dict mapping tooth numbers to bounding boxes."""
    if tooth_model is None:
        raise RuntimeError("Tooth numbering model is not loaded/configured.")
    results = tooth_model.predict(source=image_path, imgsz=1024, conf=0.3)
    tooth_boxes: Dict[str, List[Tuple[int, int, int, int]]] = {}
    for result in results:
        if not hasattr(result, "boxes") or len(result.boxes) == 0:
            continue
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls = int(box.cls.item())
            tooth_number = str(tooth_model.names[cls])
            tooth_boxes.setdefault(tooth_number, []).append((x1, y1, x2, y2))
    return tooth_boxes


def assign_problems_to_numbered_teeth(detection_results, tooth_boxes):
    """Map detected problems to the nearest tooth boxes using IoU + distance fallback."""
    if detection_model is None:
        raise RuntimeError("Detection model is not loaded/configured.")
    findings: Dict[str, List[Tuple[str, float]]] = {}
    for result in detection_results:
        if not hasattr(result, "boxes") or len(result.boxes) == 0:
            continue
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls = int(box.cls.item())
            label = str(detection_model.names[cls])
            conf = float(box.conf[0])

            detection_box = (x1, y1, x2, y2)

            # Step 1: IoU match
            best_iou = 0.0
            nearest_tooth = None
            for tooth_num, boxes in tooth_boxes.items():
                for tb in boxes:
                    iou = compute_iou(detection_box, tb)
                    if iou > best_iou:
                        best_iou = iou
                        nearest_tooth = tooth_num

            # Step 2: Distance fallback if IoU too low
            if best_iou < 0.1:
                cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
                min_dist = float("inf")
                for tooth_num, boxes in tooth_boxes.items():
                    for (tx1, ty1, tx2, ty2) in boxes:
                        tcx, tcy = (tx1 + tx2) // 2, (ty1 + ty2) // 2
                        dist = (cx - tcx) ** 2 + (cy - tcy) ** 2
                        if dist < min_dist:
                            min_dist = dist
                            nearest_tooth = tooth_num

            if nearest_tooth:
                findings.setdefault(nearest_tooth, []).append((label, conf))
            else:
                findings.setdefault("Unknown", []).append((label, conf))
    return findings


def draw_problem_overlays(img, findings, tooth_boxes, draw_numbering=True, draw_problem_boxes=True):
    """
    Draw tooth boxes (if provided) and problem labels (if provided) on a copy of the image.
    draw_numbering: draw blue tooth boxes + numbers
    draw_problem_boxes: draw green detected problem boxes + labels
    """
    img_copy = img.copy()

    # Draw tooth numbering
    if draw_numbering:
        for tooth_num, boxes in tooth_boxes.items():
            for (x1, y1, x2, y2) in boxes:
                cv2.rectangle(img_copy, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(
                    img_copy,
                    f"Tooth {tooth_num}",
                    (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 0, 0),
                    1,
                )

    # Draw detected problems
    if draw_problem_boxes:
        for tooth_num, issues in findings.items():
            if tooth_num not in tooth_boxes:
                continue
            x1, y1, x2, y2 = tooth_boxes[tooth_num][0]
            for i, (label, conf) in enumerate(issues):
                cv2.putText(
                    img_copy,
                    f"{label} {conf:.2f}",
                    (x1, y2 + 15 + i * 15),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (0, 255, 0),
                    1,
                )
                cv2.rectangle(img_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)

    return img_copy



def _safe_place_image(pdf: FPDF, image_path: Optional[str], label: str) -> None:
    """
    Helper: place an image in the PDF if the path is valid; otherwise skip gracefully.
    """
    if not image_path:
        return
    p = str(image_path)
    if not os.path.exists(p):
        return
    # Section label
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, label, ln=True)
    # Place image at current cursor; scale to width 180
    pdf.image(p, x=10, w=180)
    # Add vertical spacing so the next section won't overlap
    pdf.ln(6)

from datetime import datetime
from fpdf import FPDF
from pathlib import Path
import os
from typing import List, Optional


def _safe_place_image(pdf: FPDF, image_path: Optional[str], label: str) -> None:
    """Helper: place an image in the PDF if valid, otherwise skip."""
    if not image_path:
        return
    p = str(image_path)
    if not os.path.exists(p):
        return
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, label, ln=True)
    pdf.image(p, x=10, w=180)
    pdf.ln(6)


def save_pdf_report(
    pdf_path: str | Path,
    patient_id: str,
    patient_name: str,
    findings_table: List[List[str]],      #[tooth, issue, confidence]
    annotated_image_path: str | Path,
    numbering_image_path: Optional[str | Path] = None,
    numbering_table: Optional[List[List[str]]] = None  #[FDI_number, Detected_label]
) -> str:
    """
    Generate a PDF dental report with:
      - patient info
      - date/time of generation
      - optional tooth numbering image + table
      - annotated image + problems table
    """

    pdf = FPDF()
    pdf.add_page()

    # Header
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Dental AI Report", ln=True)

    # Patient info
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 7, f"Patient: {patient_name} (ID: {patient_id})", ln=True)

    # Date/time
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pdf.cell(0, 7, f"Report generated: {now_str}", ln=True)
    pdf.ln(4)

    #Tooth numbering section
    if numbering_image_path or numbering_table:
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 8, "Tooth Numbering", ln=True)

        _safe_place_image(pdf, str(numbering_image_path) if numbering_image_path else None,
                          "Numbering Image")

        if numbering_table:
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 8, "Numbering Table:", ln=True)

            # Table headers
            pdf.set_font("Arial", "B", 10)
            pdf.cell(60, 8, "FDI Number", 1)
            pdf.cell(120, 8, "Detected Label", 1)
            pdf.ln()

            # Rows
            pdf.set_font("Arial", "", 10)
            for row in numbering_table:
                fdi, label = (row + ["", ""])[:2]
                pdf.cell(60, 8, str(fdi), 1)
                pdf.cell(120, 8, str(label), 1)
                pdf.ln()

            pdf.ln(4)

    #Findings section
    _safe_place_image(pdf, str(annotated_image_path), "Annotated Findings")

    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, "Detected Problems:", ln=True)

    # Table headers
    pdf.set_font("Arial", "B", 10)
    pdf.cell(40, 8, "Tooth", 1)
    pdf.cell(100, 8, "Issue", 1)
    pdf.cell(40, 8, "Confidence", 1)
    pdf.ln()

    # Rows
    pdf.set_font("Arial", "", 10)
    for row in findings_table:
        tooth, issue, conf = (row + ["", "", ""])[:3]
        pdf.cell(40, 8, str(tooth), 1)
        pdf.cell(100, 8, str(issue), 1)
        pdf.cell(40, 8, str(conf), 1)
        pdf.ln()

    # Save
    out_path = str(pdf_path)
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    pdf.output(out_path)

    return out_path
