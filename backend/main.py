import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import pymupdf
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_DIR))

from matching_engine import match_resume_to_job
from predict_match import MODEL_PATH, predict_match

MAX_UPLOAD_BYTES = 10 * 1024 * 1024
DEFAULT_ORIGINS = "http://127.0.0.1:5173,http://localhost:5173,http://localhost:3000,http://127.0.0.1:3000"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = joblib.load(MODEL_PATH) if MODEL_PATH.exists() else None
    yield
    app.state.model = None


app = FastAPI(
    title="ResumeIQ API",
    description="Resume parsing and experimental resume-to-job matching.",
    version="0.1.0",
    lifespan=lifespan,
)

origins = [
    origin.strip()
    for origin in os.getenv("RESUMEIQ_CORS_ORIGINS", DEFAULT_ORIGINS).split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "model_loaded": app.state.model is not None,
    }


@app.post("/api/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
):
    if not resume.filename or Path(resume.filename).suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="Upload a PDF resume.")
    if not job_description.strip():
        raise HTTPException(status_code=422, detail="Job description cannot be empty.")

    pdf_bytes = await resume.read(MAX_UPLOAD_BYTES + 1)
    if len(pdf_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="PDF must be 10 MB or smaller.")
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="The uploaded PDF is empty.")

    try:
        with pymupdf.open(stream=pdf_bytes, filetype="pdf") as document:
            resume_text = "\n".join(page.get_text("text") for page in document).strip()
    except Exception:
        raise HTTPException(status_code=400, detail="The uploaded file is not a readable PDF.") from None

    if not resume_text:
        raise HTTPException(status_code=422, detail="No selectable text was found in the PDF.")
    if app.state.model is None:
        raise HTTPException(
            status_code=503,
            detail="The trained model is unavailable. Run python src/train_model.py first.",
        )

    try:
        result = match_resume_to_job(resume_text, job_description)
        category = predict_match(resume_text, job_description, model=app.state.model)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    return {
        "predicted_category": category,
        "similarity_percentage": result["similarity_percentage"],
        "skill_coverage_percentage": result["skill_coverage_percentage"],
        "matched_skills": result["matched_skills"],
        "missing_skills": result["missing_skills"],
        "job_skills_detected": result["job_skills_detected"],
        "notice": "Experimental result from synthetic-data training; not a hiring decision.",
    }

