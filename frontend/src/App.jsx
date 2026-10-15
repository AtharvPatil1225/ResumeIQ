import { useEffect, useRef, useState } from "react";

const API = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
const MAX_SIZE = 10 * 1024 * 1024;

function SkillList({ title, items, color }) {
  return <section><h3 className="mb-3 text-sm font-semibold text-slate-700">{title}</h3>{items?.length ? <ul className="flex flex-wrap gap-2">{items.map((item) => <li key={item} className={"rounded-full px-3 py-1.5 text-xs font-medium " + color}>{item}</li>)}</ul> : <p className="text-sm text-slate-400">No skills to show.</p>}</section>;
}

function App() {
  const inputRef = useRef(null);
  const [file, setFile] = useState(null);
  const [job, setJob] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [api, setApi] = useState("checking");

  useEffect(() => {
    let active = true;
    fetch(API + "/api/health")
      .then((res) => { if (!res.ok) throw new Error(); return res.json(); })
      .then((data) => { if (active) setApi(data.model_loaded ? "ready" : "missing"); })
      .catch(() => { if (active) setApi("offline"); });
    return () => { active = false; };
  }, []);

  function chooseFile(next) {
    setError("");
    setResult(null);
    if (!next) { setFile(null); return; }
    if (!next.name.toLowerCase().endsWith(".pdf")) { setFile(null); setError("Choose a PDF file."); return; }
    if (next.size > MAX_SIZE) { setFile(null); setError("The PDF must be 10 MB or smaller."); return; }
    setFile(next);
  }

  async function submit(event) {
    event.preventDefault();
    setError("");
    setResult(null);
    if (!file) { setError("Upload a PDF resume to continue."); return; }
    if (!job.trim()) { setError("Add the job description to continue."); return; }
    const body = new FormData();
    body.append("resume", file);
    body.append("job_description", job.trim());
    setBusy(true);
    try {
      const response = await fetch(API + "/api/analyze", { method: "POST", body });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.detail || "Analysis failed (HTTP " + response.status + ").");
      setResult(data);
    } catch (err) {
      setError(err.message || "Could not reach the API. Check that the backend is running.");
    } finally {
      setBusy(false);
    }
  }

  const statuses = {
    checking: ["Connecting to API", "bg-amber-50 text-amber-700", "bg-amber-500"],
    ready: ["API and model ready", "bg-emerald-50 text-emerald-700", "bg-emerald-500"],
    missing: ["API ready  model missing", "bg-rose-50 text-rose-700", "bg-rose-500"],
    offline: ["API offline", "bg-rose-50 text-rose-700", "bg-rose-500"],
  };
  const status = statuses[api];

  return <div className="min-h-screen bg-[#f7f8fc]">
    <div className="pointer-events-none fixed inset-0 overflow-hidden" aria-hidden="true"><div className="absolute -right-32 -top-40 h-[28rem] w-[28rem] rounded-full bg-violet-100/70 blur-3xl" /><div className="absolute -left-36 top-[35rem] h-80 w-80 rounded-full bg-sky-100/60 blur-3xl" /></div>
    <header className="relative mx-auto flex max-w-7xl items-center justify-between px-5 py-5 sm:px-8">
      <a href="#" className="flex items-center gap-3 text-ink no-underline"><span className="grid h-10 w-10 place-items-center rounded-xl bg-violet-600 text-lg font-bold text-white shadow-lg shadow-violet-600/20">R</span><span className="text-lg font-bold tracking-tight">Resume<span className="text-violet-600">IQ</span></span></a>
      <div className={"flex items-center gap-2 rounded-full px-3 py-2 text-xs font-medium " + status[1]}><span className={"h-2 w-2 rounded-full " + status[2]} />{status[0]}</div>
    </header>
    <main className="relative mx-auto max-w-7xl px-5 pb-16 pt-8 sm:px-8 sm:pt-14">
      <section className="mx-auto mb-10 max-w-3xl text-center">
        <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-violet-100 bg-white/80 px-3 py-1.5 text-xs font-semibold text-violet-700 shadow-sm"><span aria-hidden="true">*</span> AI-assisted resume analysis</div>
        <h1 className="text-4xl font-bold tracking-tight text-ink sm:text-6xl">Find your next <span className="bg-gradient-to-r from-violet-600 to-indigo-500 bg-clip-text text-transparent">great fit.</span></h1>
        <p className="mx-auto mt-5 max-w-2xl text-base leading-7 text-slate-600 sm:text-lg">Compare a resume with a job description and see matching skills and potential gaps.</p>
      </section>
      <div className="mx-auto grid max-w-6xl gap-6 lg:grid-cols-[1.05fr_0.95fr]">
        <section className="rounded-3xl border border-white bg-white p-5 shadow-card sm:p-8">
          <p className="text-xs font-bold uppercase tracking-[0.16em] text-violet-600">Start an analysis</p><h2 className="mt-2 text-2xl font-bold tracking-tight text-ink">Add your resume and role</h2><p className="mb-7 mt-2 text-sm leading-6 text-slate-500">The API processes your PDF in memory for this request.</p>
          <form onSubmit={submit} className="space-y-6">
            <div><label htmlFor="resume" className="mb-2 block text-sm font-semibold text-slate-700">Resume PDF</label><input ref={inputRef} id="resume" type="file" accept="application/pdf,.pdf" className="sr-only" onChange={(e) => chooseFile(e.target.files?.[0])} />
              <button type="button" onClick={() => inputRef.current?.click()} onDragOver={(e) => e.preventDefault()} onDrop={(e) => { e.preventDefault(); chooseFile(e.dataTransfer.files?.[0]); }} className="group flex min-h-36 w-full flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-200 bg-slate-50/70 px-4 py-6 text-center transition hover:border-violet-300 hover:bg-violet-50/50 focus:outline-none focus:ring-4 focus:ring-violet-100">
                <span className="mb-3 grid h-11 w-11 place-items-center rounded-xl bg-violet-100 text-xl text-violet-600 group-hover:bg-violet-600 group-hover:text-white">PDF</span><span className="text-sm font-semibold text-slate-700">{file ? file.name : "Choose a PDF to upload"}</span><span className="mt-1 text-xs text-slate-400">{file ? Math.ceil(file.size / 1024) + " KB  PDF" : "Text-based PDF  up to 10 MB"}</span>
              </button>
              {file && <button type="button" onClick={() => { setFile(null); if (inputRef.current) inputRef.current.value = ""; }} className="mt-2 text-xs font-medium text-slate-500 underline hover:text-violet-700">Remove file</button>}
            </div>
            <div><div className="mb-2 flex items-center justify-between gap-3"><label htmlFor="job" className="text-sm font-semibold text-slate-700">Job description</label><span className="text-xs text-slate-400">{job.length} characters</span></div><textarea id="job" value={job} onChange={(e) => setJob(e.target.value)} rows={7} maxLength={12000} placeholder="Paste the role, responsibilities, and required skills..." className="w-full resize-y rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm leading-6 text-slate-700 outline-none placeholder:text-slate-400 focus:border-violet-400 focus:ring-4 focus:ring-violet-100" /></div>
            {error && <p role="alert" className="rounded-xl border border-rose-100 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</p>}
            <button type="submit" disabled={busy} className="w-full rounded-xl bg-violet-600 px-5 py-3.5 text-sm font-semibold text-white shadow-lg shadow-violet-600/20 transition hover:bg-violet-700 focus:outline-none focus:ring-4 focus:ring-violet-200 disabled:cursor-wait disabled:opacity-60">{busy ? "Analyzing resume..." : "Analyze match"} {!busy && <span aria-hidden="true">*</span>}</button>
          </form>
        </section>
        <section className="rounded-3xl border border-white bg-white p-5 shadow-card sm:p-8" aria-live="polite">
          {result ? <div>
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-emerald-600">Analysis complete</p><h2 className="mt-2 text-2xl font-bold tracking-tight text-ink">Your match overview</h2>
            <div className="mt-6 rounded-2xl bg-gradient-to-br from-violet-600 to-indigo-600 p-5 text-white sm:p-6"><p className="text-sm font-medium text-violet-100">Predicted match category</p><p className="mt-2 text-3xl font-bold">{result.predicted_category}</p><p className="mt-2 text-xs leading-5 text-violet-100">Experimental category from the ResumeIQ classifier</p></div>
            <div className="mt-5 grid grid-cols-2 gap-3"><div className="rounded-2xl border border-slate-100 bg-slate-50 p-4"><p className="text-xs text-slate-500">Text similarity</p><p className="mt-2 text-2xl font-bold text-ink">{result.similarity_percentage}%</p></div><div className="rounded-2xl border border-slate-100 bg-slate-50 p-4"><p className="text-xs text-slate-500">Detected skill coverage</p><p className="mt-2 text-2xl font-bold text-ink">{result.skill_coverage_percentage}%</p></div></div>
            <div className="mt-6 space-y-5"><SkillList title={"Matched skills  " + (result.matched_skills?.length || 0)} items={result.matched_skills} color="bg-emerald-50 text-emerald-700" /><SkillList title={"Potential skill gaps  " + (result.missing_skills?.length || 0)} items={result.missing_skills} color="bg-amber-50 text-amber-800" />{!result.job_skills_detected?.length && <p className="text-xs text-slate-500">No skills from the current predefined dictionary were detected.</p>}</div>
            <p className="mt-6 rounded-xl bg-slate-50 px-4 py-3 text-xs leading-5 text-slate-500">{result.notice || "Experimental results are not a hiring decision. Similarity is not a probability."}</p>
          </div> : <div className="flex min-h-[32rem] flex-col items-center justify-center px-4 py-12 text-center"><div className="mb-6 grid h-24 w-24 place-items-center rounded-3xl bg-violet-50 text-4xl text-violet-600">PDF</div><p className="text-xs font-bold uppercase tracking-[0.16em] text-violet-600">Your results will appear here</p><h2 className="mt-3 max-w-sm text-2xl font-bold tracking-tight text-ink">A clearer picture of role alignment</h2><p className="mt-3 max-w-sm text-sm leading-6 text-slate-500">Add a resume and job description to see the predicted category, shared skills, and possible gaps.</p><div className="mt-8 flex flex-wrap justify-center gap-2">{["Match category", "Skill overlap", "Potential gaps"].map((item) => <span key={item} className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-500">{item}</span>)}</div></div>}
        </section>
      </div>
      <footer className="mx-auto mt-8 max-w-6xl text-center text-xs leading-5 text-slate-400">ResumeIQ is experimental and trained on synthetic examples. Its output is not a hiring recommendation or a probability of success.</footer>
    </main>
  </div>;
}

export default App;
