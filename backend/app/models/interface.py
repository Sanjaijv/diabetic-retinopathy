from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image


@dataclass(frozen=True)
class Prediction:
    predicted_class: str
    scores: list[tuple[str, float]]
    dr_grade: int | None = None


class ModelNotConfiguredError(RuntimeError):
    """No reviewed model weights are configured."""


class InferenceError(RuntimeError):
    """The configured model could not produce a prediction."""


class ScreeningModel(ABC):
    name = "No model configured"
    version = "unavailable"
    architecture = "Not configured"
    classes: tuple[str, ...] = ()
    input_dimensions = (224, 224, 3)
    dataset: str | None = None

    @property
    @abstractmethod
    def available(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def predict(self, image: Image.Image) -> Prediction:
        raise NotImplementedError

    def info(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "architecture": self.architecture,
            "supported_tasks": ["five-level diabetic retinopathy grading"]
            if self.classes
            else [],
            "supported_classes": list(self.classes),
            "input_dimensions": list(self.input_dimensions),
            "dataset": self.dataset,
            "model_available": self.available,
            "limitations": [
                "This is a research and educational screening tool, not a diagnosis.",
                "Model performance and calibration must be established on a held-out dataset.",
            ],
        }


class UnavailableModel(ScreeningModel):
    @property
    def available(self) -> bool:
        return False

    def predict(self, image: Image.Image) -> Prediction:
        raise ModelNotConfiguredError(
            "No reviewed model weights are configured. Set MODEL_PATH to enable analysis."
        )


class KerasModel(ScreeningModel):
    name = "Configured Keras retinal grading model"
    version = "configured-by-deployment"
    architecture = "Keras model (architecture must be documented by the deployer)"
    classes = ("no diabetic retinopathy", "mild", "moderate", "severe", "proliferative")
    input_dimensions = (224, 224, 3)

    def __init__(self, path: Path) -> None:
        try:
            import tensorflow as tf
        except ImportError as exc:
            raise InferenceError(
                "TensorFlow is required for the configured Keras model."
            ) from exc
        try:
            self._model = tf.keras.models.load_model(path, compile=False)
        except Exception as exc:
            raise InferenceError("The configured model weights could not be loaded.") from exc

    @property
    def available(self) -> bool:
        return True

    def predict(self, image: Image.Image) -> Prediction:
        try:
            fitted = image.resize(self.input_dimensions[:2])
            data = np.asarray(fitted, dtype=np.float32) / 127.0 - 1.0
            raw = self._model.predict(data[None, ...], verbose=0)[0]
            scores = np.asarray(raw, dtype=np.float32).reshape(-1)
            if len(scores) != len(self.classes):
                raise ValueError("The model output does not match its documented classes.")
            # Softmax is only used for logits; probabilities are not claimed calibrated.
            if not np.isclose(scores.sum(), 1, atol=0.05) or np.any(scores < 0):
                scores = np.exp(scores - np.max(scores))
                scores = scores / scores.sum()
            index = int(np.argmax(scores))
            return Prediction(self.classes[index], list(zip(self.classes, scores.tolist())), index)
        except Exception as exc:
            if isinstance(exc, ValueError):
                raise InferenceError(str(exc)) from exc
            raise InferenceError("Model inference failed.") from exc


def load_model(model_path: str | None) -> ScreeningModel:
    if not model_path:
        return UnavailableModel()
    path = Path(model_path).expanduser()
    if not path.is_file():
        raise InferenceError("The configured model weights could not be found.")
    if path.suffix.lower() in {".h5", ".keras"}:
        return KerasModel(path)
    if path.suffix.lower() == ".pth":
        return EfficientNetModel(path)
    raise InferenceError("Unsupported model format. Configure a reviewed .h5 or .keras model.")


class EfficientNetModel(ScreeningModel):
    name = "Shifaa Diabetic Retinopathy EfficientNet-B0"
    version = "Ahmed-Selem/Shifaa-Diabetic-Retinopathy-EfficientNetB0"
    architecture = "torchvision EfficientNet-B0"
    classes = ("no diabetic retinopathy", "mild", "moderate", "severe", "proliferative")
    input_dimensions = (224, 224, 3)
    dataset = "Dataset documented by the model author as Diabetic Retinopathy 224x224 2019 Data"

    def __init__(self, path: Path) -> None:
        try:
            import torch
            from torchvision.models import efficientnet_b0
        except ImportError as exc:
            raise InferenceError(
                "PyTorch and torchvision are required for the configured EfficientNet model."
            ) from exc
        try:
            model = efficientnet_b0(weights=None)
            state_dict = torch.load(path, map_location="cpu", weights_only=True)
            model.classifier[1] = torch.nn.Linear(
                model.classifier[1].in_features, len(self.classes)
            )
            model.load_state_dict(state_dict, strict=True)
            model.eval()
            self._torch = torch
            self._model = model
        except Exception as exc:
            raise InferenceError("The configured EfficientNet weights are incompatible.") from exc

    @property
    def available(self) -> bool:
        return True

    def predict(self, image: Image.Image) -> Prediction:
        try:
            import torchvision.transforms as transforms

            transform = transforms.Compose(
                [
                    transforms.Resize(self.input_dimensions[:2]),
                    transforms.ToTensor(),
                    transforms.Normalize(
                        mean=[0.485, 0.456, 0.406],
                        std=[0.229, 0.224, 0.225],
                    ),
                ]
            )
            tensor = transform(image).unsqueeze(0)
            with self._torch.inference_mode():
                logits = self._model(tensor)
                probabilities = self._torch.softmax(logits, dim=1)[0].tolist()
            index = int(max(range(len(probabilities)), key=probabilities.__getitem__))
            return Prediction(
                self.classes[index],
                list(zip(self.classes, [float(value) for value in probabilities])),
                index,
            )
        except Exception as exc:
            raise InferenceError("Model inference failed.") from exc
