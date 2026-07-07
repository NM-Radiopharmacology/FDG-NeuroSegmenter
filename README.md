# FDG-NeuroSegmenter
<b>FDG-NeuroSegmenter</b> is a deep-learning-based model developed to perform the automatic segmentation of 52 
anatomical regions in brain [<sup>18</sup>F]FDG PET images.

Please cite [REF!]

<img src="/figures/fdg_brain_segmentation.png" alt="[18F]FDG PET brain anatomical segmentation" style="max-width: 95%; height: auto;">

1736 brain [<sup>18</sup>F]FDG PET studies of 1197 subjects with and without cognitive impairments were used to train 
and test a deep-learning-based anatomical segmentation model ([nnU-Net](https://github.com/MIC-DKFZ/nnUNet)). Ground-truth 
segmentations were obtained on the respectively paired T1-weighted MRI studies using 
[FastSurfer](https://github.com/Deep-MI/FastSurfer). All images belong to different neuroimaging initiatives 
(please refer to the [Acknowledgements](#acknowledgements) section for more information).

## Installation & Usage
Using a virtual environment is recommended! (Git Bash: `source <path-to-venv>/Scripts/activate` - Windows)

**PyTorch must be installed beforehand!!** 
[Refer to their website and install PyTorch](https://pytorch.org/get-started/locally/) with support for your hardware 
([CUDA](https://developer.nvidia.com/cuda-toolkit), CPU).

Only then (on Git Bash):

```
git clone https://github.com/NM-Radiopharmacology/FDG-NeuroSegmenter.git
cd FDG-NeuroSegmenter
pip install .
```

### Anatomical Segmentation ⟶ `fdg-neurosegmenter`

To perform the anatomical segmentation of [<sup>18</sup>F]FDG PET images, simply run:
```
fdg-neurosegmenter -i /path/to/your/dataset_folder
```

Options:

- `-i`, `--input`: path to the directory containing your NIfTI brain [<sup>18</sup>F]FDG PET images
- `--fast`: runs inference using only a single fold (fold 0) instead of ensembling all 5 folds. Highly recommended for 
fast previews or restricted compute environments.

There is no need to pre-process or re-organise data. The output segmentations will be stored in a folder created next to
 the dataset folder, with the suffix `_FDG-NeuroSegmenter`.

Label correspondence is stored in [`label_correspondence.csv`](src/fdg_neurosegmenter/data/label_correspondence.csv) and displayed below:

<table>
  <thead>
    <tr>
      <th>Label (L, R)<sup>*</sup></th>
      <th>Anatomical Structure</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td align="center">1, 2</td>
      <td align="left">Superior Frontal Gyrus</td>
    </tr>
    <tr>
      <td align="center">3, 4</td>
      <td align="left">Orbitofrontal Cortex</td>
    </tr>
    <tr>
      <td align="center">5, 6</td>
      <td align="left">Dorsolateral Frontal Cortex</td>
    </tr>
    <tr>
      <td align="center">7, 8</td>
      <td align="left">Paracentral Lobule</td>
    </tr>
    <tr>
      <td align="center">9, 10</td>
      <td align="left">Postcentral Gyrus</td>
    </tr>
    <tr>
      <td align="center">11, 12</td>
      <td align="left">Dorsolateral Parietal Cortex</td>
    </tr>
    <tr>
      <td align="center">13, 14</td>
      <td align="left">Precuneus</td>
    </tr>
    <tr>
      <td align="center">15, 16</td>
      <td align="left">Anterior Cingulate Cortex</td>
    </tr>
    <tr>
      <td align="center">17, 18</td>
      <td align="left">Posterior Cingulate Cortex</td>
    </tr>
    <tr>
      <td align="center">19, 20</td>
      <td align="left">Isthmus Cingulate Cortex</td>
    </tr>
    <tr>
      <td align="center">21, 22</td>
      <td align="left">Lateral Temporal Cortex</td>
    </tr>
    <tr>
      <td align="center">23, 24</td>
      <td align="left">Mesial Temporal Cortex</td>
    </tr>
    <tr>
      <td align="center">25, 26</td>
      <td align="left">Lateral Occipital Cortex</td>
    </tr>
    <tr>
      <td align="center">27, 28</td>
      <td align="left">Pericalcarine Cortex</td>
    </tr>
    <tr>
      <td align="center">29, 30</td>
      <td align="left">Lingual Gyrus</td>
    </tr>
    <tr>
      <td align="center">31, 32</td>
      <td align="left">Cuneus</td>
    </tr>
    <tr>
      <td align="center">33, 34</td>
      <td align="left">Insula</td>
    </tr>
    <tr>
      <td align="center">35, 36</td>
      <td align="left">Cerebellar Cortex</td>
    </tr>
    <tr>
      <td align="center">37, 38</td>
      <td align="left">Thalamus</td>
    </tr>
    <tr>
      <td align="center">39, 40</td>
      <td align="left">Caudate</td>
    </tr>
    <tr>
      <td align="center">41, 42</td>
      <td align="left">Putamen</td>
    </tr>
    <tr>
      <td align="center">43, 44</td>
      <td align="left">Globus Pallidus</td>
    </tr>
    <tr>
      <td align="center">45</td>
      <td align="left">Brainstem w/o Pons</td>
    </tr>
    <tr>
      <td align="center">46</td>
      <td align="left">Pons</td>
    </tr>
    <tr>
      <td align="center">47, 48</td>
      <td align="left">Hippocampus</td>
    </tr>
    <tr>
      <td align="center">49, 50</td>
      <td align="left">Amygdala</td>
    </tr>
    <tr>
      <td align="center">51, 52</td>
      <td align="left">Ventral Diencephalon</td>
    </tr>
  </tbody>
</table>
<sup>*</sup> <small>For all paired anatomical structures (left and right hemispheres), odd labels refer to the left hemisphere 
(L) and even labels to the right hemisphere (R). Single labels (45 and 46) represent non-lateralised or singular structures.</small>

### Quantification ⟶ `fdg-neuroquantifier`

To perform the semi-quantitative assessment of [<sup>18</sup>F]FDG PET images, run:
```
fdg-neuroquantifier -i /path/to/your/dataset_folder
```

Options:

- `-i`, `--input`: path to the directory containing your NIfTI brain [<sup>18</sup>F]FDG PET images
- `--fast`: runs inference (if needed) using only a single fold (fold 0) instead of ensembling all 5 folds. Highly 
recommended for fast previews or restricted compute environments.

There is no need to pre-process or re-organise data. If the segmentation folder is not found, segmentation will be 
performed and the outputs stored in a folder created next to the dataset folder, with the suffix `_FDG-NeuroSegmenter`. 
Pons-based SUVR normalisation<sup>1</sup> will be applied to each image for quantification purposes. The output 
quantification files will be stored in a folder created next to the dataset folder, with the suffix 
`_FDG-NeuroSegmenter_quantification`. 

Each quantification file stores:
- `SUVRmean`: the SUVR<sub>mean</sub> in the respective anatomical region for the given [<sup>18</sup>F]FDG PET image.
- `zscore`: the z-score of `SUVRmean` relative to the cognitively normal cohort<sup>2</sup>.
- `percentile`: the percentile in which `SUVRmean` is placed relative to the SUVR<sub>mean</sub> distribution of that anatomical region in 
the cognitively normal cohort<sup>2</sup>.

<sup>1</sup> <small>By default, an erosion filter (spherical kernel of 3 mm radius) is applied to the segmentation of 
the pons, to minimise the contribution of background/vicinity signal to the normalisation constant.</small>

<sup>2</sup> <small>537 [<sup>18</sup>F]FDG PET studies of 355 cognitively normal subjects.</small>

## Acknowledgements

#### Dataset
- [Alzheimer's Disease Neuroimaging Initiative (ADNI)](https://adni.loni.usc.edu/)
- [Frontotemporal Lobar Degeneration Neuroimaging Initiative (FTLDNI/NIFD)](http://memory.ucsf.edu/research/studies/nifd)
- [National Alzheimer's Coordinating Center (NACC):  Standardized Centralized Alzheimer’s & Related Dementias 
Neuroimaging (SCAN)](https://scan.naccdata.org/)
- [Open Access Series of Imaging Studies 3 (OASIS-3)](https://sites.wustl.edu/oasisbrains/)

For more information click [here](ACKNOWLEDGEMENTS.md).

#### Methods
- [nnU-Net](https://github.com/MIC-DKFZ/nnUNet) ([Isensee & Jaeger et al. (2021)](https://www.nature.com/articles/s41592-020-01008-z)) - 
used for training and inference of the segmentation models
- [FastSurfer](https://github.com/Deep-MI/FastSurfer) ([Henschel et al. (2020)](https://doi.org/10.1016/j.neuroimage.2020.117012); 
[Henschel et al. (2022)](https://doi.org/10.1016/j.neuroimage.2022.118933); 
[Faber et al. (2022)](https://doi.org/10.1016/j.neuroimage.2022.119703); 
[Estrada et al. (2023)](https://doi.org/10.1162/imag_a_00034)) - used to obtain the ground-truth MRI-based segmentation
