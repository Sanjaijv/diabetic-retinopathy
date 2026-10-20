export type AnalysisResult = {
  analysis_id: string;
  image_quality: { status: string; width: number; height: number; warnings: string[] };
  screening_class: "normal" | "abnormal" | "uncertain" | "ungradable" | null;
  predicted_class: string | null;
  scores: { label: string; value: number }[];
  dr_grade: number | null;
  findings: {
    name: string;
    status: string;
    explanation: string;
    significance: string;
  }[];
  explanation_available: boolean;
  explanation_message: string;
  model_available: boolean;
  model_name: string;
  model_version: string;
  limitations: string[];
  follow_up: string;
};

export type ModelInfo = {
  name: string;
  version: string;
  architecture: string;
  supported_tasks: string[];
  supported_classes: string[];
  input_dimensions: number[];
  dataset: string | null;
  model_available: boolean;
  limitations: string[];
};
