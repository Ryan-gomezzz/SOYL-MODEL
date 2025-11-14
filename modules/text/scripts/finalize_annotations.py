import pandas as pd
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ANNOT = ROOT / "data" / "annotations"
PROCESSED = ROOT / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)

input_file = ANNOT / "sample_for_annotation.csv"
if not input_file.exists():
    print(f"Error: {input_file} not found.")
    exit(1)

df = pd.read_csv(input_file)

# compute averages across annotator columns that exist
v_cols = [c for c in df.columns if "annotator" in c and "valence" in c]
a_cols = [c for c in df.columns if "annotator" in c and "arousal" in c]

print(f"Found valence columns: {v_cols}")
print(f"Found arousal columns: {a_cols}")


def safe_mean(row, cols):
    vals = []
    for c in cols:
        try:
            v = float(row[c])
            if not pd.isna(v):
                vals.append(v)
        except (ValueError, TypeError):
            pass
    return np.mean(vals) if vals else np.nan


df["avg_valence"] = df.apply(lambda r: safe_mean(r, v_cols), axis=1)
df["avg_arousal"] = df.apply(lambda r: safe_mean(r, a_cols), axis=1)

# Compute inter-annotator agreement (if multiple annotators)
if len(v_cols) > 1:
    print("\nComputing inter-annotator agreement...")
    from scipy.stats import pearsonr

    for i, col1 in enumerate(v_cols):
        for col2 in v_cols[i + 1 :]:
            vals1 = []
            vals2 = []
            for _, row in df.iterrows():
                try:
                    v1 = float(row[col1])
                    v2 = float(row[col2])
                    if not (pd.isna(v1) or pd.isna(v2)):
                        vals1.append(v1)
                        vals2.append(v2)
                except:
                    pass
            if len(vals1) > 5:
                corr, pval = pearsonr(vals1, vals2)
                print(f"Correlation {col1} vs {col2}: {corr:.3f} (p={pval:.3f})")

df.to_csv(PROCESSED / "annotation_final.csv", index=False)
print(f"\nWrote: {PROCESSED / 'annotation_final.csv'} ({len(df)} rows)")
