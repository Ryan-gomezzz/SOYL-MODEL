"""
Quick Annotation Helper Script

This script helps you annotate samples interactively.
Run: python -m modules.text.scripts.quick_annotate
Or: python modules/text/scripts/quick_annotate.py
"""

import pandas as pd
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
ANNOT = ROOT / "data" / "annotations"
CSV_FILE = ANNOT / "sample_for_annotation.csv"


def annotate_interactive(start_idx=0, annotator_num=1):
    """
    Interactive annotation session.
    
    Args:
        start_idx: Row index to start from (0-based)
        annotator_num: Which annotator (1, 2, or 3)
    """
    df = pd.read_csv(CSV_FILE)
    
    v_col = f"annotator_{annotator_num}_valence"
    a_col = f"annotator_{annotator_num}_arousal"
    
    # Ensure columns exist
    if v_col not in df.columns:
        df[v_col] = ""
    if a_col not in df.columns:
        df[a_col] = ""
    
    print(f"\n{'='*60}")
    print(f"Annotation Session - Annotator {annotator_num}")
    print(f"{'='*60}")
    print("\nInstructions:")
    print("- Enter valence (0.0-1.0): negative=low, positive=high")
    print("- Enter arousal (0.0-1.0): calm=low, excited=high")
    print("- Press Enter to skip a row")
    print("- Type 'quit' or 'q' to save and exit")
    print("- Type 'save' to save progress and continue")
    print(f"\nStarting from row {start_idx + 1} of {len(df)}\n")
    
    for idx in range(start_idx, len(df)):
        row = df.iloc[idx]
        text = row['text']
        
        # Skip if already annotated
        if pd.notna(row.get(v_col)) and str(row.get(v_col)).strip() != "":
            print(f"\n[Row {idx+1}/{len(df)}] ALREADY ANNOTATED - Skipping")
            print(f"Text: {text[:100]}...")
            print(f"Current: V={row.get(v_col)}, A={row.get(a_col)}")
            print("\nPress Enter to continue, or type 'a' to re-annotate")
            choice = input().strip().lower()
            if choice != 'a':
                continue
        
        print(f"\n{'='*60}")
        print(f"Row {idx+1}/{len(df)}")
        print(f"ID: {row['id']}")
        print(f"Source: {row['source']}")
        print(f"\nText: {text}")
        print(f"{'='*60}")
        
        # Get valence
        while True:
            v_input = input(f"Valence (0.0-1.0): ").strip()
            if v_input.lower() in ['quit', 'q']:
                df.to_csv(CSV_FILE, index=False)
                print(f"\nProgress saved. Exiting at row {idx+1}.")
                return
            if v_input.lower() == 'save':
                df.to_csv(CSV_FILE, index=False)
                print(f"\nProgress saved. Continuing...")
                continue
            if v_input == '':
                print("Skipping this row...")
                break
            try:
                v = float(v_input)
                if 0.0 <= v <= 1.0:
                    break
                else:
                    print("Value must be between 0.0 and 1.0")
            except ValueError:
                print("Invalid input. Enter a number between 0.0 and 1.0")
        
        if v_input == '':
            continue
        
        # Get arousal
        while True:
            a_input = input(f"Arousal (0.0-1.0): ").strip()
            if a_input.lower() in ['quit', 'q']:
                df.to_csv(CSV_FILE, index=False)
                print(f"\nProgress saved. Exiting at row {idx+1}.")
                return
            if a_input == '':
                print("Skipping this row...")
                break
            try:
                a = float(a_input)
                if 0.0 <= a <= 1.0:
                    break
                else:
                    print("Value must be between 0.0 and 1.0")
            except ValueError:
                print("Invalid input. Enter a number between 0.0 and 1.0")
        
        if a_input == '':
            continue
        
        # Save to dataframe
        df.at[idx, v_col] = v
        df.at[idx, a_col] = a
        
        print(f"Saved: V={v}, A={a}")
    
    # Save final results
    df.to_csv(CSV_FILE, index=False)
    print(f"\n{'='*60}")
    print("Annotation complete! All annotations saved.")
    print(f"{'='*60}")


def show_statistics():
    """Show current annotation statistics."""
    df = pd.read_csv(CSV_FILE)
    
    print("\nCurrent Annotation Status:")
    print("=" * 60)
    
    for ann_num in [1, 2, 3]:
        v_col = f"annotator_{ann_num}_valence"
        a_col = f"annotator_{ann_num}_arousal"
        
        if v_col in df.columns:
            v_filled = df[v_col].notna().sum()
            a_filled = df[a_col].notna().sum()
            total = len(df)
            
            print(f"\nAnnotator {ann_num}:")
            print(f"  Valence: {v_filled}/{total} ({v_filled/total*100:.1f}%)")
            print(f"  Arousal: {a_filled}/{total} ({a_filled/total*100:.1f}%)")
    
    print("\n" + "=" * 60)


def batch_annotate_from_examples():
    """Show examples and let user annotate based on similar texts."""
    print("\nBatch annotation mode - coming soon!")
    print("For now, use Excel/Sheets or interactive mode.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "stats":
            show_statistics()
        elif sys.argv[1] == "interactive":
            annotator = int(sys.argv[2]) if len(sys.argv) > 2 else 1
            start = int(sys.argv[3]) if len(sys.argv) > 3 else 0
            annotate_interactive(start_idx=start, annotator_num=annotator)
        else:
            print("Usage:")
            print("  python -m modules.text.scripts.quick_annotate stats                    # Show statistics")
            print("  python -m modules.text.scripts.quick_annotate interactive [1|2|3] [start_idx]  # Start annotation")
    else:
        # Default: show stats and offer to start
        show_statistics()
        print("\nTo start annotating, run:")
        print("  python -m modules.text.scripts.quick_annotate interactive 1")
        print("\nOr open the CSV file in Excel/Google Sheets for manual annotation.")


