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
