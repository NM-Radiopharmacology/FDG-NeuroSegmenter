import os

import itk

from utilities import *

print('-' * (80 - (len('segmenter') + 1)) + ' ' + str('segmenter'))
input_path = None
while input_path is None:
    input_path = input("Introduce path to brain [18F]FDG images: ")
    if not os.path.isdir(input_path):
        print(f"{input_path} is not a directory")
        input_path = None

non_gz_files = [f_ for f_ in os.listdir(input_path) if f_.endswith('.nii')]
for f_ in non_gz_files:
    itk.imwrite(itk.imread(os.path.join(input_path, f_)),
                os.path.join(input_path, f_.replace('.nii', '.nii.gz')))

run_segmenter(input_path)
for f_ in non_gz_files:
    os.remove(os.path.join(input_path, f_.replace('.nii', '.nii.gz')))
