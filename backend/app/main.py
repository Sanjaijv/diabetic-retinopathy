import os
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.models.interface import InferenceError, ScreeningModel, load_model
from app.schemas.analysis import AnalysisResult, HealthResponse, ModelInfo
from app.services.analysis import analyze
from app.utils.images import ImageValidationError, validate_image


def create_app(model: ScreeningModel | None = None) -> FastAPI:
    app = FastAPI(
        title="Diabetic Retinopathy Screening API",
        description="Research and educational screening only; not a diagnostic system.",
        version="1.0.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,"
            "http://localhost:5174,http://127.0.0.1:5174",
        ).split(","),
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )
    try:
        default_model_path = Path(__file__).resolve().parents[1] / "weights" / "DiabeticRetinopathy.pth"
        loaded_model = model or load_model(os.getenv("MODEL_PATH") or str(default_model_path))
        model_error = None
    except InferenceError as exc:
        loaded_model = load_model(None)
        model_error = str(exc)
    app.state.model = loaded_model
    app.state.model_error = model_error

    @app.get("/api/health", response_model=HealthResponse)
    async def health() -> HealthResponse:
        return HealthResponse(status="ok", model_available=app.state.model.available)

    @app.get("/api/model-info", response_model=ModelInfo)
    async def model_info() -> ModelInfo:
        info = app.state.model.info()
        if app.state.model_error:
            info["limitations"].append(app.state.model_error)
        return ModelInfo(**info)

    @app.post("/api/analyze", response_model=AnalysisResult)
    async def analyze_image(file: UploadFile = File(...)) -> AnalysisResult:
        try:
            data = await file.read()
            validated = validate_image(data)
        except ImageValidationError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        try:
            return analyze(validated, app.state.model)
        except InferenceError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    @app.get("/api/results/{analysis_id}")
    async def result_not_available(analysis_id: str) -> None:
        raise HTTPException(
            status_code=404,
            detail="Results are not persisted; this analysis ID is no longer available.",
        )

    return app


app = create_app()
