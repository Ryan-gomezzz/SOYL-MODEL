import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)


def run(cmd):
    print("RUN:", cmd)
    subprocess.check_call(cmd, shell=True)


def download_goemotions():
    # official storage root (Google): downloads as CSV
    ROOT_URL = "https://storage.googleapis.com/gresearch/goemotions/data/full_dataset"
    for part in ["goemotions_1.csv", "goemotions_2.csv", "goemotions_3.csv"]:
        out = RAW / part
        if not out.exists():
            # Use curl on Windows/Mac, or urllib
            try:
                import urllib.request

                url = f"{ROOT_URL}/{part}"
                print(f"Downloading {url} to {out}")
                urllib.request.urlretrieve(url, out)
                print(f"Downloaded: {out}")
            except Exception as e:
                print(f"Error downloading {part}: {e}")
                # Try wget/curl if available
                try:
                    run(f'curl -L -o "{out}" "{ROOT_URL}/{part}"')
                except:
                    print(f"Manual download needed: {ROOT_URL}/{part} -> {out}")
        else:
            print(f"Exists: {out}")


def download_emobank():
    # EmoBank is available via the JULIElab repo – we'll fetch the corpus file if present
    # If private restrictions exist, print instructions to download manually.
    out = RAW / "emobank.csv"
    if out.exists():
        print("EmoBank already present.")
        return
    print(
        "Please download EmoBank from the JULIElab page (license terms may apply) and place the CSV at:",
        out,
    )
    print(
        "Source: https://github.com/JULIELab/EmoBank or https://github.com/JULIELab/EmoBank/tree/master/corpus"
    )
    # Optionally try known mirrors (Kaggle) if authorized; we do not automate kaggle here.


def download_semeval_2018():
    out = RAW / "semeval2018_task1.zip"
    if out.exists():
        print("SemEval dataset already present.")
        return
    print(
        "Please download SemEval-2018 Task 1 data from: https://competitions.codalab.org/competitions/17751 or the ACL anthology page."
    )
    print(f"Place the downloaded file at: {out}")
    # Automated download may not be available; manual step needed due to licensing


def download_isear():
    out = RAW / "isear.csv"
    if out.exists():
        print("ISEAR already present.")
        return
    print(
        "ISEAR is available from public mirrors (Kaggle). You can download and place it at:",
        out,
    )
    print(
        "Source: https://www.kaggle.com/datasets/ismailmohsen/isear-emotion-dataset or other public repositories"
    )


if __name__ == "__main__":
    print("Starting dataset downloads...")
    download_goemotions()
    download_emobank()
    download_semeval_2018()
    download_isear()
    print("\nDownload complete / instructions printed. Check modules/text/data/raw for files.")
