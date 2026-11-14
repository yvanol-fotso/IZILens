import sys
from pathlib import Path

from paddleocr import PaddleOCR


def main(image_path: str) -> None:
    path = Path(image_path)
    if not path.exists():
        sys.exit(f"Fichier introuvable : {path}")

    ocr = PaddleOCR(
        lang="fr",
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False,
        enable_mkldnn=False,
    )

    for res in ocr.predict(str(path)):
        for text, score in zip(res["rec_texts"], res["rec_scores"]):
            print(f"{score:.2f}  {text}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage : python scripts/test_ocr.py <chemin_image>")
    main(sys.argv[1])