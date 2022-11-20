""" File to store constants """
from enum import Enum

class ConfigFile(Enum):
    """
    config file location
    """
    CONFIG = 'common\\config.yaml'


class LocalStorageLocation(Enum):
    """
    config file location
    """
    INCOMING = "J:\msavoy\incomming"
    OUTPUT = "J:\msavoy\output"
    PROCESSED = "J:\msavoy\processed"
    METADATA = "J:\msavoy\metadata"
    BAD_FILES = r"J:\msavoy\bad_files"
    FINALPRODUCT = r"J:\msavoy\final_product"
    RAW = r"J:\msavoy\raw"
    XML = 'xml'
    CSV = 'csv'
    HDF = 'h5'


class FileTypes(Enum):
    """
    supported file types for S3BucketConnector
    """
    CSV = 'csv'
    XML = 'xml'
    PARQUET = 'parquet'
    LOG = 'log'


class S3FileTypes(Enum):
    """
    supported file types for S3BucketConnector
    """
    CSV = 'csv'
    XML = 'xml'
    PARQUET = 'parquet'

class MetaProcessFormat(Enum):
    """
    formation for MetaProcess class
    """
    META_DATE_FORMAT = '%Y-%m-%d'
    META_PROCESS_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    META_SOURCE_DATE_COL = 'source_date'
    META_PROCESS_COL = 'datetime_of_processing'
    META_FILE_FORMAT = 'csv'



class CsvFileFormat(Enum):
    """
    formation for MetaProcess class
    """
    META_DATE_FORMAT = '%Y-%m-%d'
    META_PROCESS_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    META_SOURCE_DATE_COL = 'source_date'
    META_PROCESS_COL = 'datetime_of_processing'
    META_FILE_FORMAT = 'csv'

class XmlFileFormat(Enum):
    """
    formation for MetaProcess class
    """
    META_DATE_FORMAT = '%Y-%m-%d'
    META_PROCESS_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    META_SOURCE_DATE_COL = 'source_date'
    META_PROCESS_COL = 'datetime_of_processing'
    META_FILE_FORMAT = 'xml'


xml_tag_dictionary = {
  0:'Volume',
  1:'Area',
  2:'Shape Compactness',
  3:'Min',
  4:'Max',
  5:'Mean',
  6:'SDev',
  7:'d1',
  8:'d2',
  9:'d1xd2',
  10:'Avg.Diameter',
  '00080052':'QueryRetrieveLevel',
  '00080054':'RetrieveAETitle',
  '00100020':'PatientID',
  '0020000D':'StudyInstanceUID',
  '00020016':'SourceApplicationEntityTitle'
}

patient_level_xml_dict = {
  'patient_name_tag_value': [],
  'patient_id_tag_value': []
}

study_level_xml_dict = {
  'study_date_dicom_format': [],
  'study_instance_uid': []
}

series_level_xml_dict = {
  'modality': [],
  'series_description': [],
  'series_instance_uid': [],
  'series_number': []
}


report_file_date_dict = {
  'report_date': []
}

patient_file_name_dict = {
  'patient_name_file': []
}

measurement_level_dict = {
  'finding_number': [],
  'radiologist_comment': [],
  'organ': [],
  'nodule_type': [],
  'lung_laterility': [],
  'lung_quandrant': [],
  'finding_type': [],
  'group_id': [],
  'study_date_measurement': [],
  'study_id': [],
  'series_id': [],
  'series_number': [],
  'volume_value': [],
  'area_name': [],
  'shape_compactness_name': [],
  'min_name': [],
  'max_name': [],
  'mean_name': [],
  'sdev_name': [],
  'd1_name': [],
  'd2_name': [],
  'd1xd2_name': [],
  'avg_diameter': []
}

csv_output_study_level_dict = {
    "PatientID": [],
    "StudyDate": [],
    "Finding": [],
    "Img": [],
    "Volume": [],
    "Area": [],
    "Shape Compactness": [],
    "Min": [],
    "Max": [],
    "Mean": [],
    "SDev": [],
    "d1": [],
    "d2": [],
    "d1xd2": [],
    "Avg.Diameter": []
}

csv_element_list = ['Volume', 'Area', 'Shape Compactness',
                'Min', 'Max', 'Mean', 'SDev', 'd1 (RECIST)', 'd2',
                'd1xd2', 'Avg.Diameter', 'Img']

