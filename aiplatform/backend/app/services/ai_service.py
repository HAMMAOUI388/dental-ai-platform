from app.services.report_generator import (
    build_table_rows,
    draw_problem_overlays,
    save_pdf_report,
    number_teeth,
    assign_problems_to_numbered_teeth
)
from ultralytics import YOLO
import cv2, os
from app.core.config import settings


def run_ai_prediction(image_path, patient_id, patient_name, conf_thres=0.25):
    #Load models
    det_model = YOLO(settings.DETECTION_MODEL_PATH)
    num_model = YOLO(settings.NUMBERING_MODEL_PATH)

    #run numbering model first to get tooth boxes
    tooth_boxes = number_teeth(image_path)

    # Run detection model
    det_results = det_model.predict(source=image_path, conf=conf_thres)

    # Assign detected problems to numbered teeth
    findings = assign_problems_to_numbered_teeth(det_results, tooth_boxes)

    # Build findings table
    rows = build_table_rows(findings)

    # Draw annotated images
    # Draw problems: green boxes + labels
    img_problems = draw_problem_overlays(
        cv2.imread(image_path),
        findings,
        tooth_boxes,
        draw_numbering=False,
        draw_problem_boxes=True
    )

    # Draw numbering: blue boxes + tooth numbers
    img_numbered = draw_problem_overlays(
        cv2.imread(image_path),
        findings={},
        tooth_boxes=tooth_boxes,
        draw_numbering=True,
        draw_problem_boxes=False
    )

    # Build numbering table
    numbering_rows = [[tooth_id, "Detected"] for tooth_id in tooth_boxes.keys()]

    # Save images
    base = os.path.splitext(os.path.basename(image_path))[0]
    os.makedirs(settings.REPORTS_DIR, exist_ok=True)

    problems_img_path = os.path.join(settings.REPORTS_DIR, f"{base}_problems.jpg")
    numbering_img_path = os.path.join(settings.REPORTS_DIR, f"{base}_numbered.jpg")

    cv2.imwrite(problems_img_path, img_problems)
    cv2.imwrite(numbering_img_path, img_numbered)

    # Save PDF with both images + tables
    pdf_path = os.path.join(settings.REPORTS_DIR, f"{base}_report.pdf")
    save_pdf_report(
        pdf_path,
        patient_id,
        patient_name,
        rows,                  # findings table
        problems_img_path,     # annotated detection image
        numbering_img_path,    # numbering image
        numbering_rows         # numbering table
    )

    # URLs for frontend
    backend_url = getattr(settings, "BACKEND_HOST", "http://localhost:8000")
    base_url = f"{backend_url}/reports"

    return {
        "summary_text": f"Found {sum(len(v) for v in findings.values())} problems",
        "annotated_image_url": f"{base_url}/{base}_problems.jpg",
        "numbering_image_url": f"{base_url}/{base}_numbered.jpg",
        "pdf_url": f"{base_url}/{base}_report.pdf",
    }
