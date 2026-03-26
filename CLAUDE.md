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
