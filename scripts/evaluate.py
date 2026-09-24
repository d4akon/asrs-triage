import numpy as np
from sklearn.metrics import f1_score, hamming_loss


def evaluate(y_true, y_pred, label_names) -> dict:
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    kw = {} if y_true.ndim == 2 else {"labels": list(label_names)}
    per_label = f1_score(y_true, y_pred, average=None, zero_division=0, **kw)
    return {
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0, **kw)),
        "micro_f1": float(f1_score(y_true, y_pred, average="micro", zero_division=0, **kw)),
        "hamming_loss": float(hamming_loss(y_true, y_pred)),
        "per_label_f1": {name: float(v) for name, v in zip(label_names, per_label)},
    }
