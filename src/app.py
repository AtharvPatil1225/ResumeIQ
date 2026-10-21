"""
app.py
------
ResumeIQ — Streamlit interactive application.

Launch with:
    streamlit run src/app.py

The application provides four tabs:
  1. Resume Analysis   — upload a PDF and inspect extracted text and skills.
  2. Job Matching      — compare the resume against a job description.
  3. Skill Gap         — visualise matched and missing skills.
  4. Section Analysis  — per-section scoring with evidence and weights.

All ML components (skill extraction, cosine similarity, classification)
are implemented in separate modules and reused here without duplication.
The ML model is optional: the app works without it; matching via
TF-IDF cosine similarity and skill-gap analysis are always available.
"""

import sys
from pathlib import Path

# Ensure project modules are importable regardless of launch directory.
_SRC = Path(__file__).resolve().parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

import streamlit as st

from pdf_extractor import (
    extract_text_from_pdf,
    validate_pdf_upload,
    is_likely_scanned,
)
from skill_extractor import extract_skills
from matching_engine import match_resume_to_job
from preprocess import clean_resume_text
from composite_scorer import compute_composite_score, DEFAULT_WEIGHTS
from section_parser import (
    SKILLS, EXPERIENCE, PROJECTS, CERTIFICATIONS, EDUCATION, ACHIEVEMENTS,
)

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="ResumeIQ — AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Main container */
    .main { background-color: #0e1117; }
    /* Card style */
    .iq-card {
        background: linear-gradient(135deg, #1a1f2e 0%, #16213e 100%);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
    }
    /* Skill pill */
    .skill-pill {
        display: inline-block;
        background: #0d6efd22;
        border: 1px solid #0d6efd88;
        border-radius: 20px;
        padding: 2px 10px;
        margin: 3px;
        font-size: 0.85em;
        color: #58a6ff;
    }
    .skill-pill-missing {
        background: #dc354522;
        border: 1px solid #dc354588;
        color: #ff6b6b;
    }
    .skill-pill-matched {
        background: #19863622;
        border: 1px solid #19863688;
        color: #4caf50;
    }
    /* Score badge */
    .score-badge {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
    }
    h1, h2, h3 { color: #e6edf3 !important; }
    /* Section analysis cards */
    .section-card {
        background: linear-gradient(135deg, #1a1f2e 0%, #16213e 100%);
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 0.8rem;
    }
    .section-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    .section-card-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #e6edf3;
    }
    .section-score-badge {
        font-size: 1.3rem;
        font-weight: 700;
        padding: 2px 12px;
        border-radius: 8px;
    }
    .score-high { background: #19863622; color: #4caf50; border: 1px solid #19863688; }
    .score-med  { background: #f5a62322; color: #f5a623; border: 1px solid #f5a62388; }
    .score-low  { background: #dc354522; color: #ff6b6b; border: 1px solid #dc354588; }
    .method-tag {
        font-size: 0.75em;
        color: #8b949e;
        background: #21262d;
        padding: 2px 8px;
        border-radius: 10px;
        display: inline-block;
        margin-top: 4px;
    }
    .evidence-snippet {
        font-size: 0.82em;
        color: #c9d1d9;
        background: #161b22;
        border-left: 3px solid #0d6efd;
        padding: 6px 10px;
        margin: 4px 0;
        border-radius: 4px;
        font-family: monospace;
    }
    .weight-bar-bg {
        background: #21262d;
        border-radius: 6px;
        height: 10px;
        width: 100%;
    }
    .weight-bar-fill {
        border-radius: 6px;
        height: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.image(
        "https://img.icons8.com/fluency/96/resume.png",
        width=72,
    )
    st.title("ResumeIQ")
    st.markdown(
        "**AI-powered resume analyzer**  \n"
        "Upload a PDF resume and compare it against a job description."
    )
    st.divider()
    st.markdown(
        "**How it works**\n"
        "1. Upload your PDF resume\n"
        "2. Paste a job description\n"
        "3. View match scores and skill gaps\n"
    )
    st.divider()
    st.caption(
        "⚠️ Similarity scores are **not** hiring probabilities.  \n"
        "Skill detection relies on a predefined dictionary.  \n"
        "No resume data is stored or shared."
    )

# ---------------------------------------------------------------------------
# Session state helpers
# ---------------------------------------------------------------------------
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
if "resume_skills" not in st.session_state:
    st.session_state.resume_skills = []

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    "<h1 style='text-align:center; color:#58a6ff;'>📄 ResumeIQ</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center; color:#8b949e;'>"
    "AI-powered resume analysis and job matching</p>",
    unsafe_allow_html=True,
)
st.divider()

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📋 Resume Analysis",
    "🎯 Job Matching",
    "📊 Skill Gap",
    "🔬 Section Analysis",
])

# ===========================================================================
# TAB 1 — RESUME ANALYSIS
# ===========================================================================
with tab1:
    st.subheader("Upload Your Resume")
    uploaded_file = st.file_uploader(
        "Choose a PDF file (max 10 MB)",
        type=["pdf"],
        help="Only PDF files are supported. Scanned-image PDFs may not extract text.",
    )

    if uploaded_file is not None:
        # Save the uploaded file to a temporary location for extraction.
        import tempfile, os

        with tempfile.NamedTemporaryFile(
            suffix=".pdf", delete=False
        ) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name

        try:
            # Validate
            ok, reason = validate_pdf_upload(tmp_path)
            if not ok:
                st.error(f"❌ {reason}")
            else:
                with st.spinner("Extracting text from PDF…"):
                    raw_text = extract_text_from_pdf(tmp_path)

                if raw_text is None:
                    st.error(
                        "❌ Could not extract text from this PDF. "
                        "It may be password-protected or corrupted."
                    )
                elif is_likely_scanned(raw_text):
                    st.warning(
                        "⚠️ Very little text was extracted. "
                        "This PDF may be a scanned image. "
                        "OCR is not currently implemented — "
                        "please use a text-based PDF."
                    )
                    st.session_state.resume_text = raw_text
                else:
                    cleaned = clean_resume_text(raw_text)
                    st.session_state.resume_text = cleaned
                    skills = extract_skills(cleaned)
                    st.session_state.resume_skills = skills

                    st.success(
                        f"✅ Resume extracted successfully — "
                        f"{len(cleaned):,} characters, "
                        f"{len(skills)} skills detected."
                    )
        finally:
            os.unlink(tmp_path)

    # Show results if text is available
    if st.session_state.resume_text:
        col_left, col_right = st.columns([3, 2])

        with col_left:
            st.markdown("### Extracted Text Preview")
            st.markdown(
                "<div class='iq-card'>",
                unsafe_allow_html=True,
            )
            preview = st.session_state.resume_text[:1500]
            if len(st.session_state.resume_text) > 1500:
                preview += "\n\n*[Remaining text truncated for privacy preview…]*"
            st.text_area(
                "Resume text (first 1500 characters)",
                value=preview,
                height=350,
                disabled=True,
                label_visibility="collapsed",
            )
            st.markdown("</div>", unsafe_allow_html=True)

        with col_right:
            st.markdown("### Detected Skills")
            skills = st.session_state.resume_skills
            if skills:
                pills_html = "".join(
                    f"<span class='skill-pill'>{s}</span>" for s in skills
                )
                st.markdown(pills_html, unsafe_allow_html=True)
                st.caption(
                    f"**{len(skills)} skills detected** using dictionary matching.  \n"
                    "This is not a trained model — only known terms are recognised."
                )
            else:
                st.info("No skills from the predefined list were detected.")

            # ML match prediction (optional — requires trained model)
            st.markdown("### ML Match Prediction")
            st.caption(
                "Predicts overall quality vs. a job description using "
                "the trained TF-IDF + ML classifier (if available)."
            )
            try:
                from predict_match import load_model
                load_model()
                st.success("✅ Trained ML model is loaded and ready.")
            except FileNotFoundError:
                st.warning(
                    "⚠️ No trained model found.  \n"
                    "Run `python src/generate_training_data.py` then "
                    "`python src/train_model.py` to create it.  \n"
                    "TF-IDF cosine similarity matching is still available."
                )
            except Exception as exc:
                st.error(f"Error loading model: {exc}")

# ===========================================================================
# TAB 2 — JOB MATCHING
# ===========================================================================
with tab2:
    st.subheader("Compare Resume with a Job Description")

    if not st.session_state.resume_text:
        st.info("👆 Please upload a PDF resume in the **Resume Analysis** tab first.")
    else:
        job_description = st.text_area(
            "Paste the job description here",
            height=220,
            placeholder=(
                "Example: We are looking for a Python developer with experience "
                "in machine learning, scikit-learn, SQL, and cloud services (AWS)…"
            ),
        )

        run_match = st.button("▶ Analyse Match", type="primary", use_container_width=True)

        if run_match:
            if not job_description.strip():
                st.error("❌ Please paste a job description before analysing.")
            else:
                with st.spinner("Computing match scores…"):
                    try:
                        result = match_resume_to_job(
                            st.session_state.resume_text,
                            job_description,
                        )
                    except ValueError as err:
                        st.error(f"❌ {err}")
                        result = None

                if result:
                    sim = result["similarity_percentage"]
                    cov = result["skill_coverage_percentage"]
                    matched = result["matched_skills"]
                    missing = result["missing_skills"]
                    job_skills = result["job_skills_detected"]

                    st.divider()
                    st.markdown("### Match Results")

                    col_sim, col_cov, col_skills = st.columns(3)
                    with col_sim:
                        st.metric(
                            "TF-IDF Text Similarity",
                            f"{sim:.1f}%",
                            help=(
                                "Cosine similarity between resume and job "
                                "description TF-IDF vectors. Not a hiring probability."
                            ),
                        )
                    with col_cov:
                        st.metric(
                            "Skill Coverage",
                            f"{cov:.1f}%",
                            help=(
                                "Fraction of skills detected in the job description "
                                "that also appear in the resume."
                            ),
                        )
                    with col_skills:
                        st.metric(
                            "Matched Skills",
                            f"{len(matched)} / {len(job_skills)}",
                        )

                    # Optional ML prediction
                    try:
                        from predict_match import predict_match as ml_predict
                        label = ml_predict(
                            st.session_state.resume_text,
                            job_description,
                        )
                        label_colour = {
                            "Strong Match": "🟢",
                            "Partial Match": "🟡",
                            "Poor Match":   "🔴",
                        }.get(label, "⚪")
                        st.info(
                            f"**ML Classifier Prediction:** {label_colour} {label}  \n"
                            "*(Experimental — trained on synthetic data only.)*"
                        )
                    except FileNotFoundError:
                        st.caption("ML prediction unavailable — model not trained yet.")
                    except Exception as exc:
                        st.caption(f"ML prediction error: {exc}")

                    # Skills breakdown
                    st.divider()
                    col_m, col_x = st.columns(2)
                    with col_m:
                        st.markdown("#### ✅ Matched Skills")
                        if matched:
                            html = "".join(
                                f"<span class='skill-pill skill-pill-matched'>{s}</span>"
                                for s in matched
                            )
                            st.markdown(html, unsafe_allow_html=True)
                        else:
                            st.write("No matching skills detected.")

                    with col_x:
                        st.markdown("#### ❌ Missing Skills")
                        if missing:
                            html = "".join(
                                f"<span class='skill-pill skill-pill-missing'>{s}</span>"
                                for s in missing
                            )
                            st.markdown(html, unsafe_allow_html=True)
                        else:
                            st.success("No skill gaps detected! 🎉")

                    st.caption(
                        "**Note:** Similarity scores are lexical measures, not "
                        "hiring probabilities. Skill detection only covers terms "
                        "in the predefined taxonomy."
                    )

# ===========================================================================
# TAB 3 — SKILL GAP
# ===========================================================================
with tab3:
    st.subheader("Skill Gap Analysis")

    if not st.session_state.resume_skills:
        st.info("👆 Upload a resume in the **Resume Analysis** tab to see your skill profile.")
    else:
        resume_skills = set(st.session_state.resume_skills)

        jd_for_gap = st.text_area(
            "Paste a job description to compare against",
            height=180,
            key="gap_jd",
            placeholder=(
                "Skills: Python, TensorFlow, Docker, Kubernetes, SQL, "
                "REST API, Git…"
            ),
        )

        if st.button("📊 Generate Skill Gap Report", use_container_width=True):
            if not jd_for_gap.strip():
                st.error("Please paste a job description.")
            else:
                job_skills = set(extract_skills(jd_for_gap))
                if not job_skills:
                    st.warning(
                        "No skills from the predefined list were detected in "
                        "the job description. Try including explicit skill names."
                    )
                else:
                    matched = resume_skills & job_skills
                    missing = job_skills - resume_skills
                    extra   = resume_skills - job_skills

                    coverage = len(matched) / len(job_skills) * 100

                    st.divider()
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Job Skills Required", len(job_skills))
                    col2.metric("Your Matched Skills", len(matched))
                    col3.metric("Missing Skills", len(missing))
                    col4.metric("Skill Coverage", f"{coverage:.1f}%")

                    st.caption(
                        f"**Coverage formula:** matched ÷ job_skills × 100 "
                        f"= {len(matched)} ÷ {len(job_skills)} × 100 = {coverage:.1f}%  \n"
                        "This measures dictionary-detected skill overlap, "
                        "not semantic similarity."
                    )

                    st.divider()
                    c1, c2, c3 = st.columns(3)

                    with c1:
                        st.markdown("#### ✅ Matched Skills")
                        for s in sorted(matched):
                            st.markdown(f"- {s}")

                    with c2:
                        st.markdown("#### ❌ Missing Skills")
                        if missing:
                            for s in sorted(missing):
                                st.markdown(f"- {s}")
                        else:
                            st.success("All detected job skills are in your resume!")

                    with c3:
                        st.markdown("#### ➕ Your Extra Skills")
                        st.caption("Skills in your resume not listed in the JD.")
                        for s in sorted(extra):
                            st.markdown(f"- {s}")

                    # Bar chart of coverage
                    import pandas as pd
                    chart_data = pd.DataFrame({
                        "Category": ["Matched", "Missing"],
                        "Count":    [len(matched), len(missing)],
                    })
                    st.bar_chart(
                        chart_data.set_index("Category"),
                        color=["#4caf50"],
                        use_container_width=True,
                    )

# ===========================================================================
# TAB 4 — SECTION ANALYSIS
# ===========================================================================

# Section display names and icons.
_SECTION_DISPLAY = {
    SKILLS: ("Technical Skills", "🛠️"),
    EXPERIENCE: ("Internship & Experience", "💼"),
    PROJECTS: ("Projects", "🚀"),
    CERTIFICATIONS: ("Certifications", "📜"),
    EDUCATION: ("Education & Coursework", "🎓"),
    ACHIEVEMENTS: ("Achievements", "🏆"),
}


def _score_class(score):
    if score >= 60:
        return "score-high"
    elif score >= 30:
        return "score-med"
    return "score-low"


with tab4:
    st.subheader("Per-Section Resume Analysis")

    if not st.session_state.resume_text:
        st.info("👆 Upload a PDF resume in the **Resume Analysis** tab first.")
    else:
        jd_section = st.text_area(
            "Paste the job description here",
            height=200,
            key="section_jd",
            placeholder=(
                "Example: We are looking for a Python developer with "
                "experience in SQL, Docker, REST APIs, and cloud services…"
            ),
        )

        run_section = st.button(
            "🔬 Run Section Analysis",
            type="primary",
            use_container_width=True,
        )

        if run_section:
            if not jd_section.strip():
                st.error("❌ Please paste a job description.")
            else:
                with st.spinner("Analysing resume sections…"):
                    result = compute_composite_score(
                        st.session_state.resume_text,
                        jd_section,
                    )

                overall = result["overall_score"]
                section_scores = result["section_scores"]
                present = result["present_sections"]
                missing = result["missing_sections"]
                eff_weights = result["effective_weights"]
                formula = result["formula"]
                weight_policy = result["weight_policy"]
                jd_analysis = result["jd_analysis"]

                # --- Overall Score ---
                st.divider()
                col_score, col_formula = st.columns([1, 2])
                with col_score:
                    cls = _score_class(overall)
                    st.markdown(
                        f"<div class='iq-card' style='text-align:center;'>"
                        f"<p style='color:#8b949e;margin:0'>Overall Match</p>"
                        f"<div class='section-score-badge {cls}' "
                        f"style='font-size:3rem'>{overall:.1f}%</div>"
                        f"</div>",
                        unsafe_allow_html=True,
                    )

                with col_formula:
                    st.markdown("**Score Formula**")
                    st.code(formula, language="text")
                    st.caption(f"**Weight Policy:** {weight_policy}")

                # --- Required vs Preferred Skills from JD ---
                req_skills = jd_analysis.get("required_skills", [])
                pref_skills = jd_analysis.get("preferred_skills", [])
                if req_skills or pref_skills:
                    st.divider()
                    c_req, c_pref = st.columns(2)
                    with c_req:
                        st.markdown("#### 🔴 Required Skills (from JD)")
                        if req_skills:
                            html = "".join(
                                f"<span class='skill-pill'>{s}</span>"
                                for s in req_skills
                            )
                            st.markdown(html, unsafe_allow_html=True)
                        else:
                            st.caption("None detected.")
                    with c_pref:
                        st.markdown("#### 🟡 Preferred Skills (from JD)")
                        if pref_skills:
                            html = "".join(
                                f"<span class='skill-pill'>{s}</span>"
                                for s in pref_skills
                            )
                            st.markdown(html, unsafe_allow_html=True)
                        else:
                            st.caption("None detected.")

                # --- Per-Section Breakdown ---
                st.divider()
                st.markdown("### Section-by-Section Breakdown")

                # Show effective weight distribution.
                if eff_weights:
                    cols = st.columns(len(eff_weights))
                    for i, (sec, weight) in enumerate(eff_weights.items()):
                        name, icon = _SECTION_DISPLAY.get(
                            sec, (sec.title(), "📌")
                        )
                        with cols[i]:
                            sec_score = section_scores.get(sec, {}).get(
                                "score", 0
                            )
                            cls = _score_class(sec_score)
                            st.markdown(
                                f"<div class='iq-card' style='text-align:center;padding:0.8rem'>"
                                f"<div>{icon}</div>"
                                f"<div style='font-size:0.85rem;color:#8b949e'>{name}</div>"
                                f"<div class='section-score-badge {cls}'>{sec_score:.0f}</div>"
                                f"<div style='font-size:0.75rem;color:#8b949e'>Weight: {weight:.0%}</div>"
                                f"</div>",
                                unsafe_allow_html=True,
                            )

                # Detailed cards for each section.
                for sec_name in [
                    SKILLS, EXPERIENCE, PROJECTS,
                    CERTIFICATIONS, EDUCATION, ACHIEVEMENTS,
                ]:
                    if sec_name not in section_scores:
                        continue

                    sec = section_scores[sec_name]
                    name, icon = _SECTION_DISPLAY.get(
                        sec_name, (sec_name.title(), "📌")
                    )
                    score = sec["score"]
                    method = sec["method"]
                    matched = sec.get("matched", [])
                    miss = sec.get("missing", [])
                    details = sec.get("details", {})

                    cls = _score_class(score)

                    with st.expander(
                        f"{icon} {name} — {score:.0f}/100", expanded=False
                    ):
                        st.markdown(
                            f"<span class='method-tag'>Method: {method}</span>",
                            unsafe_allow_html=True,
                        )

                        col_m, col_x = st.columns(2)
                        with col_m:
                            st.markdown("**✅ Matched**")
                            if matched:
                                html = "".join(
                                    f"<span class='skill-pill skill-pill-matched'>{s}</span>"
                                    for s in matched
                                )
                                st.markdown(html, unsafe_allow_html=True)
                            else:
                                st.caption("No matches.")

                        with col_x:
                            st.markdown("**❌ Missing**")
                            if miss:
                                html = "".join(
                                    f"<span class='skill-pill skill-pill-missing'>{s}</span>"
                                    for s in miss
                                )
                                st.markdown(html, unsafe_allow_html=True)
                            else:
                                st.caption("No gaps detected.")

                        # Evidence snippets.
                        evidence = details.get("evidence", [])
                        if evidence:
                            st.markdown("**📎 Evidence**")
                            for snip in evidence[:5]:
                                st.markdown(
                                    f"<div class='evidence-snippet'>{snip}</div>",
                                    unsafe_allow_html=True,
                                )

                        # Section-specific details.
                        if sec_name == SKILLS:
                            mr = details.get("matched_required", [])
                            mp = details.get("matched_preferred", [])
                            if mr:
                                st.caption(
                                    f"Required matched: {', '.join(mr)}"
                                )
                            if mp:
                                st.caption(
                                    f"Preferred matched: {', '.join(mp)}"
                                )

                        elif sec_name == PROJECTS:
                            sim = details.get("similarity", 0)
                            to = details.get("tech_overlap", 0)
                            st.caption(
                                f"TF-IDF similarity: {sim:.1f}%  |  "
                                f"Tech overlap: {to:.1f}%"
                            )

                        elif sec_name == EXPERIENCE:
                            sim = details.get("similarity", 0)
                            so = details.get("skill_overlap", 0)
                            st.caption(
                                f"TF-IDF similarity: {sim:.1f}%  |  "
                                f"Skill overlap: {so:.1f}%"
                            )

                        elif sec_name == EDUCATION:
                            dr = details.get("degree_relevance", 0)
                            co = details.get("coursework_overlap", 0)
                            st.caption(
                                f"Degree relevance: {dr:.1f}%  |  "
                                f"Coursework overlap: {co:.1f}%"
                            )

                # --- Missing Sections ---
                if missing:
                    st.divider()
                    st.markdown("### ⚠️ Missing Sections")
                    st.caption(
                        "These sections were not detected in the resume. "
                        "Their weights have been redistributed proportionally."
                    )
                    for m in missing:
                        name, icon = _SECTION_DISPLAY.get(
                            m, (m.title(), "📌")
                        )
                        base_w = DEFAULT_WEIGHTS.get(m, 0)
                        st.markdown(
                            f"- {icon} **{name}** "
                            f"(base weight: {base_w:.0%})"
                        )

                st.divider()
                st.caption(
                    "**Disclaimer:** Scores are heuristic estimates using "
                    "TF-IDF cosine similarity and dictionary matching. "
                    "They are not hiring probabilities. "
                    "Certification scores do not imply practical competence. "
                    "No resume data is stored or shared."
                )
