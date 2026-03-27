import json
import os
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

from ocr import collect_images, get_output_path, ocr_image, process_folder, trash_old_files


# --- collect_images ---

def test_collect_images_returns_image_files(tmp_path):
    (tmp_path / "a.jpg").touch()
    (tmp_path / "b.JPEG").touch()
    (tmp_path / "c.png").touch()
    (tmp_path / "d.TIFF").touch()
    (tmp_path / "e.pdf").touch()    # 除外
    (tmp_path / "f.txt").touch()    # 除外
    sub = tmp_path / "sub"
    sub.mkdir()
    (sub / "g.jpg").touch()         # サブフォルダ除外

    result = collect_images(tmp_path)
    names = {p.name for p in result}
    assert names == {"a.jpg", "b.JPEG", "c.png", "d.TIFF"}


def test_collect_images_empty_folder(tmp_path):
    result = collect_images(tmp_path)
    assert result == []


# --- get_output_path ---

def test_get_output_path_returns_txt(tmp_path):
    image = tmp_path / "photo.jpg"
    output_dir = tmp_path / "output"
    result = get_output_path(image, output_dir)
    assert result == output_dir / "photo.txt"


def test_get_output_path_preserves_stem_case(tmp_path):
    image = tmp_path / "MyImage.PNG"
    output_dir = tmp_path / "output"
    result = get_output_path(image, output_dir)
    assert result == output_dir / "MyImage.txt"


# --- ocr_image ---

def test_ocr_image_returns_text(tmp_path):
    image_path = tmp_path / "photo.jpg"
    image_path.write_bytes(b"fake image content")

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.full_text_annotation.text = "認識されたテキスト"
    mock_client.document_text_detection.return_value = mock_response

    result = ocr_image(image_path, mock_client)
    assert result == "認識されたテキスト"


def test_ocr_image_returns_empty_string_when_no_text(tmp_path):
    image_path = tmp_path / "blank.jpg"
    image_path.write_bytes(b"fake image content")

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.full_text_annotation.text = None  # Vision API が None を返すケース
    mock_client.document_text_detection.return_value = mock_response

    result = ocr_image(image_path, mock_client)
    assert result == ""


# --- trash_old_files ---

def test_trash_old_files_sends_old_files_to_trash(tmp_path):
    processed = tmp_path / "processed"
    processed.mkdir()
    old_file = processed / "old.jpg"
    old_file.write_bytes(b"fake")
    old_time = time.time() - 4 * 86400  # 4日前
    os.utime(old_file, (old_time, old_time))

    with patch("ocr.send2trash") as mock_trash:
        count = trash_old_files(processed)

    mock_trash.assert_called_once_with(str(old_file))
    assert count == 1


def test_trash_old_files_keeps_recent_files(tmp_path):
    processed = tmp_path / "processed"
    processed.mkdir()
    new_file = processed / "new.jpg"
    new_file.write_bytes(b"fake")

    with patch("ocr.send2trash") as mock_trash:
        count = trash_old_files(processed)

    mock_trash.assert_not_called()
    assert count == 0


def test_trash_old_files_nonexistent_dir_returns_zero(tmp_path):
    with patch("ocr.send2trash") as mock_trash:
        count = trash_old_files(tmp_path / "nonexistent")

    mock_trash.assert_not_called()
    assert count == 0


def test_trash_old_files_continues_after_send2trash_failure(tmp_path, capsys):
    processed = tmp_path / "processed"
    processed.mkdir()
    old_file = processed / "old.jpg"
    old_file.write_bytes(b"fake")
    old_time = time.time() - 4 * 86400
    os.utime(old_file, (old_time, old_time))

    with patch("ocr.send2trash", side_effect=OSError("trash failed")):
        count = trash_old_files(processed)

    captured = capsys.readouterr()
    assert "[WARN]" in captured.out
    assert count == 0  # 失敗したので0件


# --- process_folder ---

def _make_dirs(tmp_path):
    input_dir = tmp_path / "input"
    input_dir.mkdir()
    output_dir = tmp_path / "output"
    processed_dir = input_dir / "processed"
    return input_dir, output_dir, processed_dir


def test_process_folder_creates_output_file(tmp_path):
    input_dir, output_dir, processed_dir = _make_dirs(tmp_path)
    img = input_dir / "test.jpg"
    img.write_bytes(b"fake")

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.full_text_annotation.text = "Hello"
    mock_client.document_text_detection.return_value = mock_response

    with patch("ocr.vision.ImageAnnotatorClient", return_value=mock_client), \
         patch("ocr.trash_old_files", return_value=0):
        counts = process_folder(input_dir, output_dir, processed_dir)

    output = output_dir / "test.txt"
    assert output.exists()
    assert output.read_text(encoding="utf-8") == "Hello"
    assert (processed_dir / "test.jpg").exists()
    assert not img.exists()
    assert counts == {"ok": 1, "skip": 0, "err": 0, "trash": 0}


def test_process_folder_creates_empty_txt_when_no_text(tmp_path):
    input_dir, output_dir, processed_dir = _make_dirs(tmp_path)
    img = input_dir / "blank.jpg"
    img.write_bytes(b"fake")

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.full_text_annotation.text = None
    mock_client.document_text_detection.return_value = mock_response

    with patch("ocr.vision.ImageAnnotatorClient", return_value=mock_client), \
         patch("ocr.trash_old_files", return_value=0):
        counts = process_folder(input_dir, output_dir, processed_dir)

    output = output_dir / "blank.txt"
    assert output.exists()
    assert output.read_text(encoding="utf-8") == ""
    assert counts == {"ok": 1, "skip": 0, "err": 0, "trash": 0}


def test_process_folder_skips_existing_output(tmp_path):
    input_dir, output_dir, processed_dir = _make_dirs(tmp_path)
    img = input_dir / "test.jpg"
    img.write_bytes(b"fake")
    output_dir.mkdir()
    (output_dir / "test.txt").write_text("existing", encoding="utf-8")

    mock_client = MagicMock()
    with patch("ocr.vision.ImageAnnotatorClient", return_value=mock_client), \
         patch("ocr.trash_old_files", return_value=0):
        counts = process_folder(input_dir, output_dir, processed_dir)

    assert mock_client.document_text_detection.call_count == 0
    assert counts == {"ok": 0, "skip": 1, "err": 0, "trash": 0}


def test_process_folder_skips_and_moves_to_processed(tmp_path):
    input_dir, output_dir, processed_dir = _make_dirs(tmp_path)
    img = input_dir / "test.jpg"
    img.write_bytes(b"fake")
    output_dir.mkdir()
    (output_dir / "test.txt").write_text("existing", encoding="utf-8")

    with patch("ocr.vision.ImageAnnotatorClient", return_value=MagicMock()), \
         patch("ocr.trash_old_files", return_value=0):
        counts = process_folder(input_dir, output_dir, processed_dir)

    assert not img.exists()
    assert (processed_dir / "test.jpg").exists()
    assert counts == {"ok": 0, "skip": 1, "err": 0, "trash": 0}


def test_process_folder_no_images(tmp_path, capsys):
    input_dir, output_dir, processed_dir = _make_dirs(tmp_path)

    with patch("ocr.trash_old_files", return_value=0):
        counts = process_folder(input_dir, output_dir, processed_dir)

    captured = capsys.readouterr()
    assert "対象ファイルが見つかりませんでした" in captured.out
    assert counts == {"ok": 0, "skip": 0, "err": 0, "trash": 0}


def test_process_folder_handles_api_error(tmp_path, capsys):
    input_dir, output_dir, processed_dir = _make_dirs(tmp_path)
    img = input_dir / "broken.jpg"
    img.write_bytes(b"fake")

    mock_client = MagicMock()
    mock_client.document_text_detection.side_effect = Exception("API error")

    with patch("ocr.vision.ImageAnnotatorClient", return_value=mock_client), \
         patch("ocr.trash_old_files", return_value=0):
        counts = process_folder(input_dir, output_dir, processed_dir)

    captured = capsys.readouterr()
    assert "[ERR]" in captured.out
    assert counts == {"ok": 0, "skip": 0, "err": 1, "trash": 0}


def test_process_folder_move_failure_rolls_back_txt(tmp_path):
    input_dir, output_dir, processed_dir = _make_dirs(tmp_path)
    img = input_dir / "test.jpg"
    img.write_bytes(b"fake")

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.full_text_annotation.text = "Hello"
    mock_client.document_text_detection.return_value = mock_response

    with patch("ocr.vision.ImageAnnotatorClient", return_value=mock_client), \
         patch("ocr.trash_old_files", return_value=0), \
         patch("pathlib.Path.rename", side_effect=OSError("permission denied")):
        counts = process_folder(input_dir, output_dir, processed_dir)

    assert not (output_dir / "test.txt").exists()
    assert img.exists()
    assert counts == {"ok": 0, "skip": 0, "err": 1, "trash": 0}


def test_process_folder_includes_trash_count(tmp_path):
    input_dir, output_dir, processed_dir = _make_dirs(tmp_path)

    with patch("ocr.trash_old_files", return_value=3):
        counts = process_folder(input_dir, output_dir, processed_dir)

    assert counts["trash"] == 3


def test_process_folder_receipt_mode_creates_json(tmp_path):
    input_dir, output_dir, processed_dir = _make_dirs(tmp_path)
    img = input_dir / "receipt.jpg"
    img.write_bytes(b"fake")

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.full_text_annotation.text = "店名 合計500"
    mock_client.document_text_detection.return_value = mock_response

    receipt_data = {"store": "テスト店", "date": "2024-01-01", "items": [], "total": 500}

    with patch("ocr.vision.ImageAnnotatorClient", return_value=mock_client), \
         patch("ocr.trash_old_files", return_value=0), \
         patch("ocr.parse_receipt", return_value=receipt_data):
        counts = process_folder(input_dir, output_dir, processed_dir, mode="receipt")

    output = output_dir / "receipt.json"
    assert output.exists()
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["store"] == "テスト店"
    assert data["total"] == 500
    assert (processed_dir / "receipt.jpg").exists()
    assert counts == {"ok": 1, "skip": 0, "err": 0, "trash": 0}


def test_process_folder_receipt_mode_parse_error_rolls_back(tmp_path):
    input_dir, output_dir, processed_dir = _make_dirs(tmp_path)
    img = input_dir / "receipt.jpg"
    img.write_bytes(b"fake")

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.full_text_annotation.text = "不明なテキスト"
    mock_client.document_text_detection.return_value = mock_response

    with patch("ocr.vision.ImageAnnotatorClient", return_value=mock_client), \
         patch("ocr.trash_old_files", return_value=0), \
         patch("ocr.parse_receipt", side_effect=ValueError("JSONが見つかりませんでした")):
        counts = process_folder(input_dir, output_dir, processed_dir, mode="receipt")

    assert not (output_dir / "receipt.json").exists()
    assert img.exists()  # 画像はinputに残る
    assert counts == {"ok": 0, "skip": 0, "err": 1, "trash": 0}
