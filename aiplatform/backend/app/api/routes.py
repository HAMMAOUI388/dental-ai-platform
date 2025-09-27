from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.services.ai_service import run_ai_prediction
import os

router = APIRouter()

REPORTS_DIR = "app/reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

@router.post("/predict")
async def predict(
    patient_id: str = Form(...),
    patient_name: str = Form(...),
    image: UploadFile = File(...)
):
    # Save uploaded image temporarily
    image_path = f"/tmp/{image.filename}"
    with open(image_path, "wb") as f:
        f.write(await image.read())

    report = run_ai_prediction(
        image_path=image_path,
        patient_id=patient_id,
        patient_name=patient_name
    )

    # Be defensive with .get(...) to avoid KeyError
    return JSONResponse({
        "summary_text": report.get("summary_text", ""),
        "annotated_image_url": report.get("annotated_image_url"),
        "pdf_url": report.get("pdf_url", ""),
        "detection_report": report.get("detection_report", []),
    })
