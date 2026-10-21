# ResumeIQ audit report

Audit date: 21 October 2026

## Verified implementation

- Streamlit is the application entry point (`src/app.py`). It processes one uploaded PDF in a temporary file, deletes it, and keeps extracted text only in the browser session.
- PDF validation and PyMuPDF extraction are implemented. Invalid, unreadable, empty, and likely image-only PDFs produce an error or warning instead of an analysis result.
- The base matching path is PDF text -> preprocessing -> dictionary skill extraction -> TF-IDF cosine similarity and skill-gap output. The UI also exposes a section-aware path.
- The ML path is separate and genuine: synthetic resume/JD pairs are generated, then a TF-IDF pipeline trains and compares Logistic Regression and Linear SVC. `predict_match.py` loads the saved model lazily. It is labelled experimental and is not presented as a hiring probability.
- Section parsing, structured extraction, required/preferred JD classification, and weighted scoring for skills, projects, experience, certifications, and education are implemented and wired to the fourth UI tab.
- Jenkins and Docker files were inspected and preserved unchanged. Jenkins installs requirements, runs tests, generates synthetic data, trains models, and conditionally builds an image.

## Corrections made during this audit

- Required and preferred skill lists are now classified line-by-line, so adjacent lists without blank lines are not merged into one category.
- Later section scorers exclude skill evidence already attributed to an earlier section. This prevents the same skill from increasing multiple coverage components while retaining text similarity as a separate relevance signal.
- Heading-free resumes now report the full-text skills fallback as present rather than simultaneously reporting it as missing.

## Limitations and follow-up priorities

1. The supervised model is trained only on the included synthetic data. Its metrics are pipeline checks, not real-world recruiting accuracy.
2. Image-only PDFs require OCR, which is intentionally not included.
3. Section detection and the skill taxonomy are heuristic; unusual layouts or unknown technologies can be missed.
4. Docker currently runs the environment check by default rather than hosting Streamlit, and its package list is deliberately independent from `requirements.txt`; changing this should be a deployment decision.
