import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModel
from peft import PeftModel, PeftConfig
from sentence_transformers import SentenceTransformer

LABELS = ["Syntax Error", "Runtime Error", "Logic Bug", "Multiple Issues"]
SAVE_PATH = "/content/drive/MyDrive/code-debugger/ml_service/model/lora_weights"

# ── Load classifier ───────────────────────────────────────────────────────────
config = PeftConfig.from_pretrained(SAVE_PATH)
base = AutoModelForSequenceClassification.from_pretrained(
    config.base_model_name_or_path, num_labels=len(LABELS)
)
model = PeftModel.from_pretrained(base, SAVE_PATH)
model.eval()
tokenizer = AutoTokenizer.from_pretrained(SAVE_PATH)

# ── Load embedding model ──────────────────────────────────────────────────────
embed_model = SentenceTransformer("BAAI/bge-small-en-v1.5")
index = []

# ── Load attention model ──────────────────────────────────────────────────────
attn_model = AutoModel.from_pretrained(
    "distilbert-base-uncased", output_attentions=True
)
attn_model.eval()


def classify(code: str) -> dict:
    inputs = tokenizer(code, return_tensors="pt", truncation=True, max_length=256)
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = torch.softmax(logits, dim=-1).squeeze().tolist()
    pred_idx = torch.argmax(logits).item()
    return {
        "label": LABELS[pred_idx],
        "confidence": round(probs[pred_idx], 3),
        "all_scores": {LABELS[i]: round(p, 3) for i, p in enumerate(probs)},
    }


def add_to_index(code: str, fix: str, explanation: str):
    emb = embed_model.encode(code, normalize_embeddings=True)
    index.append({"code": code, "fix": fix, "explanation": explanation, "emb": emb})


def search_similar(query_code: str, top_k: int = 3) -> list:
    if not index:
        return []
    q_emb = embed_model.encode(query_code, normalize_embeddings=True)
    scores = [float(np.dot(q_emb, item["emb"])) for item in index]
    ranked = sorted(zip(scores, index), key=lambda x: x[0], reverse=True)
    return [
        {"score": round(s, 3), "code": item["code"], "explanation": item["explanation"]}
        for s, item in ranked[:top_k]
    ]


def get_attention(code: str) -> dict:
    inputs = tokenizer(code, return_tensors="pt", truncation=True, max_length=64)
    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0].tolist())
    with torch.no_grad():
        outputs = attn_model(**inputs)
    last_layer = outputs.attentions[-1][0]
    avg_attn = last_layer.mean(dim=0).tolist()
    return {
        "tokens": tokens,
        "matrix": avg_attn,
        "num_layers": len(outputs.attentions),
        "num_heads": int(last_layer.shape[0]),
    }
