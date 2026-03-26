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
