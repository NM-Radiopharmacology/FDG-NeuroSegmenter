import os
import sys
import argparse
import itk
from fdg_neurosegmenter.utilities import run_segmenter

def main():

    parser = argparse.ArgumentParser(
        description="FDG-NeuroSegmenter: AI-based anatomical segmentation of brain [18F]FDG PET images"
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Path to the directory containing the input brain FDG PET images"
    )
    parser.add_argument(
        "--fast",
        action="store_true",  # This makes it a boolean switch (True if present, False if absent)
        help="Run in fast mode using only a single fold (0) instead of ensembling all 5 folds."
    )

    args = parser.parse_args()
    input_path = args.input
    if not os.path.isdir(input_path):
        print(f"Error: {input_path} is not a valid directory.")
        sys.exit(1)

    print('=' * (80 - (len('FDG-NeuroSegmenter') + 1)) + ' ' + str('FDG-NeuroSegmenter'))

    run_segmenter(input_path, fast_mode=args.fast)

if __name__ == "__main__":
    main()
