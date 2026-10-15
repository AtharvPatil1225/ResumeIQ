
FROM python:3.13-slim

WORKDIR /app

# Install the libraries used by ResumeIQ's ML scripts.
RUN pip install --no-cache-dir \
    pandas \
    numpy \
    scikit-learn \
    joblib \
    pymupdf

# Copy the project source code into the image.
COPY src/ ./src/

# Copy the dataset-inspection notebook if needed later.
COPY 01_dataset_inspection.ipynb ./

# Run a basic ResumeIQ environment check by default.
CMD ["python", "src/test_setup.py"]
