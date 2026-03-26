import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from ocr import collect_images, get_output_path, ocr_image, process_folder


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


# --- process_folder ---

def test_process_folder_creates_output_file(tmp_path):
    img = tmp_path / "test.jpg"
    img.write_bytes(b"fake")

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.full_text_annotation.text = "Hello"
    mock_client.document_text_detection.return_value = mock_response

    with patch("ocr.vision.ImageAnnotatorClient", return_value=mock_client):
        counts = process_folder(tmp_path)

    output = tmp_path / "output" / "test.txt"
    assert output.exists()
    assert output.read_text(encoding="utf-8") == "Hello"
    assert counts == {"ok": 1, "skip": 0, "err": 0}


def test_process_folder_creates_empty_txt_when_no_text(tmp_path):
    img = tmp_path / "blank.jpg"
    img.write_bytes(b"fake")

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.full_text_annotation.text = None
    mock_client.document_text_detection.return_value = mock_response

    with patch("ocr.vision.ImageAnnotatorClient", return_value=mock_client):
        counts = process_folder(tmp_path)

    output = tmp_path / "output" / "blank.txt"
    assert output.exists()
    assert output.read_text(encoding="utf-8") == ""
    assert counts == {"ok": 1, "skip": 0, "err": 0}


def test_process_folder_skips_existing_output(tmp_path):
    img = tmp_path / "test.jpg"
    img.write_bytes(b"fake")
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    (output_dir / "test.txt").write_text("existing", encoding="utf-8")

    mock_client = MagicMock()
    with patch("ocr.vision.ImageAnnotatorClient", return_value=mock_client):
        counts = process_folder(tmp_path)

    assert mock_client.document_text_detection.call_count == 0
    assert counts == {"ok": 0, "skip": 1, "err": 0}


def test_process_folder_no_images(tmp_path, capsys):
    with patch("ocr.vision.ImageAnnotatorClient", return_value=MagicMock()):
        counts = process_folder(tmp_path)

    captured = capsys.readouterr()
    assert "対象ファイルが見つかりませんでした" in captured.out
    assert counts == {"ok": 0, "skip": 0, "err": 0}


def test_process_folder_handles_api_error(tmp_path, capsys):
    img = tmp_path / "broken.jpg"
    img.write_bytes(b"fake")

    mock_client = MagicMock()
    mock_client.document_text_detection.side_effect = Exception("API error")

    with patch("ocr.vision.ImageAnnotatorClient", return_value=mock_client):
        counts = process_folder(tmp_path)

    captured = capsys.readouterr()
    assert "[ERR]" in captured.out
    assert counts == {"ok": 0, "skip": 0, "err": 1}
