import os
import shutil
import sys
import torch
cpu = not torch.cuda.is_available()


def printdt(*args):
    import datetime
    print(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), *args)


input_path = None
while input_path is None:
    input_path = input("Introduce path to brain [18F]FDG images: ")
    if not os.path.isdir(input_path):
        print(f"{input_path} is not a directory")
        input_path = None

output_path = input_path + '_FDG-NeuroSegmenter'
if not os.path.exists(output_path):
    os.makedirs(output_path)

printdt("pre-processing images...")
img_files = [f for f in os.listdir(input_path) if f.endswith('.nii.gz') or f.endswith('.nii')]
if len(img_files) == 0:
    print(f"no NIfTI images in {input_path}!")
    sys.exit()
temp_path = input_path + '_FDG-NeuroSegmenter_temp'
if not os.path.exists(temp_path):
    os.makedirs(temp_path)
else:
    shutil.rmtree(temp_path)
    os.makedirs(temp_path)
for i, img_file in enumerate(sorted(img_files)):
    shutil.copy(os.path.join(input_path, img_file),
                os.path.join(temp_path, f"FDGNeuroSeg_{str(i).zfill(4)}_0000.nii.gz"))

printdt("running predictions...")
command = (f"set nnUNet_raw=''&&set nnUNet_preprocessed=''&&"
           f"set nnUNet_results={os.path.join(os.getcwd(), 'models')}&&"
           f"nnUNetv2_predict -i {temp_path} -o {output_path} -d 505 -c 3d_fullres -step_size 0.2")
if cpu:
    command = command + " -device cpu --disable_tta"
os.system(command)

shutil.rmtree(temp_path)
