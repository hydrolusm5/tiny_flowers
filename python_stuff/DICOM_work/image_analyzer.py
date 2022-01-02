#!/usr/bin/env python3

import logging
import os
import shutil
import pydicom
import pandas as pd
import numpy
import numpy as np
import os
import logging
from time import strftime, gmtime
from PIL import Image
from pydicom import dcmread
import copy
from datetime import datetime
import os

log = logging.getLogger(__name__)
directory = r"image dir...."
path = directory
output_path = path + "\\" + f"image_stats_{datetime.now().strftime('%d-%m-%Y_%H-%M-%S')}.csv"

OUTPUT_TEMPLATE = {
    "file_name": [],
    "file_path": [],
    "manufacturer": [],
    "model": [],
    "bit_allocation": [],
    "photo_interp": [],
    #"pixel_data": [],
    "avg_color": [],
    "sd_color_per_row": [],
    "sd_color_per_col": [],
    "sd_color_of_rows": [],
    "sd_color_of_cols": [],
    "mean_of_sd_rows": [],
    "mean_of_sd_cols": [],
    "sd_color_overall": [],
    "min_color": [],
    "max_color": [],
    "color_delta": [],
    "file_size": [],
    "image_creation_date": [],
    "image_modification_date": [],
    "image_last_access_date": [],
    "view_position": [],
    "processing_desc": [],
    
}

# get image attributes
def get_image_mode(img):
    """Returns attribute/value list of jpg or png mode

    Parameters
    ----------
    img : PIL image object

    Returns
    -------
    output : list
    """
    logging.debug('Getting image mode')

    img_mode = img.mode
    attribute_list = [{'attribute': 'image_mode', 'value': img_mode}]

    return attribute_list


def dcm_to_attribute_list(ds):
    """Turn a pydicom Dataset into a dict with keys derived from the Element tags.

    Parameters
    ----------
    ds : pydicom.filereader.dcmread()
    The data set to turn into an attribute list

    Returns
    -------
    output : list
    """
    logging.debug('Putting dcm metadata into attribute list format')

    output_list = []

    try:
        pixel_data = ds.PixelData
    except Exception as e:
        pixel_data = "none"
        
    try:
        bit_allocation = ds.BitsAllocated
    except Exception as e:
        bit_allocation = "none"
        
    try:
         photo = ds.PhotometricInterpretation
    except Exception as e:  
         photo = "none"
        
    try:
        manufacturer = ds.Manufacturer
    except Exception as e:
        manufacturer = "none"
        
    try:
        model = ds.ManufacturerModelName
    except Exception as e:
        model = "none"
        
    try:
        viewposition = ds.viewposition
    except Exception as e:
        viewposition = "none"
        
    try:
        processing_desc = ds[(0x0018, 0x1400)]
    except Exception as e:
        processing_desc = "none"
        
    return pixel_data, bit_allocation, photo, manufacturer, model, viewposition, processing_desc


def get_color_scale(img):
    """Returns attribute/value list of jpg, png, or dcm color data

    Parameters
    ----------
    filepath : the filepath of jpg, png, or dcm image

    Returns
    -------
    output : list
    """
    logging.debug('Getting image color scale values')

    avg_color = numpy.mean(img)
    sd_color_per_row = numpy.std(img, axis=0)
    sd_color_per_col = numpy.std(img, axis=1)
    sd_color_of_rows = numpy.std(sd_color_per_row)
    sd_color_of_cols = numpy.std(sd_color_per_col)
    mean_of_sd_rows = numpy.mean(sd_color_per_row)
    mean_of_sd_cols = numpy.mean(sd_color_per_col)
    sd_color_overall = numpy.std(img)
    min_color = numpy.min(img)
    max_color = numpy.max(img)
    color_delta = max_color - min_color
    # TODO invalid_image = some kind of measure of contrast to indicate whether image is all gray


    return avg_color, sd_color_per_row,sd_color_per_col,sd_color_of_rows, sd_color_of_cols, mean_of_sd_rows, mean_of_sd_cols, mean_of_sd_cols, sd_color_overall, min_color, max_color, color_delta

def get_image_file_size(filepath):
    """Returns attribute/value list of file size from filepath

    Parameters
    ----------
    filepath : the filepath of jpg or png image

    Returns
    -------
    output : list
    """
    logging.debug('Getting image filesize')

    file_size = os.stat(filepath).st_size / 1000000


    return file_size


def get_image_dates(filepath):  # TEST
    """Returns attribute/value list of jpg, png, or dcm date

    Parameters
    ----------
    filepath : the filepath of jpg, png, or dcm image

    Returns
    -------
    output : list
    """
    logging.debug('Getting image dates')

    image_creation_date = strftime("%Y-%m-%d %H:%M:%S UTC", gmtime(os.path.getctime(filepath)))
    image_modification_date = strftime("%Y-%m-%d %H:%M:%S UTC", gmtime(os.path.getmtime(filepath)))
    image_last_access_date = strftime("%Y-%m-%d %H:%M:%S UTC", gmtime(os.path.getatime(filepath)))


    return image_creation_date, image_modification_date, image_last_access_date


def get_file_details(filepath):
    """Returns dataset information filepath

    Parameters
    ----------
    filepath : the filepath of jpg, png, or dcm image

    Returns
    -------
    output : list
    """
    logging.debug('Getting image format')

    image_dates = get_image_dates(filepath)

    file_size = get_image_file_size(filepath)

def save_csv(output_dict, path):
    """
    Saves the list of roi dictionaries into a .csv file
    Args:
        output_dict (list): a list of ROI dictionaries
        path (PathLike): the location to save the .csv file to

    """

    # Save without index since that clutters the csv and the ROI's will be unique
    df = pd.DataFrame.from_dict(output_dict)
    df.to_csv(path, index=False)

    return df


def main(file):
    try:
        RefDs = dcmread(file)
        # convert DCM to array
        dcm_array = RefDs.pixel_array
        # covert array to an image
        dcm_img = Image.fromarray(np.ones((100, 100, 3), dtype=np.uint8))
        ds = dcmread(file)
        base_name = os.path.basename(file)
        get_file_details(file)
        (pixel_data, bit_allocation, photo, manufacturer, model, viewposition, processing_desc) = dcm_to_attribute_list(ds)
        (avg_color, sd_color_per_row,sd_color_per_col,sd_color_of_rows, sd_color_of_cols, mean_of_sd_rows, mean_of_sd_cols, mean_of_sd_cols, sd_color_overall, min_color, max_color, color_delta) = get_color_scale(dcm_array)
        file_size = get_image_file_size(file)
        (image_creation_date, image_modification_date, image_last_access_date) = get_image_dates(file)

        output_dict["file_name"].append(base_name)
        output_dict["file_path"].append(base_name)
        output_dict["manufacturer"].append(manufacturer)
        output_dict["model"].append(model)
        output_dict["bit_allocation"].append(bit_allocation)
        output_dict["photo_interp"].append(photo)
        #output_dict["pixel_data"].append(pixel_data)
        output_dict["avg_color"].append(avg_color)
        output_dict["sd_color_per_row"].append(sd_color_per_row)
        output_dict["sd_color_per_col"].append(sd_color_per_col)
        output_dict["sd_color_of_rows"].append(sd_color_of_rows)
        output_dict["sd_color_of_cols"].append(sd_color_of_cols)
        output_dict["mean_of_sd_rows"].append(mean_of_sd_rows)
        output_dict["mean_of_sd_cols"].append(mean_of_sd_cols)
        output_dict["sd_color_overall"].append(sd_color_overall)
        output_dict["min_color"].append(min_color)
        output_dict["max_color"].append(max_color)
        output_dict["color_delta"].append(color_delta)
        output_dict["file_size"].append(file_size)
        output_dict["image_creation_date"].append(image_creation_date)
        output_dict["image_modification_date"].append(image_modification_date)
        output_dict["image_last_access_date"].append(image_last_access_date)
        
        output_dict["view_position"].append(viewposition)
        output_dict["processing_desc"].append(processing_desc)

        save_csv(output_dict, output_path)




    except Exception as e:
        log.exception(e, )
        log.fatal("Error executing image-profiler.", )
        return 1

    log.info("image-profiler completed Successfully!")

    return 0



output_dict = copy.deepcopy(OUTPUT_TEMPLATE)

listOfFiles = []
for root, directories, files in os.walk(directory, topdown=False):
    for name in files:
        dcmfile = (os.path.join(root, name))
        if dcmfile.endswith(".dcm"):
            listOfFiles += [os.path.join(root, name)]  # for file in filenames]



if __name__ == "__main__":
    for file in listOfFiles:
        exit_status = main(file)
        log.info("exit_status is %s", exit_status)

    os.sys.exit(exit_status)
