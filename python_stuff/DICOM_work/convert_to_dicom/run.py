from util import convert_array_to_dcm_slice
from util import convert_image_to_dicom

import logging
import os
from datetime import datetime
from pathlib import Path
from zipfile import ZipFile

import pathtools
import numpy as np
import pydicom
from PIL import Image
from pydicom.dataset import Dataset, FileMetaDataset
from pydicom.sequence import Sequence

log = logging.getLogger(__name__)
directory = r'C:\archive\VinBigData\train'
listOfFiles = list()


if __name__ == '__main__':


    for (dirpath, dirnames, filenames) in os.walk(directory):
        listOfFiles += [os.path.join(dirpath, file) for file in filenames]


    for dcmfile in listOfFiles:
        if dcmfile.endswith('.jpg'):
            filename = dcmfile
            newdirpath = (os.path.dirname(filename))
            prebasename = (os.path.basename(dcmfile))
            basename = (os.path.splitext(prebasename)[0])
            print(basename)
            print(filename)
            print(newdirpath)
            convert_image_to_dicom(filename, newdirpath, basename)
