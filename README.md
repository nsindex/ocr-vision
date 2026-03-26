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
