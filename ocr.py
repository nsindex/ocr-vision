import os
import sys
import time
from pathlib import Path

import google.cloud.vision as vision
from dotenv import load_dotenv
from send2trash import send2trash

BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"
PROCESSED_DIR = INPUT_DIR / "processed"

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


def trash_old_files(processed_dir: Path, days: int = 3) -> int:
    if not processed_dir.exists():
        return 0
    cutoff = time.time() - days * 86400
    count = 0
    for f in processed_dir.iterdir():
        if not f.is_file():
            continue
        try:
            if f.stat().st_mtime < cutoff:
                send2trash(str(f))
                count += 1
        except Exception as e:
            print(f"[WARN] ゴミ箱移動失敗: {f.name}: {e}")
    return count


def process_folder(input_dir: Path, output_dir: Path, processed_dir: Path) -> dict:
    output_dir.mkdir(exist_ok=True)
    processed_dir.mkdir(exist_ok=True)

    trash_count = trash_old_files(processed_dir)
    images = collect_images(input_dir)
    counts = {"ok": 0, "skip": 0, "err": 0, "trash": trash_count}

    if not images:
        print("対象ファイルが見つかりませんでした")
        print(f"完了: 処理{counts['ok']}件 / スキップ{counts['skip']}件 / エラー{counts['err']}件 / ゴミ箱{counts['trash']}件")
        return counts

    client = vision.ImageAnnotatorClient()

    for image_path in images:
        out_path = get_output_path(image_path, output_dir)

        if out_path.exists():
            dest = processed_dir / image_path.name
            if not dest.exists():
                try:
                    image_path.rename(dest)
                except Exception:
                    pass
            print(f"[SKIP] {out_path.name} already exists")
            counts["skip"] += 1
            continue

        try:
            text = ocr_image(image_path, client)
            out_path.write_text(text, encoding="utf-8")
            try:
                image_path.rename(processed_dir / image_path.name)
            except Exception as move_err:
                out_path.unlink(missing_ok=True)
                raise move_err
            print(f"[OK]   {image_path.name} -> output/{out_path.name}")
            counts["ok"] += 1
        except Exception as e:
            print(f"[ERR]  {image_path.name}: {e}")
            counts["err"] += 1

    print(f"完了: 処理{counts['ok']}件 / スキップ{counts['skip']}件 / エラー{counts['err']}件 / ゴミ箱{counts['trash']}件")
    return counts


def main():
    load_dotenv()

    creds = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds:
        print("エラー: GOOGLE_APPLICATION_CREDENTIALS が設定されていません。.env を確認してください。")
        sys.exit(1)
    if not Path(creds).exists():
        print(f"エラー: 認証ファイルが見つかりません: {creds}")
        sys.exit(1)

    if not INPUT_DIR.exists():
        print(f"エラー: input/ フォルダが見つかりません: {INPUT_DIR}")
        sys.exit(1)

    process_folder(INPUT_DIR, OUTPUT_DIR, PROCESSED_DIR)


if __name__ == "__main__":
    main()
