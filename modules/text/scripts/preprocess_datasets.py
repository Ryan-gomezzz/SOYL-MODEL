import csv
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
INTERIM = ROOT / "data" / "interim"
PROCESSED = ROOT / "data" / "processed"
for d in (INTERIM, PROCESSED):
    d.mkdir(parents=True, exist_ok=True)


def process_goemotions():
    # merge parts and convert: GoEmotions has categorical labels; valence/arousal empty (we'll fill later or map)
    parts = [RAW / f"goemotions_{i}.csv" for i in [1, 2, 3]]
    rows = []
    for p in parts:
        if not p.exists():
            print("Missing:", p)
            continue
        try:
            df = pd.read_csv(p)
            # expected columns: text, labels (or multi-hot), etc. This code may need adjustment based on file layout.
            if "text" in df.columns:
                for i, r in df.iterrows():
                    rows.append(
                        {
                            "id": f"go_{p.stem}_{i}",
                            "text": str(r["text"]) if pd.notna(r["text"]) else "",
                            "source": "goemotions",
                            "raw_label": (
                                str(r.get("labels", ""))
                                if pd.notna(r.get("labels", ""))
                                else ""
                            ),
                            "valence": "",
                            "arousal": "",
                            "annotation_source": "goemotions",
                            "notes": "",
                        }
                    )
        except Exception as e:
            print(f"Error processing {p}: {e}")
            continue
    if rows:
        out = INTERIM / "goemotions_unified.csv"
        pd.DataFrame(rows).to_csv(out, index=False)
        print(f"Wrote: {out} ({len(rows)} rows)")
    else:
        print("No GoEmotions data processed.")


def process_emobank():
    # Try multiple possible file names and formats
    possible_files = [
        RAW / "emobank.csv",
        RAW / "emobank.tsv",
        RAW / "emobank.txt",
        RAW / "emobank.json",
    ]
    src = None
    for f in possible_files:
        if f.exists():
            src = f
            break
    
    if not src:
        print("EmoBank missing; skip")
        print("Expected files: emobank.csv, emobank.tsv, emobank.txt, or emobank.json")
        return
    
    try:
        # Handle different file formats
        if src.suffix == ".csv":
            df = pd.read_csv(src)
        elif src.suffix == ".tsv":
            df = pd.read_csv(src, sep="\t")
        elif src.suffix == ".txt":
            # Try TSV first, then CSV
            try:
                df = pd.read_csv(src, sep="\t")
            except:
                df = pd.read_csv(src)
        elif src.suffix == ".json":
            df = pd.read_json(src)
        else:
            # Default to CSV
            df = pd.read_csv(src)
        
        print(f"Loading EmoBank from {src.name} ({src.suffix} format)")
        print(f"Columns found: {list(df.columns)}")
        
        # EmoBank has columns: ID, Text, V, A, D etc — adapt to actual columns
        out_rows = []
        for i, r in df.iterrows():
            text = (
                r.get("text")
                or r.get("sentence")
                or r.get("Sentence")
                or r.get("Text")
                or r.get("text_tokenized")
                or r.get("sentence_text")
            )
            if pd.isna(text):
                continue
            v = r.get("V") or r.get("valence") or r.get("Valence") or r.get("v")
            a = r.get("A") or r.get("arousal") or r.get("Arousal") or r.get("a")
            out_rows.append(
                {
                    "id": f"emobank_{i}",
                    "text": str(text),
                    "source": "emobank",
                    "raw_label": "",
                    "valence": float(v) if pd.notna(v) else "",
                    "arousal": float(a) if pd.notna(a) else "",
                    "annotation_source": "emobank",
                    "notes": "",
                }
            )
        if out_rows:
            pd.DataFrame(out_rows).to_csv(PROCESSED / "emobank_va.csv", index=False)
            print(f"Wrote: {PROCESSED / 'emobank_va.csv'} ({len(out_rows)} rows)")
    except Exception as e:
        print(f"Error processing EmoBank: {e}")
        print(f"File: {src}")
        print(f"Columns: {list(df.columns) if 'df' in locals() else 'N/A'}")


def process_semeval():
    src = RAW / "semeval2018_task1.zip"
    if not src.exists():
        print("SemEval dataset missing; skip")
        return
    print(
        "SemEval processing: extract zip and process manually or add custom extraction logic."
    )


def process_isear():
    # Try multiple possible file names for ISEAR
    possible_files = [
        RAW / "isear.csv",
        RAW / "eng_dataset.csv",  # Alternative name
    ]
    src = None
    for f in possible_files:
        if f.exists():
            src = f
            break
    
    if not src:
        print("ISEAR missing; skip")
        print("Expected files: isear.csv or eng_dataset.csv")
        return
    
    try:
        df = pd.read_csv(src)
        print(f"Loading ISEAR from {src.name}")
        print(f"Columns found: {list(df.columns)}")
        
        out_rows = []
        # ISEAR typically has columns like 'SIT', 'EMOT', 'TEXT' or 'content', 'sentiment'
        # Try multiple possible column names
        text_col = None
        for col_name in ["TEXT", "text", "content", "Text", "Content"]:
            if col_name in df.columns:
                text_col = col_name
                break
        
        if not text_col:
            # Fallback: use first non-ID column that looks like text
            for col in df.columns:
                if col.upper() not in ["ID", "EMOT", "SENTIMENT"] and df[col].dtype == "object":
                    text_col = col
                    break
        
        if not text_col:
            print("ISEAR: Could not find text column")
            return
        
        # Find emotion/label column
        label_col = None
        for col_name in ["EMOT", "sentiment", "Sentiment", "emotion", "label"]:
            if col_name in df.columns:
                label_col = col_name
                break
        
        for i, r in df.iterrows():
            text = r.get(text_col)
            if pd.isna(text) or str(text).strip() == "":
                continue
            
            label = ""
            if label_col:
                label = str(r.get(label_col, "")) if pd.notna(r.get(label_col)) else ""
            
            out_rows.append(
                {
                    "id": f"isear_{i}",
                    "text": str(text),
                    "source": "isear",
                    "raw_label": label,
                    "valence": "",
                    "arousal": "",
                    "annotation_source": "isear",
                    "notes": "",
                }
            )
        if out_rows:
            pd.DataFrame(out_rows).to_csv(INTERIM / "isear_unified.csv", index=False)
            print(f"Wrote: {INTERIM / 'isear_unified.csv'} ({len(out_rows)} rows)")
    except Exception as e:
        print(f"Error processing ISEAR: {e}")
        print(f"File: {src}")
        if 'df' in locals():
            print(f"Columns: {list(df.columns)}")


def merge_all():
    # Merge interim & processed CSVs into a single processed/unified csv
    files = list(INTERIM.glob("*.csv")) + list(PROCESSED.glob("*.csv"))
    dfs = []
    for f in files:
        try:
            df = pd.read_csv(f)
            if len(df) > 0:
                dfs.append(df)
        except Exception as e:
            print(f"Error reading {f}: {e}")
            continue
    if not dfs:
        print("Nothing to merge.")
        return
    merged = pd.concat(dfs, ignore_index=True, sort=False)
    # Remove duplicates based on text
    merged = merged.drop_duplicates(subset=["text"], keep="first")
    # Filter very short texts (< 3 words)
    merged["word_count"] = merged["text"].str.split().str.len()
    merged = merged[merged["word_count"] >= 3].drop(columns=["word_count"])
    merged.to_csv(PROCESSED / "all_text_emotion_dataset.csv", index=False)
    print(
        f"Wrote merged dataset: {PROCESSED / 'all_text_emotion_dataset.csv'} ({len(merged)} rows)"
    )


if __name__ == "__main__":
    print("Processing datasets...")
    process_goemotions()
    process_emobank()
    process_semeval()
    process_isear()
    print("\nMerging all datasets...")
    merge_all()
    print("Preprocessing complete.")
