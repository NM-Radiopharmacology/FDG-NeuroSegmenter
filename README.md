# FDG-NeuroSegmenter
<b>Automatic segmentation of 52 anatomical regions in brain [<sup>18</sup>F]FDG PET</b>

<img src="/figures/fdg_brain_segmentation.png" alt="[18F]FDG PET brain anatomical segmentation" style="max-width: 95%; height: auto;">

## Installation & Usage
P.S.: Using a virtual environment is recommended! (Git Bash: `source <path-to-venv>/Scripts/activate` - Windows)

**PyTorch must be installed beforehand!!** 
[Refer to their website and install PyTorch](https://pytorch.org/get-started/locally/) with support for your hardware 
([CUDA](https://developer.nvidia.com/cuda-toolkit), CPU).

Only then (on Git Bash):

```
git clone https://github.com/NM-Radiopharmacology/FDG-NeuroSegmenter.git
cd FDG-NeuroSegmenter
pip install -r requirements.txt
```

### Anatomical Segmentation ⟶ `apply_segmenter.py`

To perform the anatomical segmentation of [<sup>18</sup>F]FDG PET images, simply run `apply_segmenter.py`. You will be 
asked to provide the path to the images (in NIfTI format!) for which to perform segmentation. There is no need to 
pre-process or re-organise data. The output segmentations will be stored in a folder created next to the dataset folder,
with the suffix `_FDG-NeuroSegmenter`.

Label correspondence is stored in `label_correspondence.csv` and displayed below:

| Label (L, R)<sup>*</sup> | Anatomical Structure         |
|:------------------------:|:-----------------------------|
|           1, 2           | Superior Frontal Gyrus       |
|           3, 4           | Orbitofrontal Cortex         |
|           5, 6           | Dorsolateral Frontal Cortex  |
|           7, 8           | Paracentral Lobule           |
|          9, 10           | Postcentral Gyrus            |
|          11, 12          | Dorsolateral Parietal Cortex |
|          13, 14          | Precuneus                    |
|          15, 16          | Anterior Cingulate Cortex    |
|          17, 18          | Posterior Cingulate Cortex   |
|          19, 20          | Isthmus Cingulate Cortex     |
|          21, 22          | Lateral Temporal Cortex      |
|          23, 24          | Mesial Temporal Cortex       |
|          25, 26          | Lateral Occipital Cortex     |
|          27, 28          | Pericalcarine Cortex         |
|          29, 30          | Lingual Gyrus                |
|          31, 32          | Cuneus                       |
|          33, 34          | Insula                       |
|          35, 36          | Cerebellar Cortex            |
|          37, 38          | Thalamus                     |
|          39, 40          | Caudate                      |
|          41, 42          | Putamen                      |
|          43, 44          | Globus Pallidus              |
|            45            | Brainstem (w/o Pons)         |
|            46            | Pons                         |
|          47, 48          | Hippocampus                  |
|          49, 50          | Amygdala                     |
|          51, 52          | Ventral Diencephalon         |
<sup>*</sup> For all paired anatomical structures (left and right hemispheres), odd labels refer to the left hemisphere 
(L) and even labels to the right hemisphere (R). Single labels (45 and 46) represent non-lateralised or singular structures.

### Quantification

WIP

## Acknowledgements

#### Dataset
- [Alzheimer's Disease Neuroimaging Initiative (ADNI)](https://adni.loni.usc.edu/)
- [Frontotemporal Lobar Degeneration Neuroimaging Initiative (FTLDNI/NIFD)](http://memory.ucsf.edu/research/studies/nifd)
- [National Alzheimer's Coordinating Center (NACC):  Standardized Centralized Alzheimer’s & Related Dementias 
Neuroimaging (SCAN)](https://scan.naccdata.org/)

#### Methods
- [nnU-Net](https://github.com/MIC-DKFZ/nnUNet) ([Isensee & Jaeger et al. (2021)](https://www.nature.com/articles/s41592-020-01008-z)) - 
used for training and inference of the segmentation models
- [FastSurfer](https://github.com/Deep-MI/FastSurfer) ([Henschel et al. (2020)](https://doi.org/10.1016/j.neuroimage.2020.117012); 
[Henschel et al. (2022)](https://doi.org/10.1016/j.neuroimage.2022.118933); 
[Faber et al. (2022)](https://doi.org/10.1016/j.neuroimage.2022.119703); 
[Estrada et al. (2023)](https://doi.org/10.1162/imag_a_00034)) - used to obtain the ground-truth MRI-based segmentation
