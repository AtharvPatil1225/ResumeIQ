# ResumeIQ — AI/ML Resume Analyzer

> A Python-based, genuinely machine-learned resume analysis and job-matching system,
> developed as a second-year BTech IT/AIML project.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Features](#features)
4. [Technology Stack](#technology-stack)
5. [Dataset Requirements](#dataset-requirements)
6. [Windows PowerShell Setup](#windows-powershell-setup)
7. [Training the ML Models](#training-the-ml-models)
8. [Evaluation Results](#evaluation-results)
9. [Running the Application](#running-the-application)
10. [Running Tests](#running-tests)
11. [Jenkins CI/CD](#jenkins-cicd)
12. [Privacy & Data Handling](#privacy--data-handling)
13. [Limitations](#limitations)
14. [Project Status](#project-status)

---

## Project Overview

ResumeIQ accepts a PDF resume, extracts its text, identifies technical
skills, classifies the resume–job fit, and displays a detailed analysis
report. The system supports:

- **PDF parsing** — PyMuPDF, with scanned-PDF detection
- **Skill extraction** — ~120-term dictionary taxonomy (Python, Java, React,
  Docker, AWS, TensorFlow, etc.)
- **Resume–job matching** — TF-IDF cosine similarity + optional ML classifier
- **Skill-gap analysis** — matched vs. missing skills with coverage %
- **ML classification** — Logistic Regression and Linear SVM, compared via
  5-fold cross-validation
- **Interactive UI** — Streamlit web application

---

## Architecture

```
src/
├── app.py                    # Streamlit UI (3 tabs)
├── preprocess.py             # Shared text cleaner (preserves C++, .NET etc.)
├── pdf_extractor.py          # PDF extraction + validation + scanned detection
├── skill_extractor.py        # ~120-skill dictionary matching
├── matching_engine.py        # TF-IDF cosine similarity + skill gap
├── predict_match.py          # Lazy-loaded ML match predictor
├── train_model.py            # LR + LinearSVC training, CV, confusion matrix
├── evaluate_model.py         # Standalone evaluation script
├── generate_training_data.py # Synthetic 90-example training dataset
├── build_resume_dataset.py   # Build JSONL from raw PDF folder
├── validate_resume_jsonl.py  # JSONL integrity validation
├── validate_resume_dataset.py# CSV integrity validation
├── analyze_skills.py         # Skill frequency analysis from JSONL
├── job_matcher.py            # CLI interactive job matcher
└── test_*.py                 # Pytest test modules
```

**Data flow:**
```
PDF Upload → pdf_extractor → preprocess → skill_extractor → matching_engine
                                        ↘ predict_match (ML) ↗
                              job description input ────────────────↗
```

---

## Features

| Feature | Status | Notes |
|---------|--------|-------|
| PDF text extraction | ✅ Implemented | PyMuPDF; detects scanned PDFs |
| PDF validation (type, size) | ✅ Implemented | Max 10 MB, .pdf only |
| Technical skill extraction | ✅ Implemented | ~120 skills, boundary-aware |
| TF-IDF cosine similarity | ✅ Implemented | Lexical baseline |
| Skill-gap analysis | ✅ Implemented | Coverage %, matched/missing |
| Logistic Regression classifier | ✅ Implemented | TF-IDF pipeline |
| Linear SVM classifier | ✅ Implemented | TF-IDF pipeline |
| 5-fold cross-validation | ✅ Implemented | Stratified |
| Confusion matrix PNG | ✅ Implemented | Saved to reports/ |
| Streamlit UI | ✅ Implemented | 3 tabs |
| Text preprocessing module | ✅ Implemented | Preserves C++, .NET, Node.js |
| Synthetic training data | ✅ Implemented | 90 examples, 6 roles × 3 labels |
| Real PICT TNP PDF support | ⏳ Data-dependent | Pipeline ready; needs real PDFs |
| Sentence Transformer matching | ⏳ Optional | Not installed by default |

---

## Technology Stack

- **Python 3.10+**
- **scikit-learn** — TF-IDF vectorisation, Logistic Regression, LinearSVC, pipelines
- **PyMuPDF (pymupdf)** — PDF text extraction
- **Pandas / NumPy** — data handling
- **Matplotlib** — confusion matrix visualisation
- **Streamlit** — interactive web UI
- **joblib** — model serialisation
- **pytest** — automated testing

---

## Dataset Requirements

### Synthetic Dataset (included)
- 90 examples across 6 job roles (Data Analyst, Backend Developer, etc.)
- 3 match labels: 0 = Poor, 1 = Partial, 2 = Strong
- **Purpose:** pipeline smoke-testing only; not real-world validation.

### Real PICT TNP Resume Data
- Obtain authorised PDF exports from PICT Training & Placement.
- Place PDFs in: `data/raw_resumes/2026/`, `data/raw_resumes/2027/`, `data/raw_resumes/2028/`
- Run: `python src/build_resume_dataset.py`
- **Never commit real student PDFs or personal information to Git.**

---

## Windows PowerShell Setup

```powershell
# 1. Clone the repository
git clone https://github.com/AtharvPatil1225/ResumeIQ.git
cd ResumeIQ\ResumeIQ

# 2. Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify the environment
python src/test_setup.py
```

---

## Training the ML Models

```powershell
# Step 1 — Generate the synthetic training dataset
python src/generate_training_data.py
# Output: data/training/resume_job_pairs_expanded.csv

# Step 2 — Train and compare Logistic Regression vs. Linear SVM
python src/train_model.py
# Output: models/resume_matcher.joblib
#         reports/confusion_matrix_logistic_regression.png
#         reports/confusion_matrix_linear_svm.png

# Step 3 — Run standalone evaluation (optional)
python src/evaluate_model.py
```

---

## Evaluation Results

> **Important:** The results below are from the synthetic training dataset only.
> They demonstrate that the ML pipeline works correctly, but do not indicate
> real-world performance on actual student resumes.

Results vary slightly with random state, but typical outputs on the
synthetic 90-example dataset (70/30 train/test split):

| Model | Test Accuracy | Notes |
|-------|--------------|-------|
| Logistic Regression | ~85–100% | Depends on split; synthetic data is easy |
| Linear SVM | ~85–100% | Often comparable to LR |

Cross-validation (5-fold stratified) is reported during training. The best
model by mean CV accuracy is saved automatically.

**Confusion matrices** are saved to `reports/` as PNG files.

*Do not use these numbers in a report as evidence of real-world accuracy.*

---

## Running the Application

```powershell
# Start the Streamlit application
streamlit run src/app.py
```

The application opens in your browser at `http://localhost:8501`.

Four tabs are available, including Section Analysis for per-section evidence and scoring:
- **Resume Analysis** — upload a PDF, see extracted text and detected skills
- **Job Matching** — paste a job description and view match scores
- **Skill Gap** — compare your skills against a job description

---

## Running Tests

```powershell
# Run all tests (pytest.ini configures src/ as pythonpath automatically)
python -m pytest -v

# Run a specific test file
python -m pytest -v src/test_skill_extractor.py

# Run with short failure summaries
python -m pytest -v --tb=short
```

Expected: all tests pass. Current test suite coverage:

| File | Tests | Covers |
|------|-------|--------|
| test_matching_engine.py | 7 | TF-IDF matching, skill gap, edge cases |
| test_skill_extractor.py | 9 | Original cases + expanded taxonomy |
| test_pdf_extractor.py | 7 | PDF extraction, folder inspection |
| test_pdf_validation.py | 8 | validate_pdf_upload, is_likely_scanned |
| test_preprocess.py | 15 | Technical term preservation, cleaning |
| test_predict_match.py | 6 | Lazy model loading, error handling |
| test_folder_inspection.py | 2 | Folder stats |

---

## Jenkins CI/CD

The `Jenkinsfile` in the project root defines the CI pipeline:

1. **Checkout** — pulls the repository
2. **Check Python** — verifies the Python interpreter
3. **Install Dependencies** — `pip install -r requirements.txt`
4. **Verify ML Environment** — runs `test_setup.py`
5. **Run Automated Tests** — `pytest -v --tb=short`
6. **Generate Synthetic Data** — creates the training CSV
7. **Train ML Models** — trains LR and LinearSVC
8. **Build Docker Image** — only if Docker is available on the agent

**Configure the Python path** on your Jenkins node by setting the
`PYTHON` environment variable (e.g., to `python` or a full path).
Do not hardcode machine-specific Windows Store paths.

---

## Privacy & Data Handling

- No student resume files are committed to Git (see `.gitignore`).
- No contact details (name, phone, email) are used as ML features.
- The Streamlit app does not permanently store uploaded files; they are
  processed in a temporary file and immediately deleted.
- No data is sent to external APIs or third-party services.
- Secrets and credentials must be stored in `.env` files (excluded from Git).

---

## Limitations

1. **Synthetic data only** — the current training dataset contains 90
   synthetic examples. Performance numbers do not predict real-world accuracy.
2. **No OCR** — scanned-image PDFs cannot be processed. A text-based PDF
   is required. OCR (e.g., Tesseract) is not implemented.
3. **Dictionary-based skill extraction** — skills not in the ~120-term
   taxonomy are not detected. The extractor does not understand context.
4. **No semantic similarity** — matching uses TF-IDF cosine similarity,
   which is lexical. Sentence Transformer embeddings are an optional
   enhancement not included by default.
5. **Labels require human annotation** — if real PICT TNP resume data is used,
   match labels must be assigned manually by qualified annotators before
   supervised training is valid.
6. **Similarity ≠ hiring probability** — all scores are experimental metrics.

---

## Section-aware scoring

The Streamlit app includes a fourth **Section Analysis** tab. It reports
separate, explainable scores for technical skills, projects, internship/work
experience, certifications, and education/coursework. Default weights are
35%, 25%, 20%, 10%, and 10%, respectively. Missing sections are excluded and
the remaining weights are proportionally normalized, so a fresher's projects
can contribute without an internship section.

Required skills receive twice the within-section weight of preferred skills.
Skill evidence is attributed to its first relevant section to avoid counting
the same coverage evidence more than once; TF-IDF text similarity remains a
separate relevance measure. These scores are experimental matching measures,
not hiring probabilities.

See [docs/AUDIT_REPORT.md](docs/AUDIT_REPORT.md) for the verified scope and limitations.

## Project Status

| Component | Status |
|-----------|--------|
| Repository structure | ✅ Complete |
| Synthetic training pipeline | ✅ Complete |
| LR + LinearSVC model comparison | ✅ Complete |
| 5-fold cross-validation | ✅ Complete |
| Confusion matrix export | ✅ Complete |
| PDF extraction + validation | ✅ Complete |
| Expanded skill taxonomy (~120) | ✅ Complete |
| Text preprocessing module | ✅ Complete |
| TF-IDF cosine matching | ✅ Complete |
| Skill-gap analysis | ✅ Complete |
| Streamlit UI | ✅ Complete |
| pytest test suite | ✅ Complete |
| Jenkins CI pipeline | ✅ Complete |
| Docker image | ✅ Dockerfile present |
| Real PICT TNP data pipeline | ⏳ Ready; awaiting authorised PDFs |
| Manual label annotation | ⏳ Required before real-data training |
