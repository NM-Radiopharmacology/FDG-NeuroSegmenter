"""
Utility script to convert standard FastSurfer segmentations (aparc.DKTatlas+aseg) into FDG-NeuroSegmenter target
ground-truth masks (52 labels).
--> Supports both single-file and batch directory processing.
--> Label correspondence is stored in src/fdg-neurosegmenter/data/label_correspondence.csv
"""
import os
import ast
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import nibabel as nib
import scipy.ndimage as ndimage

try:
    from skimage.segmentation import expand_labels

    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False


def load_label_mapping():
    """
    Locates label_correspondence.csv relative to this script's repository location and parses it into a dictionary
    """
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    csv_path = repo_root / "src" / "fdg_neurosegmenter" / "data" / "label_correspondence.csv"

    if not csv_path.is_file():
        raise FileNotFoundError(
            f"Could not find label correspondence file at expected location:\n{csv_path}\n"
            "Please ensure you are running this script within the repository tree."
        )

    df = pd.read_csv(csv_path)
    mapping = {}

    for _, row in df.iterrows():
        target_idx = int(row['Label'])
        raw_fs_str = row['FastSurferLabels']

        if pd.isna(raw_fs_str) or not str(raw_fs_str).strip():
            continue

        try:
            fs_list = ast.literal_eval(str(raw_fs_str))
            for fs_id in fs_list:
                mapping[int(fs_id)] = target_idx
        except (ValueError, SyntaxError):
            continue

    return mapping


def resample_mask_to_isotropic(img, target_spacing=(1.5, 1.5, 1.5)):
    """
    Resamples a nibabel segmentation volume to target voxel spacing (mm) using nearest-neighbor interpolation.
    """
    data = img.get_fdata().astype(np.int32)
    current_zooms = img.header.get_zooms()[:3]

    if isinstance(target_spacing, (int, float)):
        target_spacing = (float(target_spacing), float(target_spacing), float(target_spacing))

    if np.allclose(current_zooms, target_spacing, atol=1e-2):
        return data, img.affine

    zoom_factors = [current_zooms[i] / target_spacing[i] for i in range(3)]
    resampled_data = ndimage.zoom(data, zoom=zoom_factors, order=0)

    new_affine = img.affine.copy()
    for i in range(3):
        new_affine[:3, i] = new_affine[:3, i] * (target_spacing[i] / current_zooms[i])

    return resampled_data, new_affine


def process_single_file(input_path, output_path, label_mapping):

    input_path = Path(input_path)
    output_path = Path(output_path)

    if len(output_path.parts) == 1:
        output_path = input_path.parent / output_path

    img = nib.load(input_path)
    data = img.get_fdata().astype(np.int32)

    remapped_data = np.zeros_like(data, dtype=np.int32)
    for fs_id, target_id in label_mapping.items():
        remapped_data[data == fs_id] = target_id

    remapped_img = nib.Nifti1Image(remapped_data, img.affine, img.header)

    # Resampling to 1.5 mm isotropic voxels
    final_data, final_affine = resample_mask_to_isotropic(
        remapped_img,
        target_spacing=(1.5, 1.5, 1.5)
    )

    # 1.5 mm label dilation
    if SKIMAGE_AVAILABLE:
        final_data = expand_labels(final_data, distance=1.5, spacing=(1.5, 1.5, 1.5))
    else:
        raise ImportError(
            "scikit-image is required for label dilation. "
            "Please install it using: pip install scikit-image"
        )

    # Save output NIfTI file
    out_img = nib.Nifti1Image(final_data, final_affine)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    nib.save(out_img, output_path)
    print(f"Successfully saved mask to: {output_path}")


def convert_fastsurfer_masks(input_path, output_path):
    label_mapping = load_label_mapping()
    input_p = Path(input_path)
    output_p = Path(output_path)

    # Single File
    if input_p.is_file():
        # Resolve destination path relative to input file if a simple filename is given
        if len(output_p.parts) == 1:
            out_file = input_p.parent / output_p
        else:
            out_file = output_p if output_p.suffix in ['.gz', '.nii',
                                                       '.mgz'] else output_p / f"{input_p.stem}_converted.nii.gz"

        print(f"Processing single file: {input_p} -> {out_file}")
        process_single_file(input_p, out_file, label_mapping)
        return

    # Folder Batch
    if input_p.is_dir():
        supported_exts = ('.nii', '.nii.gz', '.mgz')
        files_to_process = [f for f in input_p.rglob('*') if f.name.endswith(supported_exts)]

        if not files_to_process:
            print(f"No neuroimaging files found in {input_p}")
            return

        print(f"Found {len(files_to_process)} file(s) to process.")
        for f in files_to_process:
            relative_path = f.relative_to(input_p)
            stem_name = f.name.split('.')[0]
            out_file = output_p / relative_path.parent / f"{stem_name}_converted.nii.gz"

            print(f"Converting: {f.name} -> {out_file.name}")
            try:
                process_single_file(f, out_file, label_mapping)
            except Exception as e:
                print(f"  [ERROR] Failed to process {f.name}: {e}")

        print("Batch processing complete!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert FastSurfer segmentations to FDG-NeuroSegmenter target masks (file or folder)."
    )
    parser.add_argument(
        "-i", "--input", required=True,
        help="Path to input file (.mgz/.nii.gz) or directory containing FastSurfer masks"
    )
    parser.add_argument(
        "-o", "--output", required=True,
        help="Path to save output converted file or destination directory"
    )

    args = parser.parse_args()
    convert_fastsurfer_masks(args.input, args.output)
