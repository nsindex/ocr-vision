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
