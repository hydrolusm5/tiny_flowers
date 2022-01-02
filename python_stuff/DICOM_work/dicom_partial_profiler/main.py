import os
import pydicom
import datetime
from time import strftime, gmtime
from variables import file_header_list
from variables import OUTPUT_TEMPLATE
from variables import image_set_header_list
from utility import parse_valid_header_dicts
from utility import FileAttributes
import numpy
import copy
from utility import save_csv


file_header_lst = file_header_list
image_header_lst = image_set_header_list
Image_dir = '#image dir'
path = '#save csv path'



def set_image_header_dict(image_set_header_list):
    '''
    :param
        image_set_header_list: a list containing the dicom image set data elements of interest
    :return:
        a dictionary of of desired dicom image set data elements
    '''
    set_image_header_dict = {}
    for item in image_set_header_list:
        set_image_header_dict[item] = item

    return set_image_header_dict


def set_file_header_dict(file_header_list):
    '''
    :param
        file_header_list: a list containing the dicom file set data elements of interest

    :return:
        a dictionary of of desired dicom file set data elements
    '''
    set_file_header_dict = {}
    for item in file_header_list:
        set_file_header_dict[item] = item

    return set_file_header_dict

def get_dicom_images(directory):
    """Create a list of subject directories. Path should be the directory of the source dicom file to be copied
    :param
        a path-like string containing the directory of the images

    :return:
        a list of dicom files found in a directory specified.
    """
    listOfFiles = []
    for root, directories, files in os.walk(directory, topdown=False):
        for name in files:
            dcmfile = (os.path.join(root, name))
            if dcmfile.endswith(".dcm"):
                listOfFiles += [os.path.join(root, name)]  # for file in filenames]

    return listOfFiles



if __name__ == "__main__":
    # get the list of dicom images

    images = get_dicom_images(Image_dir)
    output_dict = copy.deepcopy(OUTPUT_TEMPLATE)
    for image in images:
        dcm_file = FileAttributes(image)
        file_attributes = dict()

        # create file attribute dic
        file_attributes['file_name'] = dcm_file.path
        file_attributes['basename'] = dcm_file.basename()
        file_attributes['file_size'] = dcm_file.file_size()
        file_attributes['file_creation_date'] = dcm_file.file_creation_date()
        file_attributes['file_modification_date'] = dcm_file.file_modification_date()

        # if the file's meta info is good, continue into the logic
        try:
            if dcm_file.header_test():
                file_readable_status = 'Valid'
                # get dicom header
                dcm_file_header = dcm_file.dicom_header()
                dcm_file_header_meta = dcm_file_header.file_meta

                # get image attributes
                image_attribute = dcm_file.image_attributes()

                # create desired dcm tag dictionaries
                image_header_dictionary = set_image_header_dict(image_header_lst)
                file_header_dictionary = set_file_header_dict(file_header_lst)

                # parse the dicom header image file set
                image_header = dcm_file.get_image_header_dict(dcm_file_header, image_header_dictionary)

                # parse the dicom file header set
                file_header = dcm_file.get_file_header_dict(dcm_file_header_meta, file_header_dictionary)

                parse_valid_header_dicts(
                    file_header,
                    image_header,
                    image_attribute,
                    file_attributes,
                    output_dict,
                    file_readable_status
                )

        except Exception as e:
            # file header dict result to none
            file_readable_status = 'invalid'
            file_header = {key: None for key in file_header_lst}
            image_header = {key: None for key in image_header_lst}
            image_attribute = dcm_file.image_attributes(valid=False)

            parse_valid_header_dicts(
                file_header,
                image_header,
                image_attribute,
                file_attributes,
                output_dict,
                file_readable_status
            )

            print(e)

local_folder_df = save_csv(output_dict, path)
