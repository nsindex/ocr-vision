# OCR Vision Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Google Cloud Vision API を使って、フォルダ内の画像を一括OCR処理し、画像1枚につき1つのテキストファイルに出力するCLIツールを実装する。

**Architecture:** 単一スクリプト `ocr.py` に全処理をまとめる。テスト可能にするため、コアロジックは独立した関数として定義し、`tests/test_ocr.py` でモックを使ってテストする。

**Tech Stack:** Python 3.10, google-cloud-vision, python-dotenv, pytest

---

## File Map

プロジェクトルート: `C:\AI_DEV\projects-B\ocr-vision\`

| ファイル | 役割 |
|---------|------|
| `C:\AI_DEV\projects-B\ocr-vision\ocr.py` | メインスクリプト（collect_images / get_output_path / ocr_image / process_folder / main） |
| `C:\AI_DEV\projects-B\ocr-vision\tests\__init__.py` | テストパッケージ初期化 |
| `C:\AI_DEV\projects-B\ocr-vision\tests\test_ocr.py` | pytest テスト（Vision API はモック化） |
| `C:\AI_DEV\projects-B\ocr-vision\requirements.txt` | 依存パッケージ |
| `C:\AI_DEV\projects-B\ocr-vision\.gitignore` | git除外設定 |
| `C:\AI_DEV\projects-B\ocr-vision\.env` | 認証情報（コミット禁止） |
| `C:\AI_DEV\projects-B\ocr-vision\.env.example` | キー名のみ（コミット可） |
| `C:\AI_DEV\projects-B\ocr-vision\CLAUDE.md` | プロジェクト固有ルール |
| `C:\AI_DEV\projects-B\ocr-vision\README.md` | プロジェクト概要・起動手順 |
| `C:\AI_DEV\projects-B\ocr-vision\docs\PROGRESS.md` | 進捗管理 |
| `C:\AI_DEV\projects-B\ocr-vision\docs\ARCHITECTURE.md` | アーキテクチャ説明 |
| `C:\AI_DEV\projects-B\ocr-vision\docs\DECISIONS.md` | 設計判断の記録 |
| `C:\AI_DEV\projects-B\ocr-vision\docs\AGENTS.md` | AI実装統制ルール |
| `C:\AI_DEV\projects-B\ocr-vision\docs\TASK_PLAN.md` | タスク管理 |
| `C:\AI_DEV\projects-B\ocr-vision\docs\PROJECT_CONTEXT.md` | プロジェクト概要 |
| `C:\AI_DEV\projects-B\ocr-vision\.claude\settings.json` | lint Hook（flake8 + black） |

---

## Task 1: プロジェクトスキャフォールディング

**Files:**
- Create: `C:\AI_DEV\projects-B\ocr-vision\.gitignore`
- Create: `C:\AI_DEV\projects-B\ocr-vision\.env.example`
- Create: `C:\AI_DEV\projects-B\ocr-vision\.env`（gitignore対象）
- Create: `C:\AI_DEV\projects-B\ocr-vision\requirements.txt`
- Create: `C:\AI_DEV\projects-B\ocr-vision\.claude\settings.json`

- [ ] **Step 1: git init**

```bash
cd C:\AI_DEV\projects-B\ocr-vision
git init
```

Expected: `Initialized empty Git repository`

- [ ] **Step 2: .gitignore を作成**

`C:\AI_DEV\projects-B\ocr-vision\.gitignore`:
```
# Python
.venv/
__pycache__/
*.pyc
*.egg-info/
.pytest_cache/

# シークレット
.env
.env.*
credentials.json
service-account.json
*.pem
*.key

# 出力
output/

# テスト用サンプル
sample_images/

# エディタ
.vscode/
.idea/

# OS
Thumbs.db
Desktop.ini
```

- [ ] **Step 3: .env.example を作成**

`C:\AI_DEV\projects-B\ocr-vision\.env.example`:
```
GOOGLE_APPLICATION_CREDENTIALS=path/to/your-service-account.json
```

- [ ] **Step 4: .env を作成（実際のパスを記入）**

`C:\AI_DEV\projects-B\ocr-vision\.env`:
```
GOOGLE_APPLICATION_CREDENTIALS=C:/path/to/your-service-account.json
```

- [ ] **Step 5: requirements.txt を作成**

`C:\AI_DEV\projects-B\ocr-vision\requirements.txt`:
```
google-cloud-vision==3.7.2
python-dotenv==1.0.1
pytest==8.3.4
```

- [ ] **Step 6: .claude/settings.json を作成**

`C:\AI_DEV\projects-B\ocr-vision\.claude\settings.json`:
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python \"C:/AI_DEV/.claude/hooks/run-lint.py\""
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 7: Python 仮想環境を作成・有効化・依存インストール**

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

Expected: 依存パッケージが正常にインストールされる

- [ ] **Step 8: 初回コミット**

```bash
git add .gitignore .env.example requirements.txt .claude/settings.json
git commit -m "chore: initial project scaffolding"
```

---

## Task 2: ドキュメントファイル作成

**Files:**
- Create: `C:\AI_DEV\projects-B\ocr-vision\CLAUDE.md`
- Create: `C:\AI_DEV\projects-B\ocr-vision\README.md`
- Create: `C:\AI_DEV\projects-B\ocr-vision\docs\PROGRESS.md`
- Create: `C:\AI_DEV\projects-B\ocr-vision\docs\ARCHITECTURE.md`
- Create: `C:\AI_DEV\projects-B\ocr-vision\docs\DECISIONS.md`
- Create: `C:\AI_DEV\projects-B\ocr-vision\docs\AGENTS.md`
- Create: `C:\AI_DEV\projects-B\ocr-vision\docs\TASK_PLAN.md`
- Create: `C:\AI_DEV\projects-B\ocr-vision\docs\PROJECT_CONTEXT.md`

- [ ] **Step 1: CLAUDE.md を作成**

`C:\AI_DEV\projects-B\ocr-vision\CLAUDE.md`:
```markdown
# ocr-vision プロジェクトルール

## プロジェクト概要

Google Cloud Vision API を使って、フォルダ内の画像を一括OCR処理するCLIツール。
対応形式：JPG/JPEG/PNG/TIFF。出力は入力フォルダ直下の output/ フォルダに .txt で保存する。

---

## 技術スタック

- 言語：Python 3.10
- 主要ライブラリ：google-cloud-vision, python-dotenv
- 外部サービス：Google Cloud Vision API

---

## ファイル構成と役割

- `ocr.py`：メインスクリプト（全処理）
- `tests/test_ocr.py`：pytest テスト
- `requirements.txt`：依存パッケージ
- `.env`：認証情報（gitignore対象）

---

## プロジェクト固有の設定

- `GOOGLE_APPLICATION_CREDENTIALS`：サービスアカウントJSONのパス（.envで管理）
- 出力先：入力フォルダ直下の `output/`（固定、変更不可）

---

## 開発ルール

- `ocr.py` を変更したら `pytest tests/` で確認する
- Vision API の実呼び出しは手動テストで確認する
- `.env` は絶対にコミットしない

---

## 注意事項

- 仮想環境を有効化してから実行する：`source .venv/Scripts/activate`
- 認証：`GOOGLE_APPLICATION_CREDENTIALS` にサービスアカウントJSONのパスを設定する
```

- [ ] **Step 2: README.md を作成**

`C:\AI_DEV\projects-B\ocr-vision\README.md`:
```markdown
# ocr-vision

Google Cloud Vision API を使って、フォルダ内の画像を一括OCR処理し、テキストファイルに出力するCLIツール。

---

## 1. プロジェクト概要

- 入力フォルダ内の JPG/JPEG/PNG/TIFF を検出
- Google Cloud Vision API（DOCUMENT_TEXT_DETECTION）でOCR処理
- 入力フォルダ直下の `output/` に `<画像名>.txt` として保存

---

## 2. 必要環境

- Python 3.10
- Google Cloud サービスアカウント（Vision API 有効化済み）

---

## 3. インストール方法

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 4. 設定

`.env.example` をコピーして `.env` を作成し、サービスアカウントJSONのパスを設定する。

```bash
cp .env.example .env
# .env を編集して実際のパスを記入
```

---

## 5. 使い方

```bash
python ocr.py <画像フォルダのパス>
```

**実行例：**

```
[OK]   photo1.jpg -> output/photo1.txt
[SKIP] output/photo2.txt already exists
[ERR]  photo3.png: API error - ...
完了: 処理1件 / スキップ1件 / エラー1件
```

---

## 6. ディレクトリ構成

```
ocr-vision/
├── ocr.py
├── requirements.txt
├── .env.example
├── tests/
│   └── test_ocr.py
└── output/           # 自動作成（gitignore対象）
```

---

## 7. 注意事項

- `.env` は Git にコミットしない
- `output/` フォルダも Git に含まれない
```

- [ ] **Step 3: docs/ 配下のファイルを作成**

`C:\AI_DEV\projects-B\ocr-vision\docs\PROGRESS.md`:
```markdown
# 進捗管理

## 完了済み
- プロジェクトセットアップ
- ドキュメント作成

## 進行中
- ocr.py 実装

## 次にやること
- 手動テスト
```

`C:\AI_DEV\projects-B\ocr-vision\docs\ARCHITECTURE.md`:
```markdown
# アーキテクチャ

## 構成

単一スクリプト `ocr.py` に全処理をまとめる。

## 処理フロー

1. argparse でフォルダパス受取
2. .env 読み込み・認証確認
3. output/ フォルダ作成
4. 対象画像ファイルを列挙
5. 各ファイルをOCR処理（スキップ/OK/ERR）
6. サマリー表示

## 主要関数

- `collect_images(folder)` - 対象ファイル列挙
- `get_output_path(image_path, output_dir)` - 出力パス計算
- `ocr_image(image_path, client)` - OCR実行（None対策で or "" を使用）
- `process_folder(folder_path)` - 全体オーケストレーション
- `main()` - CLI エントリポイント
```

`C:\AI_DEV\projects-B\ocr-vision\docs\DECISIONS.md`:
```markdown
# 設計判断

## 2026-03-26: 単一スクリプト構成を採用
- 理由: 単一目的の小規模CLIツールのため、分割不要
- 代替案: モジュール分割（却下：過剰）

## 2026-03-26: PDFを対象外とした
- 理由: Vision API の PDF 処理は GCS バケットが必要で複雑
- 対応形式: JPG/JPEG/PNG/TIFF のみ

## 2026-03-26: output/ は入力フォルダ直下に固定
- 理由: シンプルさ優先。オプション追加は YAGNI

## 2026-03-26: ocr_image は `text or ""` で None ガード
- 理由: Vision API はテキスト未検出時 full_text_annotation.text が None を返す場合がある
```

`C:\AI_DEV\projects-B\ocr-vision\docs\AGENTS.md`:
```markdown
# AI実装統制ルール

## Claude Code の役割
- 実装・修正・git操作

## Codex の役割
- コードレビュー・設計相談（300行超または複数ファイル横断）

## 禁止事項
- .env のコミット
- グローバル pip install
```

`C:\AI_DEV\projects-B\ocr-vision\docs\TASK_PLAN.md`:
```markdown
# タスク計画

## フェーズ1: セットアップ（完了）
- [x] git init
- [x] .gitignore / .env / .env.example
- [x] requirements.txt / .venv

## フェーズ2: 実装
- [ ] ocr.py（TDD）
- [ ] 手動動作確認
```

`C:\AI_DEV\projects-B\ocr-vision\docs\PROJECT_CONTEXT.md`:
```markdown
# プロジェクト概要

## 目的
画像フォルダを引数に受け取り、Google Cloud Vision API でOCR処理して
テキストファイルに出力するCLIツール。

## 設計方針
- シンプル・単一スクリプト
- TDD（pytestでモックテスト）
- YAGNI（オプション機能は追加しない）

## 制約
- Python 3.10
- Vision API: DOCUMENT_TEXT_DETECTION
- 対応形式: JPG/JPEG/PNG/TIFF
```

- [ ] **Step 4: コミット**

```bash
git add CLAUDE.md README.md docs/
git commit -m "docs: add project documentation"
```

---

## Task 3: コアロジック TDD (collect_images / get_output_path)

**Files:**
- Create: `C:\AI_DEV\projects-B\ocr-vision\tests\__init__.py`
- Create: `C:\AI_DEV\projects-B\ocr-vision\tests\test_ocr.py`
- Create: `C:\AI_DEV\projects-B\ocr-vision\ocr.py`（純粋関数部分のみ）

- [ ] **Step 1: tests/__init__.py を作成（空ファイル）**

`C:\AI_DEV\projects-B\ocr-vision\tests\__init__.py` を空ファイルで作成する。

- [ ] **Step 2: テストを書く**

`C:\AI_DEV\projects-B\ocr-vision\tests\test_ocr.py`:
```python
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
```

- [ ] **Step 3: テストが失敗することを確認**

```bash
pytest tests/test_ocr.py -v
```

Expected: `ModuleNotFoundError: No module named 'ocr'`

- [ ] **Step 4: ocr.py を実装**

`C:\AI_DEV\projects-B\ocr-vision\ocr.py`:
```python
import argparse
import os
import sys
from pathlib import Path

import google.cloud.vision as vision
from dotenv import load_dotenv

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff"}


def collect_images(folder: Path) -> list:
    result = []
    for f in folder.iterdir():
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
            result.append(f)
    return sorted(result)


def get_output_path(image_path: Path, output_dir: Path) -> Path:
    return output_dir / (image_path.stem + ".txt")


def ocr_image(image_path: Path, client) -> str:
    with open(image_path, "rb") as f:
        content = f.read()
    image = vision.Image(content=content)
    image_context = vision.ImageContext(language_hints=["ja", "en"])
    response = client.document_text_detection(image=image, image_context=image_context)
    return response.full_text_annotation.text or ""


def process_folder(folder_path: Path) -> dict:
    output_dir = folder_path / "output"
    output_dir.mkdir(exist_ok=True)

    images = collect_images(folder_path)
    counts = {"ok": 0, "skip": 0, "err": 0}

    if not images:
        print("対象ファイルが見つかりませんでした")
        return counts

    client = vision.ImageAnnotatorClient()

    for image_path in images:
        out_path = get_output_path(image_path, output_dir)

        if out_path.exists():
            print(f"[SKIP] output/{out_path.name} already exists")
            counts["skip"] += 1
            continue

        try:
            text = ocr_image(image_path, client)
            out_path.write_text(text, encoding="utf-8")
            print(f"[OK]   {image_path.name} -> output/{out_path.name}")
            counts["ok"] += 1
        except Exception as e:
            print(f"[ERR]  {image_path.name}: {e}")
            counts["err"] += 1

    print(f"完了: 処理{counts['ok']}件 / スキップ{counts['skip']}件 / エラー{counts['err']}件")
    return counts


def main():
    load_dotenv()

    creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds:
        print("エラー: GOOGLE_APPLICATION_CREDENTIALS が設定されていません。.env を確認してください。")
        sys.exit(1)
    if not Path(creds).exists():
        print(f"エラー: 認証ファイルが見つかりません: {creds}")
        sys.exit(1)

    parser = argparse.ArgumentParser(description="Google Cloud Vision API を使った一括OCRツール")
    parser.add_argument("folder", help="処理対象のフォルダパス")
    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.is_dir():
        print(f"エラー: フォルダが見つかりません: {args.folder}")
        sys.exit(1)

    process_folder(folder)


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: 全テストが通ることを確認**

```bash
pytest tests/ -v
```

Expected: 11 passed

- [ ] **Step 6: コミット**

```bash
git add ocr.py tests/
git commit -m "feat: implement OCR CLI with full test coverage"
```

---

## Task 4: 動作確認

- [ ] **Step 1: テスト用の画像フォルダを用意**

`C:\AI_DEV\projects-B\ocr-vision\sample_images\` フォルダを作成し、JPG/PNG ファイルを1〜2枚置く。
（実際の画像ファイルが必要。手動で用意する。sample_images/ は .gitignore 対象）

- [ ] **Step 2: 手動実行**

```bash
source .venv/Scripts/activate
python ocr.py sample_images/
```

Expected:
```
[OK]   photo.jpg -> output/photo.txt
完了: 処理1件 / スキップ0件 / エラー0件
```

- [ ] **Step 3: スキップ動作確認（再実行）**

```bash
python ocr.py sample_images/
```

Expected:
```
[SKIP] output/photo.txt already exists
完了: 処理0件 / スキップ1件 / エラー0件
```

- [ ] **Step 4: エラー系確認**

```bash
python ocr.py nonexistent/
```

Expected: `エラー: フォルダが見つかりません: nonexistent/`

- [ ] **Step 5: 最終コミット**

```bash
git add docs/PROGRESS.md docs/TASK_PLAN.md
git commit -m "chore: update progress docs after implementation"
```
