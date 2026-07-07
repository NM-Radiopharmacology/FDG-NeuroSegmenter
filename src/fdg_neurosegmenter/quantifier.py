import os
import sys
import argparse
import itk
import numpy as np
import pandas as pd
import scipy
from tqdm import tqdm
from fdg_neurosegmenter.utilities import (
    printdt, resample_volume, resample_to_reference,
    pons_normalisation, run_segmenter, get_package_data_path
)


def main():
    parser = argparse.ArgumentParser(
        description="Brain [18F]FDG PET regional quantification and Z-score mapping against a normal cohort."
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Path to the directory containing input NIfTI brain FDG PET images"
    )
    parser.add_argument(
        "--fast",
        action="store_true",  # This makes it a boolean switch (True if present, False if absent)
        help="Run in fast mode using only a single fold (0) instead of ensembling all 5 folds."
    )

    args = parser.parse_args()
    input_path = args.input
    if not os.path.isdir(input_path):
        print(f"Error: {input_path} is not a directory")
        sys.exit(1)

    # ----------------------------------------------------------------------------------------------------- segmentation
    seg_path = input_path + '_FDG-NeuroSegmenter'
    if not os.path.isdir(seg_path) or len(os.listdir(seg_path)) == 0:
        printdt("No segmentation folder found for quantification! Running segmenter first...")
        print('=' * (80 - (len('FDG-NeuroSegmenter') + 1)) + ' ' + str('FDG-NeuroSegmenter'))
        return_code = run_segmenter(input_path, fast_mode=args.fast)
        if return_code != 0:
            printdt("Unable to run segmenter. Exiting...")
            sys.exit(return_code)
        printdt("Segmentations completed successfully")
    else:
        print("Segmentations found")
        if args.fast:
            print("Fast mode enabled but segmentation needn't be performed!")

    # --------------------------------------------------------------------------------------------------- quantification
    print('=' * (80 - (len('FDG-NeuroQuantifier') + 1)) + ' ' + str('FDG-NeuroQuantifier'))
    printdt("quantifying...")
    output_path = seg_path + '_quantification'

    cn = pd.read_csv(get_package_data_path("CN_quantification.csv"))
    cn_mean = cn.mean()
    cn_std = cn.std()
    label_correspondence = pd.read_csv(get_package_data_path("label_correspondence.csv"))
    label_correspondence.set_index("Label", inplace=True)

    non_gz_files = [f_ for f_ in os.listdir(input_path) if f_.endswith('.nii')]
    for f_ in non_gz_files:
        itk.imwrite(itk.imread(os.path.join(input_path, f_)),
                    os.path.join(input_path, f_.replace('.nii', '.nii.gz')))
    img_files = [f for f in sorted(os.listdir(input_path)) if f.endswith('.nii.gz')]
    for img_file in img_files:
        quantification = {
            'AnatomicalStruct': [],
            'SUVRmean': [],
            'zscore': [],
            'percentile': []
        }

        img = itk.imread(os.path.join(input_path, img_file))
        img = resample_volume(img, [1.5, 1.5, 1.5])
        seg_file = img_file.replace('.nii', '_FDGNeuroSeg.nii')

        if not os.path.isfile(os.path.join(seg_path, seg_file)):
            print(f"segmentation of {img_file} not found! skipping...")
            continue

        seg = itk.imread(os.path.join(seg_path, seg_file))
        seg = resample_to_reference(seg, img, interpolation_mode="nearestneighbour")
        img_arr = np.asarray(img)
        seg_arr = np.asarray(seg)
        pons_seg_arr = (seg_arr == 46) * 1
        img_suvr = pons_normalisation(img_arr, pons_seg_arr)

        labels = [int(l_) for l_ in np.unique(seg_arr) if l_ > 0]

        for label in tqdm(labels, file=sys.stdout, desc=img_file):

            anatomical_region = label_correspondence.loc[label, 'AnatomicalStruct']
            mean_cn = cn_mean.loc[anatomical_region]
            std_cn = cn_std.loc[anatomical_region]

            suvrmean = np.mean(img_suvr[seg_arr == label])
            zscore = (suvrmean - mean_cn)/std_cn
            pctl = scipy.stats.percentileofscore(cn[anatomical_region].values.tolist(), suvrmean)

            quantification['AnatomicalStruct'].append(anatomical_region)
            quantification['SUVRmean'].append(suvrmean)
            quantification['zscore'].append(zscore)
            quantification['percentile'].append(pctl)

        quantification_df = pd.DataFrame(quantification)
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        quantification_df.to_csv(os.path.join(output_path, img_file.split('.')[0] + '_FDGNeuroSeg-quant.csv'), index=False)

    for f_ in non_gz_files:
        os.remove(os.path.join(input_path, f_.replace('.nii', '.nii.gz')))


if __name__ == "__main__":
    main()
