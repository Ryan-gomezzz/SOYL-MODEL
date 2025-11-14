import random
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
ANNOT = ROOT / "data" / "annotations"
ANNOT.mkdir(parents=True, exist_ok=True)


def sample(n=300, seed=42):
    input_file = PROCESSED / "all_text_emotion_dataset.csv"
    if not input_file.exists():
        print(f"Error: {input_file} not found. Run preprocess_datasets.py first.")
        return

    df = pd.read_csv(input_file)
    df = df.dropna(subset=["text"])
    # Filter out empty texts
    df = df[df["text"].str.strip() != ""]

    if len(df) == 0:
        print("No data to sample from.")
        return

    sample_size = min(n, len(df))
    df_sample = df.sample(n=sample_size, random_state=seed)

    out = ANNOT / "sample_for_annotation.csv"
    # create columns for 3 annotators (they will fill)
    cols = [
        "id",
        "text",
        "source",
        "annotator_1_valence",
        "annotator_1_arousal",
        "annotator_2_valence",
        "annotator_2_arousal",
        "annotator_3_valence",
        "annotator_3_arousal",
        "avg_valence",
        "avg_arousal",
        "notes",
    ]
    df_out = pd.DataFrame(columns=cols)
    df_out["id"] = (
        df_sample["id"].values if "id" in df_sample.columns else range(len(df_sample))
    )
    df_out["text"] = df_sample["text"].values
    df_out["source"] = (
        df_sample.get("source", "").values if "source" in df_sample.columns else ""
    )
    df_out.to_csv(out, index=False)
    print(f"Wrote sample for annotation: {out} ({len(df_out)} rows)")
    print(f"Columns ready for annotators: {', '.join(cols[3:9])}")


if __name__ == "__main__":
    sample(300)
