import json
import os
import urllib.request
from json import JSONDecodeError, JSONDecoder
from urllib.parse import urlparse

MODEL = os.environ.get("OLLAMA_MODEL", "gemma3:4b").strip() or "gemma3:4b"


def _build_ollama_url() -> str:
    raw = os.environ.get("OLLAMA_URL", "http://localhost:11434").strip() or "http://localhost:11434"
    parsed = urlparse(raw)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("OLLAMA_URL は http(s)://host[:port] 形式で指定してください")
    if parsed.path.rstrip("/") == "/api/generate":
        return raw.rstrip("/")
    return f"{raw.rstrip('/')}/api/generate"

PROMPT_TEMPLATE = """以下はレシートのOCRテキストです。JSON形式で構造化してください。
出力はJSONのみ、余分なテキストなしで返してください。

形式:
{{"store": "店名", "date": "日付", "items": [{{"name": "品名", "qty": 数量, "price": 単価}}], "total": 合計金額}}

品名の正規化ルール:
- 品名の先頭にある税区分コード（例：外8、内10、外8%、内10%）は除去する
- 品名の先頭にある4〜5桁の数字（SKUコード）は除去する
- 除去後に残った品名のみをnameに設定する

数値が読み取れない場合のルール:
- 価格(price)が読み取れない場合は 0 ではなく null にする
- 数量(qty)が読み取れない場合は 1 にする

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
        _build_ollama_url(),
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
