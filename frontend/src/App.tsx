import { useEffect, useState } from "react";
import { AlertTriangle, CheckCircle2, FileImage, Info, ShieldCheck, Upload, X } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { analyzeImage, getModelInfo } from "./services/api";
import type { AnalysisResult, ModelInfo } from "./types/api";

const gradeNames = ["No diabetic retinopathy", "Mild", "Moderate", "Severe", "Proliferative"];

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [model, setModel] = useState<ModelInfo | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => { getModelInfo().then(setModel).catch((e: Error) => setError(e.message)); }, []);

  function selectFile(next: File | undefined) {
    if (!next) return;
    setError(null); setResult(null); setFile(next);
    setPreview(URL.createObjectURL(next));
  }
  function removeFile() {
    if (preview) URL.revokeObjectURL(preview);
    setFile(null); setPreview(null); setResult(null);
  }
  async function submit() {
    if (!file) return setError("Choose a retinal fundus image first.");
    setBusy(true); setError(null);
    try { setResult(await analyzeImage(file)); } catch (e) { setError((e as Error).message); }
    finally { setBusy(false); }
  }

  return <div className="app-shell">
    <header className="topbar"><div className="brand"><div className="brand-mark">R</div><div><strong>RetinaScreen</strong><span>Research screening workspace</span></div></div><nav><a href="#how">How it works</a><a href="#model">About the model</a><a href="#disclaimer">Disclaimer</a></nav></header>
    <main>
      <section className="hero"><div><p className="eyebrow">AI-ASSISTED SCREENING</p><h1>Understand a retinal image with care.</h1><p className="hero-copy">Upload a fundus photograph to screen for possible retinal abnormalities. Results are model outputs for research and education, never a diagnosis.</p></div><div className="hero-badge"><ShieldCheck size={22}/><span>Privacy-first<br/><small>Images are not stored</small></span></div></section>
      {error && <div className="alert error"><AlertTriangle size={18}/>{error}</div>}
      <section className="workspace">
        <div className="card upload-card"><div className="section-heading"><div><p className="eyebrow">01 / UPLOAD</p><h2>Choose a fundus image</h2></div><FileImage size={28} className="muted"/></div>
          {!preview ? <label className="dropzone"><Upload size={30}/><strong>Drop an image here</strong><span>or browse from your device</span><input type="file" accept=".jpg,.jpeg,.png,image/jpeg,image/png" onChange={e => selectFile(e.target.files?.[0])}/><small>JPEG or PNG · up to 10 MB · minimum 128 × 128 px</small></label> : <div className="preview-wrap"><img src={preview} alt="Selected retinal image preview"/><button className="icon-button" onClick={removeFile} aria-label="Remove selected image"><X size={18}/></button><div className="file-meta"><strong>{file?.name}</strong><span>{file?.size ? `${(file.size / 1024 / 1024).toFixed(2)} MB` : ""}</span></div></div>}
          <button className="primary-button" onClick={submit} disabled={!file || busy}>{busy ? "Analyzing…" : "Analyze image"}</button>
          <p className="microcopy"><Info size={14}/> The image is decoded and checked for format, dimensions, and basic quality before analysis.</p>
        </div>
        <div className="card model-card"><div className="section-heading"><div><p className="eyebrow">02 / MODEL STATUS</p><h2>Analysis readiness</h2></div><div className={`status-dot ${model?.model_available ? "ready" : ""}`}/></div>{model?.model_available ? <><p className="ready-text"><CheckCircle2 size={18}/> Reviewed model configured</p><dl><dt>Model</dt><dd>{model.name}</dd><dt>Architecture</dt><dd>{model.architecture}</dd><dt>Input</dt><dd>{model.input_dimensions.join(" × ")}</dd></dl></> : <div className="unavailable"><AlertTriangle size={22}/><strong>Analysis unavailable</strong><p>No reviewed model weights are configured. Set <code>MODEL_PATH</code> in the backend environment to enable real predictions.</p></div>}<p className="microcopy">No simulated scores or findings are shown when a model is unavailable.</p></div>
      </section>
      {result && <Results result={result}/>}
      <section id="how" className="info-grid"><div className="info-card"><span>01</span><h3>Validate</h3><p>We inspect decoded image content, dimensions, and conservative quality signals.</p></div><div className="info-card"><span>02</span><h3>Analyze</h3><p>Only a configured model’s documented classes and scores can appear in results.</p></div><div className="info-card"><span>03</span><h3>Review</h3><p>Possible abnormalities and ungradable images should be assessed by an eye-care professional.</p></div></section>
      <section id="disclaimer" className="disclaimer"><AlertTriangle size={22}/><div><strong>Medical disclaimer</strong><p>RetinaScreen is a research and educational screening tool. It is not clinically validated here, does not diagnose disease, and must not guide treatment decisions. Seek professional care for symptoms or concerns.</p></div></section>
    </main>
    <footer id="model">Model metadata is supplied by the backend deployment. Validate weights, calibration, licensing, and performance on a properly held-out dataset before any real-world use.</footer>
  </div>;
}

function Results({ result }: { result: AnalysisResult }) {
  const title = result.screening_class === "normal" ? "No apparent abnormality" : result.screening_class === "abnormal" ? "Possible retinal abnormality" : "Uncertain / ungradable";
  return <section className="results"><div className="section-heading"><div><p className="eyebrow">03 / RESULTS</p><h2>Screening summary</h2></div><span className={`result-pill ${result.screening_class ?? "unknown"}`}>{title}</span></div><div className="result-grid"><div><div className="summary-box"><span>Predicted class</span><strong>{result.predicted_class ?? "Not available"}</strong>{result.dr_grade !== null && <p>Grade {result.dr_grade}: {gradeNames[result.dr_grade]}</p>}<small>{result.follow_up}</small></div><div className="quality"><strong>Image quality: {result.image_quality.status}</strong>{result.image_quality.warnings.map(w => <span key={w}>• {w}</span>)}</div></div><div className="chart-card"><h3>Model scores</h3>{result.scores.length ? <ResponsiveContainer width="100%" height={240}><BarChart data={result.scores} layout="vertical" margin={{ left: 16, right: 16 }}><CartesianGrid strokeDasharray="3 3"/><XAxis type="number" domain={[0, 1]}/><YAxis type="category" dataKey="label" width={130} tick={{ fontSize: 11 }}/><Tooltip formatter={(v) => [Number(v).toFixed(3), "Score"]}/><Bar dataKey="value" fill="#0f8b8d" radius={[0, 5, 5, 0]}/></BarChart></ResponsiveContainer> : <div className="empty-state"><AlertTriangle size={20}/> Scores are unavailable until a model is configured.</div>}<small>Scores are model outputs, not necessarily calibrated clinical probabilities.</small></div></div><div className="findings"><h3>Possible visual findings</h3>{result.findings.length ? result.findings.map(f => <div className="finding" key={f.name}><div><strong>{f.name}</strong><span className={`finding-status ${f.status}`}>{f.status.replace("_", " ")}</span></div><p>{f.explanation}</p><small>{f.significance}</small></div>) : <p>Not evaluated by this model.</p>}<div className="explainability"><strong>Explanation visualization</strong><p>{result.explanation_message}</p></div></div><div className="limitations"><strong>Limitations</strong>{result.limitations.map(item => <span key={item}>• {item}</span>)}</div></section>;
}

export default App;
