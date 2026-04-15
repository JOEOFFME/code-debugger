import gradio as gr
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from groq_fixer import fix_with_groq,generate_diff


matplotlib.use("Agg")

BADGE_COLORS = {
    "Syntax Error":    "#f97583",
    "Runtime Error":   "#ffab70",
    "Logic Bug":       "#ffd700",
    "Multiple Issues": "#b392f0",
}

EXAMPLES = [
    "def greet(name)\n    print('Hello, ' + name)",
    "numbers = [1, 2, 3]\nprint(numbers[10])",
    "def is_even(n):\n    return n % 2 == 1",
    "def factorial(n)\n    if n = 0:\n        return 1\n    return n * factorial(n-1)",
]

CSS = """
* { font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace !important; }

body, .gradio-container {
    background-color: #1e1e1e !important;
    color: #d4d4d4 !important;
}

.gr-button-primary {
    background: #0e639c !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 3px !important;
}

.gr-button-primary:hover {
    background: #1177bb !important;
}

.gr-button-secondary {
    background: #3c3c3c !important;
    border: 1px solid #555 !important;
    color: #d4d4d4 !important;
    border-radius: 3px !important;
}

textarea, .gr-textbox textarea {
    background-color: #1e1e1e !important;
    color: #d4d4d4 !important;
    border: 1px solid #3c3c3c !important;
    border-radius: 3px !important;
    font-size: 13px !important;
    line-height: 1.6 !important;
}

.gr-tab-item {
    background: #2d2d2d !important;
    color: #d4d4d4 !important;
    border: none !important;
    border-radius: 0 !important;
}

.gr-tab-item.selected {
    background: #1e1e1e !important;
    border-top: 2px solid #0e639c !important;
    color: #ffffff !important;
}

.gr-panel {
    background: #252526 !important;
    border: 1px solid #3c3c3c !important;
    border-radius: 3px !important;
}

label, .gr-label {
    color: #9cdcfe !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}

.gr-markdown {
    background: transparent !important;
    color: #d4d4d4 !important;
}

footer { display: none !important; }

"""
def classify(code:str) -> dict:
  inputs=tokenizer(code,return_tensors="pt",truncation=True,max_lenght=256)
  with torch.no_grad():
    logits=classifier(**inputs).logits
  probs=torch.softmax(logits,dim=-1).squeeze().tolist()
  pred_idx=torch.argmax(logits).item()
  return {
      "label":LABELS[pred_idx],
      "confidence":round(probs[pred_idx],3),
      "all_scores":{LABELS[i]:round(p,3) for i,p in enumerate(probs)}
  }
def add_to_idx(code:str,fix:str,explanation:str):
    emb=embed_model.encode(code, normalize_embeddings=True)
    index.append({"code":code,"fix":fix,"explanation":explanation,"embedding":emb})
def search_similar(query_code, top_k=3):
    if not index:
        return []
    q_emb = embed_model.encode(query_code, normalize_embeddings=True)
    scores = [float(np.dot(q_emb, item["embedding"])) for item in index]
    ranked = sorted(zip(scores, index), key=lambda x: x[0], reverse=True)
    return [
        {"score": round(s, 3), "code": item["code"], "explanation": item["explanation"]}
        for s, item in ranked[:top_k]
    ]
def get_attention(code):
    inputs = tokenizer(code, return_tensors="pt", truncation=True, max_length=64)
    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0].tolist())
    with torch.no_grad():
        outputs = attn_model(**inputs)
    last_layer = outputs.attentions[-1][0]
    avg_attn = last_layer.mean(dim=0).tolist()
    return {"tokens": tokens, "matrix": avg_attn}

def debug(code):
      clf=classify(code)
      similar=search_similar(code)
      fix=fix_with_groq(code,clf["label"])
      diff=generate_diff(code,fix["fixed_code"])
      attention=get_attention(code)
      if fix["fixed_code"]:
        add_to_idx(code, fix["fixed_code"], fix["explanation"])
      return clf, fix["explanation"], fix["fixed_code"], diff, similar, attention

def plot_attention_heatmap(attention_data):
    tokens = attention_data["tokens"]
    matrix = np.array(attention_data["matrix"])

    fig, ax = plt.subplots(figsize=(8, 6))
    fig.patch.set_facecolor("#1e1e1e")
    ax.set_facecolor("#1e1e1e")

    im = ax.imshow(matrix, cmap="Blues", aspect="auto")

    ax.set_xticks(range(len(tokens)))
    ax.set_yticks(range(len(tokens)))
    ax.set_xticklabels(tokens, rotation=45, ha="right",
                       fontsize=8, color="#d4d4d4")
    ax.set_yticklabels(tokens, fontsize=8, color="#d4d4d4")

    cbar = plt.colorbar(im, ax=ax)
    cbar.ax.yaxis.set_tick_params(color="#d4d4d4")
    plt.setp(cbar.ax.yaxis.get_ticklabels(), color="#d4d4d4")

    ax.set_title("Attention weights — last layer avg across 12 heads",
                 color="#9cdcfe", fontsize=10, pad=12)
    ax.tick_params(colors="#d4d4d4")
    for spine in ax.spines.values():
        spine.set_edgecolor("#3c3c3c")

    plt.tight_layout()
    return fig


def format_similar_bugs(similar_bugs):
    if not similar_bugs:
        return "```\n// No similar bugs in index yet.\n// Index grows as you debug more code.\n```"
    out = ""
    for i, bug in enumerate(similar_bugs, 1):
        out += f"// #{i} — similarity score: {bug['score']}\n"
        out += f"// {bug['explanation']}\n"
        out += f"{bug['code']}\n\n"
    return f"```python\n{out}```"


def run_debug(code):
    if not code.strip():
        return (
            "// Paste some buggy Python code and click Debug",
            "", "", "", None,
            "```\n// No results yet\n```"
        )

    clf, explanation, fixed_code, diff, similar, attention = debug(code)

    label = clf["label"]
    confidence = clf["confidence"] * 100
    scores = clf["all_scores"]

    # Classification panel
    color = BADGE_COLORS.get(label, "#d4d4d4")
    classification_md = f"""
<div style='background:#252526; border:1px solid #3c3c3c; border-radius:3px; padding:16px;'>
  <div style='display:flex; align-items:center; gap:12px; margin-bottom:12px;'>
    <span style='background:{color}22; color:{color}; border:1px solid {color}44;
                 padding:3px 10px; border-radius:3px; font-size:12px; font-weight:600;'>
      {label}
    </span>
    <span style='color:#858585; font-size:12px;'>confidence: {confidence:.1f}%</span>
  </div>
  <div style='color:#9cdcfe; font-size:11px; margin-bottom:8px; text-transform:uppercase; letter-spacing:0.08em;'>explanation</div>
  <div style='color:#d4d4d4; font-size:13px; line-height:1.6;'>{explanation}</div>
  <div style='margin-top:12px; color:#9cdcfe; font-size:11px; text-transform:uppercase; letter-spacing:0.08em;'>score breakdown</div>
  <div style='margin-top:6px; display:flex; flex-direction:column; gap:4px;'>
"""
    for lbl, score in scores.items():
        bar_color = BADGE_COLORS.get(lbl, "#555")
        width = int(score * 200)
        classification_md += f"""
    <div style='display:flex; align-items:center; gap:8px;'>
      <span style='color:#858585; font-size:11px; width:120px;'>{lbl}</span>
      <div style='background:{bar_color}; height:4px; width:{width}px; border-radius:2px;'></div>
      <span style='color:#858585; font-size:11px;'>{score*100:.1f}%</span>
    </div>"""
    classification_md += "</div></div>"

    fig = plot_attention_heatmap(attention)
    similar_md = format_similar_bugs(similar)

    return (
        classification_md,
        fixed_code,
        diff if diff else "// No changes detected",
        similar_md,
        fig,
    )


with gr.Blocks(css=CSS, theme=gr.themes.Base(), title="Code Debugger") as demo:

    gr.HTML("""
    <div style='background:#252526; border-bottom:1px solid #3c3c3c;
                padding:10px 20px; display:flex; align-items:center; gap:12px;'>
        <div style='display:flex; gap:6px;'>
            <div style='width:12px; height:12px; border-radius:50%; background:#ff5f57;'></div>
            <div style='width:12px; height:12px; border-radius:50%; background:#ffbd2e;'></div>
            <div style='width:12px; height:12px; border-radius:50%; background:#28c840;'></div>
        </div>
        <span style='color:#858585; font-size:12px;'>code-debugger — AI Python Debugger</span>
    </div>
    """)

    with gr.Row():
        with gr.Column(scale=1):
            gr.HTML("<div style='color:#858585; font-size:11px; padding:8px 0; text-transform:uppercase; letter-spacing:0.08em;'>explorer</div>")
            gr.HTML("""
            <div style='color:#d4d4d4; font-size:12px; line-height:2;'>
                <div style='color:#9cdcfe;'> code-debugger</div>
                <div style='padding-left:16px; color:#858585;'> dataset.py</div>
                <div style='padding-left:16px; color:#858585;'> train_lora.py</div>
                <div style='padding-left:16px; color:#858585;'> inference.py</div>
                <div style='padding-left:16px; color:#858585;'> groq_fixer.py</div>
                <div style='padding-left:16px; color:#4ec9b0;'> pipeline.py</div>
                <div style='padding-left:16px; color:#ce9178;'> app.py </div>
            </div>
            """)

        with gr.Column(scale=4):
            gr.HTML("<div style='color:#858585; font-size:11px; padding:8px 0;'>buggy_code.py  ×</div>")
            code_input = gr.Code(
                language="python",
                label="",
                value="# Paste your buggy Python code here\n",
                lines=12,
            )
            with gr.Row():
                debug_btn = gr.Button("▶  Debug", variant="primary")
                clear_btn = gr.Button("⟳  Clear", variant="secondary")

            gr.Examples(
                examples=[[e] for e in EXAMPLES],
                inputs=code_input,
                label="examples",
            )

        with gr.Column(scale=4):
            gr.HTML("<div style='color:#858585; font-size:11px; padding:8px 0;'>output</div>")

            classification_out = gr.HTML(
                value="<div style='color:#858585; font-size:12px; padding:16px;'>// Run the debugger to see results</div>"
            )

            with gr.Tabs():
                with gr.Tab("fixed_code.py"):
                    fixed_out = gr.Code(language="python", label="", lines=10)

                with gr.Tab("diff.py"):
                    diff_out = gr.Code(language=None, label="", lines=10)

                with gr.Tab("similar_bugs.py"):
                    similar_out = gr.Code(language="python", label="", lines=10)

                with gr.Tab("attention.png"):
                    attn_out = gr.Plot(label="")

    debug_btn.click(
        fn=run_debug,
        inputs=code_input,
        outputs=[classification_out, fixed_out, diff_out, similar_out, attn_out],
    )
    clear_btn.click(
        fn=lambda: ("# Paste your buggy Python code here\n", "", "", "", None,
                    "<div style='color:#858585; font-size:12px; padding:16px;'>// Run the debugger to see results</div>"),
        outputs=[code_input, fixed_out, diff_out, similar_out, attn_out, classification_out],
    )

demo.launch(share=True, debug=True)
