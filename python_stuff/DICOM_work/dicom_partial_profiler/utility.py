import os
import pydicom
from pydicom.filebase import DicomFile
import datetime
from time import strftime, gmtime
from variables import file_header_list
from variables import image_set_header_list
import numpy
import pandas as pd
import re
from datetime import datetime, timedelta

class FileName(object):
    def __init__(self, path):
        '''
        :param path: (string) the file's full path
        '''
        self.path = path
        if not os.path.isfile(path):
            raise FileNotFoundError('{.path} is not a valid file'.format(self))


# funcs
class FileAttributes(FileName):
    def basename(self):
        '''
        :return: the string value of a file path's basename
        '''
        base_name = os.path.basename(self.path)

        return base_name


    def file_size(self):
        """Returns attribute/value list of file size from filepath

        Parameters
        ----------
        filepath : the filepath of jpg or png image

        Returns
        -------
        output : int
        """

        file_size = os.stat(self.path).st_size / 1000000

        return file_size

    def file_creation_date(self):  # TEST
        """Returns attribute/value list of jpg, png, or dcm date

        Parameters
        ----------
        filepath : the filepath of jpg, png, or dcm image

        Returns
        -------
        output : list
        """
        image_creation_date = strftime("%Y-%m-%d %H:%M:%S UTC", gmtime(os.path.getctime(self.path)))

        return image_creation_date

    def file_modification_date(self):
        """Returns attribute/value list of jpg, png, or dcm date

            Parameters
            ----------
            filepath : the filepath of jpg, png, or dcm image

            Returns
            -------
            output : list
            """
        image_modification_date = strftime("%Y-%m-%d %H:%M:%S UTC", gmtime(os.path.getmtime(self.path)))

        return image_modification_date

    def header_test(self):
        status = pydicom.filereader.read_file_meta_info(self.path)

        return status

    def dicom_header(self):
        '''
        :return: a pydicom dicom read object
        '''
        dicom_read = pydicom.read_file(self.path)

        return dicom_read

    def pixel_array(self):
        '''
        :param dcm_header: a pydicom dicom read object
        :return: image array
        '''

        self.dicom_header()
        np_pixel_array = self.dicom_header().pixel_array

        return np_pixel_array

    def image_attributes(self, valid=True):
        """Returns attribute/value list of jpg, png, or dcm color data

        Parameters
        ----------
        file path : the filepath of jpg, png, or dcm image

        Returns
        -------
        output : list
        """
        self.pixel_array()
        image_attribute = {}

        if valid:
            avg_color = numpy.mean(self.pixel_array())
            sd_color_per_row = numpy.std(self.pixel_array(), axis=0)
            sd_color_per_col = numpy.std(self.pixel_array(), axis=1)
            sd_color_of_rows = numpy.std(sd_color_per_row)
            sd_color_of_cols = numpy.std(sd_color_per_col)
            mean_of_sd_rows = numpy.mean(sd_color_per_row)
            mean_of_sd_cols = numpy.mean(sd_color_per_col)
            sd_color_overall = numpy.std(self.pixel_array())
            min_color = numpy.min(self.pixel_array())
            max_color = numpy.max(self.pixel_array())
            color_delta = max_color - min_color

            image_attribute['avg_color'] = avg_color
            image_attribute['sd_color_per_row'] = sd_color_per_row
            image_attribute['sd_color_per_col'] = sd_color_per_col
            image_attribute['sd_color_of_rows'] = sd_color_of_rows
            image_attribute['sd_color_of_cols'] = sd_color_of_cols
            image_attribute['mean_of_sd_rows'] = mean_of_sd_rows
            image_attribute['mean_of_sd_cols'] = mean_of_sd_cols
            image_attribute['sd_color_overall'] = sd_color_overall
            image_attribute['min_color'] = min_color
            image_attribute['max_color'] = max_color
            image_attribute['color_delta'] = color_delta
        else:
            image_attribute['avg_color'] = None
            image_attribute['sd_color_per_row'] = None
            image_attribute['sd_color_per_col'] = None
            image_attribute['sd_color_of_rows'] = None
            image_attribute['sd_color_of_cols'] = None
            image_attribute['mean_of_sd_rows'] = None
            image_attribute['mean_of_sd_cols'] = None
            image_attribute['sd_color_overall'] = None
            image_attribute['min_color'] = None
            image_attribute['max_color'] = None
            image_attribute['color_delta'] = None




        return image_attribute

    @staticmethod
    def get_image_header_dict(header, set_image_header_dict):
        '''
        :param header: a pydicom dicom read object
        :param set_image_header_dict: a dictionary of desired dicom header tags
        :return: a dictionary of the images' dicom file header element value in line with specified desired tags
        '''
        get_image_header_dict = {}
        for elem in set_image_header_dict.keys():
            dcm_image_key = elem
            dcm_image_value = header.get(elem)
            get_image_header_dict[dcm_image_key] = dcm_image_value



        return get_image_header_dict

    @staticmethod
    def get_file_header_dict(header_meta, set_file_header_dict):
        '''
        :param header:  a pydicom dicom read object
        :param set_file_header_dict: a dictionary of desired dicom header tags
        :return: a dictionary of the images' dicom file header element value in line with specified desired tags
        '''
        get_file_header_dictionary = {}
        for elem in set_file_header_dict.keys():
            dcm_file_key = elem
            dcm_file_value = header_meta.get(elem)

            get_file_header_dictionary[dcm_file_key] = dcm_file_value



        return get_file_header_dictionary


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

def parse_valid_header_dicts(
        file_dict,
        header_dict,
        image_attribute,
        file_attributes,
        output_dict,
        file_readable_status=True
):
    '''
    :param file_readable_status:
    :param output_dict:
    :param file_attributes:
    :param image_attribute:
    :param image_attribute_dict:
    :param file_dict: a dictionary containing the dicom header file set data
    :param header_dict: a dictionary containing the dicom header image set data
    :return:
    '''

    # parse the file header
    file_meta_information_version = file_dict.get("FileMetaInformationVersion")
    media_storage_sop_class_uid = file_dict.get("MediaStorageSOPClassUID")
    media_storage_sop_instance_uid = file_dict.get("MediaStorageSOPInstanceUID")
    transfer_syntax_uid = file_dict.get("TransferSyntaxUID")
    implementation_class_uid = file_dict.get("ImplementationClassUID")
    implementation_version_name = file_dict.get("ImplementationVersionName")
    source_application_entity_title = file_dict.get("SourceApplicationEntityTitle")
    sending_application_entity_title = file_dict.get("SendingApplicationEntityTitle")
    receiving_application_entity_title = file_dict.get("ReceivingApplicationEntityTitle")

    # parse image header

    sop_class_uid = header_dict.get("SOPClassUID")
    view_position = header_dict.get("ViewPosition")
    sop_instance_uid = header_dict.get("SOPInstanceUID")
    study_date = header_dict.get("StudyDate")
    series_date = header_dict.get("SeriesDate")
    acquisition_date = header_dict.get("AcquisitionDate")
    content_date = header_dict.get("ContentDate")
    study_time = header_dict.get("StudyTime")
    series_time = header_dict.get("SeriesTime")
    acquisition_time = header_dict.get("AcquisitionTime")
    content_time = header_dict.get("ContentTime")
    accession_number = header_dict.get("AccessionNumber")
    modality = header_dict.get("Modality")
    station_name = header_dict.get("StationName")
    study_description = header_dict.get("StudyDescription")
    series_description = header_dict.get("SeriesDescription")
    manufacturer_model_name = header_dict.get("ManufacturerModelName")
    manufacturer = header_dict.get("Manufacturer")
    irradiation_event_uid = header_dict.get("IrradiationEventUID")
    patient_name = header_dict.get("PatientName")
    patient_id = header_dict.get("PatientID")
    software_versions = header_dict.get("SoftwareVersions")
    imager_pixel_spacing = header_dict.get("ImagerPixelSpacing")
    target_exposure_index = header_dict.get("TargetExposureIndex")
    deviation_index = header_dict.get("DeviationIndex")
    patient_position = header_dict.get("PatientPosition")
    sensitivity = header_dict.get("Sensitivity")
    study_instance_uid = header_dict.get("StudyInstanceUID")
    series_instance_uid = header_dict.get("SeriesInstanceUID")
    study_id= header_dict.get("StudyID")
    series_number = header_dict.get("SeriesNumber")
    acquisition_number = header_dict.get("AcquisitionNumber")
    instance_number = header_dict.get("InstanceNumber")
    patient_orientation = header_dict.get("PatientOrientation")
    photometric_interpretation = header_dict.get("PhotometricInterpretation")
    rows = header_dict.get("Rows")
    columns = header_dict.get("Columns")
    pixel_spacing = header_dict.get("PixelSpacing")
    pixel_aspect_ratio = header_dict.get("PixelAspectRatio")
    bits_allocated = header_dict.get("BitsAllocated")
    bits_stored = header_dict.get("BitsStored")
    high_bit = header_dict.get("HighBit")
    smallest_image_pixel_value = header_dict.get("SmallestImagePixelValue")
    largest_image_pixel_value = header_dict.get("LargestImagePixelValue")
    window_center = header_dict.get("WindowCenter")
    window_width = header_dict.get("WindowWidth")
    rescale_intercept = header_dict.get("RescaleIntercept")
    rescale_slope = header_dict.get("RescaleSlope")
    rescale_type = header_dict.get("RescaleType")
    lossy_image_compression = header_dict.get("LossyImageCompression")

    # parse image attributes
    avg_color = image_attribute.get('avg_color')
    sd_color_per_row = image_attribute.get('sd_color_per_row')
    sd_color_per_col = image_attribute.get('sd_color_per_col')
    sd_color_of_rows = image_attribute.get('sd_color_of_rows')
    sd_color_of_cols = image_attribute.get('sd_color_of_cols')
    mean_of_sd_rows = image_attribute.get('mean_of_sd_rows')
    mean_of_sd_cols = image_attribute.get('mean_of_sd_cols')
    sd_color_overall = image_attribute.get('sd_color_overall')
    min_color = image_attribute.get('min_color')
    max_color = image_attribute.get('max_color')
    color_delta = image_attribute.get('color_delta')

    # parse file attributes
    file_name = file_attributes.get('file_name')
    basename = file_attributes.get('basename')
    file_size = file_attributes.get('file_size')
    file_creation_date = file_attributes.get('file_creation_date')
    file_modification_date = file_attributes.get('file_modification_date')

    # parse the time stats
    def change_date_format(dt):
        newdate = "{}-{}-{}".format(dt[:4], dt[4:6], dt[6:])

        return newdate


    def get_image_90_day_range(image_date):
        date = datetime.strptime(image_date, "%Y-%m-%d")
        modified_date_up_90 = date + timedelta(days=90)
        modified_date_convert_u90 = datetime.strftime(modified_date_up_90, "%Y-%m-%d")

        modified_date_down_90 = date - timedelta(days=90)
        modified_date_convert_d90 = datetime.strftime(modified_date_down_90, "%Y-%m-%d")

        return modified_date_convert_u90, modified_date_convert_d90

    if study_date:
        converted_date = change_date_format(study_date)
        (
            nintey_days_up,
            ninety_days_down
        ) = get_image_90_day_range(converted_date)
    else:
        converted_date = None
        nintey_days_up = None
        ninety_days_down = None

    output_dict["file_name"].append(file_name)
    output_dict["basename"].append(basename)
    output_dict["file_size"].append(file_size)
    output_dict["file_creation_date"].append(file_creation_date)
    output_dict["file_modification_date"].append(file_modification_date)
    output_dict["file_readable_status"].append(file_readable_status)
    output_dict["modality"].append(modality)
    output_dict["patient_name"].append(patient_name)
    output_dict["patient_id"].append(patient_id)
    output_dict["accession_number"].append(accession_number)
    output_dict["study_description"].append(study_description)
    output_dict["series_description"].append(series_description)
    output_dict["view_position"].append(view_position)
    output_dict["patient_orientation"].append(patient_orientation)
    output_dict["patient_position"].append(patient_position)
    output_dict["study_date"].append(study_date)
    output_dict["converted_date"].append(converted_date)
    output_dict["90_days_up"].append(nintey_days_up)
    output_dict["90_days_down"].append(ninety_days_down)
    output_dict["series_date"].append(series_date)
    output_dict["content_date"].append(content_date)
    output_dict["acquisition_date"].append(acquisition_date)
    output_dict["study_time"].append(study_time)
    output_dict["series_time"].append(series_time)
    output_dict["acquisition_time"].append(acquisition_time)
    output_dict["content_time"].append(content_time)
    output_dict["station_name"].append(station_name)
    output_dict["manufacturer_model_name"].append(manufacturer_model_name)
    output_dict["manufacturer"].append(manufacturer)
    output_dict["software_versions"].append(software_versions)
    output_dict["study_id"].append(study_id)
    output_dict["study_instance_uid"].append(study_instance_uid)
    output_dict["series_instance_uid"].append(series_instance_uid)
    output_dict["acquisition_number"].append(acquisition_number)
    output_dict["series_number"].append(series_number)
    output_dict["instance_number"].append(instance_number)
    output_dict["sop_class_uid"].append(sop_class_uid)
    output_dict["sop_instance_uid"].append(sop_instance_uid)
    output_dict["irradiation_event_uid"].append(irradiation_event_uid)
    output_dict["imager_pixel_spacing"].append(imager_pixel_spacing)
    output_dict["target_exposure_index"].append(target_exposure_index)
    output_dict["deviation_index"].append(deviation_index)
    output_dict["sensitivity"].append(sensitivity)
    output_dict["photometric_interpretation"].append(photometric_interpretation)
    output_dict["rows"].append(rows)
    output_dict["columns"].append(columns)
    output_dict["pixel_spacing"].append(pixel_spacing)
    output_dict["pixel_aspect_ratio"].append(pixel_aspect_ratio)
    output_dict["bits_allocated"].append(bits_allocated)
    output_dict["bits_stored"].append(bits_stored)
    output_dict["high_bit"].append(high_bit)
    output_dict["smallest_image_pixel_value"].append(smallest_image_pixel_value)
    output_dict["largest_image_pixel_value"].append(largest_image_pixel_value)
    output_dict["window_center"].append(window_center)
    output_dict["window_width"].append(window_width)
    output_dict["rescale_intercept"].append(rescale_intercept)
    output_dict["rescale_slope"].append(rescale_slope)
    output_dict["rescale_type"].append(rescale_type)
    output_dict["lossy_image_compression"].append(lossy_image_compression)
    output_dict["file_meta_information_version"].append(file_meta_information_version)
    output_dict["media_storage_sop_class_uid"].append(media_storage_sop_class_uid)
    output_dict["media_storage_sop_instance_uid"].append(media_storage_sop_instance_uid)
    output_dict["transfer_syntax_uid"].append(transfer_syntax_uid)
    output_dict["implementation_class_uid"].append(implementation_class_uid)
    output_dict["implementation_version_name"].append(implementation_version_name)
    output_dict["source_application_entity_title"].append(source_application_entity_title)
    output_dict["sending_application_entity_title"].append(sending_application_entity_title)
    output_dict["receiving_application_entity_title"].append(receiving_application_entity_title)
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

    return output_dict


