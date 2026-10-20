from uuid import uuid4

from app.models.interface import InferenceError, ModelNotConfiguredError, ScreeningModel
from app.schemas.analysis import AnalysisResult, Finding, ImageQuality, Score
from app.utils.images import ValidatedImage


LIMITATIONS = [
    "This result is a screening output and is not a medical diagnosis.",
    "A model score is not necessarily a calibrated clinical probability.",
    "The result does not guarantee that an eye is healthy and does not replace professional care.",
]


def analyze(image: ValidatedImage, model: ScreeningModel) -> AnalysisResult:
    quality = ImageQuality(
        status=image.status, width=image.width, height=image.height, warnings=image.warnings
    )
    base = dict(
        analysis_id=str(uuid4()),
        image_quality=quality,
        model_available=model.available,
        model_name=model.name,
        model_version=model.version,
        limitations=LIMITATIONS,
        follow_up="Seek assessment by an ophthalmologist or qualified eye-care professional for concerns.",
    )
    if image.status == "warning":
        base["follow_up"] = (
            "The image has quality warnings. Consider a clearer image or professional assessment."
        )
    if not model.available:
        return AnalysisResult(
            **base,
            screening_class=None,
            explanation_available=False,
            explanation_message="Analysis is unavailable until reviewed model weights are configured.",
        )
    try:
        prediction = model.predict(image.image)
    except (ModelNotConfiguredError, InferenceError):
        raise

    grade = prediction.dr_grade
    screening = "normal" if grade == 0 else "abnormal"
    findings = [
        Finding(
            name="Diabetic retinopathy grade",
            status="detected" if grade is not None else "not_evaluated",
            explanation="The grading model assigned the displayed supported class.",
            significance="This may warrant clinical assessment; it is not a confirmed diagnosis.",
        )
    ]
    return AnalysisResult(
        **base,
        screening_class=screening,
        predicted_class=prediction.predicted_class,
        scores=[Score(label=label, value=float(value)) for label, value in prediction.scores],
        dr_grade=grade,
        findings=findings,
        explanation_available=False,
        explanation_message="No Grad-CAM or localization output is available for this model.",
    )
