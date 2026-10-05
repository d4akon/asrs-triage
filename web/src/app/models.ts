export interface PredictRequest {
  text: string;
}

export interface LabelScore {
  label: string;
  score: number;
  predicted: boolean;
  terms: string[];
}

export interface SimilarReport {
  acn: string;
  date: string;
  similarity: number;
  anomaly: string[];
  primary_problem: string | null;
  snippet: string;
}

export interface PredictResponse {
  model: string;
  anomaly: LabelScore[];
  primary_problem: LabelScore[];
  similar: SimilarReport[];
}

export interface LabelTrend {
  label: string;
  mean_share: number;
  tracking_corr: number;
  true_share: number[];
  predicted_share: number[];
  change_points: string[];
}

export interface LabelTrends {
  months: string[];
  reports: number[];
  labels_per_report: number[];
  labels: LabelTrend[];
}

export interface TopicTrend {
  topic: number;
  words: string;
  count: number;
  share: number[];
}

export interface TopicTrends {
  months: string[];
  topics: TopicTrend[];
}
