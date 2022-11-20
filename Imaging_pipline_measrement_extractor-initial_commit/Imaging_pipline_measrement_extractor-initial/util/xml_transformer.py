import pandas as pd
import logging
from typing import NamedTuple
import xml.etree.ElementTree as ET
import os
import logging
from common.constants import xml_tag_dictionary
from datetime import datetime
from common.constants import ConfigFile, patient_level_xml_dict,\
    series_level_xml_dict, study_level_xml_dict,\
    report_file_date_dict, patient_file_name_dict, measurement_level_dict
from path import Path
from itertools import chain
from util.local_storage import LocalStorage
from common.constants import LocalStorageLocation
from util.s3 import S3BucketConnector
from common.custom_expression import WrongSourceHeaderException


class XmlConfig(NamedTuple):
    """
    Class for source configuration data


    """
    src_columns: list
    src_format: str


class XmlEtl:
    """
    Reads the xml file, transforms and writes the transformed to target
    """

    def __init__(self, local: LocalStorage, config, s3_bucket_src: S3BucketConnector,
                s3_bucket_trg: S3BucketConnector, src_args: XmlConfig,
                file_format='xml'):
        """
        Constructor for xmlTransformer

        :param s3_bucket_src: connection to source S3 bucket
        :param s3_bucket_trg: connection to target S3 bucket
        :param meta_key: used as self.meta_key -> key of meta file
        :param src_args: NamedTouple class with source configuration data
        :param trg_args: NamedTouple class with target configuration data
        """
        self.output_folder = LocalStorageLocation.OUTPUT.value
        self.config = config
        self.file_format = file_format
        self.local = local
        self._logger = logging.getLogger(__name__)
        self.s3_bucket_src = s3_bucket_src
        self.s3_bucket_trg = s3_bucket_trg
        self.src_args = src_args

        # we will need the local storage information

    def extract_s3(self):
        """
        Read the source data and concatenates them to single pandas DataFrame

        :returns:
          data_frame: Pandas DataFrame with the extracted data
        """

        # Go to S3 and get the file
        self._logger.info('Extracting S3 source files started...')
        pass

    def extract_local(self):
        """
        Get a list of xml files from the incoming folder

        :returns:list of xml files
        """

        # Go to local drive and get the files

        self._logger.info(f'Extracting {self.file_format} from the local source ----------> started')
        print(f'Extracting local source files started...{self.file_format}')
        pre_list = self.local.list_files_in_local_storage(self.file_format)

        # run list of files through the rigor
        final_list = self.local.get_final_file_list(pre_list)

        return final_list

    def transform(self, list_files: list):
        """

        :param list_files: final list of xml files to parse
        :return: None
        """
        self._logger.info('Starting the XMTransformation process...')
        for file in list_files:
            # initialize the xml parser
            # pass files into the xml parser
            xparser = XmlParser(file, self.config)
            final_df = xparser.xml_parser_etl()
            # quick run to rename the columns to a standard naming
            final_df = xparser.clean_column_names(final_df)
            # save the dict
            results = self.load_local(final_df, file)
            if results:
                self.local.write_metadata(file)
                self.local.move_processed_file(file)


    def load_s3(self, data_frame: pd.DataFrame):
        """
        Saves a Pandas DataFrame to the target

        :param data_frame: Pandas DataFrame as Input
        """

        # save file as patient name_time
        pass

    def load_local(self, df, file_name):
        """

        :param df:
        :param file_name:
        :return:
        """
        self._logger.info('Saving the transformed XML file as a CSV')
        file_base_name = os.path.basename(file_name)
        patient_id = file_base_name.split('_')[0]
        print(patient_id)
        # check the headers make sure all are counted for
        if all(value in df.columns for value in self.src_args.src_columns):
            try:
                dir = self.output_folder
                df.to_csv(f"{dir}\\{patient_id}_xml_{datetime.now().strftime('%m-%d-%Y_%H-%M-%S')}.csv",
                    index=False)
                return True

            except Exception as error:
                print(error)
                self._logger.critical('Failed to save transform XML as a CSV')
                return False
        else:
            self._logger.critical('The transformed XML has missing headers')
            raise WrongSourceHeaderException

    def etl(self):
        """
        Single run to process the xml files
        :return:
        """
        self._logger.info('Staring xml ETL process ---------->')
        xml_files = self.extract_local()
        self.transform(xml_files)


class XmlParser:
    """
    Extract data elements from the xml to the main
    return: output dictionary
    """
    def __init__(self, xml_file: str, config):
        """

        :param xml_file:
        :param config: a safe loaded yaml file
        """
        self.xml_file = xml_file
        self.tree = ET.parse(xml_file)
        self.root = self.tree.getroot()
        self._logger = logging.getLogger(__name__)

        # get the xml args
        self.xml_args = config['xml_root']

    def xml_parser_measurement_level(self):
        """
        extracts measurement level xml elements
        """
        self._logger.info(f'Working on parsing XML file {self.xml_file} ---------->')
        self._logger.info('Parsing XML file at the measurement level')
        measurement_dict = measurement_level_dict
        root = self.xml_args['MeasurementList']['root']
        level = self.xml_args['MeasurementList']['level']
        # level is none
        measurement_level = self.root[root]
        for ele in measurement_level:
            finding_number = ele.get('Name')
            measurement_dict['finding_number'].append(finding_number)

            radiologist_comment = ele.get('Comment')
            if radiologist_comment == '':
                radiologist_comment = 'None'
            measurement_dict['radiologist_comment'].append(radiologist_comment)

            organ = ele.get('Organ')
            measurement_dict['organ'].append(organ)

            nodule_type = ele.get('NoduleType')
            measurement_dict['nodule_type'].append(nodule_type)

            lung_laterility = ele.get('LungLaterality')
            measurement_dict['lung_laterility'].append(lung_laterility)

            lung_quandrant = ele.get('LungLobe')
            measurement_dict['lung_quandrant'].append(lung_quandrant)

            finding_type = ele.get('FindingCategory')
            measurement_dict['finding_type'].append(finding_type)

            group_id = ele.get('GroupUID')
            measurement_dict['group_id'].append(group_id)

            study_date_measurement = ele[0].get('StudyDate')
            study_date_measurement = datetime.strptime(study_date_measurement.strip(), "%m/%d/%Y").date()
            study_date_measurement = study_date_measurement.strftime("%Y%m%d")
            measurement_dict['study_date_measurement'].append(study_date_measurement)

            study_id = ele[0].get('StudyUID')
            measurement_dict['study_id'].append(study_id)

            series_id = ele[0][0].get('SeriesUID')
            measurement_dict['series_id'].append(series_id)

            series_number = ele[0][0].get('SeriesNumber')
            measurement_dict['series_number'].append(series_number)

            # check the for volume tag
            lut_volume_name = xml_tag_dictionary.get(0)
            potential_volume_name = (ele[1][0].get('Name'))
            if lut_volume_name == potential_volume_name:
                volume_value = (ele[1][0].get('Value'))
                measurement_dict['volume_value'].append(volume_value)

            else:
                print(False)
                measurement_dict['volume_value'].append('None')

            # check the for Area tag
            lut_area_name = xml_tag_dictionary.get(1)
            potential_area_name = (ele[1][1].get('Name'))
            if lut_area_name.lower() == potential_area_name.lower():

                area_name = (ele[1][1].get('Value'))
                measurement_dict['area_name'].append(area_name)
            else:
                print(False)
                measurement_dict['area_name'].append(None)

            # check the for Shape_Compactness tag
            lut_shape_compactness_name = xml_tag_dictionary.get(2)
            potential_shape_compactness_name = (ele[1][2].get('Name'))
            if lut_shape_compactness_name.lower() == potential_shape_compactness_name.lower():

                shape_compactness_name = (ele[1][2].get('Value'))
                measurement_dict['shape_compactness_name'].append(shape_compactness_name)
            else:
                print(False)
                measurement_dict['shape_compactness_name'].append(None)

            # check the for Min tag
            lut_min_name = xml_tag_dictionary.get(3)
            potential_min_name = (ele[1][3].get('Name'))
            if lut_min_name.lower() == potential_min_name.lower():

                min_name = (ele[1][3].get('Value'))
                measurement_dict['min_name'].append(min_name)
            else:
                print(False)
                measurement_dict['min_name'].append(None)

            # check the for Max tag
            lut_max_name = xml_tag_dictionary.get(4)
            potential_max_name = (ele[1][4].get('Name'))
            if lut_max_name.lower() == potential_max_name.lower():

                max_name = (ele[1][4].get('Value'))
                measurement_dict['max_name'].append(max_name)
            else:
                print(False)
                measurement_dict['max_name'].append(None)

            # check the for Mean tag
            lut_mean_name = xml_tag_dictionary.get(5)
            potential_mean_name = (ele[1][5].get('Name'))
            if lut_mean_name.lower() == potential_mean_name.lower():

                mean_name = (ele[1][5].get('Value'))
                measurement_dict['mean_name'].append(mean_name)
            else:
                print(False)
                measurement_dict['mean_name'].append(None)

            # check the for SDev tag
            lut_sdev_name = xml_tag_dictionary.get(6)
            potential_sdev_name = (ele[1][6].get('Name'))
            if lut_sdev_name.lower() == potential_sdev_name.lower():

                sdev_name = (ele[1][6].get('Value'))
                measurement_dict['sdev_name'].append(sdev_name)
            else:
                print(False)
                measurement_dict['sdev_name'].append(None)

            # check the for d1 tag
            lut_d1_name = xml_tag_dictionary.get(7)
            potential_d1_name = (ele[1][7].get('Name'))
            if lut_d1_name.lower() == potential_d1_name.lower():

                d1_name = (ele[1][7].get('Value'))
                measurement_dict['d1_name'].append(d1_name)
            else:
                print(False)
                measurement_dict['d1_name'].append(None)

            # check the for d2 tag
            lut_d2_name = xml_tag_dictionary.get(8)
            potential_d2_name = (ele[1][8].get('Name'))
            if lut_d2_name.lower() == potential_d2_name.lower():

                d2_name = (ele[1][8].get('Value'))
                measurement_dict['d2_name'].append(d2_name)
            else:
                print(False)
                measurement_dict['d2_name'].append(None)

            # check the for d1xd2 tag
            lut_d1xd2_name = xml_tag_dictionary.get(9)
            potential_d1xd2_name = (ele[1][9].get('Name'))
            if lut_d1xd2_name.lower() == potential_d1xd2_name.lower():

                d1xd2_name = (ele[1][9].get('Value'))
                measurement_dict['d1xd2_name'].append(d1xd2_name)
            else:
                print(False)
                measurement_dict['d1xd2_name'].append(None)

            # check the for d1xd2 tag
            lut_avg_diameter_name = xml_tag_dictionary.get(10)
            potential_avg_diameter_name = (ele[1][10].get('Name'))
            if lut_avg_diameter_name.lower() == potential_avg_diameter_name.lower():

                avg_diameter_name = (ele[1][10].get('Value'))
                measurement_dict['avg_diameter'].append(avg_diameter_name)
            else:
                print(False)
                measurement_dict['avg_diameter'].append(None)

        return measurement_dict

    def xml_parser_study_level(self):
        """
        extracts study level xml elements
        """
        self._logger.info('Parsing XML file at the study level')
        study_dict = study_level_xml_dict
        root = self.xml_args['GeneralStudyRevision']['root']
        level = self.xml_args['GeneralStudyRevision']['level']
        study_level = self.root[root][level]

        # study date
        study_date_dicom_format = study_level.findtext('StudyDateDicomFormat')

        # get study instance uid
        study_instance_uid = study_level.findtext('StudyInstanceUID')

        study_dict['study_date_dicom_format'].append(study_date_dicom_format)
        study_dict['study_instance_uid'].append(study_instance_uid)

        return study_dict

    def xml_parser_patient_level(self):
        """
        extract patient level xml elements
        :return: None
        """
        self._logger.info('Parsing XML file at the patient level')
        patient_dict = patient_level_xml_dict
        root = (self.xml_args['PatientRevision']['root'])
        level = (self.xml_args['PatientRevision']['level'])
        patient_level = self.root[root][level]

        # get patient name
        patient_name_tag = patient_level.find('DisplayName')
        patient_dict['patient_name_tag_value'].append(patient_name_tag.text)

        # get the patient value
        patient_id_tag = patient_level.find('ID')
        patient_dict['patient_id_tag_value'].append(patient_id_tag.text)

        return patient_dict

    def xml_parser_series_level(self):
        """
        extracts series level xml elements
        """
        self._logger.info('Parsing XML file at the series level')
        series_dict = series_level_xml_dict
        root = self.xml_args['GeneralSeriesRevision']['root']
        level = self.xml_args['GeneralSeriesRevision']['level']
        series_level = self.root[root][level]

        # get modality, series desc, serius uid, series nuber
        modality = series_level.findtext('Modality')
        series_description = series_level.findtext('SeriesDescription')
        series_instance_uid = series_level.findtext('SeriesInstanceUID')
        series_number = series_level.findtext('SeriesNumber')

        # fill dict
        series_dict['modality'].append(modality)
        series_dict['series_description'].append(series_description)
        series_dict['series_instance_uid'].append(series_instance_uid)
        series_dict['series_number'].append(series_number)

        return series_dict

    def get_report_file_date(self):
        """
        The file name contains the patient's name.
        :param file_name:
        :return: string value of report's date DDMMYYYY
        """
        report_date_dict = report_file_date_dict
        file_base_name = os.path.basename(self.xml_file)
        report_date_string = file_base_name.split('_')[3]
        report_date_string_DDMMYY = report_date_string[0:8]
        report_date = datetime.strptime(report_date_string_DDMMYY, "%d%m%Y").date()
        report_date = report_date.strftime("%Y%m%d")
        # update the dictionary
        report_date_dict['report_date'].append(report_date)

        return report_date_dict

    def get_patient_file_name(self):
        """
        The file name contains the patient's name. This wrangles the file name to get the
        patient's name
        :return: string value of patient's name
        """
        patient_dict = patient_file_name_dict
        file_base_name = os.path.basename(self.xml_file)
        try:
            patient_name_file = file_base_name.split('_')[0]
        except Exception as error:
            patient_name_file = None
            print(error)
        patient_dict['patient_name_file'].append(patient_name_file)

        return patient_dict

    def data_element_loader(self):
        """
        The main run for extracting each level
        and loading the main dictionary
        :return: list of dictionary of xml elements
        """
        self._logger.info('Generating the XML measurement file final dictionary')
        _patient_level_xml_dict = self.xml_parser_patient_level()
        _study_level_xml_dict = self.xml_parser_study_level()
        _series_level_xml_dict = self.xml_parser_series_level()
        _report_file_date_dict = self.get_report_file_date()
        _patient_file_name_dict = self.get_patient_file_name()

        # the main dictionary that hold all findings
        _measurement_level_dict = self.xml_parser_measurement_level()

        # convert the main dictionary to a dataframe
        df = self.dict_dataframe(_measurement_level_dict)

        # add report Date
        report_date = _report_file_date_dict.get('report_date')
        report_date = str(report_date).replace('[', '').replace(']', '')
        report_date = (report_date.strip('\''))
        df.insert(1, 'Report_Date', report_date)

        # add patient file dictionary
        patient_name_file = _patient_file_name_dict.get('patient_name_file')
        patient_name_file = str(patient_name_file).replace('[', '').replace(']', '')
        patient_name_file = (patient_name_file.strip('\''))
        df.insert(0, 'Patient_name_on_file', patient_name_file)

        # add patient level dictionary

        patient_name_tag_value = _patient_level_xml_dict.get('patient_name_tag_value')
        patient_id_tag_value = patient_level_xml_dict.get('patient_id_tag_value')
        patient_name_tag_value = str(patient_name_tag_value).replace('[', '').replace(']', '')
        patient_id_tag_value = str(patient_id_tag_value).replace('[', '').replace(']', '')
        patient_name_tag_value = (patient_name_tag_value.strip('\''))
        patient_id_tag_value = (patient_id_tag_value.strip('\''))
        df.insert(0, 'Patient_name_on_xml_tag', patient_name_tag_value)
        df.insert(0, 'Patient_ID_on_xml_tag', patient_id_tag_value)

        # add study level
        study_date_dicom_format = _study_level_xml_dict.get('study_date_dicom_format')
        study_instance_uid = _study_level_xml_dict.get('study_instance_uid')

        study_date_dicom_format = str(study_date_dicom_format).replace('[', '').replace(']', '')
        study_date_dicom_format = (study_date_dicom_format.strip('\''))

        study_instance_uid = str(study_instance_uid).replace('[', '').replace(']', '')
        study_instance_uid = (study_instance_uid.strip('\''))
        df.insert(13, 'study_instance_uid', study_instance_uid)
        df.insert(4, 'study_date_dicom_format', study_date_dicom_format)


        # add series level
        # ['modality', 'series_description', 'series_instance_uid', 'series_number']
        modality = _series_level_xml_dict.get('modality')
        modality = str(modality).replace('[', '').replace(']', '')
        modality = (modality.strip('\''))
        df.insert(13, 'modality', modality)

        series_description = _series_level_xml_dict.get('patient_name_file')
        series_description = str(series_description).replace('[', '').replace(']', '')
        series_description = (series_description.strip('\''))
        df.insert(13, 'series_description', series_description)

        series_instance_uid = _series_level_xml_dict.get('series_instance_uid')
        series_instance_uid = str(series_instance_uid).replace('[', '').replace(']', '')
        series_instance_uid = (series_instance_uid.strip('\''))
        df.insert(13, 'series_instance_uid', series_instance_uid)

        series_number = _series_level_xml_dict.get('series_number')
        series_number = str(series_number).replace('[', '').replace(']', '')
        series_number = (series_number.strip('\''))
        df.insert(20, 'series_number_measurement_level', series_number)

        return df

    @staticmethod
    def dict_merger(*dictionary_list):
        """
        mergeers all dictionaries into one final dictionary
        :param dictionary_list:
        :return: dictionary
        """

        return dict(chain.from_iterable(d.items() for d in dictionary_list))

    @staticmethod
    def dict_dataframe(dict_measurement:dict):
        """convert dictionary to dataframe"""

        df = pd.DataFrame.from_dict(dict_measurement, orient='columns')

        return df

    @staticmethod
    def clean_column_names(dataframe):
        """
        This is a method to rename the columns to more human friendly
        :param dataframe:
        :return:
        """
        try:
            dataframe.rename(columns={'volume_value':'volume', 'area_name':'area',
                                      'shape_compactness_name': 'shape_compactness','min_name': 'min',
                                      'max_name': 'max', 'mean_name': 'mean', 'sdev_name':'sdev', 'd1_name': 'd1',
                                      'd2_name': 'd2', 'd1xd2_name': 'd1xd2'}, inplace=True)
        except Exception as e:
            print(e)

        return dataframe

    def xml_parser_etl(self):
        """
        run responsible for parsing the xml file
        :return: final dataframe from parsed xml
        """
        final_df = self.data_element_loader()

        return final_df
