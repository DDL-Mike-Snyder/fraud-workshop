"""Fine-tune a small open LLM (LoRA) to classify card transactions as fraud / legitimate.

Run as a Domino Job on a GPU hardware tier, after step 2 (needs clean_cc_transactions.csv):
    python exercises/f_OpenModelAgents/finetune_fraud_llm.py

Logs params, metrics (roc_auc, f1_fraud, accuracy, ...) and the LoRA adapter to an
Experiments run, and writes the merged model to <dataset>/models/fraud-llm for serving.
The score is P(label=1) read from the model's next-token probabilities.
"""
import os, sys, json, time
import numpy as np, pandas as pd, torch, mlflow
from sklearn.metrics import roc_auc_score, f1_score, accuracy_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments
from peft import LoraConfig, get_peft_model

sys.path.append(os.environ.get("DOMINO_WORKING_DIR", "/mnt/code"))
from domino_short_id import domino_short_id
from exercises.f_OpenModelAgents.common import FRAUD_BASE_MODEL, transaction_prompt

N_TRAIN = int(os.environ.get("N_TRAIN", 20000))
N_EVAL = int(os.environ.get("N_EVAL", 2000))
EPOCHS = float(os.environ.get("EPOCHS", 1))
LR = float(os.environ.get("LR", 2e-4))

_proj = os.environ.get("DOMINO_PROJECT_NAME", "fraud-workshop")
_data = os.environ.get("DOMINO_DATASETS_DIR", "/domino/datasets")
_git = os.environ.get("DOMINO_IS_GIT_BASED") == "true"
# Domino-hosted projects: <datasets>/local/<project>. Git-based projects: <datasets>/<project>/<user>.
ds = f"{_data}/{_proj}/{os.environ.get('DOMINO_USER_NAME')}" if _git else f"{_data}/local/{_proj}"
out_dir = f"{ds}/models/fraud-llm"
os.environ.setdefault("HF_HOME", f"{ds}/hf_cache")
art_dir = (f"{os.environ.get('DOMINO_ARTIFACTS_DIR', '/mnt/artifacts')}/f_fraud_llm" if _git
           else f"{os.environ.get('DOMINO_WORKING_DIR', '/mnt/code')}/artifacts/f_fraud_llm")
os.makedirs(art_dir, exist_ok=True)

df = pd.read_csv(f"{ds}/clean_cc_transactions.csv").dropna(subset=["Class"])
train_df, eval_df = train_test_split(df, test_size=N_EVAL, stratify=df["Class"], random_state=7)
train_df = train_df.sample(min(N_TRAIN, len(train_df)), random_state=7)

tok = AutoTokenizer.from_pretrained(FRAUD_BASE_MODEL)
tok.padding_side = "left"
ID = {0: tok.encode("0", add_special_tokens=False)[0], 1: tok.encode("1", add_special_tokens=False)[0]}


class DS(torch.utils.data.Dataset):
    def __init__(self, frame):
        self.p = [tok.encode(transaction_prompt(r), add_special_tokens=False) for _, r in frame.iterrows()]
        self.y = frame["Class"].astype(int).tolist()
    def __len__(self): return len(self.y)
    def __getitem__(self, i):
        ids = self.p[i] + [ID[self.y[i]]]
        labels = [-100] * len(self.p[i]) + [ID[self.y[i]]]   # loss on the label token only
        return {"input_ids": ids, "labels": labels}


def collate(batch):
    m = max(len(b["input_ids"]) for b in batch)
    pad = tok.pad_token_id
    ids = torch.tensor([[pad] * (m - len(b["input_ids"])) + b["input_ids"] for b in batch])
    lab = torch.tensor([[-100] * (m - len(b["labels"])) + b["labels"] for b in batch])
    return {"input_ids": ids, "labels": lab, "attention_mask": (ids != pad).long()}


@torch.no_grad()
def score(model, frame, bs=64):
    """P(fraud) = softmax over the two label tokens at the next-token position."""
    model.eval(); out = []
    prompts = [transaction_prompt(r) for _, r in frame.iterrows()]
    for i in range(0, len(prompts), bs):
        enc = tok(prompts[i:i + bs], return_tensors="pt", padding=True, add_special_tokens=False).to(model.device)
        logits = model(**enc).logits[:, -1, :]
        two = torch.stack([logits[:, ID[0]], logits[:, ID[1]]], dim=1).float()
        out += torch.softmax(two, dim=1)[:, 1].cpu().tolist()
    return np.array(out)


mlflow.set_experiment(f"CC Fraud LLM Fine-tuning {domino_short_id()}")
with mlflow.start_run(run_name="Granite-LoRA"):
    mlflow.log_params({"base_model": FRAUD_BASE_MODEL, "n_train": len(train_df), "n_eval": len(eval_df),
                       "epochs": EPOCHS, "lr": LR, "lora_r": 16, "lora_alpha": 32})
    model = AutoModelForCausalLM.from_pretrained(FRAUD_BASE_MODEL, dtype=torch.bfloat16).cuda()

    base = score(model, eval_df)
    mlflow.log_metric("base_roc_auc", roc_auc_score(eval_df["Class"], base))
    print("base model roc_auc (no tuning):", roc_auc_score(eval_df["Class"], base))

    model = get_peft_model(model, LoraConfig(r=16, lora_alpha=32, lora_dropout=0.05, task_type="CAUSAL_LM",
                           target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]))
    t0 = time.time()
    Trainer(model=model, train_dataset=DS(train_df), data_collator=collate,
            args=TrainingArguments(output_dir="/tmp/ft", num_train_epochs=EPOCHS, learning_rate=LR,
                                   per_device_train_batch_size=16, gradient_accumulation_steps=2,
                                   bf16=True, logging_steps=25, save_strategy="no", report_to=[],
                                   lr_scheduler_type="cosine", warmup_steps=20, remove_unused_columns=False)).train()
    mlflow.log_metric("train_seconds", time.time() - t0)

    p = score(model, eval_df); y = eval_df["Class"].values
    best = max(np.linspace(0.05, 0.95, 19), key=lambda t: f1_score(y, p >= t))
    pred = p >= best
    mlflow.log_metrics({"roc_auc": roc_auc_score(y, p), "f1_fraud": f1_score(y, pred),
                        "precision_fraud": precision_score(y, pred), "recall_fraud": recall_score(y, pred),
                        "accuracy": accuracy_score(y, pred), "tau_best_f1": float(best)})
    print(json.dumps({k: round(float(v), 4) for k, v in zip(
        ["roc_auc", "f1_fraud", "accuracy", "tau_best_f1"],
        [roc_auc_score(y, p), f1_score(y, pred), accuracy_score(y, pred), best])}, indent=2))

    model.save_pretrained(f"{art_dir}/lora_adapter")
    mlflow.log_artifacts(f"{art_dir}/lora_adapter", "lora_adapter")
    pd.DataFrame({"y": y, "p_fraud": p}).to_csv(f"{art_dir}/eval_scores.csv", index=False)
    mlflow.log_artifact(f"{art_dir}/eval_scores.csv")

    merged = model.merge_and_unload()
    os.makedirs(out_dir, exist_ok=True)
    merged.save_pretrained(out_dir); tok.save_pretrained(out_dir)
    json.dump({"threshold": float(best)}, open(f"{out_dir}/fraud_threshold.json", "w"))
    print("Merged model saved to", out_dir)
    print("Fine-tuning completed successfully")
