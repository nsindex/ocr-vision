# 進捗管理

## 完了済み
- プロジェクトセットアップ
- ドキュメント作成
- ocr.py 実装（TDD）
- 仕様変更対応（固定フォルダ化・画像移動・ゴミ箱機能）
  - 引数なし実行（python ocr.py）
  - input/ 固定・output/ 固定
  - OCR済み画像を input/processed/ に移動
  - 3日以上前のファイルを send2trash でゴミ箱送り
  - サマリーにゴミ箱件数を追加

## 進行中

- レシートモード追加（parser/receipt.py・ocr.py --mode引数・テスト32件）

## 次にやること
- 手動テスト（実画像・サービスアカウント設定後）
- レシートモード手動テスト（Ollama gemma3:4b 起動後）
