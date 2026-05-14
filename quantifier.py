import sys
import itk
import pandas as pd
import scipy
from tqdm import tqdm
from utilities import *

# --------------------------------------------------------------------------------------------------------- segmentation
print('-' * (80 - (len('quantifier') + 1)) + ' ' + str('quantifier'))
input_path = None
while input_path is None:
    input_path = input("Introduce path to brain [18F]FDG images: ")
    if not os.path.isdir(input_path):
        print(f"{input_path} is not a directory")
        input_path = None

if not os.path.isdir(input_path + '_FDG-NeuroSegmenter'):
    seg_path = None
else:
    seg_path = input_path + '_FDG-NeuroSegmenter'
    if len(os.listdir(seg_path)) == 0:
        seg_path = None
    else:
        printdt("segmentation folder found & not empty")

if seg_path is None:
    print("No segmentation folder found for quantification!")
    proceed = None
    while proceed not in [True, False]:
        proceed = input("Apply segmenter? (y/n) ")
        if proceed.lower() in ['y', '']:
            proceed = True
        elif proceed.lower() == 'n':
            proceed = False

    if not proceed:
        sys.exit(0)

    return_code = run_segmenter(input_path)
    if return_code != 0:
        print("Unable to run segmenter. Exiting...")
        sys.exit(return_code)
    printdt("segmentations performed successfully")

seg_path = input_path + '_FDG-NeuroSegmenter'

# ------------------------------------------------------------------------------------------------------- quantification
printdt("quantifying...")
output_path = seg_path + '_quantification'

cn = pd.read_csv("resources/CN_quantification.csv")
cn_mean = cn.mean()
cn_std = cn.std()
label_correspondence = pd.read_csv("resources/label_correspondence.csv")
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
    seg = itk.imread(os.path.join(seg_path, img_file.replace('.nii', '_FDGNeuroSeg.nii')))
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
