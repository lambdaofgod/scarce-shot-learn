import glob
import os
import pathlib
import tarfile

import numpy as np
from skimage.io import imread
from skimage.transform import resize as imresize

from .conf import FEW_SHOT_LEARN_PATH

CUB_DATA_PATH = os.path.join(FEW_SHOT_LEARN_PATH, 'data', 'cub')


def _get_image_basepaths(split_text_filename):
    image_paths = open(os.path.join(CUB_DATA_PATH, 'lists', split_text_filename)).readlines()
    return [os.path.basename(path[:-1]) for path in image_paths]


def _load_images_with_labels(image_paths, image_size):
    images = np.stack([
        imresize(imread(path), image_size)
        for path in image_paths
    ])
    labels = np.array([
        path.split('/')[-2]
        for path in image_paths
    ])

    return images, labels


def load_split(images_dir, split_image_filenames):
    image_paths = glob.glob(os.path.join(images_dir, '*/**'), recursive=True)
    split_image_paths = set(_get_image_basepaths(split_image_filenames))
    return [image_path for image_path in image_paths if os.path.basename(image_path) in split_image_paths]


def prepare_data(data_path):
    pathlib.Path(CUB_DATA_PATH).mkdir(parents=True, exist_ok=True)
    data_path_files = glob.glob(os.path.join(data_path, '**'))
    expected_directories = [
        os.path.join(data_path, path)
        for path in ['images', 'lists', 'attributes']
    ]
    print(expected_directories)
    print(data_path_files)
    if not set(expected_directories).issubset(set(data_path_files)):
        prepare_tars(data_path)


def prepare_tars(data_path):
    data_path_files = glob.glob(os.path.join(data_path, '*'))
    expected_tars = [
        os.path.join(data_path, path + '.tgz')
        for path in ['images', 'lists', 'attributes']
    ]
    if not set(expected_tars).issubset(set(data_path_files)):
        download_tars(data_path)
    else:
        for path in expected_tars:
            print(path)
            tar = tarfile.open(path)
            tar.extractall(path=data_path)
            tar.close()


def download_tars(data_path):
    pass


def load_cub(image_size=(128, 128)):
    prepare_data(CUB_DATA_PATH)

    images_dir = os.path.join(CUB_DATA_PATH, 'images')
    train_image_paths = load_split(images_dir, 'train.txt')
    test_image_paths = load_split(images_dir, 'test.txt')

    return {
        'train': _load_images_with_labels(train_image_paths, image_size),
        'test': _load_images_with_labels(test_image_paths, image_size)
    }