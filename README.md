# ocr-vision

Google Cloud Vision API を使って、フォルダ内の画像を一括OCR処理し、通常モードではテキスト、レシートモードではJSONとして出力するCLIツール。

---

## 1. プロジェクト概要

- `input/` フォルダ内の JPG/JPEG/PNG/TIFF を検出
- Google Cloud Vision API（DOCUMENT_TEXT_DETECTION）でOCR処理
- `output/` に `<画像名>.txt` として保存
- OCR済み画像は `input/processed/` に移動
- `input/processed/` 内の3日以上前のファイルは自動でゴミ箱に送る

**レシートモード（`--mode receipt`）：**

- OCRテキストを Ollama（ローカルLLM）に送り、JSON形式に構造化して出力
- `output/` に `<画像名>.json` として保存（店名・日付・品目・合計金額）

---

## 2. 必要環境

- Python 3.10
- Google Cloud サービスアカウント（Vision API 有効化済み）
- レシートモード利用時は Ollama の起動環境
- レシートモード利用時は `qwen2.5:14b` モデルが利用可能であること

---

## 3. インストール方法

```bash
python -m venv .venv
source .venv/Scripts/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 4. 設定

`.env.example` をコピーして `.env` を作成し、必要な設定を記入する。

```bash
cp .env.example .env
# .env を編集して実際のパスを記入
```

| 変数名 | 説明 | 必須 |
|--------|------|------|
| `GOOGLE_APPLICATION_CREDENTIALS` | サービスアカウントJSONのパス | 常時必須 |
| `OLLAMA_URL` | Ollama サーバーのベースURL。未設定時は `http://localhost:11434` を使用 | 任意 |

---

## 5. 使い方

処理したい画像を `input/` フォルダに置いてから実行する。

```bash
python ocr.py                  # 通常モード（テキスト出力）
python ocr.py --mode receipt   # レシートモード（JSON出力）
```

Windows の場合、bat ファイルをダブルクリックでも実行できる。

| ファイル | 説明 |
|----------|------|
| `run.bat` | 通常モードで実行（テキスト出力） |
| `run_receipt.bat` | レシートモードで実行（JSON出力） |

**通常モード 実行例：**

```
[OK]   photo1.jpg -> output/photo1.txt
[SKIP] photo2.txt already exists
[ERR]  photo3.png: API error - ...
完了: 処理1件 / スキップ1件 / エラー1件 / ゴミ箱2件
```

**レシートモード 実行例：**

```
[OK]   receipt1.jpg -> output/receipt1.json
完了: 処理1件 / スキップ0件 / エラー0件 / ゴミ箱0件
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
├── output/                 # OCR結果（自動作成）
├── parser/
│   └── receipt.py          # レシートモード：OCRテキスト→JSON構造化（Ollama使用）
└── tests/
    ├── test_ocr.py
    └── test_receipt.py
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
- TDDで32テストを実装

---
