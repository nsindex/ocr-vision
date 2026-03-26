# OCR Vision CLI Tool - Design Spec

Date: 2026-03-26

## Overview

Google Cloud Vision API を使って、フォルダ内の画像を一括OCR処理し、
画像1枚につき1つのテキストファイルに出力するCLIツール。

## Requirements

- 入力：フォルダパスをコマンド引数で指定
- 対応形式：JPG / JPEG / PNG / TIFF（PDFは対象外）
- 出力：画像と同名の .txt ファイル（入力フォルダ直下の output/ に保存）
- OCR言語：日本語・英語の両方
- 処理：フォルダ直下の対象画像を全件一括処理（サブフォルダは非対象）
- API：Google Cloud Vision API（DOCUMENT_TEXT_DETECTION）

## Architecture

### Project Structure

```
ocr-vision/
├── ocr.py              # メインスクリプト（全処理）
├── .env                # GOOGLE_APPLICATION_CREDENTIALS（gitignore対象）
├── .env.example        # キー名のみ（コミット可）
├── requirements.txt
├── .gitignore
└── output/             # 出力先（自動作成、gitignore対象）
```

### Processing Flow

```
引数でフォルダパス受取・存在確認
    → 認証確認（GOOGLE_APPLICATION_CREDENTIALS）
    → <入力フォルダ>/output/ を自動作成
    → フォルダ直下の JPG/JPEG/PNG/TIFF を列挙（大文字小文字両対応、サブフォルダ除く）
    → 対象ファイル0件の場合 → 「対象ファイルが見つかりませんでした」と表示して正常終了
    → 各ファイルについて：
        - output/<同名stem>.txt が存在 → スキップ
        - 存在しない → Vision API で OCR
            - 成功 → output/<同名stem>.txt に書き込み（テキスト0文字でも作成、UTF-8）
            - 失敗 → エラーをコンソールに出力してスキップ
    → 完了サマリー表示（処理数/スキップ数/エラー数）
```

## Implementation Details

### ocr.py

- `argparse` でフォルダパスを受取・存在確認
- `pathlib.Path` で対象ファイルを列挙（glob パターン、サブフォルダなし）
- `output/` は入力フォルダ直下に自動作成（固定・変更不可）
- `google.cloud.vision.ImageAnnotatorClient` で `DOCUMENT_TEXT_DETECTION`
- 認証：`GOOGLE_APPLICATION_CREDENTIALS` 環境変数（`.env` から読込）
  - 未設定または無効な場合 → エラーメッセージを表示して即時終了
- 言語ヒント：`ja` / `en` を両方指定
- 出力ファイル名：元ファイルの stem をそのまま使用（例: `Image.JPG` → `Image.txt`）
- 出力エンコーディング：UTF-8

### Console Output Format

```
[SKIP] output/image1.txt already exists
[OK]   image2.jpg -> output/image2.txt
[ERR]  image3.png: API error - ...
完了: 処理1件 / スキップ1件 / エラー1件
```

## Error Handling

| 状況 | 挙動 |
|------|------|
| フォルダパス不正 | エラーメッセージ表示して即時終了 |
| 認証未設定・無効 | エラーメッセージ表示して即時終了 |
| 対象ファイル0件 | 「対象ファイルが見つかりませんでした」と表示して正常終了 |
| 画像1枚のOCR失敗 | コンソールにエラー出力してスキップ、残りを処理継続 |
| 出力ファイル既存 | スキップ（上書きしない） |
| OCR成功・テキスト0文字 | 空の .txt を作成（正常扱い） |

## Tech Stack

- Python 3.10
- google-cloud-vision
- python-dotenv
