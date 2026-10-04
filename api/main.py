import os
import re
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

MODEL_PATH = Path(os.environ.get("MODEL_PATH", "models/baseline/model.joblib"))
MODEL_NAME = "tfidf-linearsvc-baseline"
ANOMALY_TOP_K = 5
PROBLEM_TOP_K = 3
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "http://localhost:4200").split(",")
# must match the placeholder rule in scripts/clean.py
PLACEHOLDER = re.compile(r"\bZZZ\w*\b")

state: dict = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    state["model"] = joblib.load(MODEL_PATH)
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


class PredictResponse(BaseModel):
    model: str
    anomaly: list[LabelScore]
    primary_problem: list[LabelScore]


def sigmoid(values: np.ndarray) -> np.ndarray:
    return 1 / (1 + np.exp(-values))


def softmax(values: np.ndarray) -> np.ndarray:
    shifted = np.exp(values - values.max())
    return shifted / shifted.sum()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "model": MODEL_NAME}


@app.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest) -> PredictResponse:
    model = state["model"]
    features = model["vectorizer"].transform([PLACEHOLDER.sub("[ANON]", request.text)])

    margins = model["anomaly"].decision_function(features)[0]
    top = np.argsort(margins)[::-1][:ANOMALY_TOP_K]
    anomaly = [
        LabelScore(label=model["anomaly_labels"][i], score=float(sigmoid(margins[i])), predicted=bool(margins[i] > 0))
        for i in top
    ]

    problem_margins = model["problem"].decision_function(features)[0]
    probabilities = softmax(problem_margins)
    best = int(np.argmax(problem_margins))
    top = np.argsort(probabilities)[::-1][:PROBLEM_TOP_K]
    problem = [
        LabelScore(label=str(model["problem"].classes_[i]), score=float(probabilities[i]), predicted=i == best)
        for i in top
    ]
    return PredictResponse(model=MODEL_NAME, anomaly=anomaly, primary_problem=problem)
