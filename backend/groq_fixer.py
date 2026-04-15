import os, re, difflib
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY", ""))

SYSTEM_PROMPT = """You are an expert Python debugger. Respond in EXACTLY this format:

## Explanation
2-3 sentences describing the bug, why it happens, and which line causes it.

## Fixed Code
```python
<complete corrected code here>
```

Rules:
- Always return the FULL corrected code not just the changed lines
- If multiple bugs exist list all of them in Explanation
- Never add new features beyond fixing the bugs
- Always mention the line number where the bug occurs"""


def fix_with_groq(code: str, error_label: str) -> dict:
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Bug type already classified as: {error_label}\n\n"
                        f"Debug this Python code:\n```python\n{code}\n```"
                    ),
                },
            ],
            temperature=0.1,
            max_tokens=1024,
        )
        raw = response.choices[0].message.content
        return {
            "explanation": _extract_section(raw, "## Explanation"),
            "fixed_code": _extract_code_block(raw),
            "raw": raw,
        }
    except Exception as e:
        return {
            "explanation": f"Groq error: {str(e)}",
            "fixed_code": code,
            "raw": "",
        }


def generate_diff(original: str, fixed: str) -> str:
    if not fixed:
        return ""
    diff = difflib.unified_diff(
        original.splitlines(keepends=True),
        fixed.splitlines(keepends=True),
        fromfile="buggy.py",
        tofile="fixed.py",
        lineterm="",
    )
    return "\n".join(list(diff))


def _extract_section(text: str, header: str) -> str:
    lines = text.split("\n")
    capturing, result = False, []
    for line in lines:
        if line.strip() == header:
            capturing = True
            continue
        if capturing and line.startswith("## "):
            break
        if capturing:
            result.append(line)
    return "\n".join(result).strip()


def _extract_code_block(text: str) -> str:
    match = re.search(r"```python\n(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else ""
