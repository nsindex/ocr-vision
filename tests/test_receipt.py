import json
import urllib.error
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from parser.receipt import _extract_json, _validate_receipt, parse_receipt


# --- _extract_json ---

def test_extract_json_parses_plain_json():
    text = '{"store": "セブン", "date": "2024-01-01", "items": [], "total": 0}'
    result = _extract_json(text)
    assert result["store"] == "セブン"
    assert result["total"] == 0


def test_extract_json_strips_surrounding_text():
    text = 'はい、こちらがJSON結果です。\n{"store": "ローソン", "date": "2024-03-01", "items": [{"name": "コーヒー", "qty": 1, "price": 150}], "total": 150}\n以上です。'
    result = _extract_json(text)
    assert result["store"] == "ローソン"
    assert result["total"] == 150
    assert len(result["items"]) == 1


def test_extract_json_raises_on_no_json():
    with pytest.raises(ValueError, match="JSONが見つかりませんでした"):
        _extract_json("JSONなしのテキストです。")


def test_extract_json_raises_on_invalid_json():
    with pytest.raises(ValueError, match="JSONが見つかりませんでした"):
        _extract_json("{invalid json here}")


def test_extract_json_handles_braces_in_surrounding_text():
    # 説明文中に不完全な {} が含まれても本体JSONを正しく抽出できる
    text = 'フォーマット例: {store必須} 実際の結果: {"store": "イオン", "date": "2024-02-01", "items": [], "total": 500}'
    result = _extract_json(text)
    assert result["store"] == "イオン"
    assert result["total"] == 500


# --- parse_receipt ---

def _make_ollama_response(response_text: str) -> MagicMock:
    body = json.dumps({"response": response_text}).encode("utf-8")
    mock_resp = MagicMock()
    mock_resp.read.return_value = body
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)
    return mock_resp


def test_parse_receipt_returns_dict_with_expected_keys():
    json_body = '{"store": "マルエツ", "date": "2024-06-15", "items": [{"name": "牛乳", "qty": 1, "price": 198}], "total": 198}'
    mock_resp = _make_ollama_response(json_body)

    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = parse_receipt("牛乳 198\n合計 198")

    assert result["store"] == "マルエツ"
    assert result["date"] == "2024-06-15"
    assert isinstance(result["items"], list)
    assert result["total"] == 198


def test_parse_receipt_raises_on_connection_error():
    with patch("urllib.request.urlopen", side_effect=urllib.error.URLError("connection refused")):
        with pytest.raises(urllib.error.URLError):
            parse_receipt("テスト")


def test_parse_receipt_raises_on_invalid_response():
    mock_resp = _make_ollama_response("すみません、JSONに変換できませんでした。")

    with patch("urllib.request.urlopen", return_value=mock_resp):
        with pytest.raises(ValueError, match="JSONが見つかりませんでした"):
            parse_receipt("不明なテキスト")


def test_parse_receipt_handles_json_with_extra_text():
    json_body = 'もちろんです！\n{"store": "ファミマ", "date": "2024-07-01", "items": [{"name": "おにぎり", "qty": 2, "price": 130}], "total": 260}\n'
    mock_resp = _make_ollama_response(json_body)

    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = parse_receipt("おにぎり x2 260")

    assert result["store"] == "ファミマ"
    assert result["total"] == 260


def test_parse_receipt_sends_configured_model():
    json_body = '{"store":"X","date":"2024-01-01","items":[],"total":0}'
    mock_resp = _make_ollama_response(json_body)

    with patch("urllib.request.urlopen", return_value=mock_resp) as mock_urlopen:
        parse_receipt("テスト")

    req = mock_urlopen.call_args.args[0]
    payload = json.loads(req.data.decode("utf-8"))
    assert payload["model"] == "gemma3:4b"


# --- _validate_receipt ---

def test_validate_receipt_raises_on_missing_keys():
    with pytest.raises(ValueError, match="必須キー不足"):
        _validate_receipt({"store": "テスト"})  # date/items/total 欠落


def test_validate_receipt_raises_when_items_not_list():
    with pytest.raises(ValueError, match="items は配列"):
        _validate_receipt({"store": "X", "date": "2024-01-01", "items": "品物", "total": 100})


def test_validate_receipt_passes_valid_data():
    data = {"store": "X", "date": "2024-01-01", "items": [], "total": 0}
    assert _validate_receipt(data) is data
