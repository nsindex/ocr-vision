import argparse
import os
import sys
from pathlib import Path

import google.cloud.vision as vision
from dotenv import load_dotenv

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tiff"}


def collect_images(folder: Path) -> list:
    result = []
    for f in folder.iterdir():
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
            result.append(f)
    return sorted(result)


def get_output_path(image_path: Path, output_dir: Path) -> Path:
    return output_dir / (image_path.stem + ".txt")


def ocr_image(image_path: Path, client) -> str:
    with open(image_path, "rb") as f:
        content = f.read()
    image = vision.Image(content=content)
    image_context = vision.ImageContext(language_hints=["ja", "en"])
    response = client.document_text_detection(image=image, image_context=image_context)
    return response.full_text_annotation.text or ""


def process_folder(folder_path: Path) -> dict:
    output_dir = folder_path / "output"
    output_dir.mkdir(exist_ok=True)

    images = collect_images(folder_path)
    counts = {"ok": 0, "skip": 0, "err": 0}

    if not images:
        print("対象ファイルが見つかりませんでした")
        return counts

    client = vision.ImageAnnotatorClient()

    for image_path in images:
        out_path = get_output_path(image_path, output_dir)

        if out_path.exists():
            print(f"[SKIP] output/{out_path.name} already exists")
            counts["skip"] += 1
            continue

        try:
            text = ocr_image(image_path, client)
            out_path.write_text(text, encoding="utf-8")
            print(f"[OK]   {image_path.name} -> output/{out_path.name}")
            counts["ok"] += 1
        except Exception as e:
            print(f"[ERR]  {image_path.name}: {e}")
            counts["err"] += 1

    print(f"完了: 処理{counts['ok']}件 / スキップ{counts['skip']}件 / エラー{counts['err']}件")
    return counts


def main():
    load_dotenv()

    parser = argparse.ArgumentParser(description="Google Cloud Vision API を使った一括OCRツール")
    parser.add_argument("folder", help="処理対象のフォルダパス")
    args = parser.parse_args()

    folder = Path(args.folder)
    if not folder.is_dir():
        print(f"エラー: フォルダが見つかりません: {args.folder}")
        sys.exit(1)

    creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds:
        print("エラー: GOOGLE_APPLICATION_CREDENTIALS が設定されていません。.env を確認してください。")
        sys.exit(1)
    if not Path(creds).exists():
        print(f"エラー: 認証ファイルが見つかりません: {creds}")
        sys.exit(1)

    process_folder(folder)


if __name__ == "__main__":
    main()
