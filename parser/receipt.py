import json
import urllib.error
import urllib.request
from json import JSONDecodeError, JSONDecoder

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "gemma3:4b"

PROMPT_TEMPLATE = """以下はレシートのOCRテキストです。JSON形式で構造化してください。
出力はJSONのみ、余分なテキストなしで返してください。

形式:
{{"store": "店名", "date": "日付", "items": [{{"name": "品名", "qty": 数量, "price": 単価}}], "total": 合計金額}}

レシートテキスト:
{text}
"""


def parse_receipt(text: str) -> dict:
    prompt = PROMPT_TEMPLATE.format(text=text)
    payload = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
    }).encode("utf-8")

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    response_text = result.get("response", "")
    return _validate_receipt(_extract_json(response_text))


def _extract_json(text: str) -> dict:
    decoder = JSONDecoder()
    for i, ch in enumerate(text):
        if ch != "{":
            continue
        try:
            obj, _ = decoder.raw_decode(text[i:])
            if isinstance(obj, dict):
                return obj
        except JSONDecodeError:
            continue
    raise ValueError(f"JSONが見つかりませんでした: {text[:100]}")


def _validate_receipt(data: dict) -> dict:
    required = {"store", "date", "items", "total"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"必須キー不足: {sorted(missing)}")
    if not isinstance(data["items"], list):
        raise ValueError("items は配列である必要があります")
    return data
