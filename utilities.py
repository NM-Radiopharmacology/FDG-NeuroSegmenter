import datetime
import os
import sys
import shutil
import numpy as np
import itk


def printdt(*args):
    print(datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"), *args)


def run_segmenter(input_path):
    import torch
    cpu = not torch.cuda.is_available()

    if not os.path.isdir(input_path):
        raise FileNotFoundError(f"{input_path} does not exist!")

    output_path = input_path + '_FDG-NeuroSegmenter'
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    printdt("pre-processing images...")
    img_files = [f for f in os.listdir(input_path) if f.endswith('.nii.gz')]
    if len(img_files) == 0:
        print(f"no NIfTI images in {input_path}!")
        sys.exit(0)
    temp_path = input_path + '_FDG-NeuroSegmenter_temp'
    if not os.path.exists(temp_path):
        os.makedirs(temp_path)
    else:
        shutil.rmtree(temp_path)
        os.makedirs(temp_path)

    for i, img_file in enumerate(sorted(img_files)):
        file_extension = img_file.replace(img_file.split('.')[0], '')
        shutil.copy(os.path.join(input_path, img_file),
                    os.path.join(temp_path, f"FDGNeuroSeg_{str(i).zfill(4)}_0000{file_extension}"))

    printdt("running predictions...")
    command = (f"set nnUNet_raw=''&&set nnUNet_preprocessed=''&&"
               f"set nnUNet_results={os.path.join(os.getcwd(), 'models')}&&"
               f"nnUNetv2_predict -i {temp_path} -o {output_path} -d 505 -c 3d_fullres -step_size 0.2")
    if cpu:
        command = command + " -device cpu --disable_tta"
    return_code = os.system(command)
    if return_code == 0:
        for i, img_file in enumerate(sorted(img_files)):
            os.rename(os.path.join(output_path, f"FDGNeuroSeg_{str(i).zfill(4)}.nii.gz"),
                      os.path.join(output_path, img_file.replace('.nii.gz', f'_FDGNeuroSeg.nii.gz')))
        to_remove = [f_ for f_ in os.listdir(output_path) if f_.endswith('.json')]
        for json_file in to_remove:
            os.remove(os.path.join(output_path, json_file))

    shutil.rmtree(temp_path)
    return return_code


def resample_volume(volume, new_spacing, interpolation_mode="bspline"):

    if interpolation_mode == "nearestneighbour":    # for masks
        interpolator = itk.NearestNeighborInterpolateImageFunction
    elif interpolation_mode == "linear":
        interpolator = itk.LinearInterpolateImageFunction
    else:
        interpolator = itk.BSplineInterpolateImageFunction

    if isinstance(volume, str):
        volume = itk.imread(volume)

    original_spacing = itk.spacing(volume)
    original_origin = itk.origin(volume)
    original_size = itk.size(volume)
    original_direction = volume.GetDirection()

    if original_spacing != new_spacing:

        # rounding up the new size! output physical space will be equal or larger to original
        new_size = [int(np.ceil(osz * ospc / nspc)) for osz, ospc, nspc in
                    zip(original_size, original_spacing, new_spacing)]

        return itk.resample_image_filter(
            volume,
            interpolator=interpolator.New(volume),
            size=new_size,
            output_spacing=new_spacing,
            output_origin=original_origin,
            output_direction=original_direction
        )

    else:
        return volume


def resample_to_reference(volume, reference, interpolation_mode="bspline"):

    if interpolation_mode == "nearestneighbour":  # for masks
        interpolator = itk.NearestNeighborInterpolateImageFunction
    elif interpolation_mode == "linear":
        interpolator = itk.LinearInterpolateImageFunction
    else:
        interpolator = itk.BSplineInterpolateImageFunction

    if isinstance(volume, str):
        volume = itk.imread(volume)

    if isinstance(reference, str):
        reference = itk.imread(reference)

    return itk.resample_image_filter(
        volume,
        interpolator=interpolator.New(volume),
        use_reference_image=True,
        reference_image=reference
    )


def get_kernel_size_in_voxels(voxel_physical_size, size_in_mm=6):

    kernel_size = []
    for s in voxel_physical_size:
        n = np.rint(size_in_mm / s)
        if n % 2 == 0:
            n = n + 1
        kernel_size.append(int(n))

    return kernel_size


def get_euclidean_distance(coord1, coord2, voxel_physical_size):
    d = None
    if len(coord1) == len(coord2) == len(voxel_physical_size):
        d2 = 0
        for i, j, s in zip(coord1, coord2, voxel_physical_size):
            d2 = d2 + (abs(j - i) * s) ** 2
        d = np.sqrt(d2)

    return d


def get_spherical_kernel(kernel_size, voxel_physical_size, radius_in_mm=3):

    kernel = None
    if len(kernel_size) == len(voxel_physical_size) == 3:
        kernel_center = [int(np.floor(s / 2)) for s in kernel_size]
        kernel = np.ones(kernel_size)
        for k in range(kernel_size[0]):
            for j in range(kernel_size[1]):
                for i in range(kernel_size[2]):
                    d = get_euclidean_distance(kernel_center, [k, j, i], voxel_physical_size)
                    if d > radius_in_mm:
                        kernel[k, j, i] = 0

    return kernel


def pons_normalisation(arr, pons_seg, erode=True):

    if erode:
        # pons erosion (to avoid including vicinity zeroes)
        from skimage.morphology import erosion
        krnl_sz = get_kernel_size_in_voxels(voxel_physical_size=[1.5, 1.5, 1.5], size_in_mm=8)
        krnl = get_spherical_kernel(kernel_size=krnl_sz, voxel_physical_size=[1.5, 1.5, 1.5])
        pons_seg = erosion(pons_seg, footprint=krnl) * 1.0

    pons_mean = np.mean(arr[pons_seg != 0])

    return arr / pons_mean


