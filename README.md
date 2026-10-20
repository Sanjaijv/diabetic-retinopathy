# RetinaScreen

RetinaScreen is a research and educational web application for screening retinal
fundus photographs. It validates image content, sends the image to a local
FastAPI service, and displays only outputs supported by the configured model.
It is **not a medical diagnosis system**, has no claim of clinical validation,
and must not be used to guide treatment.

## Current model status

The application includes the public
`Ahmed-Selem/Shifaa-Diabetic-Retinopathy-EfficientNetB0` checkpoint in
`backend/weights/DiabeticRetinopathy.pth`. It is loaded by default and uses
PyTorch EfficientNet-B0 inference. The model card describes an MIT license,
224×224 RGB input, ImageNet normalization, and five severity classes. Its
dataset is documented by the author as “Diabetic Retinopathy 224x224 2019
Data”; it is not represented as an APTOS model. The author's reported metrics
are not independently verified by this application.

To use another reviewed model, set `MODEL_PATH`. The application supports
`.pth` EfficientNet checkpoints matching this adapter and reviewed Keras
`.h5`/`.keras` models matching the Keras adapter. It never produces simulated
scores, findings, or heatmaps.

The included adapter currently supports a documented five-class output:

| Class | Meaning |
| --- | --- |
| 0 | No diabetic retinopathy |
| 1 | Mild non-proliferative diabetic retinopathy |
| 2 | Moderate non-proliferative diabetic retinopathy |
| 3 | Severe non-proliferative diabetic retinopathy |
| 4 | Proliferative diabetic retinopathy |

This mapping must only be used if it matches the reviewed model. A generic
abnormality classifier must not be presented as diabetic-retinopathy grading.
Grad-CAM is intentionally reported as unavailable because no model-specific
localization implementation is included.

## Structure

```text
backend/
  app/
    main.py                 FastAPI app and endpoints
    models/interface.py     Explicit model adapter and unavailable state
    schemas/analysis.py     Typed response models
    services/analysis.py    Screening orchestration
    utils/images.py         Safe decoding and quality checks
  tests/
frontend/
  src/App.tsx               Upload flow and results dashboard
  src/services/api.ts       Backend integration
```

## Prerequisites

- Python 3.10+
- Node.js 18+
- A reviewed model and its compatible inference framework, only if analysis is
  required.

### Backend: Windows

```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
copy ..\.env.example .env
# Edit .env and set MODEL_PATH only after reviewing the weights.
uvicorn app.main:app --reload --port 8001
```

### Backend: Linux/macOS

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp ../.env.example .env
uvicorn app.main:app --reload --port 8001
```

The requirements include PyTorch and torchvision for the bundled checkpoint.
Do not download or execute unknown model files.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend defaults to `http://localhost:8001`. Set `VITE_API_URL` if the
backend runs elsewhere. The backend allows the Vite development origins on
ports 5173 and 5174 by default. Build a production bundle with `npm run build`.

## API

- `GET /api/health` returns service status and `model_available`.
- `GET /api/model-info` returns the deployment's documented model metadata.
- `POST /api/analyze` accepts one multipart field named `file` and returns a
  validated structured result.
- `GET /api/results/{analysis_id}` returns `404`: results are not persisted.

Example:

```bash
curl -F "file=@fundus.jpg" http://localhost:8001/api/analyze
```

Uploads must be decoded JPEG or PNG files, at most 10 MB, with dimensions of
at least 128 × 128 and no more than 40 million pixels. Basic warnings may flag
blur, exposure, or unusually narrow framing. These checks cannot prove that an
image is a fundus photograph; ungradable images must not be treated as normal.

## Tests

```bash
cd backend
pytest
```

The tests cover health and model metadata, empty/corrupt/unsupported/small
uploads, and the explicit model-unavailable response. Synthetic images in
tests are software fixtures, not evidence of model accuracy.

## Privacy and safety

Images are processed in memory and are not persisted by default. Do not put
patient identifiers in filenames or logs. Do not send uploads to external
services unless that behavior is explicitly configured and disclosed. Keep
secrets in environment variables. Model weights, `.env` files, uploaded
images, caches, and build output are ignored by Git.

Seek an ophthalmologist or qualified eye-care professional for symptoms,
concerns, suspected abnormalities, or ungradable images. This tool does not
prescribe medication or treatment and does not promise regulatory compliance.
# diabetic-retinopathy
