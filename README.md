# ocr-vision

Google Cloud Vision API を使って、フォルダ内の画像を一括OCR処理し、テキストファイルに出力するCLIツール。

---

## 1. プロジェクト概要

- `input/` フォルダ内の JPG/JPEG/PNG/TIFF を検出
- Google Cloud Vision API（DOCUMENT_TEXT_DETECTION）でOCR処理
- `output/` に `<画像名>.txt` として保存
- OCR済み画像は `input/processed/` に移動
- `input/processed/` 内の3日以上前のファイルは自動でゴミ箱に送る

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

処理したい画像を `input/` フォルダに置いてから実行する。

```bash
python ocr.py
```

**実行例：**

```
[OK]   photo1.jpg -> output/photo1.txt
[SKIP] photo2.txt already exists
[ERR]  photo3.png: API error - ...
完了: 処理1件 / スキップ1件 / エラー1件 / ゴミ箱2件
```

---

## 6. ディレクトリ構成

```
ocr-vision/
├── ocr.py
├── requirements.txt
├── .env.example
├── input/                  # 処理対象画像を置く
│   └── processed/          # OCR済み画像（自動移動）
├── output/                 # OCR結果テキスト（自動作成）
└── tests/
    └── test_ocr.py
```

---

## 7. 注意事項

- `.env` は Git にコミットしない
- `output/` フォルダも Git に含まれない

---

## 開発背景と目的

以前、完全な独学・ゼロ知識の状態でGoogle Cloud Vision APIを使った
OCR画像テキスト化ツールを作成しました。
実務では今もバリバリ使っていますが、当時のコードは：

- スパゲティコード
- ドキュメントなし
- テストなし
- 壊れるのが怖くて改修できない状態

この反省を活かし、Claude Code + Codex CLIを活用した
AI駆動開発で、同じツールをゼロから作り直したのが本プロジェクトです。

## AI駆動開発の実践

- Claude Code：設計・実装・ドキュメント生成
- Codex CLI：コードレビュー・品質チェック
- 独自のMDファイル構成でAIへの指示を標準化
- TDDで18テストを実装

---
