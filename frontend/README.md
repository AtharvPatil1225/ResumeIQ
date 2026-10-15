# ResumeIQ frontend

React + Vite + Tailwind CSS interface for the ResumeIQ FastAPI service.

## Run

Install Node.js (which includes npm). Start the backend from the repository root:

```powershell
python -m uvicorn backend.main:app --reload --port 8000
```

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open http://127.0.0.1:5173. The frontend calls http://127.0.0.1:8000 by default. Set VITE_API_BASE_URL before starting Vite if the backend uses another address.

The form sends a PDF in the resume field and text in the job_description field to POST /api/analyze. The backend processes uploads in memory.
