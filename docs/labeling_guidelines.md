# ResumeIQ: Resume–Job Matching Labeling Guidelines

## Purpose
These guidelines define consistent labels for evaluating how well a resume
matches a job description. The labels are intended for project experimentation,
not as a definitive hiring decision.

## Label 0 — Poor Match
Use when the resume provides little evidence of relevant skills,
qualifications, projects, or experience required by the job.

## Label 1 — Partial Match
Use when the resume demonstrates some relevant skills or experience,
but important job requirements are missing or insufficiently supported.

## Label 2 — Strong Match
Use when the resume provides evidence for most essential job requirements,
with relevant skills supported by projects, education, or experience.

## Labeling Rules
1. Evaluate the resume against the specific job description.
2. Consider required skills and relevant supporting evidence.
3. Do not assign a strong match based only on unrelated keywords.
4. Missing information must not automatically be treated as proof that a
   candidate lacks a skill.
5. Apply the same criteria consistently to all examples.
6. Review ambiguous examples before assigning a final label.
7. These labels measure estimated job relevance, not hiring probability,
   candidate worth, or guaranteed job performance.

## Current Dataset Limitations
The initial training dataset contains only nine short synthetic examples.
It is suitable for testing the training pipeline, but not for establishing
reliable real-world model performance.

Before reporting model performance, create a larger, diverse dataset with
consistent labels and evaluate it on examples not used during training.
