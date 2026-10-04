export interface PredictRequest {
  text: string;
}

export interface LabelScore {
  label: string;
  score: number;
  predicted: boolean;
}

export interface PredictResponse {
  model: string;
  anomaly: LabelScore[];
  primary_problem: LabelScore[];
}
