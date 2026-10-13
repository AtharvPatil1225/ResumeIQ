
from pathlib import Path
from pdf_extractor import extract_text_from_pdf

# Select one PDF from the 2026 folder
resume_folder = Path(r"E:\ResumeIQ\data\raw_resumes\2026")
pdf_files = list(resume_folder.glob("*.pdf"))

if not pdf_files:
    print("No PDF files found.")
else:
    pdf_path = pdf_files[0]
    extracted_text = extract_text_from_pdf(pdf_path)

    print("ResumeIQ - PDF Extractor Test")
    print("PDF found: Yes")

    if extracted_text is None:
        print("Extraction status: Failed")
    elif extracted_text:
        print("Extraction status: Success")
        print("Extracted character count:", len(extracted_text))
    else:
        print("Extraction status: No text found")
