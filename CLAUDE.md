# ocr-vision プロジェクトルール

## プロジェクト概要

Google Cloud Vision API を使って、`input/` フォルダ内の画像を一括OCR処理するCLIツール。
対応形式：JPG/JPEG/PNG/TIFF。出力はプロジェクトルート直下の `output/` フォルダに .txt で保存する。
OCR済み画像は `input/processed/` に移動し、3日以上前のファイルはゴミ箱に送る。

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
- 入力元：プロジェクトルート直下の `input/`（固定）
- 出力先：プロジェクトルート直下の `output/`（固定、変更不可）
- 移動先：`input/processed/`（OCR済み画像）
- ゴミ箱対象：`input/processed/` 内の更新日時が3日以上前のファイル

---

## 開発ルール

- `ocr.py` を変更したら `pytest tests/` で確認する
- Vision API の実呼び出しは手動テストで確認する
- `.env` は絶対にコミットしない

---

## 注意事項

- 仮想環境を有効化してから実行する：`source .venv/Scripts/activate`
- 認証：`GOOGLE_APPLICATION_CREDENTIALS` にサービスアカウントJSONのパスを設定する
