AI-Based Diabetic Retinopathy Detection Application
Implementation Specification for Google Antigravity
Goal: Build a functional web application that accepts retinal fundus photographs, screens for possible diabetic retinopathy, classifies images as normal or abnormal when supported by the installed model, and explains supported findings in plain language.

Safety: This is a research/educational screening tool, not a medical diagnosis system. Do not claim clinical validation or medical-grade accuracy without evidence.

1. Instructions to the Antigravity Agent
Act as a senior full-stack developer, machine-learning engineer, and computer-vision specialist. Inspect the existing workspace first, then implement the application end to end.

Do not stop after creating a visual prototype. Implement the frontend, backend, image validation, model-inference integration, results dashboard, tests, and setup documentation. Run the application and tests where possible, fix errors, and report any blockers honestly.

Never fabricate model predictions, confidence scores, findings, training results, or clinical accuracy. If model weights are unavailable, implement a clearly marked model-integration interface and report that real predictions are not available until the weights are configured. Do not silently substitute mock results.
2. Product Requirements
The application must let a user:
1. Upload a retinal fundus image.
2. Preview or remove the selected image.
3. Validate file format, image dimensions, and basic image quality.
4. Analyze the image with a configured trained model.
5. View a Normal / No apparent abnormality or Abnormal / Possible retinal abnormality screening result, only when the installed model supports that classification.
6. View diabetic retinopathy severity grading if the installed model supports it.
7. Review possible visual findings that are actually supported by the model.
8. View prediction scores and an optional Grad-CAM explanation.
9. Read a plain-language explanation, limitations, and recommended professional follow-up.
10. Receive clear errors when the image is invalid, the model is unavailable, or inference fails.
The application must not treat every abnormal image as diabetic retinopathy. It must distinguish model outputs from additional inferences and must not claim to detect a specific lesion from a generic classifier alone.
3. Technology Stack
Frontend
- React
- Vite
- TypeScript
- Tailwind CSS
- Recharts for prediction charts
- Lucide icons
- Responsive and accessible components
Backend
- Python
- FastAPI
- Pydantic
- Uvicorn
- Pillow and OpenCV for image validation/preprocessing
- NumPy
- PyTorch or TensorFlow, chosen to match the selected model
Explainability
- Grad-CAM or a suitable equivalent, only if supported by the chosen model architecture.
- Label heatmaps as regions that influenced the model prediction, not proof that a lesion exists at the highlighted location.
Keep frontend, backend, preprocessing, model inference, schemas, and tests separated.
4. Suggested Project Structure
Create or adapt this structure:
diabetic-retinopathy-app/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── types/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   └── ...
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── utils/
│   │   └── main.py
│   ├── weights/
│   ├── tests/
│   └── requirements.txt
├── .env.example
├── .gitignore
└── README.md
Do not commit private patient images, secrets, or large model weights to source control.
5. Frontend Pages and UI
Create these sections:
1. Home / Upload
2. Results
3. How It Works
4. About the Model
5. Medical Disclaimer
Visual design
- Clean medical-AI dashboard
- White/light background with navy-blue and teal accents
- Clear typography, accessible contrast, subtle shadows, and rounded cards
- Responsive desktop, tablet, and mobile layouts
- Minimal animation and no distracting visual clutter
Upload screen
Include:
- Heading: AI-Powered Diabetic Retinopathy Detection
- Subtitle explaining that the tool screens retinal fundus photographs for possible abnormalities
- Drag-and-drop upload area
- Browse file button
- JPG/JPEG/PNG support
- Image preview and remove button
- File size and dimensions feedback
- Analyze button
- Loading, success, empty, and error states
- Disclaimer visible before analysis
Validate the actual file contents and decoded image, not only the filename or MIME type. Set a reasonable configurable upload-size limit. Reject corrupt or unsupported images. Flag likely blur, underexposure, overexposure, or poor retinal framing where a reliable quality check is available.

If the input is not recognizably a fundus image or is ungradable, do not report it as normal.
6. Model Integration
Use a real trained model with documented weights. Suitable starting points include a model trained on a properly licensed retinal fundus dataset such as APTOS 2019 Blindness Detection or EyePACS, subject to dataset terms and intended use.

Candidate architectures include EfficientNet, ResNet, or ConvNeXt. Choose the architecture based on available compatible pretrained/trained weights, not merely preference.
Model requirements
- Document architecture, model version, input dimensions, preprocessing, class mapping, training dataset, and known limitations.
- Configure model weights through an environment variable or documented path, for example MODEL_PATH.
- Load model weights once during backend startup.
- Support CPU inference; use an accelerator only when available and compatible.
- Match preprocessing to the model's training pipeline.
- Return real output scores from the model.
- Fail clearly if weights are missing, invalid, or incompatible.
- Do not download unknown weights or execute arbitrary model files without review.
- Do not expose local filesystem paths or stack traces to the public API.
If no suitable weights are available, implement a model interface and a clear model_available: false state. The UI must say that analysis is unavailable until a trained model is configured. It must not display simulated results as genuine analysis.
Model interface
Define a small, testable interface that separates API code from the underlying model, such as:
- load_model()
- predict(image)
- get_model_info()
- generate_explanation(image, prediction) when supported
Use typed response schemas and explicit errors for model-not-configured and inference-failed conditions.
7. Screening Classification
Normal / No Apparent Abnormality
Show this only when the installed model's documented output supports this category and the image is suitable for analysis.

Display:
- Screening result
- Relevant model score or probabilities
- A short explanation of what the model evaluated
- A reminder that the result does not guarantee a healthy eye
Abnormal / Possible Retinal Abnormality
Show this when the model supports an abnormal classification and the output meets its documented decision criteria.

Display:
- Screening result
- Predicted class or supported grade
- Relevant scores
- Supported findings and their explanations
- Recommended professional assessment
Use documented, validated decision thresholds where available. Do not invent a threshold or present a model score as a calibrated probability unless calibration has been established.
Uncertain / Ungradable
Support an explicit uncertain or ungradable state where possible. Use it when image quality is insufficient, model output is unsupported, or confidence/quality criteria do not permit a reliable result. Do not force every image into normal or abnormal.
8. Diabetic Retinopathy Grading
If and only if the installed model supports the five-level grading task, map its documented classes to:
- Grade 0: No diabetic retinopathy detected by the grading model
- Grade 1: Mild non-proliferative diabetic retinopathy
- Grade 2: Moderate non-proliferative diabetic retinopathy
- Grade 3: Severe non-proliferative diabetic retinopathy
- Grade 4: Proliferative diabetic retinopathy
Explain each grade in plain language. Do not display these grades when the configured model only supports binary classification or a different label set. A grade prediction is not a confirmed clinical diagnosis.
9. Possible Visual Findings
Create a Possible Visual Findings section. Report each finding only when a validated detector, segmenter, or appropriately trained classifier supports it. If the configured model does not evaluate a finding, display Not evaluated by this model, not Absent.

Potential findings to support in future or additional models:
Microaneurysms
Tiny red dots that can be associated with early diabetic retinopathy.
Retinal hemorrhages
Dark-red dots, blot-like lesions, or flame-shaped hemorrhages. They may occur in diabetic retinopathy and other conditions.
Hard exudates
Yellowish or white lipid deposits that may be associated with retinal vascular leakage.
Cotton-wool spots
Pale, fluffy-appearing lesions associated with retinal nerve fiber layer ischemia and other vascular conditions.
Optic disc pallor
An unusually pale optic disc may warrant assessment for optic nerve abnormalities. Color alone is not sufficient to diagnose optic neuropathy; normal variation and image illumination must be considered.
Abnormal blood vessels
Suspected neovascularization or other vascular changes, only if the model can identify them.
Macular abnormalities
Report only supported image findings. Do not claim to diagnose macular edema from a color fundus photograph alone.
Image quality issues
Blur, poor illumination, overexposure, underexposure, obstructed view, or poor centering.

For each finding returned, show:
- Finding name
- Status: detected, suspected, or not evaluated, based on the model's actual output
- Plain-language explanation
- Possible significance, using cautious language
- Highlighted region, only if supported by localization output
Do not infer a specific lesion from a general abnormality score. Do not call an optic disc pale merely because the overall image looks washed out.
10. Results Dashboard
Display:
Summary
- Original uploaded image
- Screening result: normal, abnormal, or uncertain/ungradable as supported
- DR grade, if available
- Model score/probabilities
- Image quality status
- Model name/version
Prediction chart
Use a bar chart for actual scores of the model's supported classes. Clearly label scores and explain that a score is not necessarily clinical certainty.
Explanation visualization
When supported, show:
- Original image
- Grad-CAM or equivalent heatmap
- Overlay
- Legend and short explanation
If explainability is unavailable, say so rather than displaying a fake heatmap.
Findings and follow-up
Show supported findings, what they may mean, and cautious follow-up guidance. Recommend assessment by an ophthalmologist or qualified eye-care professional for suspected abnormalities or ungradable images. Do not prescribe medication or treatment.

Allow the user to analyze another image. Avoid persistent storage of retinal images by default.
11. Backend API
Implement these endpoints:
GET /api/health
Return service status and whether a compatible model is loaded.
GET /api/model-info
Return documented model metadata:
- Name and version
- Architecture
- Supported tasks and classes
- Input dimensions
- Dataset information, if known
- Model availability
- Limitations
POST /api/analyze
Accept one uploaded image and return a validated structured result:
- Analysis ID
- Image-quality status and warnings
- Screening class, if supported
- Predicted class
- Actual output scores/probabilities
- DR grade, if supported
- Supported findings
- Explanation availability
- Limitations and follow-up message
GET /api/results/{analysis_id}
Optional endpoint for retrieving results if temporary or persistent result storage is implemented. If no result storage is enabled, return a clear not-found/feature-disabled response. Do not imply that results persist when they do not.

Use FastAPI request validation, safe image decoding, configurable size limits, and appropriate HTTP status codes. Avoid logging image bytes or sensitive image data. Use restrictive CORS settings configured for the local frontend.
12. Security and Privacy
- Treat all uploads as untrusted input.
- Validate decoded file contents and enforce file-size and pixel-count limits.
- Use safe temporary-file handling and delete temporary data after processing.
- Do not store images by default.
- Do not send images to external services unless explicitly configured and disclosed.
- Do not include patient-identifying information in logs.
- Keep secrets in environment variables, never in frontend source.
- Add .env.example with placeholders only.
- Do not promise regulatory compliance or security certification without verification.
13. Testing
Write automated tests for:
- Health endpoint
- Model info when weights are available and unavailable
- Empty upload
- Unsupported format
- Corrupt image
- Oversized upload
- Excessive image dimensions
- Valid image preprocessing
- Model-not-configured behavior
- Inference error handling
- Response schema validation
- Frontend loading, success, and error states
- Explainability unavailable state
- Image-quality warning behavior
Use synthetic or sample images only for software tests, and never treat them as proof of model accuracy. Evaluate model performance with a properly labeled held-out dataset, keeping training and test data separate.

When training/evaluating a model, report suitable metrics such as sensitivity, specificity, precision, recall, F1-score, ROC-AUC where appropriate, and quadratic weighted kappa for ordinal DR grading. Document class imbalance, dataset limitations, and intended use. Do not fabricate results.
14. Documentation
Create a detailed README.md that includes:
- Project overview and limitations
- Architecture and directory structure
- Prerequisites
- Windows setup instructions and Linux/macOS alternatives
- Backend virtual environment and dependency installation
- Frontend dependency installation
- Model-weight configuration
- Commands to run backend and frontend
- Tests
- API examples
- Supported image types
- Dataset licensing and model references
- Troubleshooting
- Privacy notes
- Medical disclaimer
Include .gitignore entries for virtual environments, build outputs, .env, uploaded images, caches, and model weights where appropriate.
15. Suggested Implementation Sequence
1. Inspect workspace and report existing files.
2. Create project structure and dependency files.
3. Implement backend schemas, health endpoint, and model-info endpoint.
4. Implement safe image decoding, validation, and quality warnings.
5. Implement real model loading and inference, with explicit missing-weight behavior.
6. Implement the analyze API and response validation.
7. Build the upload UI and API integration.
8. Build results dashboard and charts.
9. Add supported explainability output.
10. Add tests and run them.
11. Start the application and test the complete workflow.
12. Finish the README and report remaining blockers.
16. Acceptance Criteria
The project is complete only when:
- Frontend and backend can be started using documented commands.
- A valid image can be uploaded and previewed.
- Invalid and ungradable images are handled safely.
- The frontend calls the real backend API.
- A configured model produces real outputs with documented class mappings.
- Missing weights produce a clear unavailable state, not fake predictions.
- Results show only tasks and findings supported by the model.
- The UI explains uncertainty and medical limitations.
- Tests run, with results reported honestly.
- The README explains setup and model configuration.
Begin by inspecting the workspace. Implement the application in stages, run it, test it, and fix errors. At the end, list what works, what still needs trained weights or validation, and the exact commands to run the project.