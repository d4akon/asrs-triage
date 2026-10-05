import ast
import os
import re
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

MODEL_PATH = Path(os.environ.get("MODEL_PATH", "models/baseline/model.joblib"))
RESULTS_DIR = Path(os.environ.get("RESULTS_DIR", "results"))
MODEL_NAME = "tfidf-linearsvc-baseline"
ANOMALY_TOP_K = 5
PROBLEM_TOP_K = 3
TERMS_PER_LABEL = 5
SIMILAR_K = 3
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:4200").split(",")
# must match the placeholder rule in scripts/clean.py
PLACEHOLDER = re.compile(r"\bZZZ\w*\b")

state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    model = joblib.load(MODEL_PATH)
    model["feature_names"] = np.asarray(model["vectorizer"].get_feature_names_out())
    state["model"] = model
    yield
    state.clear()


app = FastAPI(title="ASRS triage", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


class PredictRequest(BaseModel):
    text: str = Field(min_length=20, max_length=20000)


class LabelScore(BaseModel):
    label: str
    score: float
    predicted: bool
    terms: list[str]


class SimilarReport(BaseModel):
    acn: str
    date: str
    similarity: float
    anomaly: list[str]
    primary_problem: str | None
    snippet: str


class PredictResponse(BaseModel):
    model: str
    anomaly: list[LabelScore]
    primary_problem: list[LabelScore]
    similar: list[SimilarReport]


class LabelTrend(BaseModel):
    label: str
    mean_share: float
    tracking_corr: float
    true_share: list[float]
    predicted_share: list[float]
    change_points: list[str]


class LabelTrends(BaseModel):
    months: list[str]
    reports: list[int]
    labels_per_report: list[float]
    labels: list[LabelTrend]


class TopicTrend(BaseModel):
    topic: int
    words: str
    count: int
    share: list[float]


class TopicTrends(BaseModel):
    months: list[str]
    topics: list[TopicTrend]


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-values))


def top_terms(model: dict, features, weights: np.ndarray) -> list[str]:
    # Terms present in the report whose weight pushes this label up, strongest first.
    contribution = features.multiply(weights.reshape(1, -1)).tocsr()
    columns, values = contribution.indices, contribution.data
    order = np.argsort(values)[::-1][:TERMS_PER_LABEL]
    return [str(model["feature_names"][columns[i]]) for i in order if values[i] > 0]


def similar_reports(model: dict, features) -> list[SimilarReport]:
    similarity = (model["corpus_features"] @ features.T).toarray().ravel()
    best = np.argsort(similarity)[::-1][:SIMILAR_K]
    return [SimilarReport(similarity=float(similarity[i]), **model["corpus_meta"][i]) for i in best]


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model": MODEL_NAME}


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest) -> PredictResponse:
    model = state["model"]
    features = model["vectorizer"].transform([PLACEHOLDER.sub("[ANON]", request.text)])

    margins = model["anomaly"].decision_function(features)[0]
    probabilities = sigmoid(margins)
    for i, calibrator in enumerate(model["anomaly_calibrators"]):
        if calibrator is not None:
            probabilities[i] = calibrator.predict_proba(margins[[i]].reshape(1, 1))[0, 1]
    top = np.argsort(margins)[::-1][:ANOMALY_TOP_K]
    anomaly = [
        LabelScore(
            label=model["anomaly_labels"][i],
            score=float(probabilities[i]),
            predicted=bool(margins[i] > 0),
            terms=top_terms(model, features, model["anomaly"].estimators_[i].coef_[0]),
        )
        for i in top
    ]

    problem_margins = model["problem"].decision_function(features)
    problem_probabilities = model["problem_calibrator"].predict_proba(problem_margins)[0]
    best = int(np.argmax(problem_margins[0]))
    top = np.argsort(problem_probabilities)[::-1][:PROBLEM_TOP_K]
    classes = model["problem"].classes_
    problem = [
        LabelScore(
            label=str(classes[i]),
            score=float(problem_probabilities[i]),
            predicted=i == best,
            terms=top_terms(model, features, model["problem"].coef_[i]),
        )
        for i in top
    ]
    return PredictResponse(
        model=MODEL_NAME, anomaly=anomaly, primary_problem=problem, similar=similar_reports(model, features)
    )


def read_results(*parts: str) -> pd.DataFrame:
    path = RESULTS_DIR.joinpath(*parts)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"{path} not found; run the trend scripts first")
    return pd.read_csv(path, index_col=0, dtype={0: str})


def format_months(index: pd.Index) -> list[str]:
    return [f"{m[:4]}-{m[4:]}" for m in index.astype(str)]


@app.get("/trends/labels", response_model=LabelTrends)
def label_trends() -> LabelTrends:
    true_share = read_results("trends", "monthly_true_share.csv")
    predicted = read_results("trends", "monthly_predicted_share.csv")
    monthly = read_results("trends", "monthly_summary.csv")
    summary = pd.read_csv(RESULTS_DIR / "trends" / "label_trend_summary.csv")
    labels = [
        LabelTrend(
            label=row.label,
            mean_share=float(row.mean_share),
            tracking_corr=float(0 if pd.isna(row.tracking_corr) else row.tracking_corr),
            true_share=true_share[row.label].tolist(),
            predicted_share=predicted[row.label].tolist(),
            change_points=ast.literal_eval(row.pred_change_points),
        )
        for row in summary.itertuples()
    ]
    return LabelTrends(
        months=format_months(true_share.index),
        reports=monthly["reports"].astype(int).tolist(),
        labels_per_report=monthly["labels_per_report"].tolist(),
        labels=labels,
    )


@app.get("/trends/topics", response_model=TopicTrends)
def topic_trends() -> TopicTrends:
    share = read_results("topics", "monthly_topic_share.csv")
    info = pd.read_csv(RESULTS_DIR / "topics" / "topics.csv")
    topics = [
        TopicTrend(topic=int(row.Topic), words=row.top_words, count=int(row.Count), share=share[str(row.Topic)].tolist())
        for row in info.itertuples()
        if row.Topic != -1
    ]
    return TopicTrends(months=format_months(share.index), topics=topics)
