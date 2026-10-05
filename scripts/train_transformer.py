import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from baseline import MIN_TRAIN_EXAMPLES, parse_labels
from evaluate import evaluate
from peft import LoraConfig, get_peft_model
from sklearn.metrics import f1_score
from torch import nn
from torch.utils.data import DataLoader
from transformers import AutoModel, AutoTokenizer, get_linear_schedule_with_warmup

IGNORE = -100
THRESHOLDS = np.arange(0.05, 0.95, 0.05)


class TwoHeadModel(nn.Module):
    def __init__(self, encoder, hidden: int, n_anomaly: int, n_problem: int):
        super().__init__()
        self.encoder = encoder
        self.anomaly_head = nn.Linear(hidden, n_anomaly)
        self.problem_head = nn.Linear(hidden, n_problem)

    def forward(self, input_ids, attention_mask):
        states = self.encoder(
            input_ids=input_ids, attention_mask=attention_mask
        ).last_hidden_state
        mask = attention_mask.unsqueeze(-1).to(states.dtype)
        pooled = (states * mask).sum(1) / mask.sum(1)
        return self.anomaly_head(pooled), self.problem_head(pooled)


def build_label_spaces(train: pd.DataFrame):
    counts = pd.Series(
        [l for v in train["anomaly"] for l in parse_labels(v)]
    ).value_counts()
    anomaly = sorted(counts[counts >= MIN_TRAIN_EXAMPLES].index)
    problem = sorted(train["primary_problem"].dropna().unique())
    return anomaly, problem


def head_tail_encode(tokenizer, texts, max_len, head_tokens):
    budget = max_len - 2
    ids = tokenizer(texts, add_special_tokens=False)["input_ids"]
    kept = [i if len(i) <= budget else i[:head_tokens] + i[-(budget - head_tokens):] for i in ids]
    input_ids = [[tokenizer.cls_token_id] + i + [tokenizer.sep_token_id] for i in kept]
    return {"input_ids": input_ids, "attention_mask": [[1] * len(i) for i in input_ids]}


def encode_split(df, tokenizer, anomaly_labels, problem_labels, max_len, truncation="head", head_tokens=128):
    texts = list(df["text"])
    if truncation == "head_tail":
        enc = head_tail_encode(tokenizer, texts, max_len, head_tokens)
    else:
        enc = tokenizer(texts, truncation=True, max_length=max_len)
    a_index = {l: i for i, l in enumerate(anomaly_labels)}
    p_index = {l: i for i, l in enumerate(problem_labels)}
    anomaly = np.zeros((len(df), len(anomaly_labels)), dtype=np.float32)
    for row, value in enumerate(df["anomaly"]):
        for label in parse_labels(value):
            if label in a_index:
                anomaly[row, a_index[label]] = 1.0
    problem = np.array([p_index.get(v, IGNORE) for v in df["primary_problem"]])
    return [
        {
            "input_ids": enc["input_ids"][i],
            "attention_mask": enc["attention_mask"][i],
            "anomaly": anomaly[i],
            "problem": int(problem[i]),
        }
        for i in range(len(df))
    ]


def make_loader(items, tokenizer, batch_size, shuffle):
    def collate(batch):
        padded = tokenizer.pad(
            [
                {"input_ids": b["input_ids"], "attention_mask": b["attention_mask"]}
                for b in batch
            ],
            return_tensors="pt",
        )
        padded["anomaly"] = torch.tensor(np.stack([b["anomaly"] for b in batch]))
        padded["problem"] = torch.tensor([b["problem"] for b in batch])
        return padded

    return DataLoader(items, batch_size=batch_size, shuffle=shuffle, collate_fn=collate)


def predict(model, loader, device):
    model.eval()
    anomaly_probs, problem_pred, anomaly_true, problem_true = [], [], [], []
    with torch.no_grad():
        for batch in loader:
            a_logits, p_logits = model(
                batch["input_ids"].to(device), batch["attention_mask"].to(device)
            )
            anomaly_probs.append(torch.sigmoid(a_logits).float().cpu().numpy())
            problem_pred.append(p_logits.argmax(-1).cpu().numpy())
            anomaly_true.append(batch["anomaly"].numpy())
            problem_true.append(batch["problem"].numpy())
    return (
        np.concatenate(anomaly_probs),
        np.concatenate(problem_pred),
        np.concatenate(anomaly_true),
        np.concatenate(problem_true),
    )


def best_threshold(probs, truth):
    scores = [
        f1_score(truth.astype(int), (probs > t).astype(int), average="macro", zero_division=0)
        for t in THRESHOLDS
    ]
    return float(THRESHOLDS[int(np.argmax(scores))])


def score(raw, threshold, anomaly_labels, problem_labels):
    a_probs, p_pred, a_true, p_true = raw
    known = p_true != IGNORE
    return {
        "anomaly": evaluate(
            a_true.astype(int), (a_probs > threshold).astype(int), anomaly_labels
        )
        | {"threshold": threshold},
        "primary_problem": evaluate(
            p_true[known], p_pred[known], range(len(problem_labels))
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="data/processed")
    parser.add_argument("--out-dir", default="results/transformer")
    parser.add_argument("--model", default="microsoft/deberta-v3-base")
    parser.add_argument("--max-len", type=int, default=512)
    parser.add_argument("--truncation", choices=["head", "head_tail"], default="head")
    parser.add_argument("--head-tokens", type=int, default=128)
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=16)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--head-lr", type=float, default=1e-3)
    args = parser.parse_args()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    data_dir, out_dir = Path(args.data_dir), Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    splits = {
        n: pd.read_csv(data_dir / f"{n}.csv", dtype=str)
        for n in ("train", "val", "test")
    }
    anomaly_labels, problem_labels = build_label_spaces(splits["train"])

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    loaders = {
        n: make_loader(
            encode_split(df, tokenizer, anomaly_labels, problem_labels, args.max_len, args.truncation, args.head_tokens),
            tokenizer,
            args.batch_size,
            shuffle=(n == "train"),
        )
        for n, df in splits.items()
    }

    encoder = AutoModel.from_pretrained(args.model, dtype=torch.float32)
    lora = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.1,
        target_modules=["query_proj", "key_proj", "value_proj", "dense"],
    )
    encoder = get_peft_model(encoder, lora)
    model = TwoHeadModel(
        encoder, encoder.config.hidden_size, len(anomaly_labels), len(problem_labels)
    ).to(device)

    head_params = list(model.anomaly_head.parameters()) + list(
        model.problem_head.parameters()
    )
    head_ids = {id(p) for p in head_params}
    lora_params = [
        p for p in model.parameters() if p.requires_grad and id(p) not in head_ids
    ]
    optimizer = torch.optim.AdamW(
        [
            {"params": lora_params, "lr": args.lr},
            {"params": head_params, "lr": args.head_lr},
        ],
        weight_decay=0.01,
    )
    steps = args.epochs * len(loaders["train"])
    scheduler = get_linear_schedule_with_warmup(optimizer, int(0.1 * steps), steps)
    scaler = torch.amp.GradScaler(enabled=device == "cuda")

    train_items = loaders["train"].dataset
    anomaly_matrix = np.stack([item["anomaly"] for item in train_items])
    positives = anomaly_matrix.sum(0)
    negatives = len(anomaly_matrix) - positives
    pos_weight = torch.tensor(
        np.clip(np.sqrt(negatives / np.maximum(positives, 1)), 1, 10),
        dtype=torch.float32,
        device=device,
    )
    problem_ids = np.array([item["problem"] for item in train_items])
    problem_counts = np.bincount(
        problem_ids[problem_ids != IGNORE], minlength=len(problem_labels)
    )
    class_weight = (problem_counts.sum() / np.maximum(problem_counts, 1)) ** 0.5
    class_weight = torch.tensor(
        class_weight / class_weight.mean(), dtype=torch.float32, device=device
    )
    bce = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    ce = nn.CrossEntropyLoss(weight=class_weight, ignore_index=IGNORE)

    best_macro, best_state, best_thr, history = -1.0, None, 0.5, []
    for epoch in range(args.epochs):
        model.train()
        total_loss = 0.0
        for batch in loaders["train"]:
            optimizer.zero_grad()
            with torch.autocast(
                device_type=device, dtype=torch.float16, enabled=device == "cuda"
            ):
                a_logits, p_logits = model(
                    batch["input_ids"].to(device), batch["attention_mask"].to(device)
                )
                loss = bce(a_logits.float(), batch["anomaly"].to(device)) + ce(
                    p_logits.float(), batch["problem"].to(device)
                )
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            scheduler.step()
            total_loss += loss.item()
        raw_val = predict(model, loaders["val"], device)
        threshold = best_threshold(raw_val[0], raw_val[2])
        val = score(raw_val, threshold, anomaly_labels, problem_labels)
        history.append(
            {
                "epoch": epoch + 1,
                "train_loss": total_loss / len(loaders["train"]),
                "threshold": threshold,
                "val_anomaly_macro_f1": val["anomaly"]["macro_f1"],
                "val_problem_macro_f1": val["primary_problem"]["macro_f1"],
            }
        )
        print(history[-1], flush=True)
        if val["anomaly"]["macro_f1"] > best_macro:
            best_macro, best_thr = val["anomaly"]["macro_f1"], threshold
            best_state = {
                n: p.detach().cpu().clone()
                for n, p in model.named_parameters()
                if p.requires_grad
            }

    model.load_state_dict(best_state, strict=False)
    raw_test = predict(model, loaders["test"], device)
    test = score(raw_test, best_thr, anomaly_labels, problem_labels)
    test_at_half = score(raw_test, 0.5, anomaly_labels, problem_labels)
    for name, raw in (("val", predict(model, loaders["val"], device)), ("test", raw_test)):
        np.savez(
            out_dir / f"{name}_predictions.npz",
            anomaly_probs=raw[0],
            problem_pred=raw[1],
            anomaly_true=raw[2],
            problem_true=raw[3],
        )
    torch.save(best_state, out_dir / "trainable_weights.pt")
    (out_dir / "labels.json").write_text(
        json.dumps({"anomaly": anomaly_labels, "primary_problem": problem_labels})
    )
    (out_dir / "metrics.json").write_text(
        json.dumps(
            {
                "config": vars(args),
                "history": history,
                "test": test,
                "test_anomaly_at_0.5": test_at_half["anomaly"],
            },
            indent=2,
        )
    )
    for task, r in test.items():
        print(
            f"{task}: macro_f1={r['macro_f1']:.3f} micro_f1={r['micro_f1']:.3f} hamming={r['hamming_loss']:.3f}"
        )


if __name__ == "__main__":
    main()
